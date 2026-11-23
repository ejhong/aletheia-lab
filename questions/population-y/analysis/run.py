#!/usr/bin/env python3
"""Run every statistic in protocol.md and apply its decision rules.

    .venv/bin/python analysis/run.py            # run from questions/population-y
    .venv/bin/python analysis/run.py --blind    # pipeline test on scrambled genomes; writes results_blind/

Reads analysis/sets.tsv and the AADR genotype file. Writes, under results/:
  f4.tsv         every f4 statistic
  admixture.tsv  the per-individual admixture diagnostic
  kinship.tsv    pairwise kinship
  verdicts.json  the composite quantities and the decision rules applied
"""
import collections
import json
import pathlib
import statistics
import sys

import numpy as np

import f4lib

HERE = pathlib.Path(__file__).resolve().parent
Q = HERE.parent
D = Q / "data" / "aadr_v66.p1"
PREFIX = "v66.p1_1240K.aadr.patch.PUB"
BLIND = "--blind" in sys.argv
PASS = {"Pass", "PROVISIONAL_PASS", "MERGE_PASS"}
AUSTRALASIAN_W = ["W.ONG", "W.JAR", "W.Papuan", "W.Nasioi", "W.Australian"]
PANELS = {
    "A": {"out": ["A.Mbuti", "A.Yoruba", "Chimp"], "aus": ["A.Papuan", "A.Australian", "ONG", "JAR"],
          "ref": ["A.Mixe", "A.MesoOther", "A.Pima"], "x": ["A.Surui", "A.Karitiana"], "amazon": "A.Amazon",
          "han": "A.Han", "french": "A.French", "sard": "A.Sardinian", "yoruba": "A.Yoruba",
          "americans": ["A.Mixe", "A.MesoOther", "A.Pima", "A.Mayan", "A.Piapoco", "A.Quechua", "A.Surui", "A.Karitiana"],
          "other": ["A.MesoOther", "A.Pima", "A.Mayan", "A.Piapoco", "A.Quechua"]},
    "B": {"out": ["B.Mbuti", "B.Yoruba", "Chimp"], "aus": ["B.Papuan", "B.Nasioi", "ONG", "JAR"],
          "ref": ["B.Pima"], "x": ["B.Surui", "B.Karitiana"], "amazon": "B.Amazon",
          "han": "B.Han", "french": "B.French", "sard": "B.Sardinian", "yoruba": "B.Yoruba",
          "americans": ["B.Pima", "B.Mayan", "B.Piapoco", "B.Surui", "B.Karitiana"],
          "other": ["B.Mayan", "B.Piapoco"]},
}
KIN_SETS = ["A.Mixe", "A.Surui", "A.Karitiana", "B.Surui", "B.Karitiana", "B.Pima"]


def load_sets():
    sets = collections.OrderedDict()
    with open(HERE / "sets.tsv") as f:
        cols = f.readline().rstrip("\n").split("\t")
        for line in f:
            p = dict(zip(cols, line.rstrip("\n").split("\t")))
            sets.setdefault(p["set"], []).append({"row": int(p["row"]), "gid": p["genetic_id"], "iid": p["individual_id"],
                                                  "group": p["group_id"], "assess": p["assessment"]})
    return sets


def kind(gid):
    if gid.endswith(".AG"):
        return "AG"
    if gid.endswith(".SG") and ".AG" not in gid:
        return "SG"
    return None


class Engine:
    def __init__(self):
        self.snps = f4lib.Snps(D / f"{PREFIX}.snp")
        self.snps10 = self.snps.with_block_size(0.10)
        self.geno = f4lib.Geno(D / f"{PREFIX}.geno", self.snps)
        self.n = self.snps.index.size
        self.cache = {}
        self.freq = {}
        self.sc = {}
        self.res = collections.OrderedDict()
        self.classes = {"all": None, "tv": self.snps.transversion}

    def read(self, row):
        g = self.geno.genotypes(row)
        if BLIND:
            # Pipeline test only: shuffle each genome's SNPs independently, which destroys every real signal.
            g = np.random.default_rng(1000 + row).permutation(g)
        return g

    def g(self, row):
        if row not in self.cache:
            self.cache[row] = self.read(row)
        return self.cache[row]

    def sumcount(self, members, keep=True, only=None):
        total = np.zeros(self.n, dtype=np.float32)
        count = np.zeros(self.n, dtype=np.float32)
        for m in members:
            g = self.g(m["row"]) if keep else self.read(m["row"])
            ok = g != 3
            if only is not None:
                ok &= only[m["row"]]
            total += np.where(ok, g, 0)
            count += 2 * ok
        return total, count

    @staticmethod
    def to_freq(total, count):
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(count > 0, total / count, np.nan).astype(np.float32)

    def define(self, name, members, keep=True, only=None):
        self.sc[name] = self.sumcount(members, keep, only)
        self.freq[name] = self.to_freq(*self.sc[name])

    def mask(self, names):
        m = np.ones(self.n, dtype=bool)
        for k in names:
            m &= ~np.isnan(self.freq[k])
        return m

    def stat(self, section, sid, p1, p2, p3, p4, cls="all", mask=None, snps=None):
        m = self.classes[cls]
        if mask is not None:
            m = mask if m is None else (m & mask)
        r = f4lib.f4(self.freq, p1, p2, p3, p4, snps or self.snps, mask=m)
        r.update(section=section, id=sid, P1=p1, P2=p2, P3=p3, P4=p4, snps=cls)
        r["lo"], r["hi"] = r["f4"] - 1.96 * r["se"], r["f4"] + 1.96 * r["se"]
        self.res[sid] = r
        return r


