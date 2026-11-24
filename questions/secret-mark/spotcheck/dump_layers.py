import sys, json
sys.path.insert(0, sys.argv[1])  # study analysis dir (study code, not downloaded data)
import run_stylometry as rs
ms = rs.load_mar_saba_texts()
json.dump(ms, open(sys.argv[2],'w'), ensure_ascii=False, indent=0)
for k,v in ms.items():
    print('==',k,len(v)); print(' '.join(v))
