"""Calibrate all 27 SI Table S1 dates under a grid of recipes and compare with the published mu/sigma/HPD bounds."""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import mycal

rows = mycal.table_s1()
DR = {'52': (71, 69), '64': (218, 135), '67': (218, 135), '77': (103, 106)}

def recipes(core):
    d, e = DR[core]
    out = []
    for curve in ('Marine20', 'IntCal20', 'Marine13', 'IntCal13'):
        for sign, lab in ((+1, '+dR'), (-1, '-dR'), (0, 'dR=0')):
            for err_lab, ee in (('tab_err', e), ('err0', 0.0), ('err50', 50.0)):
                if sign == 0 and err_lab != 'err0':
                    continue
                out.append((f'{curve} {lab} ({err_lab})', curve, sign * d, ee))
    return out

results = {}
for core in ('52', '64', '67', '77'):
    cr = [r for r in rows if r['core'] == core]
    res = {}
    for name, curve, dR, ee in recipes(core):
        per = []
        for r in cr:
            c = mycal.calibrate(float(r['c14']), float(r['err']), curve, dR, ee)
            per.append(dict(lab=r['lab_id'], depth=r['depth'], pub_mu=int(r['mu']), pub_sd=int(r['sigma']),
                            mu=round(c['mean'], 1), sd=round(c['sd'], 1), d_mu=round(c['mean'] - int(r['mu']), 1),
                            d_sd=round(c['sd'] - int(r['sigma']), 1),
                            d_h68=[round(c['h68'][1] - int(r['h68_hi']), 0), round(c['h68'][0] - int(r['h68_lo']), 0)],
                            d_h95=[round(c['h95'][1] - int(r['h95_hi']), 0), round(c['h95'][0] - int(r['h95_lo']), 0)]))
        res[name] = per
    results[core] = res

out = pathlib.Path(__file__).resolve().parent.parent / 'out_recipe_grid.json'
out.write_text(json.dumps(results, indent=1))

# Summary: for each core and recipe, max |d_mu| over all dates, and over the 'deglacial' dates 8000-15000 14C
for core, res in results.items():
    print(f'\n=== Core {core} (n={len(next(iter(res.values())))}) — max |mu diff| all dates / median |mu diff| / max |sd diff|')
    ranked = sorted(res.items(), key=lambda kv: max(abs(x['d_mu']) for x in kv[1]))
    for name, per in ranked[:8]:
        dm = sorted(abs(x['d_mu']) for x in per)
        print(f'  {name:32s} max={dm[-1]:8.1f}  median={dm[len(dm)//2]:7.1f}  max|dsd|={max(abs(x["d_sd"]) for x in per):6.1f}')