def paired_pools(E, name_a, name_b, mem_a, mem_b):
    """Pools of the same people in two versions; at each SNP only people with data in both versions count."""
    both = {}
    for a, b in zip(mem_a, mem_b):
        assert a["iid"] == b["iid"]
        ok = (E.g(a["row"]) != 3) & (E.g(b["row"]) != 3)
        both[a["row"]] = ok
        both[b["row"]] = ok
    E.define(name_a, mem_a, only=both)
    E.define(name_b, mem_b, only=both)


def run(E, sets, out):
    S = E.stat
    info = {}
    fixed = [n for n in sets if n.startswith(("A.", "B.")) or n in ("ONG", "JAR", "Chimp", "Tianyuan")]
    for name in fixed:
        E.define(name, sets[name])
    yri = E.freq["B.Yoruba"]
    E.classes["yri"] = (yri > 0.05) & (yri < 0.95)

    # ---- T: technical ----
    by_iid = lambda mem: sorted(mem, key=lambda m: m["iid"])
    dup_a, dup_b = by_iid(sets["DUP.SGDP"]), by_iid(sets["DUP.NYGC"])
    paired_pools(E, "DUP.SGDP", "DUP.NYGC", dup_a, dup_b)
    am = [i for i, m in enumerate(dup_b) if m["group"] in ("Surui", "Karitiana")]
    paired_pools(E, "DUP.SGDP.Amazon", "DUP.NYGC.Amazon", [dup_a[i] for i in am], [dup_b[i] for i in am])
    for a, b in zip(dup_a, dup_b):
        E.define(f"DUP.SGDP:{a['iid']}", [a])
        E.define(f"DUP.NYGC:{a['iid']}", [b])
    for L in ("A.Papuan", "ONG", "A.Han", "A.French"):
        S("T1", f"T1|{L}", "A.Mbuti", L, "DUP.SGDP", "DUP.NYGC")
        S("T1", f"T1amazon|{L}", "A.Mbuti", L, "DUP.SGDP.Amazon", "DUP.NYGC.Amazon")
        for a in dup_a:
            S("T1person", f"T1person|{L}|{a['iid']}", "A.Mbuti", L, f"DUP.SGDP:{a['iid']}", f"DUP.NYGC:{a['iid']}")
    ver_a, ver_b = by_iid(sets["VER.AG"]), by_iid(sets["VER.SG"])
    paired_pools(E, "VER.AG", "VER.SG", ver_a, ver_b)
    for a, b in zip(ver_a, ver_b):
        E.define(f"VER.AG:{a['iid']}", [a])
        E.define(f"VER.SG:{a['iid']}", [b])
    for L in ("A.Papuan", "A.Han"):
        S("T2", f"T2|{L}", "A.Mbuti", L, "VER.AG", "VER.SG")
        for a in ver_a:
            S("T2person", f"T2person|{L}|{a['iid']}", "A.Mbuti", L, f"VER.AG:{a['iid']}", f"VER.SG:{a['iid']}")

    # ---- per panel: P, support, admixture, R, L ----
    info["composite"] = {}
    info["flagged"] = {}
    adm_lines = []
    for pn, P in PANELS.items():
        o, pap, ref, amz, han, fr, sard, yor = (P["out"][0], P["aus"][0], P["ref"][0], P["amazon"], P["han"], P["french"],
                                                 P["sard"], P["yoruba"])
        S("P", f"P_{pn}", o, pap, ref, amz)
        for x in P["x"]:
            S("P", f"Pcommunity.{pn}|{x}", o, pap, ref, x)
        for group in (ref, amz):
            for m in sets[group]:
                name = f"{group}-{m['gid']}"
                E.define(name, [x for x in sets[group] if x["row"] != m["row"]])
                S(f"LOO.{pn}", f"LOO.{pn}|{name}", o, pap, name if group == ref else ref, name if group == amz else amz)
        # Admixture: per individual
        flagged = set()
        for name in P["americans"]:
            for m in sets[name]:
                E.define("adm.i", [m])
                u = amz
                if any(a["row"] == m["row"] for a in sets[amz]):
                    u = f"{amz}-{m['gid']}"
                e = f4lib.f4(E.freq, o, fr, u, "adm.i", E.snps)
                a = f4lib.f4(E.freq, "Chimp", yor, u, "adm.i", E.snps)
                flag = e["z"] >= 3 or a["z"] >= 3
                if flag:
                    flagged.add(m["row"])
                adm_lines.append((pn, name, m["gid"], e["f4"], e["z"], a["f4"], a["z"], int(flag)))
        info["flagged"][pn] = sorted(m["gid"] for name in P["americans"] for m in sets[name] if m["row"] in flagged)
        keep_ref = [m for m in sets[ref] if m["row"] not in flagged]
        keep_amz = [m for m in sets[amz] if m["row"] not in flagged]
        if flagged & {m["row"] for m in sets[ref] + sets[amz]} and keep_ref and keep_amz:
            E.define(f"{ref}.unflagged", keep_ref)
            E.define(f"{amz}.unflagged", keep_amz)
            S("P", f"P_{pn}.unflagged", o, pap, f"{ref}.unflagged", f"{amz}.unflagged")
        # Admixture: group level, joint jackknife on one mask
        # g(S) = f4(Mbuti, Sardinian; Amazon, S), h(S) = f4(Chimp, Mbuti; Amazon, S); solve the two mixture equations.
        quartets = [(o, pap, ref, amz),                                            # 0: P
                    (o, sard, amz, ref), (o, sard, amz, fr), (o, sard, amz, yor),       # 1-3: g(Ref), g(French), g(Yoruba)
                    ("Chimp", o, amz, ref), ("Chimp", o, amz, fr), ("Chimp", o, amz, yor),  # 4-6: h(Ref), h(French), h(Yoruba)
                    (o, pap, fr, amz), (o, pap, yor, amz)]                              # 7-8

        def solve(v):
            det = v[2] * v[6] - v[3] * v[5]
            return (v[1] * v[6] - v[3] * v[4]) / det, (v[2] * v[4] - v[1] * v[5]) / det

        def p_adj(v):
            ae, aa = solve(v)
            return (v[0] - ae * v[7] - aa * v[8]) / (1 - ae - aa)

        comp = {"alpha_eur": f4lib.composite(E.freq, quartets, lambda v: solve(v)[0], E.snps),
                "alpha_afr": f4lib.composite(E.freq, quartets, lambda v: solve(v)[1], E.snps),
                "P_adj": f4lib.composite(E.freq, quartets, p_adj, E.snps),
                "P_on_admixture_mask": f4lib.composite(E.freq, quartets, lambda v: v[0], E.snps)}
        info["composite"][pn] = comp
        # Robustness grid
        for oo in P["out"]:
            for a in P["aus"]:
                for r in P["ref"]:
                    for x in P["x"]:
                        for cls in ("all", "tv", "yri"):
                            S(f"R.{pn}", f"R.{pn}|{oo}|{a}|{r}|{x}|{cls}", oo, a, r, x, cls=cls)
        for m in sets[amz]:
            E.define(f"{pn}.ind.{m['gid']}", [m])
            S(f"Rind.{pn}", f"Rind.{pn}|{m['gid']}", o, pap, ref, f"{pn}.ind.{m['gid']}")
            S(f"Rind.{pn}", f"RindHan.{pn}|{m['gid']}", o, han, ref, f"{pn}.ind.{m['gid']}")
        for x in P["other"]:
            S(f"Rother.{pn}", f"Rother.{pn}|{x}", o, pap, ref, x)
        for cls in ("all", "yri"):
            S(f"Rother.{pn}", f"SuruiKaritiana.{pn}|{cls}", o, pap, P["x"][0], P["x"][1], cls=cls)
        # Specificity and lineage on one mask
        mk = E.mask([o, pap, "ONG", han, "Tianyuan", ref, amz])
        S(f"L.{pn}", f"P_L.{pn}", o, pap, ref, amz, mask=mk)
        S(f"L.{pn}", f"Han.{pn}", o, han, ref, amz, mask=mk)
        S(f"L.{pn}", f"L3.{pn}", han, pap, ref, amz, mask=mk)
        S(f"L.{pn}", f"L2.{pn}", "ONG", pap, ref, amz, mask=mk)
        S(f"L.{pn}", f"L1.{pn}", o, "Tianyuan", ref, amz, mask=mk)
        S(f"L.{pn}", f"L4.{pn}", "Tianyuan", pap, ref, amz, mask=mk)
        S(f"L.{pn}", f"L1tv.{pn}", o, "Tianyuan", ref, amz, cls="tv", mask=mk)
        S(f"L.{pn}", f"L4tv.{pn}", "Tianyuan", pap, ref, amz, cls="tv", mask=mk)
        S(f"L.{pn}", f"Pong.{pn}", o, "ONG", ref, amz, mask=mk)
    S("P", "P_B.heldout", "B.Mbuti", "B.Papuan", "B.Pima.heldout", "B.Amazon.heldout")
    S("P", "Anchor", "A.Yoruba", "A.Papuan", "A.Mixe", "A.Surui")
    S("P", "P_A.10cM", "A.Mbuti", "A.Papuan", "A.Mixe", "A.Amazon", snps=E.snps10)
    with open(out / "admixture.tsv", "w") as f:
        f.write("panel\tset\tgenetic_id\te_f4\te_Z\ta_f4\ta_Z\tflagged\n")
        for ln in adm_lines:
            f.write("\t".join(f"{x:.6g}" if isinstance(x, float) else str(x) for x in ln) + "\n")

    # ---- Relatives (descriptive) ----
    print("kinship", flush=True)
    unrel = {}
    kin = {}
    with open(out / "kinship.tsv", "w") as f:
        f.write("set\tid1\tid2\tkinship\n")
        for name in KIN_SETS:
            mem = sets[name]
            pairs = {}
            for i in range(len(mem)):
                for j in range(i + 1, len(mem)):
                    pairs[(i, j)] = f4lib.kinship(E.g(mem[i]["row"]), E.g(mem[j]["row"]))
                    f.write(f"{name}\t{mem[i]['gid']}\t{mem[j]['gid']}\t{pairs[(i, j)]:.4f}\n")
            kin[name] = (mem, pairs)
            alive = set(range(len(mem)))
            while True:
                deg = {i: sum(1 for (a, b), k in pairs.items() if k > 0.0884 and a in alive and b in alive and i in (a, b))
                       for i in alive}
                worst = max(deg.values()) if deg else 0
                if worst == 0:
                    break
                alive.remove(max(i for i in alive if deg[i] == worst))
            unrel[name] = [mem[i] for i in sorted(alive)]
    if len(unrel["B.Surui"]) + len(unrel["B.Karitiana"]) >= 2 and len(unrel["B.Pima"]) >= 2:
        E.define("B.Amazon.unrel", unrel["B.Surui"] + unrel["B.Karitiana"])
        E.define("B.Pima.unrel", unrel["B.Pima"])
        S("P", "P_B.unrel", "B.Mbuti", "B.Papuan", "B.Pima.unrel", "B.Amazon.unrel")
    info["unrelated"] = {k: [m["gid"] for m in v] for k, v in unrel.items()}
    dup_people = {m["iid"] for m in sets["DUP.NYGC"]}
    info["heldout_max_kinship_to_panel_A"] = {}
    for name in ("B.Surui", "B.Karitiana", "B.Pima"):
        mem, pairs = kin[name]
        ks = [k for (i, j), k in pairs.items() if (mem[i]["iid"] in dup_people) != (mem[j]["iid"] in dup_people)]
        info["heldout_max_kinship_to_panel_A"][name] = round(max(ks), 3) if ks else None
    info["kinship_summary"] = {name: {"pairs": len(p), "median": round(statistics.median(p.values()), 3),
                                      "max": round(max(p.values()), 3)} for name, (m, p) in kin.items() if p}

    # ---- S: world ranking ----
    print("world panel", flush=True)
    for w in [n for n in sets if n.startswith("W.")]:
        E.define(w, sets[w], keep=False)
        for pn, P in PANELS.items():
            S(f"S.{pn}", f"S.{pn}|{w}", P["out"][0], w, P["ref"][0], P["amazon"])
        del E.sc[w]

    # ---- N: ancient ----
    print("ancient sets", flush=True)
    groups = [n for n in sets if n.startswith(("CELL.", "REGION.", "ANC.", "EARLY."))]
    base = {t: [m for m in sets["ANC.NC"] if kind(m["gid"]) == t] for t in ("AG", "SG")}
    for t in base:
        E.define(f"BASE.{t}", base[t])
    present = ["A.Mbuti", "A.Papuan", "ONG", "A.Han", "A.French"]
    tested = []
    for gname in groups:
        mem = sets[gname]
        E.define(gname, mem)
        people = {m["iid"] for m in mem}
        for t in ("AG", "SG"):
            gt = [m for m in mem if kind(m["gid"]) == t]
            b = [m for m in base[t] if m["iid"] not in people]
            if not gt or len(b) < 10:
                continue
            overlap = [m for m in base[t] if m["iid"] in people]
            tot, cnt = E.sc[f"BASE.{t}"]
            if overlap:
                ot, oc = E.sumcount(overlap)
                tot, cnt = tot - ot, cnt - oc
            bname, tname = f"BASE.{t}-{gname}", f"{gname}@{t}"
            E.freq[bname] = E.to_freq(tot, cnt)
            E.define(tname, gt)
            mk = E.mask(present + [bname, tname])
            S("M", f"M1|{tname}", "A.Mbuti", "A.Papuan", bname, tname, mask=mk)
            S("M", f"M1ong|{tname}", "A.Mbuti", "ONG", bname, tname, mask=mk)
            S("M", f"M1tv|{tname}", "A.Mbuti", "A.Papuan", bname, tname, cls="tv", mask=mk)
            S("M", f"M3|{tname}", "A.Han", "A.Papuan", bname, tname, mask=mk)
            S("M", f"MF|{tname}", "A.Mbuti", "A.French", bname, tname, mask=mk)
            tested.append({"set": gname, "type": t, "n": len(gt), "baseline_n": len(b),
                           "pass": all(m["assess"] in PASS for m in gt)})
            del E.freq[bname]
        mk = E.mask(present + ["A.Mixe", "A.Amazon", gname])
        for x, tag in (("A.Papuan", "Npap"), ("ONG", "Nong"), ("A.Han", "Nhan"), ("A.French", "Nfrench")):
            S("Npaper", f"{tag}|{gname}", "A.Mbuti", x, "A.Mixe", gname, mask=mk)
        S("Npaper", f"Npaptv|{gname}", "A.Mbuti", "A.Papuan", "A.Mixe", gname, cls="tv", mask=mk)
        S("Npaper", f"Namazon|{gname}", "A.Mbuti", "A.Papuan", gname, "A.Amazon", mask=mk)
    inland, coast = "REGION.ANDES_INLAND@AG", "REGION.ANDES_COAST@AG"
    mk = E.mask(present + [inland, coast])
    S("C", "C1", "A.Mbuti", "A.Papuan", inland, coast, mask=mk)
    S("C", "C1tv", "A.Mbuti", "A.Papuan", inland, coast, cls="tv", mask=mk)
    S("C", "C3", "A.Han", "A.Papuan", inland, coast, mask=mk)
    S("C", "CF", "A.Mbuti", "A.French", inland, coast, mask=mk)
    info["tested"], info["groups"] = tested, groups

    with open(out / "f4.tsv", "w") as f:
        f.write("section\tid\tP1\tP2\tP3\tP4\tsnps\tn_snps\tn_blocks\tf4\tse\tZ\tci_lo\tci_hi\tD\tD_se\tD_Z\tf4_centred\tf4_centred_se\t"
                "f4_centred_Z\tbalance_P3_minus_P4\n")
        for r in E.res.values():
            f.write("\t".join(str(x) for x in (r["section"], r["id"], r["P1"], r["P2"], r["P3"], r["P4"], r["snps"], r["n_snps"],
                                               r["n_blocks"], f"{r['f4']:.8g}", f"{r['se']:.8g}", f"{r['z']:.4f}", f"{r['lo']:.8g}",
                                               f"{r['hi']:.8g}", f"{r['D']:.8g}", f"{r['D_se']:.8g}", f"{r['D_z']:.4f}",
                                               f"{r['f4c']:.8g}", f"{r['f4c_se']:.8g}", f"{r['f4c_z']:.4f}", f"{r['balance']:.6g}")) + "\n")
    return info


