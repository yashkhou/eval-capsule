import hashlib,json,os,tempfile,zipfile
from pathlib import Path
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pack(case_dir,out):
 root=Path(case_dir); manifest=json.loads((root/'manifest.json').read_text()); files=sorted(set(manifest.get('files',[])+['manifest.json'])); hashes={f:sha(root/f) for f in files}; manifest['_hashes']=hashes
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('manifest.json',json.dumps(manifest,sort_keys=True,indent=2))
  for f in files:
   if f!='manifest.json': z.write(root/f,f)
def safe_extract(z,dst):
 root=Path(dst).resolve()
 for m in z.infolist():
  p=(root/m.filename).resolve()
  if root not in p.parents and p!=root: raise ValueError('unsafe zip path')
  z.extract(m,root)
def verify(dir):
 root=Path(dir); m=json.loads((root/'manifest.json').read_text()); bad=[]
 for f,h in m.get('_hashes',{}).items():
  if f=='manifest.json': continue
  if not (root/f).exists() or sha(root/f)!=h: bad.append(f)
 return m,bad
def run(capsule):
 with tempfile.TemporaryDirectory() as d:
  with zipfile.ZipFile(capsule) as z: safe_extract(z,d)
  m,bad=verify(d)
  if bad:return {'passed':False,'hash_failures':bad,'assertions':[]}
  data=json.loads((Path(d)/m['actual']).read_text()); results=[]
  for a in m.get('assertions',[]):
   val=data
   for part in a['path'].strip('/').split('/') if a['path'].strip('/') else []: val=val[int(part)] if isinstance(val,list) else val[part]
   ok=(val==a['equals']) if 'equals' in a else (a['contains'] in val if isinstance(val,(str,list)) else False); results.append({'assertion':a,'passed':ok,'actual':val})
  return {'passed':all(x['passed'] for x in results),'hash_failures':[],'assertions':results}
