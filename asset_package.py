from pathlib import Path
import copy, json, zipfile, hashlib, time
from PIL import Image
import app_paths

LIB=app_paths.DATA_ROOT/"library.json"
EXT=".psasset"

def _load():
 try:return json.loads(LIB.read_text(encoding="utf-8"))
 except Exception:return {"version":"0.22.0","assets":[]}

def _save(d):
 LIB.parent.mkdir(parents=True,exist_ok=True);LIB.write_text(json.dumps(d,indent=2),encoding="utf-8")

def _safe_member(name):
 p=Path(name)
 return not p.is_absolute() and ".." not in p.parts

def export_piece(asset_id,destination):
 lib=_load();asset=next((a for a in lib.get("assets",[]) if a.get("id")==asset_id),None)
 if not asset:raise ValueError("Reusable piece was not found.")
 if str(asset.get("source","")).startswith("RPG Maker MZ"):
  raise ValueError("Imported RPG Maker MZ stock artwork cannot be exported as a Project Shonen asset package.")
 files=[];pack=copy.deepcopy(asset)
 for rep,o in pack.get("outputs",{}).items():
  paths=o.get("paths") or ([o.get("path")] if o.get("path") else [])
  new=[]
  for n,rel in enumerate(paths):
   p=app_paths.resolve(rel)
   if not p.exists():continue
   arc=f"artwork/{rep}/{n:02d}_{p.name}";files.append((p,arc));new.append(arc)
  if new:o["paths"]=new;o["path"]=new[0]
 manifest={"schemaVersion":1,"packageType":"Project Shonen Reusable Piece","created":time.strftime("%Y-%m-%dT%H:%M:%S"),"asset":pack}
 dest=Path(destination)
 if dest.suffix.lower()!=EXT:dest=dest.with_suffix(EXT)
 with zipfile.ZipFile(dest,"w",zipfile.ZIP_DEFLATED) as z:
  z.writestr("manifest.json",json.dumps(manifest,indent=2))
  for p,arc in files:z.write(p,arc)
 return {"path":str(dest),"files":len(files),"name":asset.get("name",asset_id)}

def inspect_package(package):
 with zipfile.ZipFile(package) as z:
  if "manifest.json" not in z.namelist():raise ValueError("Package has no manifest.")
  m=json.loads(z.read("manifest.json"))
  if m.get("packageType")!="Project Shonen Reusable Piece":raise ValueError("Not a Project Shonen reusable-piece package.")
  a=m.get("asset",{})
  if not a.get("id") or not a.get("name"):raise ValueError("Package asset metadata is incomplete.")
  if str(a.get("source","")).startswith("RPG Maker MZ"):raise ValueError("Stock RPG Maker MZ artwork packages are not accepted.")
  return m

def import_piece(package,replace=False):
 m=inspect_package(package);a=copy.deepcopy(m["asset"]);lib=_load();existing=next((x for x in lib.get("assets",[]) if x.get("id")==a["id"]),None)
 if existing and not replace:raise FileExistsError(f'Asset ID {a["id"]} already exists.')
 base=app_paths.DATA_ROOT/"assets"/"imported_packages"/a["id"]
 with zipfile.ZipFile(package) as z:
  for rep,o in a.get("outputs",{}).items():
   paths=o.get("paths") or ([o.get("path")] if o.get("path") else []);new=[]
   for arc in paths:
    if not _safe_member(arc) or arc not in z.namelist():continue
    data=z.read(arc)
    try:
     import io
     im=Image.open(io.BytesIO(data));im.verify()
    except Exception:raise ValueError(f"Invalid PNG in package: {arc}")
    target=base/rep/Path(arc).name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    new.append(str(target.relative_to(app_paths.DATA_ROOT)).replace("\\","/"))
   if new:o["paths"]=new;o["path"]=new[0]
 if existing:lib["assets"].remove(existing)
 a["source"]="Project Shonen portable package";lib.setdefault("assets",[]).append(a);_save(lib)
 return {"id":a["id"],"name":a["name"],"replaced":bool(existing)}
