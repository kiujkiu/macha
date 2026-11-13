# -*- coding: utf-8 -*-
"""plot board-coords copper (from dump_geom.py JSON) — front view (= from outside), both layers side by side.
    ../../../../.venv/bin/python plot_layers.py geom.json out.png [mech_constraints.json]"""
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Circle, Rectangle  # noqa: E402

g = json.load(open(sys.argv[1]))
mc = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None
W, H = 40.0, 22.5
COL = {'GND': '#888888', '+3V3': '#d62728'}
fig, axs = plt.subplots(1, 2, figsize=(18, 6.2), dpi=130)
for ax, L in zip(axs, 'FB'):
    ax.add_patch(Rectangle((0, 0), W, H, fc='#e8f5e9', ec='k'))
    for X, Y in ((3.5, 10), (36.5, 10)):
        ax.add_patch(Circle((X, Y), 1.6, fc='w', ec='k'))
        ax.add_patch(Circle((X, Y), (4.8 if L == 'F' else 8.0) / 2, fc='none', ec='m', ls='--'))
    for p in g['pads']:
        if not p[L]:
            continue
        X0, Y0, X1, Y1 = p['box']
        ax.add_patch(Rectangle((X0, Y0), X1 - X0, Y1 - Y0, fc=COL.get(p['net'], '#ff9900'), alpha=.8, ec='k', lw=.3))
        ax.text((X0 + X1) / 2, (Y0 + Y1) / 2, p['num'], fontsize=4, ha='center', va='center')
    for t in g['tracks']:
        if t['L'] != L:
            continue
        ax.plot([t['a'][0], t['b'][0]], [t['a'][1], t['b'][1]], color=COL.get(t['net'], '#1f77b4'), lw=t['w'] * 14, solid_capstyle='round')
    for v in g['vias']:
        ax.add_patch(Circle(v['p'], 0.3, fc=COL.get(v['net'], '#1f77b4'), ec='k', lw=.4))
    for f in g['fps']:
        if f['side'] == L and not f['ref'].startswith('H'):
            ax.text(f['X'], f['Y'] + 0.2, f['ref'], fontsize=6, color='navy', ha='center')
    if mc and L == 'B':
        for kx in mc.get('keepouts_back', []):
            if 'rect' in kx:
                x0, y0, x1, y1 = kx['rect']
                ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc='none', ec='r', ls=':'))
    ax.set_xlim(-1, W + 1); ax.set_ylim(-1, H + 1); ax.set_aspect('equal'); ax.grid(alpha=.2)
    ax.set_title(f'{L}.Cu  (front view from outside; board coords X right, Y up)')
plt.tight_layout(); plt.savefig(sys.argv[2])
