import ast, csv, sys, pathlib
src = pathlib.Path(sys.argv[1]).read_text()
tree = ast.parse(src)
study = None
for node in tree.body:
    if isinstance(node, ast.AnnAssign) and getattr(node.target, 'id', '') == 'BAFFIN_SI_TABLE_S1':
        study = ast.literal_eval(node.value)
mine = list(csv.DictReader(open(sys.argv[2])))
assert len(study) == len(mine) == 27, (len(study), len(mine))
n = 0
for s, m in zip(study, mine):
    lo, hi = m['depth'].split('-')
    checks = [('core', s['core'], m['core']), ('depth_lo', s['depth_lo_cm'], float(lo)), ('depth_hi', s['depth_hi_cm'], float(hi)),
              ('lab', s['lab_id'], m['lab_id']), ('c14', s['c14_age'], float(m['c14'])), ('err', s['c14_err'], float(m['err'])),
              ('mu', s['si_mu'], int(m['mu'])), ('sigma', s['si_sig'], int(m['sigma'])), ('material', s['material'], m['material'])]
    for k, a, b in checks:
        if a != b:
            n += 1; print('MISMATCH', m['lab_id'], k, 'study=', a, 'image=', b)
print('rows compared:', len(mine), 'fields mismatched:', n)
