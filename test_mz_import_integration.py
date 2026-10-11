from pathlib import Path
import json, os, tempfile, zipfile
from PIL import Image

# This test uses generated stand-ins only. No RPG Maker artwork is stored in the repository.
root=Path(tempfile.mkdtemp(prefix="ps_mz_import_"))
os.environ["PROJECT_SHONEN_DATA"]=str(root/"data")
import app_paths
import mz_generator_importer as mz

def png(path,size,rgba):
    path.parent.mkdir(parents=True,exist_ok=True)
    Image.new("RGBA",size,rgba).save(path)

src=root/"generator"
for sex in ("Female","Male","Kid"):
    png(src/"TV"/sex/"TV_Body_p01.png",(144,192),(30,30,30,255))
    png(src/"TVD"/sex/"TVD_Body_p01.png",(144,48),(30,30,30,255))
    png(src/"SV"/sex/"SV_body_p01.png",(576,384),(30,30,30,255))
    png(src/"Face"/sex/"FG_Body_p01_c1_m001.png",(144,144),(30,30,30,255))
    # representative front, split rear/front, and color-mask companions
    png(src/"TV"/sex/"TV_FrontHair1_p01.png",(144,192),(255,0,0,80))
    png(src/"TV"/sex/"TV_FrontHair1_p01_c.png",(144,192),(255,255,255,80))
    png(src/"TV"/sex/"TV_RearHair1_p01.png",(144,192),(0,255,0,80))
    png(src/"TV"/sex/"TV_RearHair2_p01.png",(144,192),(0,0,255,80))
    png(src/"Variation"/sex/"icon_FrontHair_p01.png",(64,64),(255,0,0,255))

zpath=root/"fixture.zip"
with zipfile.ZipFile(zpath,"w",zipfile.ZIP_DEFLATED) as z:
    for p in src.rglob("*"):
        if p.is_file(): z.write(p,"generator/"+p.relative_to(src).as_posix())

r1=mz.import_generator_zip(zpath)
lib1=json.loads((app_paths.DATA_ROOT/"library.json").read_text(encoding="utf-8"))
reg1=json.loads((app_paths.DATA_ROOT/"master_registry.json").read_text(encoding="utf-8"))
ids1=[a.get("id") for a in lib1.get("assets",[])]
assert r1["renderSafetyValidated"] is True
assert r1["nativeFormatValidated"] is True
assert [144,144] in r1["nativeFormatAudit"]["faceSizes"]
assert len([m for m in reg1["masters"] if str(m.get("id","")).startswith("PS-MZ-")])==3
assert len(ids1)==len(set(ids1))
for sex in ("FEMALE","MALE","KID"):
    a=next(x for x in lib1["assets"] if x["id"]==f"MZ-{sex}-FRONTHAIR-001")
    o=a["outputs"]["TV"]
    assert all(x.get("role")=="art" for x in o["layers"])
    assert len(o["layers"])==1 and len(o.get("masks",[]))==1
    assert not (set(o["paths"]) & {x["path"] for x in o["masks"]})
    rear=next(x for x in lib1["assets"] if x["id"]==f"MZ-{sex}-REARHAIR-001")
    assert sorted(x["nativeLayer"] for x in rear["outputs"]["TV"]["layers"])==[1,2]

r2=mz.refresh_local_import()
lib2=json.loads((app_paths.DATA_ROOT/"library.json").read_text(encoding="utf-8"))
reg2=json.loads((app_paths.DATA_ROOT/"master_registry.json").read_text(encoding="utf-8"))
ids2=[a.get("id") for a in lib2.get("assets",[])]
assert ids2==ids1, "refresh changed or duplicated component identities"
assert len(reg2["masters"])==len(reg1["masters"]), "refresh duplicated masters"
assert r2["componentsAdded"]==0 and r2["mastersAdded"]==0
assert r2["renderSafetyValidated"] is True
assert r2["nativeFormatValidated"] is True
print("MZ IMPORT INTEGRATION: PASS")
