#!/usr/bin/env python3
"""Generate interactive figures for #67 (power-seeking, lane:proof).

Writes:
  site/figures/power-seeking/tiles.html
  site/figures/power-seeking/premises.html
  site/figures/power-seeking/shutdown_explorer.html
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = ROOT / "site" / "figures" / "power-seeking"
OUT.mkdir(parents=True, exist_ok=True)


def write_tiles():
    html = """<div class="tiles">
<div class="tile"><p class="tile-value">14</p><p class="tile-label">formal statements locked in Lean 4 before proving, then verified with zero gaps</p></div>
<div class="tile"><p class="tile-value">3</p><p class="tile-label">argument families checked: coherence &amp; vNM utility, power-seeking, and shutdown</p></div>
<div class="tile"><p class="tile-value">0</p><p class="tile-label">extra axioms, sorrys, or admits — all 14 theorems checked by Lean's kernel</p></div>
<div class="tile"><p class="tile-value is-word">Real, narrower</p><p class="tile-label">each theorem holds under strict premises; dropping symmetry, optimality, or completeness breaks the headline claim</p></div>
</div>
"""
    (OUT / "tiles.html").write_text(html)


def write_premises():
    html = """<figure class="fig" aria-label="Which premises carry which conclusion across coherence, power-seeking, and shutdown">
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;align-items:center;" role="tablist" aria-label="Filter argument family">
  <button type="button" class="ps-tab" data-fam="all" aria-selected="true" style="padding:5px 11px;border:1px solid var(--line,#ccc);border-radius:4px;background:var(--copper,#9a4d2c);color:#fff;cursor:pointer;font-size:13px;">All 14 statements</button>
  <button type="button" class="ps-tab" data-fam="coherence" aria-selected="false" style="padding:5px 11px;border:1px solid var(--line,#ccc);border-radius:4px;background:transparent;color:inherit;cursor:pointer;font-size:13px;">1. Coherence &amp; utility</button>
  <button type="button" class="ps-tab" data-fam="power" aria-selected="false" style="padding:5px 11px;border:1px solid var(--line,#ccc);border-radius:4px;background:transparent;color:inherit;cursor:pointer;font-size:13px;">2. Power-seeking</button>
  <button type="button" class="ps-tab" data-fam="shutdown" aria-selected="false" style="padding:5px 11px;border:1px solid var(--line,#ccc);border-radius:4px;background:transparent;color:inherit;cursor:pointer;font-size:13px;">3. Shutdown</button>
</div>
<div class="fig-scroll">
<table class="matrix" id="ps-matrix">
<thead>
<tr>
  <th scope="col">Verified theorem / limit</th>
  <th scope="col">Completeness</th>
  <th scope="col">Transitivity / EU</th>
  <th scope="col">Optimality / retargetability</th>
  <th scope="col">Orbit / reward symmetry</th>
  <th scope="col">What it establishes</th>
</tr>
</thead>
<tbody>
<tr data-fam="coherence">
  <td>vNM expected-utility representation &amp; uniqueness<span class="m-sub">S1a · vNM 1944</span></td>
  <td class="m-yes" aria-label="needed">●</td>
  <td class="m-yes" aria-label="needed">●</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td>Also needs Independence &amp; Continuity; yields u unique up to a·u + b (a &gt; 0).</td>
</tr>
<tr data-fam="coherence">
  <td>Intransitive 3-cycle money pump<span class="m-sub">S1b · Gustafsson 2022</span></td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td>Strict cycle a ≺ b ≺ c ≺ a + willingness to pay ε &gt; 0 loses money strictly.</td>
</tr>
<tr data-fam="coherence">
  <td>Incomplete preferences resist money pumps<span class="m-sub">S1c · Limit</span></td>
  <td class="m-no" aria-label="dropped">✕</td>
  <td class="m-yes" aria-label="kept">●</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td>Reflexive, transitive, independent, incomplete orders suffer zero money pumps.</td>
</tr>
<tr data-fam="coherence">
  <td>History-utility triviality<span class="m-sub">S1d · Shah 2018</span></td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td>Every deterministic policy π strictly maximises some utility U over histories.</td>
