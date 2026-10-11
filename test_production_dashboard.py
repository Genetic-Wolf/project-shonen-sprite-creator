import production_dashboard as d
masters=[{"id":"B1","name":"Male Standard"}]
ref={"id":"R","name":"Stock Hair","source":"RPG Maker MZ (user-owned local import)","category":"Hair / Front"}
draft={"id":"D","name":"Shinobi Vest","status":"draft","category":"Clothing / Shirt","compatibility":{"homeMasterId":"B1","matrix":{}},"outputs":{}}
assert d.classify(ref,masters)["state"]=="Imported MZ Reference"
info=d.classify(draft,masters);assert info["missing"]==5 and info["action"]=="Continue Production" and info["progress"]=="W· F· D· B· P·"
q=d.queues([ref,draft],masters);assert len(q["Imported References"])==1 and len(q["In Production"])==1
assert d.body_label(draft,masters)=="Male Standard"
assert [x[0]["id"] for x in d.filter_assets([ref,draft],masters,query="vest")]==["D"]
assert [x[0]["id"] for x in d.filter_assets([ref,draft],masters,category="Hair / Front")]==["R"]
assert [x[0]["id"] for x in d.filter_assets([ref,draft],masters,body="Male Standard")]==["D"]
assert [x[0]["id"] for x in d.filter_assets([ref,draft],masters,queue="Imported References")]==["R"]
from pathlib import Path
src=Path("integrated_editors.py").read_text(encoding="utf-8")
for token in ("Search","Category","Body","Sort","Showing ","def clear_filters(self):"):assert token in src
print("Visual production dashboard regression: OK")
