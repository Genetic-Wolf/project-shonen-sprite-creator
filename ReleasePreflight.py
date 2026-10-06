from pathlib import Path
import json,sys,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parent
EXPECTED={"TV":(144,192),"FG":(144,144),"TVD":(144,192),"SV":(576,384),"Variation":(144,144)}
def load(p):
 try:return json.load(open(p,encoding="utf-8"))
 except Exception as e:return {"__error__":str(e)}
def run():
 problems=[];warnings=[];passes=[]
 for name in ("master_registry.json","library.json"):
  d=load(ROOT/name)
  if "__error__" in d:problems.append(f"{name}: {d['__error__']}")
  else:passes.append(f"{name}: valid JSON")
 reg=load(ROOT/"master_registry.json");lib=load(ROOT/"library.json")
 if "__error__" not in reg:
  ids=set()
  for m in reg.get("masters",[]):
   if m.get("id") in ids:problems.append(f"Duplicate master ID: {m.get('id')}")
   ids.add(m.get("id"))
   for typ,o in m.get("outputs",{}).items():
    p=ROOT/o.get("base","")
    if not p.exists():problems.append(f"{m.get('name')} {typ}: registered base missing");continue
    try:
     size=Image.open(p).size
     expected=tuple(o.get("size",EXPECTED.get(typ,())))
     if size!=expected:problems.append(f"{m.get('name')} {typ}: {size} != {expected}")
    except Exception as e:problems.append(f"{m.get('name')} {typ}: unreadable image: {e}")
    if o.get("status")!="approved" or not o.get("locked"):warnings.append(f"{m.get('name')} {typ}: not production-approved + locked")
 if "__error__" not in lib:
  ids=set()
  for a in lib.get("assets",[]):
   if a.get("id") in ids:problems.append(f"Duplicate asset ID: {a.get('id')}")
   ids.add(a.get("id"))
   for typ,o in a.get("outputs",{}).items():
    if o.get("status")=="complete":
     p=ROOT/o.get("path","")
     if not p.exists():problems.append(f"{a.get('name')} {typ}: marked complete but file missing")
 report=["PROJECT SHONEN SPRITE CREATOR — RELEASE PREFLIGHT",""]
 report += ["PASS: "+x for x in passes]
 report += ["ERROR: "+x for x in problems]
 report += ["NOTICE: "+x for x in warnings]
 report += ["",f"RESULT: {'FAIL' if problems else 'PASS WITH READINESS NOTICES' if warnings else 'PASS'}"]
 (ROOT/"PREFLIGHT_RESULT.txt").write_text("\n".join(report),encoding="utf-8")
 print("\n".join(report))
 return 1 if problems else 0
if __name__=="__main__":sys.exit(run())
