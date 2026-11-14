"""Small synthetic edge cases are TEST FIXTURES ONLY, never production data."""
import csv
import io
import json
import zipfile
from collections import Counter
import numpy as np
import pandas as pd
import pytest

from core import (BBOX, PLATFORMS, parse_utc, normalize_record, filter_data, validate_bbox,
                  monthly_counts, csv_bytes, inspect_zips, experimental_overlap, sha256)


def test_utc_leading_zero_and_leap_day():
    assert parse_utc("2024-02-29", "54").isoformat() == "2024-02-29T00:54:00+00:00"
    assert parse_utc("2024-02-29", "0054").hour == 0


@pytest.mark.parametrize("d,t", [("2023-02-29","1200"),("2024-01-01","2400"),("2024-01-01","1261"),("01/02/2024","1200"),("2024-01-01","nan")])
def test_invalid_dates_rejected(d,t):
    with pytest.raises(ValueError): parse_utc(d,t)


def test_boundary_points_and_utc_end_inclusive(data):
    # Deliberately constructed software boundary fixture, not a claimed NASA record.
    x = pd.concat([data.iloc[:1].copy() for _ in range(6)], ignore_index=True)
    x["longitude"] = [29.5,32.8,30,29.4999,30,30]
    x["latitude"] = [36.1,37.5,36.5,36.5,37.5001,36.5]
    x["timestamp_utc"] = pd.to_datetime(["2021-07-01T00:00Z", "2021-07-31T23:59Z", "2021-08-01T00:00Z", "2021-07-05T00:00Z", "2021-07-05T00:00Z", "2021-06-30T23:59Z"])
    got=filter_data(x,"2021-07-01","2021-07-31")
    assert len(got)==2


@pytest.mark.parametrize("bbox", [(32,36,30,37),(29.5,37.5,32.8,36.1),(29.4,36.1,32.8,37.5),(29.5,36.1,float("nan"),37.5)])
def test_invalid_or_outside_bbox(bbox):
    with pytest.raises(ValueError): validate_bbox(bbox)


def test_date_order(data):
    with pytest.raises(ValueError):filter_data(data,"2025-01-01","2024-01-01")


def test_platform_normalization_preserves_raw(data):
    snpp=data[data.platform.eq("Suomi-NPP")]
    assert set(snpp.instrument_raw)=={"SNPP"}
    assert set(snpp.sensor)=={"VIIRS"}
    assert set(data.platform)==set(PLATFORMS)
    terra=filter_data(data,"2000-01-01","2026-12-31",platforms=["Terra"])
    assert len(terra)==2177 and set(terra.platform)=={"Terra"}


def test_no_duplicate_formats_or_files(root):
    paths=list((root/"data/raw").glob("*.zip"))
    clean,audit,prov=inspect_zips(paths+[paths[0]])
    assert len(clean)==29640
    assert all(item["exact_equal"] for item in audit["format_equivalence"])
    assert clean.record_id.is_unique
    assert not audit["rejected"]
    assert not audit["archive_superseded_nrt_ids"]
    assert len(prov)==88920


def test_frozen_raw_hashes_and_audit(root):
    audit=json.loads((root/"reports/audit.json").read_text())
    for name,h in audit["zip_sha256"].items():
        assert sha256((root/"data/raw"/name).read_bytes())==h
    assert audit["physical_rows"]==88920
    assert audit["duplicate_copies_removed"]==59280
    assert audit["out_of_bbox"]==0
    assert not audit["coverage_verified"]


def test_every_csv_month_matches_independent_raw_count(root,data):
    # Independent standard-library reference, without core normalization or aggregation.
    expected=Counter()
    lookup={"SNPP":"Suomi-NPP","N20":"NOAA-20","N21":"NOAA-21","Aqua":"Aqua","Terra":"Terra"}
    for p in (root/"data/raw").glob("*.zip"):
        with zipfile.ZipFile(p) as z:
            for name in z.namelist():
                if not name.endswith(".csv"):continue
                for r in csv.DictReader(io.StringIO(z.read(name).decode())):
                    if 29.5<=float(r["longitude"])<=32.8 and 36.1<=float(r["latitude"])<=37.5:
                        expected[(lookup[r["satellite"]],r["acq_date"][:7])]+=1
    actual=data.groupby(["platform","month"]).size().to_dict()
    assert actual==dict(expected)
    assert actual[("Aqua","2021-07")]==426
    assert actual[("Terra","2021-07")]==364
    assert actual[("Suomi-NPP","2021-07")]==2268
    assert actual[("NOAA-20","2021-07")]==2580


