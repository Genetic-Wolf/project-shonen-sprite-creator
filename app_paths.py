from pathlib import Path
import os, sys, shutil, json

APP_NAME = "Project Shonen Sprite Creator"

def resource_root():
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
    return Path(__file__).resolve().parent

def data_root():
    override = os.environ.get("PROJECT_SHONEN_DATA")
    if override:
        return Path(override).expanduser().resolve()
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "Project Shonen" / "Sprite Creator"
    return Path.home() / ".project-shonen" / "sprite-creator"

RESOURCE_ROOT = resource_root()
DATA_ROOT = data_root()

WRITABLE_DIRS = ("assets", "masters", "artist_workspace", "character_projects", "exports", "backups")
DEFAULT_FILES = ("library.json", "master_registry.json", "asset_outputs.json", "artist_settings.json")

def bootstrap():
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    for name in WRITABLE_DIRS:
        (DATA_ROOT / name).mkdir(parents=True, exist_ok=True)
    # First-run copy only. Upgrades never overwrite artist data.
    for name in ("library.json", "master_registry.json", "asset_outputs.json"):
        dst = DATA_ROOT / name
        src = RESOURCE_ROOT / name
        if not dst.exists() and src.exists():
            shutil.copy2(src, dst)
    return DATA_ROOT

def resource(*parts):
    return RESOURCE_ROOT.joinpath(*parts)

def data(*parts):
    bootstrap()
    return DATA_ROOT.joinpath(*parts)

def resolve(rel):
    rel = Path(rel)
    writable = DATA_ROOT / rel
    if writable.exists():
        return writable
    return RESOURCE_ROOT / rel

def self_test():
    bootstrap()
    checks = {
        "resourceRoot": str(RESOURCE_ROOT),
        "dataRoot": str(DATA_ROOT),
        "resourceRootExists": RESOURCE_ROOT.exists(),
        "dataRootWritable": os.access(DATA_ROOT, os.W_OK),
        "library": data("library.json").is_file(),
        "masterRegistry": data("master_registry.json").is_file(),
        "templates": resource("templates").is_dir(),
    }
    try:
        json.loads(data("library.json").read_text(encoding="utf-8"))
        json.loads(data("master_registry.json").read_text(encoding="utf-8"))
        checks["jsonValid"] = True
    except Exception:
        checks["jsonValid"] = False
    checks["ok"] = all(v for k,v in checks.items() if isinstance(v,bool))
    return checks
