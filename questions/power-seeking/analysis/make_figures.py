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
<div class="tile"><p class="tile-value">14 of 14</p><p class="tile-label">statements proved; the proof checker accepts every one</p></div>
<div class="tile"><p class="tile-value">6</p><p class="tile-label">say what a published source says, when checked against the papers by a second company's models</p></div>
<div class="tile"><p class="tile-value">5</p><p class="tile-label">are small examples that do not carry the conclusions first drawn from them</p></div>
<div class="tile"><p class="tile-value is-word">No</p><p class="tile-label">the theorems do not show that capable AI must seek power, and their authors say so; this study adds less than it first claimed</p></div>
</div>
"""
    (OUT / "tiles.html").write_text(html)


def write_premises():
    html = """<figure class="fig" aria-label="What each of the fourteen proved statements says, and how it stands against its source">
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;align-items:center;" role="tablist" aria-label="Filter by family">
  <button type="button" class="ps-tab" data-fam="all" aria-selected="true" style="padding:5px 11px;border:1px solid var(--line,#ccc);border-radius:4px;cursor:pointer;font-size:13px;background:var(--copper,#9a4d2c);color:#fff;">All 14</button>
  <button type="button" class="ps-tab" data-fam="coherence" aria-selected="false" style="padding:5px 11px;border:1px solid var(--line,#ccc);border-radius:4px;cursor:pointer;font-size:13px;background:transparent;color:inherit;">Coherence</button>
  <button type="button" class="ps-tab" data-fam="power" aria-selected="false" style="padding:5px 11px;border:1px solid var(--line,#ccc);border-radius:4px;cursor:pointer;font-size:13px;background:transparent;color:inherit;">Power-seeking</button>
  <button type="button" class="ps-tab" data-fam="shutdown" aria-selected="false" style="padding:5px 11px;border:1px solid var(--line,#ccc);border-radius:4px;cursor:pointer;font-size:13px;background:transparent;color:inherit;">Shutdown</button>
</div>
<style>#ps-matrix td:nth-child(2),#ps-matrix td:nth-child(3){text-align:left}</style>
<div class="fig-scroll">
<table class="matrix" id="ps-matrix">
<thead>
<tr>
  <th scope="col">Statement</th>
  <th scope="col">What it says</th>
  <th scope="col">Against its source</th>
  <th scope="col">Standing</th>
</tr>
</thead>
<tbody>
<tr data-fam="coherence">
  <td>The expected-utility theorem<span class="m-sub">S1a</span></td>
  <td>Preferences over gambles that are complete, transitive, independent and continuous can be scored by an expected utility, unique up to scale and shift.</td>
  <td>von Neumann and Morgenstern, in the modern four-axiom form</td>
  <td style="white-space:nowrap;font-weight:600">Same</td>
</tr>
<tr data-fam="coherence">
  <td>The plain money pump<span class="m-sub">S1b</span></td>
  <td>If each paid trade round a cycle of three is accepted, the agent ends where it began with less money.</td>
  <td>Gustafsson (2022) grants that foresight blocks this version</td>
  <td style="white-space:nowrap">Simplified</td>
</tr>
<tr data-fam="coherence">
  <td>Gaps without a pump<span class="m-sub">S1c</span></td>
  <td>Transitive preferences with gaps exist that have no losing chain of preferred trades.</td>
  <td>No source. The clause holds for transitivity alone, and the disputed pump trades across the gaps, which the statement rules out</td>
  <td style="white-space:nowrap">Example only</td>
</tr>
<tr data-fam="coherence">
  <td>Any behaviour maximises something<span class="m-sub">S1d</span></td>
  <td>Any fixed way of acting maximises some utility defined over whole histories.</td>
  <td>Shah (2018)</td>
  <td style="white-space:nowrap;font-weight:600">Same</td>
</tr>
<tr data-fam="power">
  <td>Retargetable, once<span class="m-sub">S2a</span></td>
  <td>If one relabelling turns every case favouring A into one favouring B, at least as many relabellings favour B.</td>
  <td>Turner and Tadepalli (2022), Prop. 3.4</td>
  <td style="white-space:nowrap;font-weight:600">Same</td>
