from pathlib import Path
import io, json, re, zipfile
from PIL import Image
import app_paths

REP_DIR={"FG":"Face","TV":"TV","TVD":"TVD","SV":"SV","Variation":"Variation"}
EXPECTED={"TV":(144,192),"TVD":(144,48),"SV":(576,384),"Variation":(64,64)}
CATEGORY_MAP={
 "FrontHair":"Hair / Front","RearHair":"Hair / Rear","Eyes":"Face / Eyes",
 "Eyebrows":"Face / Eyebrows","Nose":"Face / Nose","Mouth":"Face / Mouth",
 "Ears":"Face / Ears","Beard":"Face / Facial Hair","FacialMark":"Face / Markings",
 "Face":"Face / Shape","Clothing":"Clothing","Cloak":"Outerwear / Cloak",
 "AccA":"Accessories / Head A","AccB":"Accessories / Head B","Headband":"Shinobi / Forehead Protector","Hat":"Accessories / Head","Tattoo":"Face / Tattoos",
 "Glasses":"Accessories / Face","BeastEars":"Special / Beast Ears",
 "Tail":"Special / Tail","Wing":"Special / Wings","Clothing1":"Clothing","Clothing2":"Clothing","Cloak1":"Outerwear / Cloak","Cloak2":"Outerwear / Cloak"
}
SEXES=("Female","Male","Kid")
RX=re.compile(r"^(FG|TV|TVD|SV|icon)_([^_]+?)([12])?_p(\d+)",re.I)
def _find_body(dest,rep,sex):
 d=dest/REP_DIR.get(rep,rep)/sex
 if not d.exists():return None
 names={"TV":["TV_Body_p01.png"],"TVD":["TVD_Body_p01.png"],"SV":["SV_body_p01.png","SV_Body_p01.png"],"FG":["FG_Body_p01_c1_m001.png","FG_Body_p01_c1.png","FG_Body_p01.png"]}
 for n in names.get(rep,[]):
  p=d/n
  if p.exists():return p
 cand=sorted([p for p in d.glob("*.png") if "body" in p.name.lower() and "_p01" in p.name.lower()])
 return cand[0] if cand else None

def _load(path,default):
 try:return json.loads(path.read_text(encoding="utf-8"))
 except Exception:return default

def _save(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(data,indent=2),encoding="utf-8")

def _png_ok(data):
 try:
  im=Image.open(io.BytesIO(data));im.verify();return True
 except Exception:return False

def _rel(path):
 return str(path.relative_to(app_paths.DATA_ROOT)).replace("\\","/")

def import_generator_zip(zip_path):
 app_paths.bootstrap()
 zip_path=Path(zip_path)
 dest=app_paths.DATA_ROOT/"mz_generator"
 valid=invalid=0
 with zipfile.ZipFile(zip_path) as z:
  names=[n for n in z.namelist() if not n.endswith("/")]
  prefix="generator/" if any(n.startswith("generator/TV/") for n in names) else ""
  if not any(n.startswith(prefix+"TV/") for n in names):
   raise ValueError("The selected ZIP does not contain the RPG Maker MZ generator structure.")
  for n in names:
   if prefix and not n.startswith(prefix):continue
   rel=Path(n[len(prefix):] if prefix else n)
   if not rel.parts or rel.parts[0] not in {"Face","TV","TVD","SV","Variation"}:
    # Preserve standard gradients too, but do not register them as pieces.
    if rel.name.lower().startswith("grad_"):
     target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(z.read(n));valid+=1
    continue
   data=z.read(n)
   if rel.suffix.lower()==".png" and not _png_ok(data):
    invalid+=1;continue
   target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);valid+=1

 return _register_existing(dest,valid,invalid)


