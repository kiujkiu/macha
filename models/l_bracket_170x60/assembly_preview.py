"""
Assembly proposal preview: l_bracket_170x60 mated to rim_ring.

Geometry assumption (to be confirmed by user):
  • rim_ring is horizontal, top of base annulus at Z=3.5.
  • bracket is rotated -90° about Y from its print orientation, so that
    the vleg's print-frame back face (X=0, 60×90) lies flat ON the rim.
  • The hleg becomes a tall vertical fin (200 mm tall) sticking up.
  • The bracket's hleg "front" 200×90 vertical face (the one that was the
    bottom of the hleg in print) is placed 14.3 mm from rim center,
    extending in the −X direction of the rim.
  • Bracket is centered on the rim's X axis (so vleg's Y_v=45 → rim Y=0).
  • The 4 vleg M3 through-holes are MOVED from their current 70×40
    rectangle to match 4 specific rim_ring holes:
        — 2 inner holes (PCD Φ70) at angles 157.5° and 202.5°
        — 2 outer holes (PCD Φ155) at angles 157.5° and 202.5°
    These 4 form a symmetric trapezoid in the rim's top plane.

Output: assembly_preview.png — top-down view of rim with bracket footprint
        overlaid + side elevation showing hleg vertical fin.
"""
import math
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyArrowPatch
import matplotlib.font_manager as fm

# Use a Chinese-capable font (SimHei mounted from Windows)
for p in ["/mnt/c/Windows/Fonts/simhei.ttf"]:
    if Path(p).exists():
        fm.fontManager.addfont(p)
        plt.rcParams["font.family"] = "SimHei"
        plt.rcParams["axes.unicode_minus"] = False
        break

# ===== rim_ring =====
RIM_OD, RIM_ID = 170.0, 60.0
R_IN_PCD, R_OUT_PCD = 35.0, 77.5
RIM_HOLE_D = 3.2
RIM_ANGLES = [22.5 + 45*k for k in range(8)]

# ===== bracket vleg footprint on rim =====
# Vleg 60 × 90 sits flat on rim. After rotation, in rim's XY plane:
#   X_rim goes from −14.3 (close to center) to −74.3 (close to outer edge)
#   Y_rim goes from −45 to +45
HLEG_DIST = 14.3      # the 200×90 face is at this distance from rim center
VLEG_RAD  = 60.0      # along radial (in rim X), = bracket LEG_B
VLEG_TAN  = 90.0      # along tangential (in rim Y), = bracket WIDTH
HLEG_THICK = 4.0      # the vertical hleg fin is 4 mm thick in rim X

# Proposed rim holes used as the 4 mounting holes
MATING = [(R_IN_PCD,  157.5), (R_IN_PCD,  202.5),
          (R_OUT_PCD, 157.5), (R_OUT_PCD, 202.5)]

# ===== Plot =====
fig, (ax_top, ax_side) = plt.subplots(1, 2, figsize=(14, 7))

# ---- Top-down view ----
ax = ax_top
ax.set_aspect("equal")
ax.set_title("装配俯视图 — rim_ring + l_bracket_170x60(立板贴 rim 顶面)", fontsize=12)
ax.set_xlim(-100, 100)
ax.set_ylim(-100, 100)
ax.grid(True, alpha=0.3, linestyle=":")
ax.axhline(0, color="gray", lw=0.4, alpha=0.4)
ax.axvline(0, color="gray", lw=0.4, alpha=0.4)

# rim disc
ax.add_patch(Circle((0, 0), RIM_OD/2, fill=False, lw=1.4, color="black"))
ax.add_patch(Circle((0, 0), RIM_ID/2, fill=False, lw=1.0, color="black"))
ax.add_patch(Circle((0, 0), 82.5,     fill=False, lw=0.5, color="gray", linestyle="--", alpha=0.6))
ax.text(0, RIM_OD/2 + 3, f"rim Φ{RIM_OD:g}", ha="center", fontsize=8, color="dimgray")
ax.text(0, RIM_ID/2 + 1.5, f"Φ{RIM_ID:g}", ha="center", fontsize=7, color="dimgray")

# all 16 rim holes (light)
for a in RIM_ANGLES:
    for R in (R_IN_PCD, R_OUT_PCD):
        cx, cy = R*math.cos(math.radians(a)), R*math.sin(math.radians(a))
        ax.add_patch(Circle((cx, cy), RIM_HOLE_D/2, color="lightgray", ec="gray", lw=0.4))

# PCD circles
ax.add_patch(Circle((0, 0), R_IN_PCD,  fill=False, lw=0.4, color="gray", linestyle=":"))
ax.add_patch(Circle((0, 0), R_OUT_PCD, fill=False, lw=0.4, color="gray", linestyle=":"))
ax.text(0, R_IN_PCD + 1.5,  f"PCD Φ{2*R_IN_PCD:g}",  ha="center", fontsize=7, color="gray")
ax.text(0, R_OUT_PCD + 1.5, f"PCD Φ{2*R_OUT_PCD:g}", ha="center", fontsize=7, color="gray")

# bracket vleg footprint (the 60 × 90 flat slab on rim, lying flat)
v_x0 = -HLEG_DIST - VLEG_RAD          # −74.3
v_y0 = -VLEG_TAN/2                    # −45
ax.add_patch(Rectangle((v_x0, v_y0), VLEG_RAD, VLEG_TAN,
                       fill=True, facecolor="#7fdf7f", alpha=0.35,
                       edgecolor="green", lw=1.5, label="立板 60×90 贴 rim"))

