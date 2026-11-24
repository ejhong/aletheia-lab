import json,sys,importlib.util,pathlib,collections
W=pathlib.Path(sys.argv[1])
spec=importlib.util.spec_from_file_location("rla",W/"analysis/run_linear_a.py"); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
sv=json.load(open(W/"data/kaphtor/data/linear-a/sign_values.json"))
sm,lb,nov=m.load_sign_table(sv)
print("n signs",len(sv["signs"]),"novel",len(nov))
for s,info in sv["signs"].items():
    p=info.get("primary") or {}
    l=info.get("linear_b"); lv=l.get("value") if isinstance(l,dict) else l
    print(f"{s:8s} kaph={str(p.get('consonant'))+str(p.get('vowel')):8s} LB={str(lv):8s} cls={sm[s.upper()] or '-':2s} {'NOVEL' if s.upper() in nov else '     '} tier={info.get('confidence') or info.get('tier') or p.get('confidence')} status={info.get('status') or p.get('status')}")
print(sorted(info.keys()))
print(sorted(p.keys()))
print(json.dumps(sv['resolution_summary']['proposed'],ensure_ascii=False)[:6000])
