#!/usr/bin/env python3
"""Generate interactive figures for #12 (linear-a) from results/linear_a_summary.json."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
RES = ROOT / "questions" / "linear-a" / "results" / "linear_a_summary.json"
OUT = ROOT / "site" / "figures" / "linear-a"
OUT.mkdir(parents=True, exist_ok=True)


def write_tiles(d):
    la3 = d["test3_linear_a_vs_linear_b"]["all"]["by_len_A1"]["L3"]["rate_a"] * 100
    lb3 = d["test3_linear_a_vs_linear_b"]["all"]["by_len_A1"]["L3"]["rate_b"] * 100
    cov2 = d["test5_lexicon_and_collision_audit"]["semitic_skeleton_space_coverage"]["9class_2cons_pct"]
    nov_p = d["test2_novel_sign_permutations"]["all_A1_ge3"]["p_perm_novel"]
    mult = d["test5_lexicon_and_collision_audit"]["mean_semitic_roots_per_skeleton"]
    html = f"""<div class="tiles">
<div class="tile"><p class="tile-value">{la3:.1f}% vs {lb3:.1f}%</p><p class="tile-label">3-consonant Semitic root hit rate in Linear A vs Mycenaean Greek Linear B (p = 0.85)</p></div>
<div class="tile"><p class="tile-value">{cov2:.0f}%</p><p class="tile-label">of all 81 two-consonant slots are occupied by Proto-Semitic roots under Linear A's mergers</p></div>
<div class="tile"><p class="tile-value">p = {nov_p:.2f}</p><p class="tile-label">Di Mino's 27 novel consonant sign values vs random shuffles of those same signs (z = −0.17)</p></div>
<div class="tile"><p class="tile-value">{mult:.1f} roots</p><p class="tile-label">average distinct Proto-Semitic roots colliding on a single Linear A skeleton in the lexicon</p></div>
</div>
"""
    (OUT / "tiles.html").write_text(html)


def write_length_and_controls(d):
    t3_all = d["test3_linear_a_vs_linear_b"]["all"]["by_len_A1"]
    t3_in = d["test3_linear_a_vs_linear_b"]["in_lexicon"]["by_len_A1"]
    t3_ho = d["test3_linear_a_vs_linear_b"]["held_out"]["by_len_A1"]
    t2 = d["test2_novel_sign_permutations"]
    payload = {
        "lengths": [
            {"label": "2 consonants (L=2)", "la_all": t3_all["L2"]["rate_a"]*100, "la_ho": t3_ho["L2"]["rate_a"]*100, "lb": t3_all["L2"]["rate_b"]*100, "n_la": t3_all["L2"]["n_a"], "n_lb": t3_all["L2"]["n_b"], "p": t3_all["L2"]["p_fisher"]},
            {"label": "3 consonants (L=3)", "la_all": t3_all["L3"]["rate_a"]*100, "la_ho": t3_ho["L3"]["rate_a"]*100, "lb": t3_all["L3"]["rate_b"]*100, "n_la": t3_all["L3"]["n_a"], "n_lb": t3_all["L3"]["n_b"], "p": t3_all["L3"]["p_fisher"]},
            {"label": "4+ consonants (L≥4)", "la_all": t3_all["L4plus"]["rate_a"]*100, "la_ho": t3_ho["L4plus"]["rate_a"]*100, "lb": t3_all["L4plus"]["rate_b"]*100, "n_la": t3_all["L4plus"]["n_a"], "n_lb": t3_all["L4plus"]["n_b"], "p": t3_all["L4plus"]["p_fisher"]},
        ],
        "novel": [
            {"label": "All affected (A1 strict)", "obs": t2["all_A1_ge3"]["obs_type_rate"]*100, "null": t2["all_A1_ge3"]["null_mean"]*100, "sd": t2["all_A1_ge3"]["null_sd"]*100, "p": t2["all_A1_ge3"]["p_perm_novel"], "n": t2["all_A1_ge3"]["n_affected_types"]},
            {"label": "In-lexicon (A1 strict)", "obs": t2["in_lexicon_A1_ge3"]["obs_type_rate"]*100, "null": t2["in_lexicon_A1_ge3"]["null_mean"]*100, "sd": t2["in_lexicon_A1_ge3"]["null_sd"]*100, "p": t2["in_lexicon_A1_ge3"]["p_perm_novel"], "n": t2["in_lexicon_A1_ge3"]["n_affected_types"]},
            {"label": "Held-out (A1 strict)", "obs": t2["held_out_A1_ge3"]["obs_type_rate"]*100, "null": t2["held_out_A1_ge3"]["null_mean"]*100, "sd": t2["held_out_A1_ge3"]["null_sd"]*100, "p": t2["held_out_A1_ge3"]["p_perm_novel"], "n": t2["held_out_A1_ge3"]["n_affected_types"]},
            {"label": "Held-out (A2 7-class)", "obs": t2["held_out_A2_ge3"]["obs_type_rate"]*100, "null": t2["held_out_A2_ge3"]["null_mean"]*100, "sd": t2["held_out_A2_ge3"]["null_sd"]*100, "p": t2["held_out_A2_ge3"]["p_perm_novel"], "n": t2["held_out_A2_ge3"]["n_affected_types"]},
            {"label": "Held-out (B affix)", "obs": t2["held_out_B_ge3"]["obs_type_rate"]*100, "null": t2["held_out_B_ge3"]["null_mean"]*100, "sd": t2["held_out_B_ge3"]["null_sd"]*100, "p": t2["held_out_B_ge3"]["p_perm_novel"], "n": t2["held_out_B_ge3"]["n_affected_types"]},
        ]
    }
    html = f"""<figure class="fig" aria-label="Length-matched Linear A vs Mycenaean Greek Linear B and novel sign-value permutation test">
