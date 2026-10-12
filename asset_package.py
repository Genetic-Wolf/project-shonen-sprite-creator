from pathlib import Path
import copy,json,zipfile,hashlib,time,io,shutil
from PIL import Image
import app_paths

LIB=app_paths.DATA_ROOT/"library.json";EXT=".psasset";SCHEMA=2

def _load():
 try:return json.loads(LIB.read_text(encoding="utf-8"))
 except Exception:return {"version":"0.22.0","assets":[]}
def _save(d):
 LIB.parent.mkdir(parents=True,exist_ok=True);tmp=LIB.with_suffix(".tmp");tmp.write_text(json.dumps(d,indent=2),encoding="utf-8");tmp.replace(LIB)
def _safe_member(name):
 p=Path(name);return bool(name) and not p.is_absolute() and ".." not in p.parts
def _png(data,arc):
 try:
  im=Image.open(io.BytesIO(data));size=im.size;im.verify();return size
 except Exception:raise ValueError("Invalid PNG in package: "+arc)
def _add(files,seen,rel,arc):
 if not rel:return None
 p=app_paths.resolve(rel)
 if not p.exists():raise ValueError("Required artwork is missing: "+str(rel))
 key=str(p.resolve())
 if key in seen:return seen[key]
 files.append((p,arc));seen[key]=arc
 return arc
def _portable_output(o,rep,prefix,files,seen):
 x=copy.deepcopy(o);paths=x.get("paths") or ([x.get("path")] if x.get("path") else []);new=[]
 for n,rel in enumerate(paths):
  p=app_paths.resolve(rel);arc=prefix+"/"+rep+"/art/"+f"{n:02d}_"+p.name;new.append(_add(files,seen,rel,arc))
 if new:x["paths"]=new;x["path"]=new[0]
 layers=[]
 for n,layer in enumerate(x.get("layers") or []):
  y=copy.deepcopy(layer);rel=y.get("path");p=app_paths.resolve(rel);arc=prefix+"/"+rep+"/layers/"+f"{n:02d}_"+p.name;y["path"]=_add(files,seen,rel,arc);layers.append(y)
 if layers:x["layers"]=layers
 masks=[]
 for n,mask in enumerate(x.get("masks") or []):
  y=copy.deepcopy(mask);rel=y.get("path");p=app_paths.resolve(rel);arc=prefix+"/"+rep+"/masks/"+f"{n:02d}_"+p.name;y["path"]=_add(files,seen,rel,arc);masks.append(y)
 if masks:x["masks"]=masks
 return x
def export_piece(asset_id,destination):
 lib=_load();asset=next((a for a in lib.get("assets",[]) if a.get("id")==asset_id),None)
 if not asset:raise ValueError("Reusable piece was not found.")
 if str(asset.get("source","")).startswith("RPG Maker MZ"):raise ValueError("Imported RPG Maker MZ stock artwork cannot be exported as a Project Shonen asset package.")
 files=[];seen={};pack=copy.deepcopy(asset)
 pack["outputs"]={rep:_portable_output(o,rep,"artwork/primary",files,seen) for rep,o in pack.get("outputs",{}).items()}
 variants={}
 for mid,v in pack.get("variants",{}).items():
  nv={"_inherit":list(v.get("_inherit") or [])}
  for rep,o in v.items():
   if rep=="_inherit":continue
   if isinstance(o,dict):nv[rep]=_portable_output(o,rep,"artwork/variants/"+str(mid),files,seen)
  variants[mid]=nv
 if variants:pack["variants"]=variants
 checks={arc:hashlib.sha256(p.read_bytes()).hexdigest() for p,arc in files}
 manifest={"schemaVersion":SCHEMA,"packageType":"Project Shonen Reusable Piece","created":time.strftime("%Y-%m-%dT%H:%M:%S"),"checksums":checks,"asset":pack}
 dest=Path(destination)
 if dest.suffix.lower()!=EXT:dest=dest.with_suffix(EXT)
 dest.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(dest,"w",zipfile.ZIP_DEFLATED) as z:
  z.writestr("manifest.json",json.dumps(manifest,indent=2))
  for p,arc in files:z.write(p,arc)
 return {"path":str(dest),"files":len(files),"name":asset.get("name",asset_id),"schemaVersion":SCHEMA}
