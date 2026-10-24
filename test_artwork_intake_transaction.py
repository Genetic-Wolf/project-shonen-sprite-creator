import os,tempfile,json
from pathlib import Path
from PIL import Image
root=Path(tempfile.mkdtemp(prefix="intake_"));os.environ["PROJECT_SHONEN_DATA"]=str(root/"data")
import app_paths,artwork_intake as a
app_paths.bootstrap()
master={"id":"B1","key":"b1","outputs":{k:{"status":"approved","locked":True} for k in a.OUTS}}
a.REG.write_text(json.dumps({"masters":[master]}),encoding="utf-8")
asset={"id":"A1","name":"Test Piece","masterId":"B1","body":None,"category":"Hair / Front","approved":True,"status":"production","outputs":{}}
a.LIB.write_text(json.dumps({"assets":[asset]}),encoding="utf-8")
def workspace(out,name):
 d=root/name;d.mkdir();p=d/"finished.png";Image.new("RGBA",a.OUTS[out],(10,20,30,128)).save(p)
 (d/"project_shonen_artwork.json").write_text(json.dumps({"assetId":"A1","output":out,"expectedSize":list(a.OUTS[out]),"destination":"assets/outputs/"+out,"masterId":"B1","body":None,"category":"Hair / Front"}));return p
tv=workspace("TV","tv");fg=workspace("FG","fg")
r=a.import_finished_pngs([tv,fg]);assert sum(x["ok"] for x in r)==2
lib=json.loads(a.LIB.read_text())["assets"][0];assert lib["approved"] is False and lib["status"]=="revision";assert set(lib["outputs"])=={"TV","FG"}
assert (a.ROOT/lib["outputs"]["TV"]["path"]).exists()
# duplicate destination in a batch must be rejected without corrupting the successful target
dup=root/"dup";dup.mkdir();dp=dup/"finished.png";Image.new("RGBA",a.OUTS["TV"],(5,5,5,128)).save(dp);(dup/"project_shonen_artwork.json").write_text((tv.parent/"project_shonen_artwork.json").read_text())
r=a.import_finished_pngs([tv,dp]);assert sum(x["ok"] for x in r)==1 and any("same piece/output" in x.get("reason","") for x in r)
# invalid companion does not prevent independently valid managed artwork
bad=root/"bad.png";bad.write_bytes(b"not png");r=a.import_finished_pngs([fg,bad]);assert any(x["ok"] for x in r) and any(not x["ok"] for x in r)
# A JPEG renamed .png must never be accepted as native artwork.
fake=root/"jpeg";fake.mkdir();jp=fake/"finished.png"
Image.new("RGB",a.OUTS["TV"],(20,30,40)).save(jp,format="JPEG")
(fake/"project_shonen_artwork.json").write_text((tv.parent/"project_shonen_artwork.json").read_text())
r=a.import_finished_pngs([jp]);assert len(r)==1 and not r[0]["ok"] and "genuine PNG" in r[0]["reason"]
# Even registered IDs are untrusted input; reject traversal before constructing a destination.
unsafe=json.loads(a.LIB.read_text());unsafe["assets"][0]["id"]="../escape";a.LIB.write_text(json.dumps(unsafe))
(fake/"project_shonen_artwork.json").write_text((tv.parent/"project_shonen_artwork.json").read_text().replace('"A1"','"../escape"'))
r=a.import_finished_pngs([jp]);assert len(r)==1 and not r[0]["ok"]
print("MANAGED ARTWORK INTAKE: PASS")
