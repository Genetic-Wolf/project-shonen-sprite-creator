import ast
from pathlib import Path
src=Path("integrated_editors.py").read_text(encoding="utf-8")
tree=ast.parse(src)
piece=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="PieceEditor")
names={n.name for n in piece.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
assert {"select_asset","continue_artwork","approve_piece","reopen_piece"}.issubset(names)
app=Path("ProjectShonenSpriteCreator.py").read_text(encoding="utf-8")
assert "select_asset_id=select_asset_id,auto_continue=auto_continue" in app
assert 'self.page("pieces",select_asset_id=(asset or {}).get("id"),auto_continue=bool(asset))' in app
assert 'self.after(100,self.continue_artwork)' in src
print("Continuous artist workflow regression: OK")