def inspect_package(package):
 with zipfile.ZipFile(package) as z:
  names=set(z.namelist())
  if "manifest.json" not in names:raise ValueError("Package has no manifest.")
  m=json.loads(z.read("manifest.json"));schema=int(m.get("schemaVersion",1))
  if schema not in (1,SCHEMA):raise ValueError("Unsupported .psasset schema version: "+str(schema))
  if m.get("packageType")!="Project Shonen Reusable Piece":raise ValueError("Not a Project Shonen reusable-piece package.")
  a=m.get("asset",{})
  if not a.get("id") or not a.get("name"):raise ValueError("Package asset metadata is incomplete.")
  if str(a.get("source","")).startswith("RPG Maker MZ"):raise ValueError("Stock RPG Maker MZ artwork packages are not accepted.")
  for arc,digest in (m.get("checksums") or {}).items():
   if not _safe_member(arc) or arc not in names:raise ValueError("Package artwork is missing: "+arc)
   if hashlib.sha256(z.read(arc)).hexdigest()!=digest:raise ValueError("Package checksum failed: "+arc)
  return m
def _restore_output(z,o,rep,base):
 x=copy.deepcopy(o)
 def restore(arc,sub):
  if not arc:return None
  if not _safe_member(arc) or arc not in z.namelist():raise ValueError("Package artwork is missing: "+str(arc))
  data=z.read(arc);_png(data,arc);target=base/sub/rep/Path(arc).name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);return str(target.relative_to(app_paths.DATA_ROOT)).replace("\\","/")
 paths=x.get("paths") or ([x.get("path")] if x.get("path") else []);new=[restore(a,"art") for a in paths]
 if new:x["paths"]=new;x["path"]=new[0]
 if x.get("layers"):
  for y in x["layers"]:y["path"]=restore(y.get("path"),"layers")
 if x.get("masks"):
  for y in x["masks"]:y["path"]=restore(y.get("path"),"masks")
 return x
def import_piece(package,replace=False,new_id=None):
 m=inspect_package(package);a=copy.deepcopy(m["asset"]);lib=_load();original_id=a["id"]
 if new_id:
  if any(x.get("id")==new_id for x in lib.get("assets",[])):raise FileExistsError("Asset ID "+new_id+" already exists.")
  a["id"]=new_id
 existing=next((x for x in lib.get("assets",[]) if x.get("id")==a["id"]),None)
 if existing and not replace:raise FileExistsError("Asset ID "+a["id"]+" already exists.")
 base=app_paths.DATA_ROOT/"assets"/"imported_packages"/a["id"];stage=base.with_name(base.name+".incoming");shutil.rmtree(stage,ignore_errors=True);stage.mkdir(parents=True)
 try:
  with zipfile.ZipFile(package) as z:
   a["outputs"]={rep:_restore_output(z,o,rep,stage) for rep,o in a.get("outputs",{}).items()}
   variants={}
   for mid,v in a.get("variants",{}).items():
    nv={"_inherit":list(v.get("_inherit") or [])}
    for rep,o in v.items():
     if rep!="_inherit" and isinstance(o,dict):nv[rep]=_restore_output(z,o,rep,stage/"variants"/str(mid))
    variants[mid]=nv
   if variants:a["variants"]=variants
  if base.exists():shutil.rmtree(base)
  stage.replace(base)
  # paths were written relative to DATA_ROOT while staged; repair the temporary directory segment.
  def fix(v):
   if isinstance(v,dict):
    for k,x in list(v.items()):
     if k in ("path","paths") and isinstance(x,str):v[k]=x.replace(a["id"]+".incoming",a["id"])
     elif k=="paths" and isinstance(x,list):v[k]=[y.replace(a["id"]+".incoming",a["id"]) for y in x]
     else:fix(x)
   elif isinstance(v,list):
    for x in v:fix(x)
  fix(a)
 except Exception:
  shutil.rmtree(stage,ignore_errors=True);raise
 if existing:lib["assets"].remove(existing)
 a["source"]="Project Shonen portable package";lib.setdefault("assets",[]).append(a);_save(lib)
 return {"id":a["id"],"originalId":original_id,"name":a["name"],"replaced":bool(existing),"copied":bool(new_id),"schemaVersion":int(m.get("schemaVersion",1))}