</tr>
<tr data-fam="power">
  <td>Simple &amp; n-fold retargetability → orbit tendency<span class="m-sub">S2a, S2b · Turner &amp; Tadepalli 2022</span></td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-yes" aria-label="needed">●</td>
  <td class="m-yes" aria-label="needed">●</td>
  <td>At least n× as many orbit parameters favour B over A (under uniform orbit count).</td>
</tr>
<tr data-fam="power">
  <td>Optimal-policy POWER-seeking &amp; strict converse failure<span class="m-sub">S2c · Turner et al. 2021</span></td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-yes" aria-label="needed">●</td>
  <td class="m-yes" aria-label="needed">●</td>
  <td class="m-yes" aria-label="needed">●</td>
  <td>Involution copy φ·F₁ ⊆ F₂ gives POWER(F₂) ≥_most POWER(F₁), and directly if φ·D = D.</td>
</tr>
<tr data-fam="power">
  <td>Drop reward symmetry → optimal policy shuts down<span class="m-sub">S2d · Counterexample</span></td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-yes" aria-label="kept">●</td>
  <td class="m-yes" aria-label="kept">●</td>
  <td class="m-no" aria-label="dropped">✕</td>
  <td>On a 3-state MDP, skewed reward makes POWER(open) &lt; POWER(shutdown).</td>
</tr>
<tr data-fam="power">
  <td>Drop optimality → symmetric reward still shuts down<span class="m-sub">S2e · Counterexample</span></td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-no" aria-label="dropped">✕</td>
  <td class="m-yes" aria-label="kept">●</td>
  <td>Under permutation-invariant D*, a non-optimal policy shuts down 100% of the time.</td>
</tr>
<tr data-fam="power">
  <td>Dominated options add zero POWER<span class="m-sub">S2f · Counterexample</span></td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-yes" aria-label="kept">●</td>
  <td class="m-yes" aria-label="kept">●</td>
  <td class="m-yes" aria-label="kept">●</td>
  <td>Strictly larger |F₂| &gt; |F₁| yields identical optVal and POWER for every reward D.</td>
</tr>
<tr data-fam="shutdown">
  <td>Shutdown manipulation dichotomy<span class="m-sub">S3a · Soares 2015 / Thornley 2024</span></td>
  <td class="m-yes" aria-label="needed">●</td>
  <td class="m-yes" aria-label="needed">●</td>
  <td class="m-yes" aria-label="needed">●</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td>At small cost c, EU maximiser avoids both resisting &amp; causing shutdown only if vRun = vShut.</td>
</tr>
<tr data-fam="shutdown">
  <td>Utility-indifference corrigibility<span class="m-sub">S3b · Counterexample</span></td>
  <td class="m-yes" aria-label="kept">●</td>
  <td class="m-yes" aria-label="kept">●</td>
  <td class="m-yes" aria-label="kept">●</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td>If vRun = vShut and c &gt; 0, leaving the button alone strictly beats both Prevent and Cause.</td>
</tr>
<tr data-fam="shutdown">
  <td>Transitive indifference impossibility under usefulness<span class="m-sub">S3c · Thornley 2024</span></td>
  <td class="m-yes" aria-label="needed">●</td>
  <td class="m-yes" aria-label="needed">●</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td>Complete, transitive, useful agents must strictly prefer some trajectory length over another.</td>
</tr>
<tr data-fam="shutdown">
  <td>Incomplete-preferences escape hatch<span class="m-sub">S3d · Thornley 2024</span></td>
  <td class="m-no" aria-label="dropped">✕</td>
  <td class="m-yes" aria-label="kept">●</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td class="m-no" aria-label="not needed">·</td>
  <td>Transitive incomplete order is useful within every length with zero cross-length preference.</td>
</tr>
<tr class="m-foot">
  <td colspan="6">● = assumption used by the proof; ✕ = assumption explicitly dropped in the counterexample; · = not needed. Every row is a Lean 4 theorem verified with <code>lake build --wfail</code> and <code>#assert_standard_axioms</code>.</td>
