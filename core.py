"""FocusTM: deterministic FIRMS audit and descriptive analysis (UTC).

No inferred zero-fire months, spatial event clustering, or validated calibration.
Raw files are opened read-only. See docs/YONTEM.md for the scientific contract.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import zipfile
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

import numpy as np
import pandas as pd
import shapefile

BBOX = (26.0 , 36.0, 45.0, 42.0)  # west, south, east, north; WGS84
AS_OF = date(2026, 11, 14)  # dossier reference date, not a live data feed
PLATFORMS = ["Terra", "Aqua", "Suomi-NPP", "NOAA-20", "NOAA-21"]
PLATFORM_MAP = {"Terra": "Terra", "T": "Terra", "Aqua": "Aqua", "A": "Aqua",
                "SNPP": "Suomi-NPP", "N": "Suomi-NPP", "N20": "NOAA-20", "N21": "NOAA-21"}
PRODUCTS = {"M-C61": ("MODIS", {"Terra", "Aqua"}), "SV-C2": ("VIIRS", {"Suomi-NPP"}),
            "J1V-C2": ("VIIRS", {"NOAA-20"}), "J2V-C2": ("VIIRS", {"NOAA-21"})}
NUMERIC = {"latitude", "longitude", "brightness", "scan", "track", "bright_t31", "frp", "type"}
REQUIRED = {"latitude", "longitude", "acq_date", "acq_time", "satellite", "instrument",
            "confidence", "version", "brightness", "scan", "track", "bright_t31", "frp", "daynight"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_utc(acq_date, acq_time) -> datetime:
    d, t = str(acq_date).strip(), str(acq_time).strip()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) or not re.fullmatch(r"\d{1,4}", t):
        raise ValueError("Tarih YYYY-MM-DD, saat HHMM olmalıdır")
    return datetime.strptime(d + " " + t.zfill(4), "%Y-%m-%d %H%M").replace(tzinfo=timezone.utc)


def normalize_record(row: dict, product: str, processing: str) -> dict:
    """Format normalization only: no coordinate rounding or confidence equivalence."""
    r = {str(k).lower(): ("" if v is None else str(v).strip()) for k, v in row.items()}
    if REQUIRED - r.keys():
        raise ValueError("Eksik sütun: " + ", ".join(sorted(REQUIRED - r.keys())))
    platform = PLATFORM_MAP.get(r["satellite"])
    sensor, allowed = PRODUCTS[product]
    if platform not in allowed:
        raise ValueError("Platform ile ürün kodu uyumsuz")
    allowed_instruments = {sensor, "SNPP"} if product == "SV-C2" else {sensor}
    if r["instrument"] not in allowed_instruments:
        raise ValueError("Bilinmeyen instrument değeri")
    ts = parse_utc(r["acq_date"], r["acq_time"])
    if ts.date() > AS_OF:
        raise ValueError("Paket referans tarihinden sonra kayıt")
    r["acq_time"] = ts.strftime("%H%M")
    for col in NUMERIC & r.keys():
        if r[col] == "":
            continue
        value = Decimal(r[col])
        if not value.is_finite():
            raise ValueError("Sonlu olmayan sayısal değer")
        r[col] = format(value.normalize(), "f")
    lat, lon = float(r["latitude"]), float(r["longitude"])
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Geçersiz koordinat")
    if sensor == "MODIS":
        conf = Decimal(r["confidence"])
        if not conf.is_finite() or not 0 <= conf <= 100:
            raise ValueError("MODIS güven değeri aralık dışında")
        r["confidence"] = format(conf.normalize(), "f")
    elif r["confidence"] not in {"l", "n", "h"}:
        raise ValueError("VIIRS güven sınıfı bilinmiyor")
    if r["daynight"] not in {"D", "N"}:
        raise ValueError("Gündüz/gece değeri bilinmiyor")
    if processing == "nrt" and "NRT" not in r["version"].upper():
        raise ValueError("Dosya NRT ama version NRT değil")
    if processing == "archive" and "NRT" in r["version"].upper():
        raise ValueError("Dosya arşiv ama version NRT")
    r.update(product=product, processing=processing, platform=platform, sensor=sensor,
             timestamp_utc=ts.isoformat(), instrument_raw=r.pop("instrument"))
    r.setdefault("type", "")
    return r


def record_hash(r: dict) -> str:
    return sha256(json.dumps(r, sort_keys=True, ensure_ascii=False).encode())


def inspect_zips(paths) -> tuple[pd.DataFrame, dict, pd.DataFrame]:
    """Read every format; exact normalized records count once, provenance stays.

    Fail on conflicting attributes at the same exact platform/time/coordinate/stage.
    Archive wins only for an exact same-position/time NRT observation, with audit.
    No fuzzy cross-sensor deduplication is attempted.
    """
    unique, provenance, inventory, members, rejected = {}, [], [], [], []
    zip_hashes = {}
    for path in sorted(map(Path, paths), key=lambda p: p.name):
        zip_hashes[path.name] = sha256(path.read_bytes())
        with zipfile.ZipFile(path) as z:
            bad = z.testzip()
            if bad:
                raise ValueError(f"Bozuk ZIP üyesi: {bad}")
            for info in z.infolist():
                blob = z.read(info.filename)
                members.append(dict(zip=path.name, member=info.filename, bytes=info.file_size,
                                    sha256=sha256(blob)))
            for member in sorted(z.namelist(), key=lambda n: ({".csv": 0, ".json": 1, ".shp": 2}.get(Path(n).suffix, 9), n)):
                match = re.fullmatch(r"fire_(archive|nrt)_(M-C61|SV-C2|J1V-C2|J2V-C2)_\d+\.(csv|json|shp)", member)
                if not match:
                    continue
                stage, product, fmt = match.groups()
                geometry_errors = 0
                crs = None
                if fmt == "csv":
                    reader = csv.DictReader(io.StringIO(z.read(member).decode("utf-8-sig")))
                    fields, rows = list(reader.fieldnames or []), list(reader)
                elif fmt == "json":
                    rows = json.loads(z.read(member))
                    if not isinstance(rows, list):
                        raise ValueError("JSON bir kayıt dizisi olmalı")
                    fields = sorted({k for r in rows for k in r})
                else:
                    stem = member[:-4]
                    crs = z.read(stem + ".prj").decode()
                    if '"4326"' not in crs or 'WGS 84' not in crs:
                        raise ValueError("Shapefile CRS doğrulanamadı")
                    reader = shapefile.Reader(shp=io.BytesIO(z.read(member)),
                                              shx=io.BytesIO(z.read(stem + ".shx")),
                                              dbf=io.BytesIO(z.read(stem + ".dbf")), encoding="utf-8")
                    fields = [f[0] for f in reader.fields[1:]]
                    rows = []
                    for sr in reader.iterShapeRecords():
                        r = {k.lower(): v for k, v in sr.record.as_dict().items()}
                        if len(sr.shape.points) != 1 or not np.allclose(
                            sr.shape.points[0], [r["longitude"], r["latitude"]], rtol=0, atol=1e-9):
                            geometry_errors += 1
                        rows.append(r)
                    reader.close()
                hashes, valid_records = [], []
                for row_number, row in enumerate(rows, 1):
                    try:
                        r = normalize_record(row, product, stage)
                    except (ValueError, InvalidOperation, KeyError) as exc:
                        rejected.append(dict(zip=path.name, member=member, row=row_number, reason=str(exc)))
                        continue
                    h = record_hash(r)
                    hashes.append(h)
                    valid_records.append(r)
                    # CSV preference is only about provenance: values must be equal.
                    unique.setdefault(h, r)
                    provenance.append(dict(record_id=h, source_zip=path.name, source_member=member,
                                           source_row=row_number, source_format=fmt))
                sample = pd.DataFrame(valid_records)
                inventory.append(dict(zip=path.name, member=member, format=fmt, product=product,
                    processing=stage, rows=len(rows), valid_rows=len(hashes), unique_rows=len(set(hashes)),
                    first_date=sample.acq_date.min() if len(sample) else None,
                    last_date=sample.acq_date.max() if len(sample) else None,
                    columns=fields, platforms=sorted(sample.platform.unique()) if len(sample) else [],
                    versions=sorted(sample.version.unique()) if len(sample) else [],
                    canonical_sha256=sha256("\n".join(sorted(hashes)).encode()),
                    geometry_errors=geometry_errors, crs=crs,
                    readme=z.read("Readme.txt").decode() if "Readme.txt" in z.namelist() else None))
                if geometry_errors:
                    raise ValueError(f"Geometri ve tablo eşleşmiyor: {member}")
    if not unique:
        raise ValueError("Okunabilir FIRMS kaydı bulunamadı")
    frame = pd.DataFrame([dict(r, record_id=h) for h, r in unique.items()])
    identity = ["platform", "timestamp_utc", "latitude", "longitude"]
    if frame.duplicated(identity + ["processing"], keep=False).any():
        raise ValueError("Aynı gözlem anahtarında çelişen alanlar var; ham veri incelemesi gerekli")
    frame = frame.sort_values("processing")  # archive before nrt
    superseded = frame[frame.duplicated(identity, keep="first")].record_id.tolist()
    frame = frame.drop_duplicates(identity, keep="first")
    frame["timestamp_utc"] = pd.to_datetime(frame.timestamp_utc, utc=True)
    for col in NUMERIC:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    frame["type"] = frame["type"].astype("Int64")
    frame["month"] = frame.timestamp_utc.dt.strftime("%Y-%m")
    frame["year"] = frame.timestamp_utc.dt.year
    frame = frame.sort_values(["timestamp_utc", "platform", "latitude", "longitude"]).reset_index(drop=True)
    prov = pd.DataFrame(provenance).drop_duplicates().sort_values(["record_id", "source_format", "source_zip", "source_row"])
    preferred = prov.drop_duplicates("record_id").set_index("record_id")
    for col in ["source_zip", "source_member", "source_row"]:
        frame[col] = frame.record_id.map(preferred[col])
    frame["source_copy_count"] = frame.record_id.map(prov.groupby("record_id").size())
    equivalence = []
    for (product, stage), files in pd.DataFrame(inventory).groupby(["product", "processing"]):
        equivalence.append(dict(product=product, processing=stage,
            formats=sorted(files.format.unique()), copies=len(files),
            exact_equal=bool(files.canonical_sha256.nunique() == 1), rows=int(files.iloc[0].rows)))
    audit = dict(reference_date=AS_OF.isoformat(), bbox=list(BBOX), zip_sha256=zip_hashes,
                 members=members, inventory=inventory, format_equivalence=equivalence,
                 physical_rows=sum(x["rows"] for x in inventory), canonical_records=len(frame),
                 duplicate_copies_removed=sum(x["valid_rows"] for x in inventory) - len(unique),
                 archive_superseded_nrt_ids=superseded, rejected=rejected,
                 coverage_verified=False, download_request_metadata_available=False)
    return frame, audit, prov


def validate_bbox(bbox, enforce_source=True):
    w, s, e, n = map(float, bbox)
    if not all(np.isfinite([w, s, e, n])) or not (-180 <= w < e <= 180 and -90 <= s < n <= 90):
        raise ValueError("Batı < doğu, güney < kuzey olmalı; koordinatlar geçerli aralıkta olmalı")
    if enforce_source and not (BBOX[0] <= w and BBOX[1] <= s and e <= BBOX[2] and n <= BBOX[3]):
        raise ValueError("Paket yalnızca 29.5, 36.1, 32.8, 37.5 kutusu içindeki alt bölgeleri destekler")
    return w, s, e, n


def utc_day(value):
    ts = pd.Timestamp(value)
    ts = ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")
    return ts.normalize()


def filter_data(frame, start, end, bbox=BBOX, platforms=None, stages=None,
                confidence="all", type_mode="all"):
    w, s, e, n = validate_bbox(bbox)
    a, b = utc_day(start), utc_day(end)
    if a > b:
        raise ValueError("Başlangıç tarihi bitişten sonra olamaz")
    mask = (frame.longitude.between(w, e) & frame.latitude.between(s, n)
            & frame.timestamp_utc.ge(a) & frame.timestamp_utc.lt(b + pd.Timedelta(days=1)))
    if platforms is not None:
        mask &= frame.platform.isin(platforms)
    if stages is not None:
        mask &= frame.processing.isin(stages)
    if confidence == "screened":
        # Pedagogic sensitivity filter, never claimed to equate sensor detection quality.
        mask &= ((frame.sensor.eq("MODIS") & pd.to_numeric(frame.confidence, errors="coerce").ge(30))
                 | (frame.sensor.eq("VIIRS") & frame.confidence.isin(["n", "h"])))
    elif confidence != "all":
        raise ValueError("Bilinmeyen güven filtresi")
    if type_mode == "vegetation":
        mask &= frame["type"].eq(0).fillna(False)
    elif type_mode != "all":
        raise ValueError("Bilinmeyen tür filtresi")
    return frame.loc[mask].copy().reset_index(drop=True)


def monthly_counts(filtered, full, start, end, platforms):
    """Positive detection counts; empty months stay NA even inside record extents.

    Extent and observed days are descriptive, NOT observation coverage denominators.
    """
    start, end = utc_day(start), utc_day(end)
    months = pd.period_range(start.tz_localize(None), end.tz_localize(None), freq="M")
    grouped = filtered.assign(_day=filtered.timestamp_utc.dt.date).groupby(["platform", "month"])
    counts = grouped.size().to_dict()
    days = grouped._day.nunique().to_dict()
    stage_counts = filtered.groupby(["platform", "month", "processing"]).size().to_dict()
    rows = []
    for platform in platforms:
        source = full[full.platform.eq(platform)]
        first = source.timestamp_utc.min() if len(source) else pd.NaT
        last = source.timestamp_utc.max() if len(source) else pd.NaT
        for period in months:
            month = str(period)
            a = period.start_time.tz_localize("UTC")
            b = period.end_time.tz_localize("UTC")
            count = counts.get((platform, month), pd.NA)
            has_records = (platform, month) in counts
            outside = pd.isna(first) or b < first or a > last
            status = "kayıt_var_kapsam_bilinmiyor" if has_records else (
                "paket_tespit_aralığı_dışında" if outside else "kayıt_yok_kapsam_bilinmiyor")
            partial = start > a or end < b.normalize()
            boundary = (not pd.isna(first)) and (a <= first <= b or a <= last <= b)
            rows.append(dict(platform=platform, month=month, year=period.year, month_number=period.month,
                detection_count=count, status=status, coverage_verified=False,
                selection_partial_month=partial, record_extent_boundary=bool(boundary),
                partial_reference_year=period.year == AS_OF.year,
                detection_days=days.get((platform, month), 0) if has_records else pd.NA,
                archive_count=stage_counts.get((platform, month,"archive"), 0) if has_records else pd.NA,
                nrt_count=stage_counts.get((platform, month,"nrt"), 0) if has_records else pd.NA))
    result = pd.DataFrame(rows)
    if len(result):
        for col in ["detection_count", "archive_count", "nrt_count"]:
            result[col] = result[col].astype("Int64")
    return result


def csv_bytes(frame):
    """Excel-friendly UTF-8 BOM. UTC timestamps keep their +00:00 suffix."""
    return frame.to_csv(index=False, lineterminator="\n").encode("utf-8-sig")


def experimental_overlap(frame):
    """Training-only through-origin least squares; held-out calendar years.

    Archive only, one platform against Aqua, shared positive months only.
    Missing months are not imputed; hence missingness-selection bias is explicit.
    This is a rejection/diagnostic experiment, not an accepted harmonized series.
    """
    pairs, summaries, predictions = [], [], []
    for quality in ["all", "screened"]:
        subset = filter_data(frame, "2000-01-01", "2025-12-31", confidence=quality, stages=["archive"])
        monthly = subset.groupby(["month", "platform"]).size().unstack("platform")
        for target in ["Suomi-NPP", "NOAA-20", "NOAA-21"]:
            pair = monthly[["Aqua", target]].dropna().copy()
            pair["year"] = pair.index.str[:4].astype(int)
            # Fixed before testing; 2021 extreme remains in training and a sensitivity exclusion.
            train_end = {"Suomi-NPP": 2021, "NOAA-20": 2022, "NOAA-21": 2024}[target]
            train, test = pair[pair.year.le(train_end)], pair[pair.year.gt(train_end)]
            if train.empty or test.empty:
                continue
            x, y = train[target].to_numpy(float), train.Aqua.to_numpy(float)
            k = float(x @ y / (x @ x))
            tx, ty = test[target].to_numpy(float), test.Aqua.to_numpy(float)
            pred = k * tx
            mae = float(np.abs(pred - ty).mean())
            naive = float(np.abs(tx - ty).mean())
            baseline = float(np.abs(ty - train.Aqua.median()).mean())
            seasonal = train.groupby(train.index.str[-2:]).Aqua.median()
            spred = np.array([seasonal.get(m[-2:], train.Aqua.median()) for m in test.index], float)
            no2021 = train[train.year.ne(2021)]
            k_no2021 = float((no2021[target] @ no2021.Aqua) / (no2021[target] @ no2021[target])) if len(no2021) else None
            yearly_k = {str(int(yr)): float((g[target] @ g.Aqua) / (g[target] @ g[target])) for yr,g in train.groupby("year")}
            summaries.append(dict(reference="Aqua", target=target, confidence=quality,
                train_end_year=train_end, train_months=len(train), test_months=len(test),
                train_first=train.index.min(), train_last=train.index.max(),
                test_first=test.index.min(), test_last=test.index.max(),
                coefficient=k, coefficient_without_2021=k_no2021,
                yearly_coefficients=yearly_k,
                heldout_mae=mae, unscaled_mae=naive, train_median_baseline_mae=baseline,
                seasonal_baseline_mae=float(np.abs(spred-ty).mean()),
                heldout_bias=float((pred-ty).mean()),
                heldout_correlation=float(pd.Series(tx).corr(pd.Series(ty))) if len(test)>2 else None,
                coverage_verified=False, status="DENEYSEL_DOĞRULANMADI"))
            for month, r in pair.iterrows():
                pairs.append(dict(month=month, reference="Aqua", target=target, confidence=quality,
                                  aqua_count=int(r.Aqua), target_count=int(r[target]),
                                  split="train" if r.year <= train_end else "test"))
            for month, a, b, c, d in zip(test.index, tx, ty, pred, spred):
                predictions.append(dict(month=month, target=target, confidence=quality,
                    target_observed_count=int(a), aqua_observed_count=int(b),
                    experimental_aqua_scale=float(c), seasonal_baseline=float(d)))
    return summaries, pd.DataFrame(pairs), pd.DataFrame(predictions)
