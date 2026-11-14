"""Run with: python pipeline.py (working directory does not matter)."""
import json
from pathlib import Path
import pandas as pd
from core import BBOX, PLATFORMS, inspect_zips, filter_data, monthly_counts, experimental_overlap, csv_bytes

ROOT = Path(__file__).resolve().parent

def run(root=ROOT):
    print("1. İşlenmiş veri ve rapor klasörleri hazırlanıyor...")
    processed, reports = root / "data/processed", root / "reports"
    processed.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    
    print("2. Ham ZIP dosyaları taranıyor ve doğrulanıyor (bu işlem birkaç saniye sürebilir)...")
    clean, audit, provenance = inspect_zips((root / "data/raw").glob("*.zip"))
    
    print(f"3. Toplam {len(clean):,} tekil kayıt WGS84 sınırlarına ({BBOX}) göre filtreleniyor...")
    in_box = filter_data(clean, "2000-01-01", "2026-11-14")
    audit["out_of_bbox"] = len(clean) - len(in_box)
    
    audit["platform_summary"] = []
    for (platform, stage), g in in_box.groupby(["platform", "processing"]):
        audit["platform_summary"].append(dict(platform=platform, processing=stage, rows=len(g),
            first=g.timestamp_utc.min().isoformat(), last=g.timestamp_utc.max().isoformat(),
            detection_days=g.timestamp_utc.dt.date.nunique(), positive_months=g.month.nunique(),
            type_counts={str(k):int(v) for k,v in g["type"].value_counts(dropna=False).items()}))
            
    print("4. Aylık sayımlar ve uyumlaştırma deneyi hesaplanıyor...")
    monthly = monthly_counts(in_box, in_box, "2000-01-01", "2026-12-31", PLATFORMS)
    experiments, pairs, predictions = experimental_overlap(in_box)
    
    print("5. Sonuçlar CSV, JSON ve rapor formatlarında kaydediliyor...")
    in_box.to_parquet(processed / "detections.parquet", index=False, compression="zstd")
    (processed / "monthly.csv").write_bytes(csv_bytes(monthly))
    provenance.to_parquet(reports / "provenance.parquet", index=False, compression="zstd")
    (reports / "audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    
    inventory = pd.DataFrame(audit["inventory"])
    (reports / "file_inventory.csv").write_bytes(csv_bytes(inventory.drop(columns=["crs", "readme"])))
    (reports / "zip_members.csv").write_bytes(csv_bytes(pd.DataFrame(audit["members"])))
    (reports / "overlap_experiment.json").write_text(json.dumps(experiments, ensure_ascii=False, indent=2), encoding="utf-8")
    (reports / "overlap_pairs.csv").write_bytes(csv_bytes(pairs))
    (reports / "overlap_predictions.csv").write_bytes(csv_bytes(predictions))
    (reports / "platform_summary.csv").write_bytes(csv_bytes(pd.DataFrame(audit["platform_summary"])))
    
    (reports / "unknown_months.csv").write_bytes(csv_bytes(monthly[monthly.detection_count.isna()]))
    positive_days = in_box.groupby(["platform", "month"]).timestamp_utc.agg(lambda x: x.dt.date.nunique()).reset_index(name="days_with_detection")
    (reports / "detection_days_NOT_coverage.csv").write_bytes(csv_bytes(positive_days))
    
    print("\n--- İŞLEM BAŞARIYLA TAMAMLANDI ---")
    print(json.dumps({k:audit[k] for k in ["physical_rows", "canonical_records", "duplicate_copies_removed", "out_of_bbox", "rejected"]}, ensure_ascii=False, indent=2))
    print(pd.DataFrame(audit["platform_summary"])[["platform", "processing", "rows", "first", "last"]].to_string(index=False))
    return clean, audit

if __name__ == "__main__":
    run()
