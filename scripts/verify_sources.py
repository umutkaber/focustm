"""Independent raw CSV vs derived data cross-check. No dependency on core.py."""
from pathlib import Path
from collections import Counter
import csv
import io
import json
import zipfile
import hashlib
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
def run():
    audit=json.loads((ROOT/'reports/audit.json').read_text(encoding='utf-8'))
    lookup={'Terra':'Terra','Aqua':'Aqua','SNPP':'Suomi-NPP','N20':'NOAA-20','N21':'NOAA-21'}
    raw_counts=Counter()
    for p in sorted((ROOT/'data/raw').glob('*.zip')):
        assert hashlib.sha256(p.read_bytes()).hexdigest()==audit['zip_sha256'][p.name]
        with zipfile.ZipFile(p) as z:
            assert z.testzip() is None
            for amember in z.namelist():
                if not member.endswith('.csv'):continue
                for row in csv.DictReader(io.StringIO(z.read(member).decode('utf-8-sig'))):
                    if 26.0<=float(row['longitude'])<=45.0 and 36.0<=float(row['latitude'])<=42.0:
                        raw_counts[(lookup[row['satellite']],row['acq_date'][:7])]+=1
    clean=pd.read_parquet(ROOT/'data/processed/detections.parquet',columns=['platform','acq_date'])
    clean_counts=Counter(zip(clean.platform,clean.acq_date.str[:7]))
    assert raw_counts==clean_counts
    with (ROOT/'data/processed/monthly.csv').open(encoding='utf-8-sig',newline='') as f:
        for r in csv.DictReader(f):
            key=(r['platform'],r['month'])
            if key in raw_counts:assert int(r['detection_count'])==raw_counts[key]
            else:assert r['detection_count']==''
    samples=[{'platform':p,'month':m,'raw_count':raw_counts[(p,m)],'processed_count':clean_counts[(p,m)]}
             for p,m in [('Aqua','2021-07'),('Terra','2021-07'),('Suomi-NPP','2021-07'),('NOAA-20','2021-07'),('NOAA-21','2026-11')]]
    report={'passed':True,'raw_zip_checksums_passed':len(audit['zip_sha256']),
            'platform_month_groups_compared':len(raw_counts),'total':sum(raw_counts.values()),
            'no_missing_month_encoded_as_zero':True,'examples':samples}
    (ROOT/'reports/raw_crosscheck.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':run()
