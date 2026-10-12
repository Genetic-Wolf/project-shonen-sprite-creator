from pathlib import Path
import tempfile,os,json
from PIL import Image
root=Path(tempfile.mkdtemp(prefix="ps_pkg_"));os.environ["PROJECT_SHONEN_DATA"]=str(root/"data")
import app_paths;app_paths.bootstrap()
import asset_package as p
def art(rel,size):
 q=app_paths.DATA_ROOT/rel;q.parent.mkdir(parents=True,exist_ok=True);im=Image.new("RGBA",size,(0,0,0,0));im.putpixel((2,2),(255,0,0,255));im.save(q);return rel
sizes={"TV":(144,192),"FG":(144,144),"TVD":(144,48),"SV":(576,384),"Variation":(64,64)}
outputs={k:{"status":"complete","path":art("assets/primary/"+k+".png",size)} for k,size in sizes.items()}
outputs["TV"]["masks"]=[{"path":art("assets/masks/tv_mask.png",sizes["TV"]),"role":"colorMask"}]
variant={"_inherit":["FG","TVD","SV","Variation"],"TV":{"status":"complete","path":art("assets/variants/tv.png",sizes["TV"])}}
asset={"id":"PS-CLOTHING-04400","name":"Portable Vest","category":"Clothing","source":"Project Shonen","compatibility":{"homeMasterId":"BODY-A","matrix":{"BODY-A":"YES","BODY-B":"CUSTOM"}},"outputs":outputs,"variants":{"BODY-B":variant},"status":"production","approved":True}
(app_paths.DATA_ROOT/"library.json").write_text(json.dumps({"version":"0.22.0","assets":[asset]},indent=2),encoding="utf-8")
pkg=root/"vest.psasset";r=p.export_piece(asset["id"],pkg);assert r["schemaVersion"]==2
m=p.inspect_package(pkg);assert m["asset"]["variants"]["BODY-B"]["_inherit"]==variant["_inherit"];assert m["asset"]["outputs"]["TV"]["masks"]
(app_paths.DATA_ROOT/"library.json").write_text(json.dumps({"version":"0.22.0","assets":[]}),encoding="utf-8")
p.import_piece(pkg);lib=json.loads((app_paths.DATA_ROOT/"library.json").read_text());a=lib["assets"][0]
assert a["compatibility"]["matrix"]["BODY-B"]=="CUSTOM";assert a["variants"]["BODY-B"]["_inherit"]==variant["_inherit"]
assert Path(app_paths.DATA_ROOT/a["variants"]["BODY-B"]["TV"]["path"]).exists();assert Path(app_paths.DATA_ROOT/a["outputs"]["TV"]["masks"][0]["path"]).exists()
copy=p.import_piece(pkg,new_id="PS-CLOTHING-04401");assert copy["copied"] and copy["originalId"]==asset["id"]
lib=json.loads((app_paths.DATA_ROOT/"library.json").read_text());assert {x["id"] for x in lib["assets"]}=={"PS-CLOTHING-04400","PS-CLOTHING-04401"}
print("Portable asset package round trip: OK")
