from pathlib import Path
import json,shutil,time,hashlib,re

DEST={"TV":"img/characters","FG":"img/faces","TVD":"img/characters","SV":"img/sv_actors"}
EXPECTED={"TV":(144,192),"FG":(144,144),"TVD":(144,48),"SV":(576,384)}

def safe_name(name):
    return re.sub(r"[^A-Za-z0-9_-]+","_",str(name).strip()).strip("_") or "Character"

def filename(name,out):
    n=safe_name(name)
    return {"TV":"$"+n+".png","FG":n+"_Face.png","TVD":"$"+n+"_Downed.png","SV":n+"_SV.png"}[out]

def staged_files(root):
    root=Path(root);rows=[]
    for out,dest in DEST.items():
        d=root/"exports"/out
        if not d.exists():continue
        for p in sorted(d.glob("*.png"),key=lambda x:x.name.casefold()):
            rows.append({"output":out,"source":str(p),"filename":p.name,"destination":dest+"/"+p.name,"size":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()})
    return rows

def write_manifest(root,character=None):
    root=Path(root);rows=staged_files(root);m={"schemaVersion":1,"kind":"Project Shonen RPG Maker MZ Export","character":character,"files":rows}
    p=root/"exports"/"project_shonen_mz_export.json";p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(m,indent=2),encoding="utf-8");return p,m

def validate_project(project):
    q=Path(project);return q.is_dir() and (q/"img").is_dir() and (q/"data").is_dir()

def install(root,project,selected=None):
    root=Path(root);project=Path(project)
    if not validate_project(project):raise ValueError("Choose a valid RPG Maker MZ project root containing img and data.")
    rows=staged_files(root);selected=set(selected or [r["destination"] for r in rows]);rows=[r for r in rows if r["destination"] in selected]
    if not rows:return {"installed":0,"backedUp":0,"manifest":None,"backup":None}
    stamp=time.strftime("%Y%m%d-%H%M%S");backup=root/"backups"/stamp;installed=[];backed=[]
    for r in rows:
        src=Path(r["source"]);target=project/r["destination"];target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():
            bp=backup/r["destination"];bp.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,bp);backed.append(r["destination"])
        shutil.copy2(src,target);installed.append(r["destination"])
    manifest={"schemaVersion":1,"kind":"Project Shonen RPG Maker MZ Install","project":str(project),"installed":installed,"backedUp":backed,"backupRoot":str(backup) if backed else None}
    mp=root/"exports"/"last_install_manifest.json";mp.write_text(json.dumps(manifest,indent=2),encoding="utf-8")
    return {"installed":len(installed),"backedUp":len(backed),"manifest":str(mp),"backup":str(backup) if backed else None}
