import os,tempfile
from pathlib import Path
from PIL import Image
with tempfile.TemporaryDirectory() as td:
 os.environ["PROJECT_SHONEN_DATA"]=td
 import app_paths,production_pipeline as pp,piece_lifecycle as pl
 root=Path(td);(root/"a").mkdir()
 asset={"status":"draft","outputs":{},"compatibility":{"matrix":{}}}
 masters=[]
 assert pl.lifecycle(asset,masters)=="Draft"
 for out,size in pp.OUTPUTS.items():
  p=root/"a"/(out+".png");im=Image.new("RGBA",size,(0,0,0,0));im.putpixel((0,0),(255,0,0,255));im.save(p)
  asset["outputs"][out]={"status":"complete","path":"a/"+out+".png"}
 assert pl.lifecycle(asset,masters)=="Review"
 ok,_=pl.approve(asset,masters);assert ok and asset["status"]=="production" and asset["approved"] is True
 assert pl.lifecycle(asset,masters)=="Production Ready"
 pl.reopen(asset);assert asset["status"]=="revision" and asset["approved"] is False
 assert pl.lifecycle(asset,masters)=="Review"
 asset["outputs"]["TV"]["path"]="a/missing.png"
 ok,_=pl.approve(asset,masters);assert not ok
 assert pl.lifecycle(asset,masters)=="Needs Attention"
print("Piece lifecycle regression: OK")
