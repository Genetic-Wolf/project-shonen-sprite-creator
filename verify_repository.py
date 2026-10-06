from pathlib import Path
import json, sys

R = Path(__file__).resolve().parent
layout = json.loads((R / "REPOSITORY_LAYOUT.json").read_text(encoding="utf-8"))
errors = []

for rel in layout["criticalFiles"]:
    if not (R / rel).is_file():
        errors.append("Missing critical file: " + rel)
for rel in layout["topLevelDirectories"]:
    if not (R / rel).is_dir():
        errors.append("Missing directory: " + rel)

for p in R.iterdir():
    name = p.name
    upper = name.upper()
    if p.is_file() and ("RELEASE_NOTES" in upper or upper.startswith("V0.") or "AUDIT_REPORT" in upper):
        errors.append("Legacy release/audit file at root: " + name)
    for prefix in layout.get("forbiddenRootPrefixes", []):
        if name.startswith(prefix):
            errors.append("Legacy release package at root: " + name)

registry = json.loads((R / "master_registry.json").read_text(encoding="utf-8"))
for master in registry.get("masters", []):
    outputs = master.get("outputs", {})
    ready = all(v.get("status") == "approved" and v.get("locked") is True for v in outputs.values())
    if master.get("status") == "production" and not ready:
        errors.append("Master marked production before all outputs are approved+locked: " + master.get("name","?"))
    for output_name, output in outputs.items():
        base = output.get("base")
        if base and not (R / base).is_file():
            errors.append(f"Missing master output: {master.get('name','?')} {output_name}: {base}")

print("REPOSITORY VALIDATION: " + ("FAIL" if errors else "PASS"))
for error in errors:
    print(" - " + error)
sys.exit(1 if errors else 0)
