import ast
from pathlib import Path

src=Path("integrated_character_rpg.py").read_text(encoding="utf-8")
tree=ast.parse(src)
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="CharacterBuilder")
fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=="compatible")
mod=ast.Module(body=[fn],type_ignores=[])
ast.fix_missing_locations(mod)
ns={}
exec(compile(mod,"<compatible>","exec"),ns)
compatible=ns["compatible"]
class Dummy: pass
d=Dummy()
m={"id":"B-FS","key":"Female_Standard","family":"Female","bodyType":"Standard","bust":"Medium"}
base={"body":"Female_Standard","masterId":"B-FS","compatibility":{"scope":"Body Specific","family":"Female","bust":"Any"}}
assert compatible(d,base,m) is True
a={"body":"Other","masterId":"OTHER","compatibility":{"scope":"Universal","matrix":{"B-FS":"NO"}}}
assert compatible(d,a,m) is False
a["compatibility"]["matrix"]["B-FS"]="CUSTOM"
assert compatible(d,a,m) is False
a["variants"]={"B-FS":{"TV":{"status":"complete","path":"assets/variants/test.png"}}}
assert compatible(d,a,m) is False
a["variants"]["B-FS"]["_inherit"]=["FG","TVD","SV","Variation"]
assert compatible(d,a,m) is True
a["compatibility"]["matrix"]["B-FS"]="YES"
assert compatible(d,a,m) is True
fam={"body":"Other","masterId":"OTHER","compatibility":{"scope":"Family Compatible","family":"Female","bust":"Medium"}}
assert compatible(d,fam,m) is True
m2={"id":"B-FL","key":"Female_Large","family":"Female","bodyType":"Standard","bust":"Large"}
assert compatible(d,fam,m2) is False
print("Compatibility matrix regression: OK")
