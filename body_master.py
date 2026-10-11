from pathlib import Path
from PIL import Image
import re
import app_paths

BODY_MIN=4000
BODY_MAX=4199

def is_reference(master):
    return master.get("status")=="reference" or str(master.get("source","")).startswith("RPG Maker MZ")

def selectable(master):
    if is_reference(master):
        return all(o.get("locked") and o.get("status")=="reference" for o in (master.get("outputs") or {}).values())
    return master.get("status")=="production" and all(o.get("locked") and o.get("status")=="approved" for o in (master.get("outputs") or {}).values())

def allocate_id(masters):
    used=set()
    for m in masters:
        hit=re.fullmatch(r"PS-BODY-(\d{5})",str(m.get("id","")))
        if hit:used.add(int(hit.group(1)))
    for n in range(BODY_MIN,BODY_MAX+1):
        if n not in used:return f"PS-BODY-{n:05d}"
    raise ValueError("Project Shonen body ID range 4000-4199 is full.")

def validate_output(master,out):
    record=(master.get("outputs") or {}).get(out)
    if not record:return False,"Output is not registered."
    if is_reference(master):return False,"Imported RPG Maker MZ reference masters are read-only."
    if record.get("status") not in ("review","approved"):return False,"Import reviewed artwork before approval."
    rel=record.get("base")
    if not rel:return False,"No master artwork path is registered."
    p=app_paths.resolve(rel)
    if not p.exists():return False,"Master artwork file is missing."
    try:
        with Image.open(p) as im:
            expected=tuple(record.get("size") or ())
            if im.size!=expected:return False,f"Expected {expected[0]}x{expected[1]} artwork."
            a=im.convert("RGBA").getchannel("A").getextrema()
            if a==(0,0):return False,"Master artwork is completely transparent."
            if a==(255,255):return False,"Master artwork must preserve transparent background."
    except Exception as e:return False,"Master artwork is unreadable: "+str(e)
    return True,"Ready for approval."