<div style="display:flex;gap:8px;margin-bottom:10px;flex-wrap:wrap;">
  <button type="button" class="la-btn" data-mode="len" style="padding:5px 11px;border:1px solid var(--line,#ccc);border-radius:4px;background:var(--copper,#9a4d2c);color:#fff;cursor:pointer;font-size:13px;">Linear A vs Mycenaean Greek (by length)</button>
  <button type="button" class="la-btn" data-mode="novel" style="padding:5px 11px;border:1px solid var(--line,#ccc);border-radius:4px;background:transparent;color:inherit;cursor:pointer;font-size:13px;">Novel Sign Permutations (27 proposed signs)</button>
</div>
<div class="fig-scroll">
<svg id="la-chart" class="chart" viewBox="0 0 720 270" role="img" aria-label="Comparison chart of Linear A Semitic root hit rates" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<figcaption>Left view: matching words of the exact same consonant length against all 5,189 Proto-Semitic roots under Linear A's neutralization classes, <strong>Linear A and Mycenaean Greek (Linear B) hit at identical rates</strong> (100% vs 100% at L=2; 85.0% vs 84.3% at L=3, p = 0.85; 7.1% vs 5.6% at L≥4, p = 0.54). Switch tabs to inspect the permutation test holding Linear B signs fixed and shuffling only Di Mino's 27 newly assigned consonant signs.</figcaption>
<script>
(function(){{
  const DATA = {json.dumps(payload)};
  const svg = document.getElementById('la-chart');
  const btns = document.querySelectorAll('.la-btn');

  function renderLen(){{
    const W = 720, left = 165, right = 665, top = 34, grpH = 70;
    const sx = function(v){{ return left + (v / 100) * (right - left); }};
    let o = [];
    [0, 25, 50, 75, 100].forEach(function(t){{
      const x = sx(t);
      o.push('<line x1="' + x.toFixed(1) + '" x2="' + x.toFixed(1) + '" y1="22" y2="236" stroke="var(--line,#ddd)" stroke-dasharray="2 3"/>');
      o.push('<text class="c-tick" x="' + x.toFixed(1) + '" y="252" text-anchor="middle">' + t + '%</text>');
    }});
    o.push('<text class="c-axis" x="' + left + '" y="266">Share of distinct words matching any of 5,189 Proto-Semitic roots (Regime A1, 9-class grid)</text>');
    // Legend
    o.push('<rect x="165" y="4" width="12" height="10" fill="var(--copper,#9a4d2c)"/><text class="c-sub" x="182" y="13">Linear A (all)</text>');
    o.push('<rect x="285" y="4" width="12" height="10" fill="#c77d52"/><text class="c-sub" x="302" y="13">Linear A (held-out)</text>');
    o.push('<rect x="440" y="4" width="12" height="10" fill="var(--faint,#6e7681)"/><text class="c-sub" x="457" y="13">Linear B (Mycenaean Greek)</text>');

    DATA.lengths.forEach(function(row, i){{
      const y = top + i * grpH;
      o.push('<text class="c-group" x="4" y="' + (y + 22) + '">' + row.label + '</text>');
      o.push('<text class="c-sub" x="4" y="' + (y + 38) + '">LA n=' + row.n_la + ', LB n=' + row.n_lb + ', p=' + row.p.toFixed(2) + '</text>');
      const bars = [
        {{val: row.la_all, col: 'var(--copper,#9a4d2c)', dy: 4}},
        {{val: row.la_ho, col: '#c77d52', dy: 21}},
        {{val: row.lb, col: 'var(--faint,#6e7681)', dy: 38}}
      ];
      bars.forEach(function(b){{
        const w = Math.max(2, sx(b.val) - left);
        o.push('<rect x="' + left + '" y="' + (y + b.dy) + '" width="' + w.toFixed(1) + '" height="14" rx="2" fill="' + b.col + '" opacity="0.9"/>');
        o.push('<text class="c-label-sm" x="' + (left + w + 5).toFixed(1) + '" y="' + (y + b.dy + 11) + '">' + b.val.toFixed(1) + '%</text>');
      }});
    }});
    svg.innerHTML = o.join('\\n');
  }}

  function renderNovel(){{
    const W = 720, left = 195, right = 665, top = 34, rowH = 42;
    const sx = function(v){{ return left + (v / 100) * (right - left); }};
    let o = [];
    [0, 25, 50, 75, 100].forEach(function(t){{
      const x = sx(t);
      o.push('<line x1="' + x.toFixed(1) + '" x2="' + x.toFixed(1) + '" y1="22" y2="236" stroke="var(--line,#ddd)" stroke-dasharray="2 3"/>');
      o.push('<text class="c-tick" x="' + x.toFixed(1) + '" y="252" text-anchor="middle">' + t + '%</text>');
    }});
    o.push('<text class="c-axis" x="' + left + '" y="266">Match rate with Di Mino\\'s 27 novel signs (copper dot) vs 1,000 random sign shuffles (grey band ±1 SD)</text>');
    DATA.novel.forEach(function(row, i){{
      const y = top + i * rowH + 14;
      o.push('<text class="c-group" x="4" y="' + (y + 3) + '">' + row.label + '</text>');
      o.push('<text class="c-sub" x="4" y="' + (y + 17) + '">n=' + row.n + ' words · p=' + row.p.toFixed(3) + '</text>');
      const xlo = sx(Math.max(0, row.null - row.sd));
      const xhi = sx(Math.min(100, row.null + row.sd));
      o.push('<rect x="' + xlo.toFixed(1) + '" y="' + (y - 6) + '" width="' + Math.max(4, xhi - xlo).toFixed(1) + '" height="12" rx="3" fill="var(--faint,#8a8f98)" opacity="0.35"/>');
      o.push('<line x1="' + sx(row.null).toFixed(1) + '" x2="' + sx(row.null).toFixed(1) + '" y1="' + (y - 9) + '" y2="' + (y + 9) + '" stroke="var(--faint,#6e7681)" stroke-width="2"/>');
      o.push('<circle cx="' + sx(row.obs).toFixed(1) + '" cy="' + y + '" r="6" fill="var(--copper,#9a4d2c)"/>');
      o.push('<text class="c-label-sm" x="' + (Math.max(sx(row.obs), xhi) + 9).toFixed(1) + '" y="' + (y + 4) + '">' + row.obs.toFixed(1) + '% vs ' + row.null.toFixed(1) + '%</text>');
    }});
    svg.innerHTML = o.join('\\n');
  }}

  btns.forEach(function(b){{
    b.addEventListener('click', function(){{
      const m = b.getAttribute('data-mode');
      btns.forEach(function(x){{
        const on = x === b;
        x.style.background = on ? 'var(--copper,#9a4d2c)' : 'transparent';
        x.style.color = on ? '#fff' : 'inherit';
      }});
      if (m === 'len') renderLen(); else renderNovel();
    }});
  }});
  renderLen();
}})();
</script>
</figure>
"""
    (OUT / "length_and_novel_signs.html").write_text(html)


def write_collision_and_lexicon(d):
    t5 = d["test5_lexicon_and_collision_audit"]
    tiers = t5["confidence_tiers"]
    cov = t5["semitic_skeleton_space_coverage"]
    html = f"""<figure class="fig" aria-label="Semitic root collision saturation and kaphtor lexicon confidence breakdown">
<div class="fig-scroll">
<table class="matrix">
<thead>
<tr>
  <th scope="col">Diagnostic</th>
  <th scope="col">Observed value</th>
  <th scope="col">Why it matters</th>
</tr>
</thead>
<tbody>
<tr>
  <td>2-consonant skeleton space occupied (9-class grid)<span class="m-sub">5,189 Proto-Semitic roots</span></td>
  <td><strong>{cov['9class_2cons_occupied']} / {cov['9class_2cons_total']} ({cov['9class_2cons_pct']:.0f}%)</strong></td>
  <td>Every possible 2-consonant string in any language automatically matches a Semitic root.</td>
</tr>
<tr>
  <td>3-consonant skeleton space occupied (9-class / 7-class)<span class="m-sub">5,189 Proto-Semitic roots</span></td>
  <td><strong>{cov['9class_3cons_pct']:.1f}%</strong> ({cov['9class_3cons_occupied']}/729) · <strong>{cov['7class_3cons_pct']:.1f}%</strong> ({cov['7class_3cons_occupied']}/343)</td>
  <td>Covers 84.3% of real Mycenaean Greek 3-consonant words in Linear B by chance alone.</td>
</tr>
<tr>
  <td>Mean Proto-Semitic roots per Linear A skeleton<span class="m-sub">lexicon.json (≥3-sign single-root words)</span></td>
  <td><strong>{t5['mean_semitic_roots_per_skeleton']:.1f} roots / word</strong></td>
  <td>High collision multiplicity allows choosing whichever semantic gloss fits context.</td>
</tr>
<tr>
  <td>Lexicon entries obeying stated neutralization rules strictly<span class="m-sub">n = {t5['evaluated_single_root_ge3_sign_words']} single-root ≥3-sign words</span></td>
  <td><strong>{t5['strict_root_match_A1_rate']*100:.1f}%</strong> (A1) · <strong>{t5['affix_tolerant_root_match_rate']*100:.1f}%</strong> (with affixes)</td>
  <td>Nearly half of proposed readings require extra unmodeled shifts, deletions, or metatheses.</td>
</tr>
<tr>
  <td>Author confidence tiers in <code>lexicon.json</code><span class="m-sub">total = {t5['total_lexicon_entries']} entries</span></td>
  <td>CONFIRMED <strong>{tiers.get('CONFIRMED',0)}</strong> (2.6%) · PROBABLE <strong>{tiers.get('PROBABLE',0)}</strong> (10.7%) · CANDIDATE <strong>{tiers.get('CANDIDATE',0)}</strong> · SPECULATIVE <strong>{tiers.get('SPECULATIVE',0)}</strong></td>
  <td>86.7% of the 736-entry lexicon is self-rated Candidate or Speculative; 290 entries are only 1–2 signs long.</td>
</tr>
</tbody>
</table>
</div>
<figcaption>Structural audit of <code>plasma-ai/kaphtor</code> (commit <code>d419ccc1e79f</code>). Once 29 Semitic consonants are projected onto Linear A's coarse syllabic merger classes, root-dictionary collisions saturate the phonetic space.</figcaption>
</figure>
"""
    (OUT / "collision_audit.html").write_text(html)


def main():
    d = json.load(open(RES))
    write_tiles(d)
    write_length_and_controls(d)
    write_collision_and_lexicon(d)
    print(f"Generated 3 figures in {OUT}")


if __name__ == "__main__":
    main()
