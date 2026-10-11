import os,tempfile
from pathlib import Path
from PIL import Image
with tempfile.TemporaryDirectory() as td:
 os.environ["PROJECT_SHONEN_DATA"]=td
 import app_paths,body_master as b
 root=Path(td)
 masters=[{"id":"MZ-FEMALE"},{"id":"PS-BODY-04000"},{"id":"PS-BODY-04002"}]
 assert b.allocate_id(masters)=="PS-BODY-04001"
 full=[{"id":f"PS-BODY-{n:05d}"} for n in range(4000,4200)]
 try:b.allocate_id(full);raise AssertionError("expected exhaustion")
 except ValueError:pass
 out={"TV":{"size":[144,192],"status":"review","locked":False,"base":"masters/test.png"}}
 m={"id":"PS-BODY-04000","source":"Project Shonen","status":"draft","outputs":out}
 ok,_=b.validate_output(m,"TV");assert not ok
 p=root/"masters"/"test.png";p.parent.mkdir(parents=True)
 im=Image.new("RGBA",(144,192),(0,0,0,0));im.putpixel((0,0),(255,255,255,255));im.save(p)
 ok,_=b.validate_output(m,"TV");assert ok
 assert not b.selectable(m)
 out["TV"]["status"]="approved";out["TV"]["locked"]=True;m["status"]="production";assert b.selectable(m)
 ref={"source":"RPG Maker MZ (user-owned local import)","status":"reference","outputs":{"TV":{"status":"reference","locked":True}}}
 assert b.is_reference(ref) and b.selectable(ref)
 ok,_=b.validate_output(ref,"TV");assert not ok
print("Body master workflow regression: OK")
