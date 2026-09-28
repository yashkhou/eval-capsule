import argparse,json
from .core import pack,run
p=argparse.ArgumentParser(); s=p.add_subparsers(dest='cmd',required=True); a=s.add_parser('pack'); a.add_argument('case'); a.add_argument('out'); b=s.add_parser('run'); b.add_argument('capsule'); x=p.parse_args()
if x.cmd=='pack': pack(x.case,x.out)
else:
 r=run(x.capsule); print(json.dumps(r,indent=2)); raise SystemExit(0 if r['passed'] else 1)
