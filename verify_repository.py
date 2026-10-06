from pathlib import Path
import json,sys
R=Path(__file__).resolve().parent
d=json.loads((R/"REPOSITORY_LAYOUT.json").read_text())
e=[]
for x in d["criticalFiles"]:
    if not (R/x).is_file(): e.append("Missing critical file: "+x)
for x in d["topLevelDirectories"]:
    if not (R/x).is_dir(): e.append("Missing directory: "+x)
for p in R.iterdir():
    if p.is_file() and ("RELEASE_NOTES" in p.name.upper() or p.name.upper().startswith("V0.")): e.append("Legacy note at root: "+p.name)
print("REPOSITORY VALIDATION: "+("FAIL" if e else "PASS"))
print("\n".join(e))
sys.exit(bool(e))