def test_source_row_round_trip(root,data):
    # Every canonical row is traceable to its preferred raw CSV data row.
    for (zip_name,member),g in data.groupby(["source_zip","source_member"]):
        assert member.endswith(".csv")
        with zipfile.ZipFile(root/"data/raw"/zip_name) as z:
            rows=list(csv.DictReader(io.StringIO(z.read(member).decode())))
        for r in g.itertuples():
            raw=rows[r.source_row-1]
            assert float(raw["latitude"])==r.latitude
            assert float(raw["longitude"])==r.longitude
            assert parse_utc(raw["acq_date"],raw["acq_time"])==r.timestamp_utc
            assert str(raw["confidence"])==str(r.confidence)


def test_missing_period_not_zero_and_partial_year(data):
    filtered=filter_data(data,"2000-01-01","2026-11-09",platforms=["NOAA-21"])
    m=monthly_counts(filtered,data,"2000-01-01","2026-11-09",["NOAA-21"])
    assert m[m.year.lt(2023)].detection_count.isna().all()
    assert not m.coverage_verified.any()
    assert m[m.year.eq(2026)].partial_reference_year.all()
    november=m[m.month.eq("2026-11")].iloc[0]
    assert november.detection_count==5 and november.selection_partial_month
    empty=filter_data(data,"2021-07-01","2021-07-31",bbox=(29.5,36.1,29.50001,36.10001))
    assert empty.empty
    em=monthly_counts(empty,data,"2021-07-01","2021-07-31",PLATFORMS)
    assert em.detection_count.isna().all()


def test_nrt_unknown_type_and_quality_filter(data):
    assert data[data.processing.eq("nrt")]["type"].isna().all()
    v=filter_data(data,"2000-01-01","2026-12-31",type_mode="vegetation")
    assert set(v.processing)=={"archive"}
    assert len(v)==21640
    quality=filter_data(data,"2000-01-01","2026-12-31",confidence="screened")
    assert set(quality[quality.sensor.eq("VIIRS")].confidence)<={"n","h"}
    assert pd.to_numeric(quality[quality.sensor.eq("MODIS")].confidence).min()>=30


def test_csv_download_round_trip_and_empty(data):
    selected=filter_data(data,"2021-07-01","2021-07-31",platforms=["Aqua"])
    payload=csv_bytes(selected)
    assert payload.startswith(b"\xef\xbb\xbf")
    reread=pd.read_csv(io.BytesIO(payload))
    assert len(reread)==426
    assert set(reread.platform)=={"Aqua"}
    assert reread.timestamp_utc.str.endswith("+00:00").all()
    empty=pd.read_csv(io.BytesIO(csv_bytes(selected.iloc[:0])))
    assert empty.empty and list(empty)==list(selected)


def test_experiment_no_test_leakage_and_not_validated(data):
    summaries, pairs, predictions=experimental_overlap(data)
    assert len(summaries)==6
    assert all(s["status"]=="DENEYSEL_DOĞRULANMADI" for s in summaries)
    assert not any(s["coverage_verified"] for s in summaries)
    for s in summaries:
        p=pairs[(pairs.target==s["target"]) & (pairs.confidence==s["confidence"])]
        assert p[p.split.eq("train")].month.max() < p[p.split.eq("test")].month.min()
        assert p.month.max()<"2026-01"
        train=p[p.split.eq("train")]
        k=(train.target_count @ train.aqua_count)/(train.target_count @ train.target_count)
        assert k==pytest.approx(s["coefficient"])
    # Perturb held-out data only: coefficients for SNPP/NOAA20 must not change.
    altered=pd.concat([data,data[(data.year>=2023)&data.platform.eq("Aqua")]],ignore_index=True)
    other,_,_=experimental_overlap(altered)
    for a,b in zip(summaries,other):
        if a["target"]!="NOAA-21":assert a["coefficient"]==pytest.approx(b["coefficient"])


def test_invalid_record_is_audited(tmp_path,root):
    with zipfile.ZipFile(root/"data/raw/DL_FIRE_M-C61_847528.zip") as z:
        rows=list(csv.DictReader(io.StringIO(z.read("fire_nrt_M-C61_847528.csv").decode())))[:1]
    broken=dict(rows[0],acq_time="2500")
    p=tmp_path/"fixture.zip"
    with zipfile.ZipFile(p,"w") as z:
        z.writestr("fire_nrt_M-C61_1.json",json.dumps(rows+[broken]))
    clean,audit,_=inspect_zips([p])
    assert len(clean)==1 and len(audit["rejected"])==1


def test_conflicting_same_observation_stops(tmp_path,root):
    with zipfile.ZipFile(root/"data/raw/DL_FIRE_M-C61_847528.zip") as z:
        row=next(csv.DictReader(io.StringIO(z.read("fire_nrt_M-C61_847528.csv").decode())))
    p=tmp_path/"conflict.zip"
    with zipfile.ZipFile(p,"w") as z:
        z.writestr("fire_nrt_M-C61_1.json",json.dumps([row,dict(row,frp="9999")]))
    with pytest.raises(ValueError,match="çelişen"):
        inspect_zips([p])
