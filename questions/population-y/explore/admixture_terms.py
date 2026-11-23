#!/usr/bin/env python3
"""EXPLORATORY (run after the lock, after the first results). Not a finding.

Why was the locked admixture check uninformative? Print the nine f4 terms that go into the joint solve.
    .venv/bin/python explore/admixture_terms.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "analysis"))
import f4lib  # noqa: E402
import run  # noqa: E402

E = run.Engine()
sets = run.load_sets()
for name in sets:
    if name.startswith(("A.", "B.")) or name == "Chimp":
        E.define(name, sets[name])
for pn, P in run.PANELS.items():
    o, pap, ref, amz, fr, sard, yor = P["out"][0], P["aus"][0], P["ref"][0], P["amazon"], P["french"], P["sard"], P["yoruba"]
    terms = {"P": (o, pap, ref, amz), "g(Ref)": (o, sard, amz, ref), "g(French)": (o, sard, amz, fr), "g(Yoruba)": (o, sard, amz, yor),
             "h(Ref)": ("Chimp", o, amz, ref), "h(French)": ("Chimp", o, amz, fr), "h(Yoruba)": ("Chimp", o, amz, yor),
             "f4(Mbuti,Papuan;French,Amazon)": (o, pap, fr, amz), "f4(Mbuti,Papuan;Yoruba,Amazon)": (o, pap, yor, amz)}
    print("panel", pn)
    vals = {}
    for k, q in terms.items():
        r = f4lib.f4(E.freq, *q, E.snps)
        vals[k] = r["f4"]
        print(f"  {k:32s} {r['f4']: .6f}  se {r['se']:.6f}  Z {r['z']:7.2f}")
    det = vals["g(French)"] * vals["h(Yoruba)"] - vals["g(Yoruba)"] * vals["h(French)"]
    print(f"  determinant {det:.3e}; product of the diagonal {vals['g(French)'] * vals['h(Yoruba)']:.3e}")