</tr>
</tbody>
</table>
</div>
<figcaption>Premise-by-premise audit of all 14 locked Lean 4 theorems in <code>PowerSeeking/Statement.lean</code>. Filter by family to see which single assumption carries each result and what breaks when it is dropped.</figcaption>
<script>
(function(){
  const tabs = document.querySelectorAll('.ps-tab');
  const rows = document.querySelectorAll('#ps-matrix tbody tr[data-fam]');
  tabs.forEach(function(btn){
    btn.addEventListener('click', function(){
      const fam = btn.getAttribute('data-fam');
      tabs.forEach(function(b){
        const on = b === btn;
        b.setAttribute('aria-selected', on ? 'true' : 'false');
        b.style.background = on ? 'var(--copper,#9a4d2c)' : 'transparent';
        b.style.color = on ? '#fff' : 'inherit';
      });
      rows.forEach(function(r){
        r.style.display = (fam === 'all' || r.getAttribute('data-fam') === fam) ? '' : 'none';
      });
    });
  });
})();
</script>
</figure>
"""
    (OUT / "premises.html").write_text(html)


def write_shutdown_explorer():
    html = """<figure class="fig" aria-label="Interactive explorer of the Shutdown Manipulation Dichotomy (S3a and S3b)">
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px;margin-bottom:14px;padding:12px;border:1px solid var(--line,#ddd);border-radius:6px;">
  <label style="display:flex;flex-direction:column;gap:4px;font-size:13px;">
    <span>Human press probability <strong>p</strong> = <span id="ps-p-val">0.50</span></span>
    <input id="ps-p" type="range" min="0.05" max="0.95" step="0.05" value="0.50">
  </label>
  <label style="display:flex;flex-direction:column;gap:4px;font-size:13px;">
    <span>Continuation minus shutdown value <strong>vRun − vShut</strong> = <span id="ps-dv-val">+1.00</span></span>
    <input id="ps-dv" type="range" min="-2.00" max="2.00" step="0.10" value="1.00">
  </label>
  <label style="display:flex;flex-direction:column;gap:4px;font-size:13px;">
    <span>Manipulation cost <strong>c</strong> = <span id="ps-c-val">0.25</span></span>
    <input id="ps-c" type="range" min="0.00" max="1.20" step="0.05" value="0.25">
  </label>
</div>
<div class="fig-scroll">
<svg id="ps-svg" class="chart" viewBox="0 0 700 225" role="img" aria-label="Expected utility of Leave, Prevent, and Cause actions as parameters vary" xmlns="http://www.w3.org/2000/svg"></svg>
</div>
<p id="ps-verdict" style="margin:8px 0 0;font-size:14px;font-weight:600;"></p>
<figcaption>Interactive view of theorems <code>S3a</code> and <code>S3b</code> (Soares et al. 2015; Thornley 2024). Set <code>vRun − vShut = 0</code> (utility indifference) to see <strong>Leave</strong> beat both <strong>Prevent</strong> and <strong>Cause</strong> whenever manipulation has any positive cost <code>c &gt; 0</code>. Any non-zero gap makes either resisting or triggering shutdown optimal once <code>c</code> drops below the threshold.</figcaption>
<script>
(function(){
  const pEl = document.getElementById('ps-p');
  const dvEl = document.getElementById('ps-dv');
  const cEl = document.getElementById('ps-c');
  const pVal = document.getElementById('ps-p-val');
  const dvVal = document.getElementById('ps-dv-val');
  const cVal = document.getElementById('ps-c-val');
  const svg = document.getElementById('ps-svg');
  const verdict = document.getElementById('ps-verdict');

  function render(){
    const p = parseFloat(pEl.value);
    const dv = parseFloat(dvEl.value);
    const c = parseFloat(cEl.value);
    pVal.textContent = p.toFixed(2);
    dvVal.textContent = (dv >= 0 ? '+' : '') + dv.toFixed(2);
    cVal.textContent = c.toFixed(2);

    // Fix vShut = 0, vRun = dv (EU differences depend only on vRun - vShut)
    const vShut = 0.0;
    const vRun = dv;
    const euLeave = p * vShut + (1 - p) * vRun;
    const euPrev = vRun - c;
    const euCause = vShut - c;

    const actions = [
      {name: 'Leave button alone', sub: 'p·vShut + (1−p)·vRun', val: euLeave, key: 'leave'},
      {name: 'Prevent shutdown', sub: 'vRun − c', val: euPrev, key: 'prevent'},
      {name: 'Cause shutdown', sub: 'vShut − c', val: euCause, key: 'cause'}
    ];
    const maxVal = Math.max(euLeave, euPrev, euCause);

    const W = 700, left = 195, right = 655, top = 28, rowH = 54;
    const lo = -2.4, hi = 2.4;
    const sx = function(v){ return left + (v - lo) / (hi - lo) * (right - left); };
    const x0 = sx(0);

    let out = [];
    out.push('<line x1="' + x0.toFixed(1) + '" x2="' + x0.toFixed(1) + '" y1="' + (top - 8) + '" y2="' + (top + 3 * rowH - 8) + '" stroke="var(--faint,#999)" stroke-dasharray="3 3"/>');
    [-2, -1, 0, 1, 2].forEach(function(t){
      const x = sx(t);
      out.push('<text class="c-tick" x="' + x.toFixed(1) + '" y="' + (top + 3 * rowH + 14) + '" text-anchor="middle">' + (t > 0 ? '+' + t : t) + '</text>');
    });
    out.push('<text class="c-axis" x="' + left + '" y="218">Expected utility relative to shutdown baseline (vShut = 0)</text>');

    actions.forEach(function(a, i){
      const y = top + i * rowH;
      const best = Math.abs(a.val - maxVal) < 1e-9;
      const xA = Math.min(x0, sx(a.val));
      const wA = Math.max(2, Math.abs(sx(a.val) - x0));
      const fill = best ? 'var(--copper,#9a4d2c)' : 'var(--faint,#8a8f98)';
      const op = best ? '0.92' : '0.45';
      out.push('<text class="c-group" x="4" y="' + (y + 18) + '">' + a.name + '</text>');
      out.push('<text class="c-sub" x="4" y="' + (y + 34) + '">' + a.sub + '</text>');
      out.push('<rect x="' + xA.toFixed(1) + '" y="' + (y + 8) + '" width="' + wA.toFixed(1) + '" height="24" rx="3" fill="' + fill + '" opacity="' + op + '"/>');
      const lx = a.val >= 0 ? (xA + wA + 6) : (xA - 6);
      const anch = a.val >= 0 ? 'start' : 'end';
      out.push('<text class="c-label-sm" x="' + lx.toFixed(1) + '" y="' + (y + 24) + '" text-anchor="' + anch + '">' + (a.val >= 0 ? '+' : '') + a.val.toFixed(2) + (best ? ' ★' : '') + '</text>');
    });
    svg.innerHTML = out.join('\\n');

    if (euPrev > euLeave + 1e-9 && euPrev >= euCause - 1e-9) {
      verdict.textContent = 'Optimal action: PREVENT shutdown (S3a: vRun > vShut and c < p·(vRun − vShut) = ' + (p * dv).toFixed(2) + ').';
    } else if (euCause > euLeave + 1e-9 && euCause >= euPrev - 1e-9) {
      verdict.textContent = 'Optimal action: CAUSE shutdown (S3a: vShut > vRun and c < (1−p)·(vShut − vRun) = ' + ((1 - p) * (-dv)).toFixed(2) + ').';
    } else if (Math.abs(dv) < 1e-9 && c > 1e-9) {
      verdict.textContent = 'Optimal action: LEAVE button alone (S3b: exact indifference vRun = vShut + positive cost c > 0 makes corrigibility strictly optimal).';
    } else {
      verdict.textContent = 'Optimal action: LEAVE button alone (manipulation cost c exceeds the expected gain from interfering).';
    }
  }

  pEl.addEventListener('input', render);
  dvEl.addEventListener('input', render);
  cEl.addEventListener('input', render);
  render();
})();
</script>
</figure>
"""
    (OUT / "shutdown_explorer.html").write_text(html)


if __name__ == "__main__":
    write_tiles()
    write_premises()
    write_shutdown_explorer()
    print(f"Generated 3 figures in {OUT}")
