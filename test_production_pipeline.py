import os,tempfile
from pathlib import Path
from PIL import Image
with tempfile.TemporaryDirectory() as td:
 os.environ["PROJECT_SHONEN_DATA"]=td
 import app_paths,production_pipeline as p
 root=Path(td);(root/"assets").mkdir()
 def png(name,size):
  q=root/"assets"/name;im=Image.new("RGBA",size,(0,0,0,0));im.putpixel((0,0),(255,0,0,255));im.save(q);return "assets/"+name
 asset={"outputs":{},"compatibility":{"matrix":{"B2":"CUSTOM"}},"variants":{"B2":{}}}
 masters=[{"id":"B1","name":"Base"},{"id":"B2","name":"Custom Body"}]
 r=p.evaluate(asset,masters);assert r["state"]=="Needs Artwork";assert len(r["blockers"])==10
 for out,size in p.OUTPUTS.items():asset["outputs"][out]={"status":"complete","path":png("p_"+out+".png",size)}
 r=p.evaluate(asset,masters);assert len(r["blockers"])==5 and p.next_job(asset,masters)["kind"]=="custom"
 for out,size in p.OUTPUTS.items():asset["variants"]["B2"][out]={"status":"complete","path":png("v_"+out+".png",size)}
 r=p.evaluate(asset,masters);assert r["complete"] and r["state"]=="Production Ready" and p.next_job(asset,masters) is None
 asset["variants"]["B2"]["TV"]["path"]="assets/missing.png";r=p.evaluate(asset,masters);assert r["state"]=="Needs Attention"
print("Production pipeline regression: OK")
