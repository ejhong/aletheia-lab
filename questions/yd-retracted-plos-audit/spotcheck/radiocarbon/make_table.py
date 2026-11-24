"""Markdown table of all 27 dates: published mu/sd vs my calibrations under the key recipes (from out_recipe_grid.json)."""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent.parent
R = json.loads((H / 'out_recipe_grid.json').read_text())
cols = [('Marine20 +dR (tab_err)', 'M20 +ΔR'), ('Marine20 -dR (tab_err)', 'M20 −ΔR'), ('IntCal20 -dR (tab_err)', 'IC20 −ΔR'), ('Marine13 +dR (tab_err)', 'M13 +ΔR')]
lines = ['| Core | Depth | Lab ID | Published μ±σ | ' + ' | '.join(f'{c[1]} μ±σ (Δμ)' for c in cols) + ' |', '|' + '---|' * (4 + len(cols))]
for core in ('52', '64', '67', '77'):
    n = len(R[core][cols[0][0]])
    for i in range(n):
        x0 = R[core][cols[0][0]][i]
        cells = [core, x0['depth'], x0['lab'], f"{x0['pub_mu']}±{x0['pub_sd']}"]
        for key, _ in cols:
            x = R[core][key][i]
            cells.append(f"{x['mu']:.0f}±{x['sd']:.0f} ({x['d_mu']:+.1f})")
        lines.append('| ' + ' | '.join(cells) + ' |')
(H / 'out_all_dates_table.md').write_text('\n'.join(lines) + '\n')
print('\n'.join(lines))