# hleg vertical fin — projected footprint in top view = 4 × 90 strip at X=−14.3..−18.3
ax.add_patch(Rectangle((-HLEG_DIST - HLEG_THICK, -VLEG_TAN/2),
                       HLEG_THICK, VLEG_TAN,
                       fill=True, facecolor="#1f8b1f", alpha=0.7,
                       edgecolor="darkgreen", lw=1.0, label="hleg 200×90 立面投影(厚 4)"))

# 4 mating holes highlighted in red
for (R, a) in MATING:
    cx = R*math.cos(math.radians(a))
    cy = R*math.sin(math.radians(a))
    ax.add_patch(Circle((cx, cy), RIM_HOLE_D/2 * 1.6,
                        fill=False, ec="red", lw=1.5))
    ax.plot(cx, cy, marker="x", color="red", markersize=6)
    ax.annotate(f"{a:g}°", (cx, cy), xytext=(cx - 4, cy + 4),
                fontsize=7, color="red")

# 14.3 mm dim arrow from center to hleg front face
ax.annotate("", xy=(-HLEG_DIST, -52), xytext=(0, -52),
            arrowprops=dict(arrowstyle="<->", color="black", lw=0.8))
ax.text(-HLEG_DIST/2, -56, f"{HLEG_DIST:g} mm",
        ha="center", fontsize=9, color="black")

# legend
ax.legend(loc="upper right", fontsize=8)
ax.set_xlabel("X_rim  (mm)")
ax.set_ylabel("Y_rim  (mm)")

# ---- Side elevation (looking along +Y_rim) ----
ax = ax_side
ax.set_aspect("equal")
ax.set_title("装配侧视图 — 沿 +Y 看 (hleg 立起 200 mm)", fontsize=12)
ax.set_xlim(-100, 100)
ax.set_ylim(-10, 220)
ax.grid(True, alpha=0.3, linestyle=":")
ax.axhline(0, color="gray", lw=0.4, alpha=0.4)
ax.axvline(0, color="gray", lw=0.4, alpha=0.4)

# rim cross-section (looking from +Y, so we see the rim's left/right halves)
# base annulus Z=0..3.5 (gray); upper rim at OD=165..170 stands at Z=3.5..9
BASE_H, RIM_H = 3.5, 5.5
ax.add_patch(Rectangle((-RIM_OD/2, 0), RIM_OD, BASE_H, fill=True,
                       facecolor="lightgray", edgecolor="black", lw=0.8,
                       label="rim base 3.5"))
# upper rim left part
ax.add_patch(Rectangle((-RIM_OD/2, BASE_H), 2.5, RIM_H, fill=True,
                       facecolor="lightgray", edgecolor="black", lw=0.6))
ax.add_patch(Rectangle((RIM_OD/2 - 2.5, BASE_H), 2.5, RIM_H, fill=True,
                       facecolor="lightgray", edgecolor="black", lw=0.6))

# bracket vleg (horizontal 60 × 4 slab) sitting on base top (Z=3.5..7.5)
ax.add_patch(Rectangle((-HLEG_DIST - VLEG_RAD, BASE_H), VLEG_RAD, HLEG_THICK,
                       fill=True, facecolor="#7fdf7f", alpha=0.6,
                       edgecolor="green", lw=1.0, label="立板 60×4 (LEG_B × THICK)"))
# hleg vertical fin (200 tall × 4 thick in rim-X)
ax.add_patch(Rectangle((-HLEG_DIST - HLEG_THICK, BASE_H), HLEG_THICK, 200,
                       fill=True, facecolor="#1f8b1f", alpha=0.85,
                       edgecolor="darkgreen", lw=1.0, label="hleg 200×4 (立面)"))

# 14.3 mm dim
ax.annotate("", xy=(-HLEG_DIST, BASE_H - 3), xytext=(0, BASE_H - 3),
            arrowprops=dict(arrowstyle="<->", color="black", lw=0.8))
ax.text(-HLEG_DIST/2, BASE_H - 6, f"{HLEG_DIST:g} mm",
        ha="center", fontsize=9, color="black")

# 200 mm height label
ax.annotate("", xy=(-HLEG_DIST - HLEG_THICK - 6, BASE_H),
            xytext=(-HLEG_DIST - HLEG_THICK - 6, BASE_H + 200),
            arrowprops=dict(arrowstyle="<->", color="darkgreen", lw=0.8))
ax.text(-HLEG_DIST - HLEG_THICK - 9, BASE_H + 100, "hleg 200",
        ha="right", va="center", fontsize=9, color="darkgreen",
        rotation=90)

ax.legend(loc="upper right", fontsize=8)
ax.set_xlabel("X_rim  (mm)")
ax.set_ylabel("Z_rim  (mm)")

plt.tight_layout()
out = Path(__file__).with_name("assembly_preview.png")
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"wrote {out}")

# ---- Also print the proposed vleg hole coordinates ----
print("\nProposed bracket vleg M3 hole positions (in vleg local frame Y_v, Z_v):")
print("  Y_v = Y_rim + WIDTH/2,    Z_v = -X_rim - HLEG_DIST")
print("  (current build's vleg Y∈[0,90], Z∈[0,60])")
WIDTH = 90.0
for (R, a) in MATING:
    cx = R*math.cos(math.radians(a))
    cy = R*math.sin(math.radians(a))
    Y_v = cy + WIDTH/2
    Z_v = -cx - HLEG_DIST
    print(f"  rim hole R={R:5.1f} @ {a:6.1f}°  ({cx:+7.3f}, {cy:+7.3f}) "
          f"→ bracket vleg (Y_v={Y_v:6.3f}, Z_v={Z_v:6.3f})")
