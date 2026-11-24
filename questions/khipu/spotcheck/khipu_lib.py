"""Own loader for OKR khipu.db (read-only). Independent of the study's code."""
import sqlite3, collections

def connect(db):
    return sqlite3.connect('file:' + db + '?mode=ro', uri=True)

def load_all(db):
    con = connect(db)
    meta = {}
    for kid, okr, inv, prov, mus, mnum in con.execute(
            "select KHIPU_ID, OKR_NUM, INVESTIGATOR_NUM, PROVENANCE, MUSEUM_NAME, MUSEUM_NUM from khipu_main"):
        meta[kid] = dict(okr=okr, inv=inv, prov=(prov or '').strip(), museum=mus, mnum=mnum)
    color = {}
    for cid, fc, c1 in con.execute("select CORD_ID, FULL_COLOR, COLOR_CD_1 from ascher_cord_color"):
        color.setdefault(cid, (fc or c1 or '').strip())
    kvt = collections.defaultdict(int)
    kstr = collections.defaultdict(list)
    kc = {r[0]: (r[1], r[2], r[3]) for r in con.execute("select CLUSTER_ID, ORDINAL, START_POS, TOTAL_VALUE from knot_cluster")}
    for cid, tc, nt, v, clid, kord in con.execute(
            "select CORD_ID, TYPE_CODE, NUM_TURNS, knot_value_type, CLUSTER_ID, KNOT_ORDINAL from knot"):
        try:
            iv = int(float(v)) if v not in (None, '') else 0
        except ValueError:
            iv = 0
        if iv > 0:
            kvt[cid] += iv
        o = kc.get(clid, (0, 0, 0))
        kstr[cid].append((o[0] or 0, kord or 0, f"{tc}{int(nt) if nt else ''}"))
    sub = collections.defaultdict(list)
    cords = collections.defaultdict(list)
    for (kid, cid, lvl, clid, clord, cord_ord, att, length, invn, pend_from, attach_pos) in con.execute(
            "select KHIPU_ID, CORD_ID, CORD_LEVEL, CLUSTER_ID, CLUSTER_ORDINAL, CORD_ORDINAL, ATTACHMENT_TYPE, CORD_LENGTH, INVESTIGATOR_CORD_NUM, PENDANT_FROM, ATTACH_POS from cord"):
        rec = dict(cid=cid, lvl=lvl, clid=clid, clord=clord, ord=cord_ord, att=(att or '').strip(), length=length,
                   invn=invn, val=kvt.get(cid, 0), color=color.get(cid, ''), pos=attach_pos,
                   knots=' '.join(s for _, _, s in sorted(kstr.get(cid, []))))
        if lvl == 1:
            cords[kid].append(rec)
        else:
            sub[pend_from].append(rec)
    clo = {r[0]: r[1] for r in con.execute("select CLUSTER_ID, ORDINAL from cord_cluster")}
    for kid in cords:
        cords[kid].sort(key=lambda c: (c['ord'] or 0, clo.get(c['clid'], 0), c['clord'] or 0, c['cid']))
        for c in cords[kid]:
            c['cl'] = clo.get(c['clid'], 0)
            c['nsub'] = len(sub.get(c['cid'], []))
            c['subvals'] = [s['val'] for s in sub.get(c['cid'], [])]
    return meta, cords

def by_okr(meta):
    return {m['okr']: k for k, m in meta.items()}
