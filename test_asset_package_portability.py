import os,tempfile,json,zipfile
from pathlib import Path
from PIL import Image
root=Path(tempfile.mkdtemp(prefix="psasset_"));os.environ["PROJECT_SHONEN_DATA"]=str(root/"data")
import app_paths
app_paths.bootstrap()
import asset_package as p
def png(rel,size=(144,192)):
 q=app_paths.DATA_ROOT/rel;q.parent.mkdir(parents=True,exist_ok=True);Image.new("RGBA",size,(1,2,3,100)).save(q);return rel
tv=png("assets/a_tv.png");mask=png("assets/a_mask.png");variant=png("assets/v_tv.png");icon=png("assets/icon.png",(64,64))
ora=app_paths.DATA_ROOT/"artist_workspace"/"a.ora";ora.parent.mkdir(parents=True,exist_ok=True);ora.write_bytes(b"editable")
asset={"id":"PS-CLOTHING-04400","name":"Portable Vest","category":"Clothing","source":"Project Shonen","compatibility":{"homeMasterId":"B1","matrix":{"B1":"YES","B2":"CUSTOM"}},"outputs":{"TV":{"status":"complete","path":tv,"paths":[tv],"masks":[{"path":mask,"role":"colorMask"}],"icon":icon,"sourceWorkspace":str(ora.relative_to(app_paths.DATA_ROOT)).replace("\\","/")}},"variants":{"B2":{"_inherit":["FG","TVD","SV","Variation"],"TV":{"status":"complete","path":variant,"paths":[variant]}}}}
lib={"version":"0.22.0","assets":[asset]};(app_paths.DATA_ROOT/"library.json").write_text(json.dumps(lib),encoding="utf-8")
pkg=root/"vest.psasset";r=p.export_piece(asset["id"],pkg);assert r["schemaVersion"]==2
m=p.inspect_package(pkg);assert m["asset"]["variants"]["B2"]["_inherit"]==["FG","TVD","SV","Variation"];assert m["asset"]["compatibility"]["matrix"]["B2"]=="CUSTOM"
with zipfile.ZipFile(pkg) as z:
 names=z.namelist();assert any("/masks/" in x for x in names);assert any("/icon/" in x for x in names);assert any("/source/" in x for x in names);assert any("variants/B2" in x for x in names)
(app_paths.DATA_ROOT/"library.json").write_text(json.dumps({"version":"0.22.0","assets":[]}),encoding="utf-8")
ri=p.import_piece(pkg);new=json.loads((app_paths.DATA_ROOT/"library.json").read_text())["assets"][0]
assert new["compatibility"]["matrix"]["B2"]=="CUSTOM";assert new["variants"]["B2"]["_inherit"]==["FG","TVD","SV","Variation"]
for rel in [new["outputs"]["TV"]["path"],new["outputs"]["TV"]["masks"][0]["path"],new["outputs"]["TV"]["icon"],new["outputs"]["TV"]["sourceWorkspace"],new["variants"]["B2"]["TV"]["path"]]:assert app_paths.resolve(rel).exists(),rel
try:p.import_piece(pkg)
except FileExistsError:pass
else:raise AssertionError("ID collision was not blocked")
copy=p.import_piece(pkg,new_id="PS-CLOTHING-04401");assert copy["copied"] is True
print("PSASSET PORTABILITY: PASS")
