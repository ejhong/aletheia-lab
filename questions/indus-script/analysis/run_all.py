#!/usr/bin/env python3
"""Run the contest for every list and apply the plan's rules.

usage: run_all.py ARCHIVE_UNZIPPED_DIR CORPUS_CSV [processes]

  ARCHIVE_UNZIPPED_DIR: tests_archive.zip of the preprint, unpacked (read as data: its Tamil, Sanskrit and
                        Akkadian lists). CORPUS_CSV: inscriptions.csv from yajnadevam/lipi at the pinned commit.

Writes results/contest_rounds.json (every run) and results/contest_summary.json (per list, and the answers).
"""
import copy
import json
import multiprocessing
import os
import statistics
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import build_inputs  # noqa: E402
import contest  # noqa: E402

FRESH_TAMIL = ["tamil_fresh_a", "tamil_fresh_b"]
CONTROLS = ["japanese", "greek", "old_english", "hebrew", "nahuatl", "sumerian", "hawaiian", "finnish"]
ROUNDS = 100            # main analysis: seeds 0 to 99
NAMES_PER_ROUND = 600   # the preprint's longer lists are sampled to this many names in each round
FLOOR = 0.25            # a pass needs a mean of at least this share of the preprint's Tamil list's mean
SHUFFLES = 20           # shuffled-pictures analysis: 20 shuffles, each over seeds 0 to 9
JAR = "740"
AKKADIAN_LETTERS = [["š", "ś"], ["ḫ", "h"], ["q", "k"], ["w", "v"], ["z", "j"], ["ʾ", ""], ["û", "ū"], ["î", "ī"],
                    ["â", "ā"], ["ê", "ē"]]


def one(job):
    key, analysis, cfg, base, seed, drop, shuffle, corpus = job
    real = contest.run(cfg, base, seed, "real", corpus_csv=corpus, drop_signs=drop, picture_shuffle=shuffle)
    null = contest.run(cfg, base, seed, "null", corpus_csv=corpus, drop_signs=drop, picture_shuffle=shuffle)
    return {"list": key, "analysis": analysis, "round": seed, "shuffle": shuffle, "dropped": list(drop),
            "real": real["heldout"], "null": null["heldout"],
            "difference": round(real["heldout"] - null["heldout"], 2), "signs_read": real["read"],
            "options_per_sign": real["pic_mean_opts"], "signs_with_options": real["signs_with_options"],
            "names": real["names"], "name_parts": real["name_parts"], "readings": real["readings"]}


def absolute(cfg, base):
    out = copy.deepcopy(cfg)
    for k in ("names", "parts", "words"):
        out[k] = cfg[k] if os.path.isabs(cfg[k]) else os.path.join(base, cfg[k])
    return out


def flattened(cfg, base, tmp):
    """The same list with every part given the one label 'other' (stability 2)."""
    out = absolute(cfg, base)
    parts = contest.read_jsonl(out["parts"])
    loan = cfg.get("loan_category", "sanskrit_loan")
    for p in parts:
        if p.get("category") != loan:
            p["category"], p["stability"] = "other", 2
    out["parts"] = os.path.join(tmp, "parts.jsonl")
    build_inputs.write_jsonl(out["parts"], parts)
    return out