def import_generator_folder(folder_path):
 app_paths.bootstrap()
 src=Path(folder_path)
 if src.name.lower()!="generator" and (src/"generator").is_dir():src=src/"generator"
 if not (src/"TV").is_dir():raise ValueError("Choose the RPG Maker MZ generator folder containing TV, Face, TVD, SV and Variation.")
 dest=app_paths.DATA_ROOT/"mz_generator";valid=invalid=0
 for p in src.rglob("*"):
  if not p.is_file():continue
  rel=p.relative_to(src)
  if rel.parts[0] not in {"Face","TV","TVD","SV","Variation"} and not p.name.lower().startswith("grad_"):continue
  data=p.read_bytes()
  if p.suffix.lower()==".png" and not _png_ok(data):invalid+=1;continue
  target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);valid+=1
 # Reuse registry builder by packaging only the local copy temporarily is unnecessary; register in-place.
 return _register_existing(dest,valid,invalid)

def refresh_local_import():
 app_paths.bootstrap()
 dest=app_paths.DATA_ROOT/"mz_generator"
 if not (dest/"TV").is_dir():raise ValueError("No previously imported RPG Maker MZ generator library was found.")
 return _register_existing(dest,0,0)

def _register_existing(dest,valid=0,invalid=0):
 regp=app_paths.DATA_ROOT/"master_registry.json";reg=_load(regp,{"schemaVersion":2,"masters":[]})
 bykey={m.get("key"):m for m in reg.get("masters",[])}
 masters_added=masters_updated=0
 for sex in SEXES:
  key=f"MZ_{sex}_Standard";candidates={rep:_find_body(dest,rep,sex) for rep in ("TV","FG","TVD","SV")}
  outputs={rep:{"status":"reference" if p and p.exists() else "missing","locked":True,"size":list(EXPECTED.get(rep,(144,144))),"base":_rel(p) if p and p.exists() else ""} for rep,p in candidates.items()}
  outputs["Variation"]={"status":"reference","locked":True,"size":[64,64],"base":""}
  record={"id":f"PS-MZ-{sex.upper()}-STANDARD","name":f"RPG Maker MZ {sex}","key":key,"sexClass":sex.lower(),"bodyClass":"kid" if sex=="Kid" else "standard","status":"reference","source":"RPG Maker MZ (user-owned local import)","outputs":outputs}
  if key in bykey:
   bykey[key].update(record);masters_updated+=1
  else:
   reg.setdefault("masters",[]).append(record);bykey[key]=record;masters_added+=1
 _save(regp,reg)
 groups={}
 for sex in SEXES:
  for rep,folder in REP_DIR.items():
   d=dest/folder/sex
   if not d.exists():continue
   for f in d.glob("*.png"):
    m=RX.match(f.name)
    if not m:continue
    _,cat,layer,pid=m.groups()
    if cat.lower()=="body":continue
    groups.setdefault((sex,cat,int(pid)),{}).setdefault(rep,[]).append((_rel(f),int(layer or 0),f.name))
 libp=app_paths.DATA_ROOT/"library.json";lib=_load(libp,{"version":"0.22.0","assets":[]});assets=lib.setdefault("assets",[]);byid={a.get("id"):a for a in assets};added=updated=0
 for (sex,cat,pid),reps in sorted(groups.items(),key=lambda x:(x[0][0],x[0][1],x[0][2])):
  aid=f"MZ-{sex.upper()}-{cat.upper()}-{pid:03d}";outputs={}
  for rep,entries in reps.items():
   paths=[x[0] for x in sorted(entries,key=lambda x:(x[1],x[2]))];outputs[rep]={"status":"complete","paths":paths,"path":paths[0]}
  record={"id":aid,"name":f"MZ {cat} {pid:02d}","category":CATEGORY_MAP.get(cat,cat),"body":f"MZ_{sex}_Standard","masterId":f"PS-MZ-{sex.upper()}-STANDARD","source":"RPG Maker MZ (user-owned local import)","nativeCategory":cat,"nativePartId":pid,"outputs":outputs}
  if aid in byid and str(byid[aid].get("source","")).startswith("RPG Maker MZ"):
   byid[aid].update(record);updated+=1
  elif aid not in byid:
   assets.append(record);byid[aid]=record;added+=1
 _save(libp,lib)
 return {"filesImported":valid,"invalidPngsSkipped":invalid,"componentsAdded":added,"componentsUpdated":updated,"componentGroupsFound":len(groups),"mastersAdded":masters_added,"mastersUpdated":masters_updated,"destination":str(dest)}
