from pathlib import Path
import json,shutil,uuid,re
from PIL import Image
import app_paths
ROOT=app_paths.DATA_ROOT;LIB=ROOT/"library.json";REG=ROOT/"master_registry.json"
OUTS={"TV":(144,192),"FG":(144,144),"TVD":(144,48),"SV":(576,384),"Variation":(64,64)}
_SAFE_ID=re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
def _load(path,default):
 try:return json.loads(path.read_text(encoding="utf-8"))
 except Exception:return default
def _save_atomic(path,data):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+"."+uuid.uuid4().hex+".tmp");tmp.write_text(json.dumps(data,indent=2),encoding="utf-8");tmp.replace(path)
def _manifest_for(p):
 for parent in [p.parent]+list(p.parents)[:4]:
  mp=parent/"project_shonen_artwork.json"
  if not mp.exists():continue
  try:data=json.loads(mp.read_text(encoding="utf-8"))
  except Exception:return None,mp
  required=("assetId","output","expectedSize","destination")
  if not isinstance(data,dict) or any(k not in data for k in required):return None,mp
  return data,mp
 return None,None
def _master(asset,reg):
 return next((m for m in reg.get("masters",[]) if m.get("id")==asset.get("masterId") or m.get("key")==asset.get("body")),None)
def _validate(p,byid,reg):
 try:
  with Image.open(p) as src:
   if src.format!="PNG":return None,"Artwork must be a genuine PNG file."
   src.verify()
  im=Image.open(p).convert("RGBA")
 except Exception as e:return None,"Unreadable PNG: "+str(e)
 alpha=im.getchannel("A").getextrema()
 if alpha==(0,0):return None,"Artwork is completely transparent."
 if alpha==(255,255):return None,"Reusable component artwork must preserve transparency; this PNG is fully opaque."
 manifest,mp=_manifest_for(p)
 if not manifest:return None,"No Project Shonen artwork manifest was found. Import this file from its Creator workspace, or use Create Piece for manual routing."
 aid=manifest.get("assetId");a=byid.get(aid)
 if not a:return None,"Manifest asset is not registered: "+str(aid)
 if not isinstance(aid,str) or not _SAFE_ID.fullmatch(aid):return None,"Registered asset ID is unsafe for an artwork filename."
 out=manifest.get("output")
 if out not in OUTS:return None,"Manifest output is unsupported: "+str(out)
 if manifest.get("destination")!="assets/outputs/"+str(out):return None,"Workspace destination metadata is invalid or no longer current."
 expected=tuple(manifest.get("expectedSize",[]))
 if expected!=OUTS[out] or im.size!=OUTS[out]:return None,f"Wrong canvas for {out}: expected {OUTS[out][0]}×{OUTS[out][1]}, got {im.size[0]}×{im.size[1]}."
 checks=(("masterId",a.get("masterId")),("body",a.get("body")),("category",a.get("category")))
 mismatch=next((k for k,v in checks if manifest.get(k)!=v),None)
 if mismatch:return None,"Workspace metadata no longer matches the registered piece ("+mismatch+")."
 m=_master(a,reg);mo=m.get("outputs",{}).get(out,{}) if m else {}
 if not m or mo.get("status") not in ("approved","reference") or not mo.get("locked"):return None,"Matching body output is not approved/reference and locked."
 return {"path":p,"image":im,"asset":a,"output":out},None
def import_finished_pngs(paths):
 lib=_load(LIB,{"assets":[]});reg=_load(REG,{"masters":[]});byid={a.get("id"):a for a in lib.get("assets",[])}
 results=[];valid=[];seen=set()
 for raw in paths:
  p=Path(raw);item,reason=_validate(p,byid,reg)
  if reason:results.append({"file":p.name,"ok":False,"reason":reason});continue
  key=(item["asset"]["id"],item["output"])
  if key in seen:results.append({"file":p.name,"ok":False,"reason":"Another selected PNG targets the same piece/output in this batch."});continue
  seen.add(key);valid.append(item)
 if not valid:return results
 txn=ROOT/"assets"/".intake"/uuid.uuid4().hex;txn.mkdir(parents=True,exist_ok=True);backups=[];installed=[]
 try:
  # Stage every PNG first. No production artwork changes until all valid items are writable.
  for item in valid:
   aid=item["asset"]["id"];out=item["output"];sp=txn/(aid+"_"+out+".png");item["image"].save(sp);item["stage"]=sp
  for item in valid:
   a=item["asset"];out=item["output"];d=ROOT/"assets"/"outputs"/out;d.mkdir(parents=True,exist_ok=True);dst=d/(a["id"]+"_"+out+".png")
   if dst.exists():
    bp=txn/"backup"/out/dst.name;bp.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,bp);backups.append((bp,dst))
   shutil.copy2(item["stage"],dst);installed.append(dst);rel=str(dst.relative_to(ROOT)).replace(chr(92),"/")
   a.setdefault("outputs",{})[out]={"status":"complete","path":rel}
   if out=="TV":a["path"]=rel
   if a.get("approved"):a["approved"]=False;a["status"]="revision"
  _save_atomic(LIB,lib)
 except Exception as e:
  for dst in installed:
   try:dst.unlink(missing_ok=True)
   except Exception:pass
  for bp,dst in backups:
   try:dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(bp,dst)
   except Exception:pass
  shutil.rmtree(txn,ignore_errors=True)
  for item in valid:results.append({"file":item["path"].name,"ok":False,"reason":"Import transaction rolled back: "+str(e)})
  return results
 shutil.rmtree(txn,ignore_errors=True)
 for item in valid:results.append({"file":item["path"].name,"ok":True,"asset":item["asset"].get("name",item["asset"]["id"]),"assetId":item["asset"]["id"],"output":item["output"]})
 return results