def respelled(cfg, base, tmp, rules):
    """The same lists with letters the contest's sound table does not know mapped to ones it does."""
    out = absolute(cfg, base)
    names = contest.read_jsonl(out["names"])
    for n in names:
        n["morphemes"] = [build_inputs.respell(m, rules) for m in n["morphemes"]]
    parts = contest.read_jsonl(out["parts"])
    for p in parts:
        p["m"] = build_inputs.respell(p["m"], rules)
    words = build_inputs.load_json(out["words"])
    words = {s: {e: [build_inputs.respell(w, rules) for w in ws] for e, ws in d.items()} for s, d in words.items()}
    out.update({"names": os.path.join(tmp, "names.jsonl"), "parts": os.path.join(tmp, "parts.jsonl"),
                "words": os.path.join(tmp, "words.json"),
                "number_words": {k: build_inputs.respell(v, rules) for k, v in cfg["number_words"].items()}})
    build_inputs.write_jsonl(out["names"], names)
    build_inputs.write_jsonl(out["parts"], parts)
    with open(out["words"], "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False)
    return out


def summarise(rows):
    d = [r["difference"] for r in rows]
    q = statistics.quantiles(d, n=4)
    return {"runs": len(d), "mean": round(statistics.mean(d), 1), "median": round(statistics.median(d), 1),
            "sd": round(statistics.stdev(d), 1), "quartiles": [round(q[0], 1), round(q[2], 1)],
            "runs_above_control": sum(x > 0 for x in d),
            "real_mean": round(statistics.mean(r["real"] for r in rows), 1),
            "null_mean": round(statistics.mean(r["null"] for r in rows), 1),
            "signs_read_mean": round(statistics.mean(r["signs_read"] for r in rows), 1),
            "options_per_sign": rows[0]["options_per_sign"], "signs_with_options": rows[0]["signs_with_options"],
            "names_per_run": rows[0]["names"], "name_parts_in_two_or_more_names": rows[0]["name_parts"]}


def answers(summary, fresh_run, controls_run):
    """The plan's rules, applied to the main analysis."""
    main = {k: v["main"] for k, v in summary.items()}
    tamil = main["tamil_preprint"]
    floor = FLOOR * tamil["mean"]

    def passes(k):
        return bool(main[k]["runs_above_control"] >= 80 and main[k]["mean"] >= floor)

    out = {"floor": round(floor, 1), "controls_run": controls_run, "fresh_tamil_run": fresh_run,
           "preprint_tamil_above_control_in_80_rounds": bool(tamil["runs_above_control"] >= 80),
           "passes": {k: passes(k) for k in fresh_run + controls_run}}
    if tamil["runs_above_control"] < 80:
        out["overall"] = "CALIBRATION FAILED: the preprint's own Tamil list is not above its control in 80 of 100 rounds"
        return out
    if len(controls_run) < 6 or not fresh_run:
        out["overall"] = "INCOMPLETE: fewer than six control languages, or no fresh Tamil list, could be run"
        return out
    passing = [c for c in controls_run if passes(c)]
    t_mean = statistics.mean(main[k]["mean"] for k in fresh_run)
    top_control = max(main[c]["mean"] for c in controls_run)
    out["controls_passing"] = passing
    out["fresh_tamil_mean"] = round(t_mean, 1)
    out["highest_control_mean"] = top_control
    out["ranking_by_mean"] = sorted(fresh_run + controls_run, key=lambda k: -main[k]["mean"])
    out["answer_1_do_unrelated_languages_pass"] = ("Yes: two or more control languages pass" if len(passing) >= 2
                                                   else "One control language passes" if passing
                                                   else "No control language passes")
    all_fresh_pass = all(passes(k) for k in fresh_run)
    if all_fresh_pass and min(main[k]["mean"] for k in fresh_run) > top_control:
        a2 = "Yes: every fresh Tamil list passes and scores above every control"
    elif top_control >= t_mean or not any(passes(k) for k in fresh_run):
        a2 = "No: a control scores as high as fresh Tamil, or no fresh Tamil list passes"
    else:
        a2 = "Partly: fresh Tamil is ahead on average, but not every list passes or a control beats one of them"
    out["answer_2_does_tamil_stand_out"] = a2
    if a2.startswith("Yes") and len(passing) <= 1 and top_control < 0.5 * t_mean:
        out["overall"] = "SUPPORTS THE PREPRINT: Tamil stands out and unrelated languages do not come near it"
    elif a2.startswith("No"):
        out["overall"] = "DOES NOT SHOW THE LANGUAGE: Tamil, built like the controls, does not stand out from them"
    else:
        out["overall"] = "MIXED"
    return out


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    arch, corpus = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    tmp = tempfile.mkdtemp(prefix="indus_run_")
    lists = {}  # key -> (settings, folder)
    for key, sub, name in (("tamil_preprint", "REP-1_tamil_vs_sanskrit/inputs", "cfg_headline_tamil.json"),
                           ("sanskrit_preprint", "REP-1_tamil_vs_sanskrit/inputs", "cfg_headline_sanskrit.json"),
                           ("akkadian_preprint", "REP-3_akkadian/inputs", "cfg_akkadian.json")):
        base = os.path.join(arch, sub)
        cfg = build_inputs.load_json(os.path.join(base, name))
        cfg["sample_n"] = NAMES_PER_ROUND
        lists[key] = (cfg, base)
    fresh_run, controls_run = [], []
    for key in FRESH_TAMIL + CONTROLS:
        base = os.path.join(ROOT, "inputs", key)
        if not os.path.exists(os.path.join(base, "cfg.json")):
            print("no inputs for", key, "- left out")
            continue
        lists[key] = (build_inputs.load_json(os.path.join(base, "cfg.json")), base)
        (fresh_run if key in FRESH_TAMIL else controls_run).append(key)
    akk_cfg, akk_base = lists["akkadian_preprint"]
    lists["akkadian_preprint_respelled"] = (respelled(akk_cfg, akk_base, os.path.join(tmp, "akk"), AKKADIAN_LETTERS),
                                            akk_base)
    jobs = []
    for key, (cfg, base) in lists.items():
        jobs += [(key, "main", cfg, base, s, (), None, corpus) for s in range(ROUNDS)]
        jobs += [(key, "jar sign left unread", cfg, base, s, (JAR,), None, corpus) for s in range(ROUNDS)]
        flat = flattened(cfg, base, os.path.join(tmp, "flat_" + key))
        jobs += [(key, "labels flattened", flat, base, s, (), None, corpus) for s in range(ROUNDS)]
        jobs += [(key, "pictures shuffled", cfg, base, s, (), k, corpus) for k in range(SHUFFLES) for s in range(10)]
        if "sample_n" in cfg:
            full = absolute(cfg, base)
            full.pop("sample_n")
            jobs += [(key, "whole list, rounds 0 to 9", full, base, s, (), None, corpus) for s in range(10)]
    with multiprocessing.Pool(procs) as pool:
        rows = pool.map(one, jobs, chunksize=4)
    summary = {}
    for key in lists:
        summary[key] = {}
        for a in sorted({r["analysis"] for r in rows if r["list"] == key}):
            summary[key][a] = summarise([r for r in rows if r["list"] == key and r["analysis"] == a])
        chosen = {}
        for r in rows:
            if r["list"] == key and r["analysis"] == "main":
                for sign, word in r["readings"].items():
                    chosen.setdefault(sign, {}).setdefault(word, 0)
                    chosen[sign][word] += 1
        summary[key]["readings_chosen"] = chosen
        summary[key]["readings_chosen_for_jar_sign"] = chosen.get(JAR, {})
    result = answers(summary, fresh_run, controls_run)

    # For every list that passes, and the preprint's Tamil list: which one sign costs most when left unread.
    passers = [k for k, v in result.get("passes", {}).items() if v] + ["tamil_preprint"]
    jobs2 = []
    for key in passers:
        cfg, base = lists[key]
        signs = sorted(contest.load_language(cfg, base)[2])
        jobs2 += [(key, "one sign left unread", cfg, base, s, (sign,), None, corpus) for sign in signs for s in range(10)]
        jobs2 += [(key, "rounds 0 to 9", cfg, base, s, (), None, corpus) for s in range(10)]
    with multiprocessing.Pool(procs) as pool:
        rows2 = pool.map(one, jobs2, chunksize=8)
    for key in passers:
        base_mean = statistics.mean(r["difference"] for r in rows2 if r["list"] == key and r["analysis"] == "rounds 0 to 9")
        falls = {}
        for r in rows2:
            if r["list"] == key and r["analysis"] == "one sign left unread":
                falls.setdefault(r["dropped"][0], []).append(r["difference"])
        ranked = sorted(((statistics.mean(v) - base_mean, s, sum(x > 0 for x in v)) for s, v in falls.items()))
        summary[key]["one_sign_left_unread_rounds_0_to_9"] = {
            "mean_with_every_sign": round(base_mean, 1),
            "largest_falls": [{"sign": s, "mean_without_it": round(base_mean + d, 1), "change": round(d, 1),
                               "rounds_above_control_of_10": n,
                               "readings_chosen_for_it": summary[key]["readings_chosen"].get(s, {})}
                              for d, s, n in ranked[:5]]}
    out = {"answers": result, "lists": summary,
           "settings": {"rounds": ROUNDS, "names_per_round_for_preprint_lists": NAMES_PER_ROUND,
                        "pass_rule": "above its scrambled control in at least 80 of 100 rounds, and a mean of at "
                                     "least a quarter of the preprint's Tamil list's mean",
                        "shuffled_pictures": f"{SHUFFLES} shuffles, each over rounds 0 to 9"}}
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    with open(os.path.join(ROOT, "results", "contest_summary.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(os.path.join(ROOT, "results", "contest_rounds.json"), "w", encoding="utf-8") as f:
        json.dump([{k: v for k, v in r.items() if k != "readings"} for r in rows + rows2], f, ensure_ascii=False)
    print(json.dumps(result, ensure_ascii=False, indent=1))
    for key, s in summary.items():
        m, j, fl, ps = s["main"], s["jar sign left unread"], s["labels flattened"], s["pictures shuffled"]
        print(f"{key:28} mean {m['mean']:7.1f} above {m['runs_above_control']:3d}/100 | jar unread {j['mean']:7.1f} "
              f"({j['runs_above_control']}) | flat {fl['mean']:7.1f} ({fl['runs_above_control']}) | pictures shuffled "
              f"{ps['mean']:7.1f} ({ps['runs_above_control']}/200) | options/sign {m['options_per_sign']}")


if __name__ == "__main__":
    main()
