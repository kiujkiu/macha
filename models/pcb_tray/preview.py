"""Top-view preview PNG showing jig outline + PCB pocket + finger cutouts."""
import json
import math
from pathlib import Path
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle, FancyBboxPatch
import numpy as np

# Register SimHei from Windows mount
_font_path = '/mnt/c/Windows/Fonts/simhei.ttf'
fm.fontManager.addfont(_font_path)
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

data = json.load(open(Path(__file__).with_name("pcb_outline_points.json")))
pts = data["pcb_pts_local"]
holes = data.get("m08_holes", [])
p = data["params"]

PCB_DX, PCB_DY = data["pcb_bbox"]
PCB_HX, PCB_HY = PCB_DX/2, PCB_DY/2
JIG_DX, JIG_DY = p["JIG_DX"], p["JIG_DY"]
JIG_HX, JIG_HY = JIG_DX/2, JIG_DY/2
JIG_R = p["JIG_R_CORNER"]
CL = p["PCB_CLEARANCE"]
CORNER = p.get("CORNER_SIZE", 18.0)
SCALLOP_W = p.get("SCALLOP_W", 24.0)
SCALLOP_REACH = p.get("SCALLOP_REACH", 2.0)
SCALLOP_DEPTH = p.get("SCALLOP_DEPTH", 2.0)

fig, ax = plt.subplots(figsize=(11, 9))

# Jig outline (rounded rect)
jig_rect = FancyBboxPatch(
    (-JIG_HX + JIG_R, -JIG_HY + JIG_R),
    JIG_DX - 2*JIG_R, JIG_DY - 2*JIG_R,
    boxstyle=f"round,pad=0,rounding_size={JIG_R}",
    linewidth=2, edgecolor='black', facecolor='#f5d480', label='Jig body')
ax.add_patch(jig_rect)

# PCB outline (offset 0 = real PCB shape)
xs = [x for x, y in pts] + [pts[0][0]]
ys = [y for x, y in pts] + [pts[0][1]]
ax.fill(xs, ys, color='#1f7a3a', alpha=0.55, label='PCB outline (示意)')
ax.plot(xs, ys, color='white', linewidth=0.8)

# Pocket outline (PCB + clearance)
def offset_polyline(pts, d):
    # naive — just scale by (1 + d/max_dim)
    return pts  # not used here; we'll just show PCB outline + small clearance text
# show clearance hint by drawing a slightly bigger dashed outline
xs2 = [x * (1 + CL/30) for x in xs]
ys2 = [y * (1 + CL/30) for y in ys]
# better: don't try analytical offset — just label clearance
# leave the green PCB outline as the visual

# 4 corner walls (yellow filled squares at jig corners — the wall-retained area)
def draw_corner(sx, sy):
    cx = sx * (JIG_HX - CORNER/2)
    cy = sy * (JIG_HY - CORNER/2)
    r = Rectangle((cx - CORNER/2, cy - CORNER/2), CORNER, CORNER, fill=False,
                  edgecolor='blue', linewidth=2.0, linestyle='-')
    ax.add_patch(r)
for sx in (-1, 1):
    for sy in (-1, 1):
        draw_corner(sx, sy)
ax.text(0, JIG_HY + 4, '4 角块墙 ' + f'{CORNER:g}×{CORNER:g}mm (蓝框)',
        ha='center', fontsize=9, color='blue')

# Top + bottom base scallops (cut 2mm into base — shown as dashed gray)
# Scallop shape = (top/bottom-half rectangle) - (PCB outline offset INWARD by SCALLOP_REACH)
from shapely.geometry import Polygon, box as shp_box
from matplotlib.patches import Polygon as MplPoly
pcb_poly = Polygon(pts).buffer(0)
pcb_inset = pcb_poly.buffer(-SCALLOP_REACH, join_style=1)  # round join
SC_HX = SCALLOP_W / 2
top_rect = shp_box(-SC_HX, 0, SC_HX, JIG_HY + 1)
bot_rect = shp_box(-SC_HX, -JIG_HY - 1, SC_HX, 0)
top_scallop = top_rect.difference(pcb_inset)
bot_scallop = bot_rect.difference(pcb_inset)

