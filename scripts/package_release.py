"""Create a reproducible distributable ZIP (no virtualenv or interpreter binaries)."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT.parent/'deliverables'
EXCLUDED={'.venv','__pycache__','.pytest_cache','.git','reference_images'}

def included():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(x in EXCLUDED for x in p.relative_to(ROOT).parts)
                  and p.name not in {'.DS_Store','PACKAGE_MANIFEST.json'} and p.suffix!='.pyc')

def run():
    DEST.mkdir(exist_ok=True)
    files=included()
    manifest={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    mp=ROOT/'PACKAGE_MANIFEST.json'
    mp.write_text(json.dumps({'release':'1.1','reference_date':'2026-11-14','file_sha256':manifest},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    out=DEST/'FocusTM_NASA_Yangin_Takvimi_v1_1_2026-11-14.zip'
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in sorted(files+[mp]):
            arc=(Path(ROOT.name)/p.relative_to(ROOT)).as_posix()
            info=zipfile.ZipInfo(arc,date_time=(2026,11,14,12,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16
            z.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        for relative,digest in manifest.items():
            assert hashlib.sha256(z.read(f'{ROOT.name}/{relative}')).hexdigest()==digest
    digest=hashlib.sha256(out.read_bytes()).hexdigest()
    out.with_suffix('.sha256.txt').write_text(f'{digest}  {out.name}\n',encoding='utf-8')
    print(json.dumps({'archive':str(out),'bytes':out.stat().st_size,'files':len(files)+1,'sha256':digest},indent=2))

if __name__=='__main__':run()
