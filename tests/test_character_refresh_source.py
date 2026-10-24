"""Source-level regression for character builder refresh method shadowing."""
import ast
import pathlib
import unittest

SOURCE=pathlib.Path(__file__).resolve().parents[1]/"integrated_character_rpg.py"

class CharacterRefreshTests(unittest.TestCase):
    def test_single_refresh_handler(self):
        tree=ast.parse(SOURCE.read_text(encoding="utf-8"))
        builder=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="CharacterBuilder")
        methods=[n for n in builder.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name=="reload_library"]
        self.assertEqual(len(methods),1,"Duplicate refresh handlers shadow the real implementation")
        names={n.id for n in ast.walk(methods[0]) if isinstance(n,ast.Name)}
        self.assertTrue({"lookup","old_ids"}.issubset(names),"Refresh must remap selected asset IDs")
        self.assertIn("self.thumbcache.clear()",ast.get_source_segment(SOURCE.read_text(encoding="utf-8"),methods[0]))
if __name__=="__main__":unittest.main()
