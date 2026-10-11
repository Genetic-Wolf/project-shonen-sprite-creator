import production_dashboard as d
masters=[]
ref={"id":"R","source":"RPG Maker MZ (user-owned local import)"}
assert d.classify(ref,masters)["state"]=="Imported MZ Reference"
assets=[ref,{"id":"D","status":"draft","outputs":{},"compatibility":{"matrix":{}}}]
q=d.queues(assets,masters)
assert len(q["Imported References"])==1 and len(q["In Production"])==1
info=d.classify(assets[1],masters)
assert info["missing"]==5 and info["action"]=="Continue Production"
print("Visual production dashboard regression: OK")
\nfrom pathlib import Path\nsrc=Path("integrated_editors.py").read_text(encoding="utf-8")\nassert '"Needs Attention","In Production","Ready for Review","Production Ready","Imported References"' in src\nassert "def rebuild_filtered(self):" in src\n