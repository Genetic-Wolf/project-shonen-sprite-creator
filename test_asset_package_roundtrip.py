import os,tempfile,json
from pathlib import Path
from PIL import Image
root=Path(tempfile.mkdtemp(prefix="psasset_"));os.environ["PROJECT_SHONEN_DATA"]=str(root/"data")
import app_paths,asset_package
app_paths.bootstrap()
def art(rel,size):
 p=app_paths.DATA_ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);Image.new("RGBA",size,(1,2,3,128)).save(p);return rel
outputs={}
sizes={"TV":(144,192),"FG":(144,144),"TVD":(144,48),"SV":(576,384),"Variation":(64,64)}
for rep,size in sizes.items():
 rel=art("assets/original/"+rep+".png",size);mask=art("assets/original/"+rep+"_mask.png",size);outputs[rep]={"status":"complete","path":rel,"paths":[rel],"layers":[{"path":rel,"role":"art"}],"masks":[{"path":mask,"role":"colorMask"}]}
vrel=art("assets/original/custom_tv.png",(144,192))
asset={"id":"PS-CLOTHING-04400","name":"Round Trip Vest","category":"Clothing","source":"Project Shonen","compatibility":{"homeMasterId":"B1","matrix":{"B1":"YES","B2":"CUSTOM"}},"outputs":outputs,"variants":{"B2":{"_inherit":["FG","TVD","SV","Variation"],"TV":{"status":"complete","path":vrel,"paths":[vrel]}}}}
lib={"version":"0.22.0","assets":[asset]};asset_package.LIB.parent.mkdir(parents=True,exist_ok=True);asset_package.LIB.write_text(json.dumps(lib),encoding="utf-8")
pkg=root/"vest.psasset";r=asset_package.export_piece(asset["id"],pkg);assert r["schemaVersion"]==2 and r["files"]>=11
m=asset_package.inspect_package(pkg);assert m["asset"]["variants"]["B2"]["_inherit"]==["FG","TVD","SV","Variation"];assert m["checksums"]
asset_package.LIB.write_text(json.dumps({"version":"0.22.0","assets":[]}),encoding="utf-8")
ri=asset_package.import_piece(pkg);assert ri["schemaVersion"]==2
got=json.loads(asset_package.LIB.read_text())["assets"][0]
assert got["compatibility"]["matrix"]["B2"]=="CUSTOM";assert got["variants"]["B2"]["_inherit"]==["FG","TVD","SV","Variation"]
for rep in sizes:
 o=got["outputs"][rep];assert Path(app_paths.DATA_ROOT/o["path"]).exists();assert Path(app_paths.DATA_ROOT/o["masks"][0]["path"]).exists()
assert Path(app_paths.DATA_ROOT/got["variants"]["B2"]["TV"]["path"]).exists()
# checksum tampering must be rejected
import zipfile
bad=root/"bad.psasset"
with zipfile.ZipFile(pkg) as src,zipfile.ZipFile(bad,"w") as dst:
 for n in src.namelist():dst.writestr(n,b"tampered" if n!="manifest.json" and n.endswith(".png") else src.read(n))
try:asset_package.inspect_package(bad);raise AssertionError("tampered package accepted")
except ValueError:pass
print("PSASSET PORTABILITY: PASS")