def verdicts(res, info, sets):
    z = {k: r["z"] for k, r in res.items()}
    r2 = lambda x: round(x, 2)
    est = lambda k: {"f4": res[k]["f4"], "se": res[k]["se"], "Z": r2(z[k]), "ci": [res[k]["lo"], res[k]["hi"]],
                     "n_snps": res[k]["n_snps"], "centred_f4": res[k]["f4c"], "centred_Z": r2(res[k]["f4c_z"])}
    v = {}
    zp, p_a = z["P_A"], res["P_A"]["f4"]
    v["P_A"] = dict(est("P_A"), D=res["P_A"]["D"],
                    verdict="detected" if zp >= 3 else ("not detected by the primary test" if zp < 2 else "inconclusive"))
    a = res["Anchor"]
    v["anchor"] = {"D": round(a["D"], 5), "D_se": round(a["D_se"], 5), "Z": r2(a["D_z"]),
                   "ci": [round(a["D"] - 1.96 * a["D_se"], 5), round(a["D"] + 1.96 * a["D_se"], 5)],
                   "skoglund_whole_genome_D": 0.0211, "skoglund_array_D_range": [0.0072, 0.0099]}
    v["P_A_10cM_blocks"] = est("P_A.10cM")
    # Checks on the primary
    checks = {}
    cells = {k: z[k] for k in z if k.startswith("R.A|")}
    v["R"] = {}
    for pn in PANELS:
        cl = {k: res[k] for k in res if k.startswith(f"R.{pn}|")}
        zs = [c["z"] for c in cl.values()]
        axes = {}
        for pos, axis in enumerate(("outgroup", "australasian", "reference", "target", "snps"), start=1):
            by = collections.defaultdict(list)
            for k, c in cl.items():
                by[k.split("|")[pos]].append(c)
            axes[axis] = {name: {"median_Z": r2(statistics.median(c["z"] for c in cs)),
                                 "median_f4": statistics.median(c["f4"] for c in cs),
                                 "fraction_positive": round(sum(1 for c in cs if c["z"] > 0) / len(cs), 3)}
                          for name, cs in by.items()}
        v["R"][pn] = {"cells": len(zs), "fraction_positive": round(sum(1 for t in zs if t > 0) / len(zs), 3),
                      "median_Z": r2(statistics.median(zs)), "min_Z": r2(min(zs)), "max_Z": r2(max(zs)), "by_axis": axes}
    checks["direction holds"] = v["R"]["A"]["fraction_positive"] >= 0.9
    v["communities"] = {k.split("|")[1]: est(k) for k in res if k.startswith("Pcommunity.")}
    checks["each community"] = all(z[f"Pcommunity.A|{x}"] >= 2 for x in PANELS["A"]["x"])
    v["leave_one_out"] = {}
    for pn in PANELS:
        loo = {k.split("|")[1]: res[k] for k in res if k.startswith(f"LOO.{pn}|")}
        full = res[f"P_{pn}"]["f4"]
        v["leave_one_out"][pn] = {"min_ratio_to_full": round(min(c["f4"] for c in loo.values()) / full, 3),
                                  "max_ratio_to_full": round(max(c["f4"] for c in loo.values()) / full, 3),
                                  "min_Z": r2(min(c["z"] for c in loo.values())),
                                  "all": {n: {"f4": c["f4"], "Z": r2(c["z"])} for n, c in loo.items()}}
    checks["donors"] = bool(p_a > 0 and v["leave_one_out"]["A"]["min_ratio_to_full"] >= 0.5)
    v["admixture"] = {}
    for pn in PANELS:
        c = info["composite"][pn]
        v["admixture"][pn] = {name: {"estimate": c[name][0], "se": c[name][1], "Z": r2(c[name][0] / c[name][1])} for name in c}
        v["admixture"][pn]["flagged_individuals"] = info["flagged"][pn]
        if f"P_{pn}.unflagged" in res:
            v["admixture"][pn]["P_unflagged"] = est(f"P_{pn}.unflagged")
    checks["admixture"] = v["admixture"]["A"]["P_adj"]["Z"] >= 2
    v["L"] = {}
    for pn in PANELS:
        pl = res[f"P_L.{pn}"]["f4"]
        frac = lambda k: [round(res[k]["lo"] / pl, 2), round(res[k]["hi"] / pl, 2)]
        l2, l1, l4 = z[f"L2.{pn}"], z[f"L1.{pn}"], z[f"L4.{pn}"]
        v["L"][pn] = {"P_L": est(f"P_L.{pn}"), "Han_control": dict(est(f"Han.{pn}"), ci_over_P_L=frac(f"Han.{pn}")),
                      "L3": est(f"L3.{pn}"), "specific": bool(z[f"L3.{pn}"] >= 2 and z[f"Han.{pn}"] < 3),
                      "P_with_ONG": est(f"Pong.{pn}"),
                      "L2": dict(est(f"L2.{pn}"), ci_over_P_L=frac(f"L2.{pn}"),
                                 reading="Papuan side" if l2 >= 3 else ("Onge side" if l2 <= -3 else "no difference detected")),
                      "L1": dict(est(f"L1.{pn}"), ci_over_P_L=frac(f"L1.{pn}"), tv_Z=r2(z[f"L1tv.{pn}"]),
                                 reading="Amazonians also share more with Tianyuan" if l1 >= 3 else "not detected"),
                      "L4": dict(est(f"L4.{pn}"), ci_over_P_L=frac(f"L4.{pn}"), tv_Z=r2(z[f"L4tv.{pn}"]),
                                 reading="more with Papuans than Tianyuan" if l4 >= 3 else
                                 ("more with Tianyuan than Papuans" if l4 <= -3 else "no difference detected"))}
    checks["beyond Han"] = v["L"]["A"]["specific"]
    v["checks_on_primary"] = {k: bool(x) for k, x in checks.items()}
    if zp >= 3:
        failed = [k for k, x in checks.items() if not x]
        line1 = "detected and robust" if not failed else "detected, with caveats: " + "; ".join(failed)
    else:
        line1 = v["P_A"]["verdict"]
    # Beyond the original donors
    zh = z["P_B.heldout"]
    line2 = ("also detected in other donors" if zh >= 3 else "weakly seen in other donors" if zh >= 2
             else "not detected in other donors")
    v["beyond_original_donors"] = {"P_B.heldout": est("P_B.heldout"), "P_B": est("P_B"),
                                   "P_B.unrel": est("P_B.unrel") if "P_B.unrel" in res else "too few unrelated donors",
                                   "unrelated_donors": info["unrelated"], "kinship_summary": info["kinship_summary"],
                                   "heldout_max_kinship_to_panel_A": info["heldout_max_kinship_to_panel_A"],
                                   "panel_B_checks": {"each community": all(z[f"Pcommunity.B|{x}"] >= 2 for x in PANELS["B"]["x"]),
                                                      "direction holds": v["R"]["B"]["fraction_positive"] >= 0.9,
                                                      "admixture": v["admixture"]["B"]["P_adj"]["Z"] >= 2,
                                                      "specific": v["L"]["B"]["specific"]}}
    v["headline"] = {"primary": line1, "beyond_original_donors": line2}
    # Technical
    v["T1"] = {k: r2(z[k]) for k in z if k.startswith(("T1|", "T1amazon|"))}
    v["T1_person_max_abs_Z"] = r2(max(abs(z[k]) for k in z if k.startswith("T1person|")))
    v["T1_pipelines_disagree"] = bool(max(abs(z[k]) for k in z if k.startswith("T1|")) >= 3)
    v["T1_Papuan_over_P_A"] = round(res["T1|A.Papuan"]["f4"] / p_a, 3)
    v["T1_centred_Z"] = {k: r2(res[k]["f4c_z"]) for k in z if k.startswith(("T1|", "T1amazon|"))}
    v["T1_balance_SGDP_minus_NYGC"] = round(res["T1|A.Papuan"]["balance"], 5)
    v["T2_centred_Z"] = {k: r2(res[k]["f4c_z"]) for k in z if k.startswith("T2|")}
    v["T2_balance_capture_minus_shotgun"] = round(res["T2|A.Papuan"]["balance"], 5)
    v["T2"] = {k: r2(z[k]) for k in z if k.startswith("T2|")}
    v["T2_person_max_abs_Z"] = r2(max(abs(z[k]) for k in z if k.startswith("T2person|")))
    v["T2_types_disagree"] = bool(max(abs(z[k]) for k in z if k.startswith("T2|")) >= 3)
    # World ranking
    v["S"] = {}
    for pn in PANELS:
        keys = [k for k in z if k.startswith(f"S.{pn}|")]
        byz = sorted(keys, key=lambda k: -z[k])
        byf = sorted(keys, key=lambda k: -res[k]["f4"])
        name = lambda k: k.split("|")[1]
        v["S"][pn] = {"groups": len(keys),
                      "rank_by_Z": {w: [name(k) for k in byz].index(w) + 1 for w in AUSTRALASIAN_W},
                      "rank_by_f4": {w: [name(k) for k in byf].index(w) + 1 for w in AUSTRALASIAN_W},
                      "top10_by_Z": [(name(k), r2(z[k])) for k in byz[:10]], "bottom3_by_Z": [(name(k), r2(z[k])) for k in byz[-3:]]}
    v["other_groups"] = {k: est(k) for k in res if k.startswith(("Rother.", "SuruiKaritiana."))}
    # Ancient
    m = sum(1 for t in info["tested"] if t["pass"])
    zstar = statistics.NormalDist().inv_cdf(1 - 0.05 / m)
    v["N"] = {"family_size": m, "threshold": round(zstar, 3), "sets": {}}
    for g in info["groups"]:
        entry = {"n": len(sets[g]), "types": {}}
        for t in info["tested"]:
            if t["set"] != g:
                continue
            k = f"{g}@{t['type']}"
            m1, m1tv = res[f"M1|{k}"], res[f"M1tv|{k}"]
            out = bool(t["pass"] and m1["z"] >= zstar and z[f"M3|{k}"] >= 2 and abs(z[f"MF|{k}"]) < 3
                       and m1tv["f4"] >= 0.5 * m1["f4"] and m1["f4c"] >= 0.5 * m1["f4"])
            entry["types"][t["type"]] = {"n": t["n"], "baseline_n": t["baseline_n"], "pass": t["pass"], "n_snps": m1["n_snps"],
                                         "M1_f4": m1["f4"], "M1_Z": r2(m1["z"]), "M1_centred_f4": m1["f4c"],
                                         "M1_centred_Z": r2(m1["f4c_z"]), "balance_baseline_minus_set": round(m1["balance"], 5),
                                         "M1ong_Z": r2(z[f"M1ong|{k}"]),
                                         "M1tv_Z": r2(m1tv["z"]), "M1tv_over_M1": round(m1tv["f4"] / m1["f4"], 2) if m1["f4"] else None,
                                         "M3_Z": r2(z[f"M3|{k}"]), "MF_Z": r2(z[f"MF|{k}"]),
                                         "detection_threshold_over_P_A": round(zstar * m1["se"] / p_a, 2) if p_a > 0 else None,
                                         "stands_out": out}
        entry["stands_out"] = any(t["stands_out"] for t in entry["types"].values())
        entry["class"] = "stands out" if entry["stands_out"] else "undetermined"
        entry["descriptive_vs_present_day_Z"] = {"Papuan": r2(z[f"Npap|{g}"]), "ONG": r2(z[f"Nong|{g}"]), "Han": r2(z[f"Nhan|{g}"]),
                                                 "French": r2(z[f"Nfrench|{g}"]), "Papuan_tv": r2(z[f"Npaptv|{g}"]),
                                                 "Amazon_minus_set": r2(z[f"Namazon|{g}"])}
        v["N"]["sets"][g] = entry
    standing = [g for g, e in v["N"]["sets"].items() if e["stands_out"]]
    v["N"]["stand_out"] = standing
    v["N"]["Sumidouro5"] = v["N"]["sets"].get("EARLY.Sumidouro5_d.SG", {}).get("class", "not in the data")
    v["N"]["early_presence"] = [g for g in standing if g.startswith("EARLY.") or g.endswith(".EARLY")]
    c1, c3, cf = z["C1"], z["C3"], z["CF"]
    balanced = res["C1"]["f4c"] >= 0.5 * res["C1"]["f4"] if res["C1"]["f4"] > 0 else res["C1"]["f4c"] <= 0.5 * res["C1"]["f4"]
    if not balanced:
        c1 = 0.0  # a difference owed to overall reference-allele share is not counted
    v["N"]["coast_vs_inland"] = {"C1": est("C1"), "C1tv_Z": r2(z["C1tv"]), "C3_Z": r2(c3), "CF_Z": r2(cf),
                                 "centred_at_least_half": bool(balanced),
                                 "reading": "coast has more" if (c1 >= 3 and c3 >= 2 and abs(cf) < 3) else
                                 ("coast has less" if (c1 <= -3 and c3 <= -2 and abs(cf) < 3) else
                                  ("a difference whose cause is unclear" if abs(c1) >= 3 else "no difference detected"))}
    return v


def main():
    sets = load_sets()
    out = Q / ("results_blind" if BLIND else "results")
    out.mkdir(exist_ok=True)
    E = Engine()
    info = run(E, sets, out)
    v = verdicts(E.res, info, sets)
    (out / "verdicts.json").write_text(json.dumps(v, indent=1) + "\n")
    print(json.dumps({k: v[k] for k in ("headline", "P_A", "anchor", "checks_on_primary", "T1", "T2")}, indent=1))
    print(len(E.res), "statistics written to", out)


if __name__ == "__main__":
    main()
