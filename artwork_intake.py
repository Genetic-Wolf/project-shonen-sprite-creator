from pathlib import Path
import json
from PIL import Image
import app_paths

ROOT=app_paths.DATA_ROOT
LIB=ROOT/"library.json"
REG=ROOT/"master_registry.json"
OUTS={"TV":(144,192),"FG":(144,144),"TVD":(144,48),"SV":(576,384),"Variation":(64,64)}

def _load(path,default):
    try:return json.load(open(path,encoding="utf-8"))
    except Exception:return default

def _save_atomic(path,data):
    tmp=path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(data,indent=2),encoding="utf-8")
    tmp.replace(path)

def _manifest_for(p):
    for parent in [p.parent]+list(p.parents)[:4]:
        mp=parent/"project_shonen_artwork.json"
        if mp.exists():
            try:return json.loads(mp.read_text(encoding="utf-8")),mp
            except Exception:return None,mp
    return None,None

def _master(asset,reg):
    return next((m for m in reg.get("masters",[]) if m.get("id")==asset.get("masterId") or m.get("key")==asset.get("body")),None)

def import_finished_pngs(paths):
    lib=_load(LIB,{"assets":[]});reg=_load(REG,{"masters":[]})
    byid={a.get("id"):a for a in lib.get("assets",[])}
    results=[];changed=False
    for raw in paths:
        p=Path(raw)
        try:
            with Image.open(p) as src:
                src.verify()
            im=Image.open(p).convert("RGBA")
        except Exception as e:
            results.append({"file":p.name,"ok":False,"reason":"Unreadable PNG: "+str(e)});continue
        if not im.getbbox():
            results.append({"file":p.name,"ok":False,"reason":"Artwork is completely transparent."});continue
        manifest,mp=_manifest_for(p)
        if not manifest:
            results.append({"file":p.name,"ok":False,"reason":"No Project Shonen artwork manifest was found. Import this file from its Creator workspace, or use Create Piece for manual routing."});continue
        aid=manifest.get("assetId");a=byid.get(aid)
        if not a:
            results.append({"file":p.name,"ok":False,"reason":"Manifest asset is not registered: "+str(aid)});continue
        out=manifest.get("output")
        if out not in OUTS:
            results.append({"file":p.name,"ok":False,"reason":"Manifest output is unsupported: "+str(out)});continue
        expected=tuple(manifest.get("expectedSize",[]))
        if expected!=OUTS[out] or im.size!=OUTS[out]:
            results.append({"file":p.name,"ok":False,"reason":f"Wrong canvas for {out}: expected {OUTS[out][0]}×{OUTS[out][1]}, got {im.size[0]}×{im.size[1]}."});continue
        checks=(("masterId",a.get("masterId")),("body",a.get("body")),("category",a.get("category")))
        mismatch=next((k for k,v in checks if manifest.get(k)!=v),None)
        if mismatch:
            results.append({"file":p.name,"ok":False,"reason":"Workspace metadata no longer matches the registered piece ("+mismatch+")."});continue
        m=_master(a,reg);mo=m.get("outputs",{}).get(out,{}) if m else {}
        if not m or mo.get("status") not in ("approved","reference") or not mo.get("locked"):
            results.append({"file":p.name,"ok":False,"reason":"Matching body output is not approved/reference and locked."});continue
        d=ROOT/"assets"/"outputs"/out;d.mkdir(parents=True,exist_ok=True)
        dst=d/f"{a['id']}_{out}.png";im.save(dst)
        rel=str(dst.relative_to(ROOT)).replace("\\","/")
        a.setdefault("outputs",{})[out]={"status":"complete","path":rel}
        if out=="TV":a["path"]=rel
        changed=True;results.append({"file":p.name,"ok":True,"asset":a.get("name",aid),"output":out})
    if changed:_save_atomic(LIB,lib)
    return results
