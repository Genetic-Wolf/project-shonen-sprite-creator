from pathlib import Path
from PIL import Image
import app_paths

OUTPUTS={"TV":(144,192),"FG":(144,144),"TVD":(144,48),"SV":(576,384),"Variation":(64,64)}
ORDER=("TV","FG","TVD","SV","Variation")

def _valid(record,out):
    if not record or record.get("status")!="complete" or not record.get("path"):
        return False,"missing"
    p=app_paths.resolve(record["path"])
    if not p.exists(): return False,"file missing"
    try:
        with Image.open(p) as im:
            if im.size!=OUTPUTS[out]: return False,"wrong size"
            a=im.convert("RGBA").getchannel("A").getextrema()
            if a==(0,0): return False,"empty"
            if a==(255,255): return False,"no transparency"
    except Exception:return False,"unreadable"
    return True,"complete"

def evaluate(asset,masters):
    blockers=[];primary={};custom={}
    for out in ORDER:
        ok,why=_valid((asset.get("outputs") or {}).get(out),out);primary[out]=why
        if not ok:blockers.append({"kind":"primary","output":out,"reason":why})
    matrix=((asset.get("compatibility") or {}).get("matrix") or {})
    variants=asset.get("variants") or {}
    byid={m.get("id"):m for m in masters}
    for mid,choice in matrix.items():
        if choice!="CUSTOM":continue
        m=byid.get(mid);name=m.get("name",mid) if m else mid;custom[mid]={}
        variant=variants.get(mid) or {}; inherit=set(variant.get("_inherit") or [])
        for out in ORDER:
            if out in inherit:
                ok,why=_valid((asset.get("outputs") or {}).get(out),out);custom[mid][out]="inherited" if ok else "inherited "+why
                if not ok:blockers.append({"kind":"primary","output":out,"reason":why,"requiredBy":name})
                continue
            ok,why=_valid(variant.get(out),out);custom[mid][out]=why
            if not ok:blockers.append({"kind":"custom","masterId":mid,"masterName":name,"output":out,"reason":why})
    state="Production Ready" if not blockers else ("Needs Artwork" if any(x["reason"]=="missing" for x in blockers) else "Needs Attention")
    return {"state":state,"primary":primary,"custom":custom,"blockers":blockers,"complete":not blockers}

def next_job(asset,masters):
    report=evaluate(asset,masters)
    return report["blockers"][0] if report["blockers"] else None
