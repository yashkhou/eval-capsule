import unittest,sys,tempfile,json,zipfile; from pathlib import Path; sys.path.insert(0,'src')
from eval_capsule.core import *
class T(unittest.TestCase):
 def test_roundtrip(self):
  with tempfile.TemporaryDirectory() as d:
   c=Path(d)/'case'; c.mkdir(); (c/'actual.json').write_text('{"x":1}'); (c/'manifest.json').write_text(json.dumps({'actual':'actual.json','files':['actual.json'],'assertions':[{'path':'/x','equals':1}]})); out=Path(d)/'a.zip'; pack(c,out); self.assertTrue(run(out)['passed'])
 def test_hash_failure(self):
  with tempfile.TemporaryDirectory() as d:
   c=Path(d)/'case'; c.mkdir(); (c/'actual.json').write_text('{"x":1}'); (c/'manifest.json').write_text(json.dumps({'actual':'actual.json','files':['actual.json'],'assertions':[]})); out=Path(d)/'a.zip'; pack(c,out)
   with zipfile.ZipFile(out,'a') as z:z.writestr('actual.json','{"x":2}')
   self.assertFalse(run(out)['passed'])