</tr>
<tr data-fam="power">
  <td>Retargetable, n times<span class="m-sub">S2b</span></td>
  <td>With n such relabellings that do not overlap, at least n times as many.</td>
  <td>Turner and Tadepalli (2022), Thm. 3.6</td>
  <td style="white-space:nowrap;font-weight:600">Same</td>
</tr>
<tr data-fam="power">
  <td>More options win most of the time<span class="m-sub">S2c</span></td>
  <td>If a set of options contains a relabelled copy of another, it is worth more at least as often as less, across the relabellings of any finite spread of rewards.</td>
  <td>Turner and others (2021), Lemma E.24. No decision process, policy or discounting in the statement</td>
  <td style="white-space:nowrap;font-weight:600">Special case</td>
</tr>
<tr data-fam="power">
  <td>Some rewards favour fewer options<span class="m-sub">S2d</span></td>
  <td>One spread of rewards favours the smaller set.</td>
  <td>The paper says so itself; its theorem never assumed otherwise</td>
  <td style="white-space:nowrap">Example only</td>
</tr>
<tr data-fam="power">
  <td>A rule that picks the smaller set<span class="m-sub">S2e</span></td>
  <td>A function that always answers &ldquo;the smaller set&rdquo; exists.</td>
  <td>The function is unconstrained. The 2022 paper puts such systems outside its results</td>
  <td style="white-space:nowrap">Example only</td>
</tr>
<tr data-fam="power">
  <td>Useless options add nothing<span class="m-sub">S2f</span></td>
  <td>Adding an option that is never strictly best changes nothing.</td>
  <td>Built into the paper's definitions</td>
  <td style="white-space:nowrap">Example only</td>
</tr>
<tr data-fam="shutdown">
  <td>When meddling pays<span class="m-sub">S3a</span></td>
  <td>In a three-row table of payoffs, blocking the button pays if running is worth more, pressing it pays if shutdown is worth more, and neither pays at every small cost only if the two are worth the same.</td>
  <td>Echoes Soares and others (2015) and Thornley (2025). Neither theorem</td>
  <td style="white-space:nowrap">Simplified</td>
</tr>
<tr data-fam="shutdown">
  <td>Indifference, assumed<span class="m-sub">S3b</span></td>
  <td>If the two are worth the same and meddling costs anything, leaving the button alone is best.</td>
  <td>The equal worth is assumed. Soares and others go on to show how the approach fails</td>
  <td style="white-space:nowrap">Simplified</td>
</tr>
<tr data-fam="shutdown">
  <td>The clash<span class="m-sub">S3c</span></td>
  <td>Complete, transitive preferences that rank better above worse at two lengths of life include a strict preference across lengths.</td>
  <td>A two-by-two case of what Thornley draws from his Second Theorem</td>
  <td style="white-space:nowrap;font-weight:600">Special case</td>
</tr>
<tr data-fam="shutdown">
  <td>A way out, pictured<span class="m-sub">S3d</span></td>
  <td>Without completeness, such preferences can have no strict preference across lengths.</td>
  <td>A four-point picture of a proposal by Thornley and others (2024). Does not show the agent stays shutdownable</td>
  <td style="white-space:nowrap">Example only</td>
</tr>
<tr class="m-foot">
  <td colspan="4">Same: the statement is the source's. Special case: the source's result in a narrower setting. Simplified: keeps the idea, loses the substance. Example only: one small object that does not support the conclusion first drawn from it. All fourteen are proved; the column says what the proof is worth.</td>
</tr>
</tbody>
</table>
</div>
<figcaption>The fourteen statements, as read by a second company's model that was given the formal text alone, without the report or the proofs, and then compared with the cited papers.</figcaption>
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
<figcaption>The three-row table behind statements S3a and S3b. Move the sliders. When staying on is worth more than being shut down and blocking the button is cheap, blocking pays; when shutdown is worth more, pressing pays; when the two are worth exactly the same, leaving the button alone is best. This is a toy model, not the theorems of the papers it echoes, and the equal worth is something a designer would have to achieve, which is the hard part.</figcaption>
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