def draw_shp(poly, label):
    if poly.is_empty: return
    if poly.geom_type == 'Polygon':
        polys = [poly]
    else:
        polys = list(poly.geoms)
    for q in polys:
        coords = list(q.exterior.coords)
        patch = MplPoly(coords, closed=True, facecolor='#d05050', alpha=0.35,
                        edgecolor='darkred', linewidth=1.8, linestyle='--')
        ax.add_patch(patch)
    c = poly.centroid
    ax.annotate(label, (c.x, c.y), color='darkred', ha='center', va='center',
                fontsize=8, fontweight='bold')

draw_shp(top_scallop, f'上指坑\n沿 PCB 外形\n向内 {SCALLOP_REACH:g}mm')
draw_shp(bot_scallop, f'下指坑')

# 4 × M3 mounting through-holes
mount_holes = data.get("mount_holes", [])
MOUNT_D = p.get("MOUNT_DIAM", 3.2)
for (hx, hy) in mount_holes:
    ax.add_patch(plt.Circle((hx, hy), MOUNT_D/2, fill=False, edgecolor='purple',
                            linewidth=1.6, zorder=6))
ax.text(-JIG_HX, -JIG_HY - 7, f'4 × Φ{MOUNT_D:g} M3 固定通孔',
        ha='left', fontsize=9, color='purple')

# Probe through-holes (Φ1.0)
PROBE_D = p.get("PROBE_DIAM", 1.0)
for (hx, hy) in holes:
    ax.add_patch(plt.Circle((hx, hy), PROBE_D/2, color='black', fill=True, zorder=5))
ax.text(JIG_HX, -JIG_HY - 6, f'{len(holes)} × Φ{PROBE_D:g} 探针通孔',
        ha='right', fontsize=9, color='black')

# Annotations
ax.set_aspect('equal')
ax.grid(True, alpha=0.3, linestyle=':')
ax.set_xlim(-JIG_HX - 8, JIG_HX + 8)
ax.set_ylim(-JIG_HY - 8, JIG_HY + 8)
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_title(f'PCB 测试治具 俯视图  (治具 {JIG_DX:.1f}×{JIG_DY:.1f}×{p["TOTAL_H"]:.0f}mm; '
             f'4 角块墙 {CORNER:g}mm 高 {p["POCKET_DEPTH"]:g}mm; 底厚 {p["FLOOR_THICK"]:g}mm; '
             f'上/下指坑沿 PCB 外形 内偏 {SCALLOP_REACH:g}mm 深 {SCALLOP_DEPTH:g}mm)',
             fontsize=10)

# Dims at edges
ax.annotate(f'{JIG_DX:.1f}', (0, -JIG_HY - 3), ha='center', fontsize=9, color='black')
ax.annotate(f'{JIG_DY:.1f}', (-JIG_HX - 4, 0), ha='center', va='center', fontsize=9,
            color='black', rotation=90)
ax.annotate(f'PCB {PCB_DX:.1f}×{PCB_DY:.1f}', (0, 0), ha='center', va='center',
            fontsize=8, color='white', alpha=0.85)

# Legend hint
ax.text(JIG_HX, -JIG_HY - 7,
        f'PCB 间隙 +{CL}mm  /  角块墙高 {p["POCKET_DEPTH"]:g}mm  /  底厚 {p["FLOOR_THICK"]:g}mm '
        f'(指坑处仅 {p["FLOOR_THICK"] - SCALLOP_DEPTH:g}mm)',
        ha='right', fontsize=9, color='dimgray')

out = Path(__file__).with_name("pcb_tray_preview.png")
fig.savefig(out, dpi=120, bbox_inches='tight')
print(f"wrote {out}")
