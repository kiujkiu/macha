#!/usr/bin/env python3
"""
ZYNQ board (鹿小班 ZYNQ-7010/7020, the INTEGRATED board the user physically has)
— mechanical digital twin reconstructed from the product PHOTO.

NOTE: this is a DIFFERENT board from the seller's `ZYNQ7000_10_20_core` KiCad
(that one is a 60×50 SoM with bottom mezzanine connectors and NO 2.54 headers /
RJ45 / HDMI).  The KiCad-based detailed model is kept as build_module_coremodule.py.

Everything here is dimensioned off the photo using the 2.54 mm pin-header pitch
as the scale reference (measured 48 px = 2.54 mm  ->  18.9 px/mm).
ACCURATE features (per user): board outline, 4 corner through-holes, the two
2.54 mm dual-row pin headers.  Other parts are rough placeholders.

Frame: board centred on XY origin, +X = photo-right, +Y = photo-up,
Z 0..1.6 = FR4, parts/pins grow +Z (component side up).
"""
import math
from pathlib import Path
import numpy as np
import manifold3d as m3d

HERE = Path(__file__).parent
STL = HERE / "zynq_board.stl"
PNG = HERE / "zynq_board_preview.png"

# ---- board (mm): user-MEASURED 82 × 52 (calipers, 2026-06-17) ------------
# Cross-check: the angled photo gave 85×52 (≈4% long, edge-shadow); the labelled
# product render gave 62×40 (badly compressed — NOT to scale).  Photo trusted,
# rescaled to the measured 82.  Width 52 was exact in the photo.
BOARD_W, BOARD_H, BOARD_T = 52.0, 82.0, 1.6
CORNER_R = 3.0
PITCH = 2.54

# 4 corner mounting holes (centred frame).  M3 Φ3.2 (user-confirmed).
# Hole rectangle 75 × 44.6 mm measured off the 200-DPI scan (inset ~3.5 mm,
# symmetric).  Long axis = Y here, short = X.
HOLE_D = 3.2
HOLES = [(-22.3,  37.5), (22.3,  37.5),          # top L / R
         (-22.3, -37.5), (22.3, -37.5)]          # bottom L / R
# KEEP-OUT (user req): leave Φ7 clear around every M3 hole on BOTH faces — no
# mount/standoff/bracket geometry may intrude (screw head + tool access).
KEEPOUT_D = 7.0

# 2.54 dual-row pin headers, 2×20 each.  From the 200-DPI scan: outer row sits
# right at the board edge (inner row 2.54 mm in); the 48.3 mm pin field is
# shifted ~3 mm off board centre toward the JTAG/button end (−Y here).
# pins point UP out of the component side.
_OUTER = BOARD_W/2 - 1.5          # 24.5  (outer row ~1.5 mm from edge)
_YCEN = -3.0                      # field centre offset toward JTAG end
_YTOP = _YCEN + (20-1)*PITCH/2    # 21.1
HEADERS = {
    "GPIO2 (left)":  dict(cols=[-_OUTER, -(_OUTER - PITCH)], y_top=_YTOP, n=20),
    "GPIO1 (right)": dict(cols=[ _OUTER,  (_OUTER - PITCH)], y_top=_YTOP, n=20),
}

# JTAG 2×7 shrouded box header, bottom-centre (approx)
JTAG = dict(center=(4.5, -35.5), nx=7, ny=2)

# rough component placeholders (centre x, y, size x, y, z) — NOT accurate.
# Kept clear of every M3 hole's Φ7 keep-out (see clearance check in main()).
PARTS = [
    ("ZYNQ",   0.0,   3.0, 17.0, 17.0, 1.6),
    ("DDR_a",  0.0, -11.0, 13.0,  8.0, 1.2),
    ("DDR_b",-13.0,   4.0,  8.0, 13.0, 1.2),
    ("RJ45",  -8.0,  26.0, 16.0, 21.0, 14.0),
    ("HDMI",   9.0,  25.0, 15.0, 12.0,  6.5),
    ("USB",   -9.0, -30.0,  8.0,  6.0,  3.0),
]


def rounded_plate(w, h, t, r):
    inner = m3d.CrossSection.square((w - 2*r, h - 2*r), center=True)
    return inner.offset(r, m3d.JoinType.Round, circular_segments=48).extrude(t)


def box(sx, sy, sz, cx, cy, z0):
    return m3d.Manifold.cube((sx, sy, sz), False).translate((cx - sx/2, cy - sy/2, z0))


# Pin headers are soldered on the BOTTOM face (user): plastic body sits under
# the board, pins point DOWN to mate below; a short tail pokes up through.
HDR_PLASTIC = 2.54
HDR_PIN_DOWN = 6.0          # mating pin length below the plastic
def pin(cx, cy):
    s = 0.64
    z_bot = -(HDR_PLASTIC + HDR_PIN_DOWN)    # -8.54
    z_top = 1.0                               # solder tail proud of the top face
    return m3d.Manifold.cube((s, s, z_top - z_bot), False).translate((cx - s/2, cy - s/2, z_bot))


def header(cols, y_top, n):
    body = None
    for cx in cols:
        # plastic strip per row, hung UNDER the board (Z -HDR_PLASTIC .. 0)
        strip = box(2.54, (n-1)*PITCH + 2.54, HDR_PLASTIC, cx,
                    y_top - (n-1)*PITCH/2, -HDR_PLASTIC)
        body = strip if body is None else body + strip
        for k in range(n):
            body = body + pin(cx, y_top - k*PITCH)
    return body


def jtag(center, nx, ny, top_z=BOARD_T):
    cx, cy = center
    spanx, spany = (nx-1)*PITCH, (ny-1)*PITCH
    shroud_w, shroud_h, shroud_z = spanx + 5.0, spany + 5.0, 9.0
    body = box(shroud_w, shroud_h, shroud_z, cx, cy, top_z)               # outer shroud
    cav = box(spanx + 1.5, spany + 1.5, shroud_z, cx, cy, top_z + 2.0)    # hollow
    body = body - cav
    for ix in range(nx):
        for iy in range(ny):
            px = cx - spanx/2 + ix*PITCH
            py = cy - spany/2 + iy*PITCH
            body = body + box(0.64, 0.64, 6.0, px, py, top_z + 1.0)
    return body


def check_keepout():
    """Assert every placeholder block + JTAG clears each hole's Φ7 keep-out.
    dist = centre-to-nearest-edge of the axis-aligned block."""
    R = KEEPOUT_D / 2.0
    boxes = [(n, x, y, sx, sy) for (n, x, y, sx, sy, _h) in PARTS]
    jw = (JTAG["nx"]-1)*PITCH + 5.0; jh = (JTAG["ny"]-1)*PITCH + 5.0
    boxes.append(("JTAG", JTAG["center"][0], JTAG["center"][1], jw, jh))
    worst = None
    for (n, x, y, sx, sy) in boxes:
        for (hx, hy) in HOLES:
            dx = max(abs(hx - x) - sx/2, 0.0)
            dy = max(abs(hy - y) - sy/2, 0.0)
            d = math.hypot(dx, dy)
            if worst is None or d < worst[0]:
                worst = (d, n, hx, hy)
            if d < R:
                raise SystemExit(f"KEEP-OUT VIOLATION: {n} only {d:.2f} mm from "
                                 f"hole ({hx},{hy}) — need ≥ {R} mm")
    print(f"Φ7 keep-out OK — tightest: {worst[1]} {worst[0]:.2f} mm to hole "
          f"({worst[2]},{worst[3]}) (need ≥ {R})")


def main():
    check_keepout()
    part = rounded_plate(BOARD_W, BOARD_H, BOARD_T, CORNER_R)
    for (hx, hy) in HOLES:
        h = m3d.Manifold.cylinder(BOARD_T + 2, HOLE_D/2, HOLE_D/2, 48, False).translate((hx, hy, -1))
        part = part - h

    for name, hd in HEADERS.items():
        part = part + header(hd["cols"], hd["y_top"], hd["n"])

    part = part + jtag(**JTAG)

    for (_n, x, y, sx, sy, h) in PARTS:
        part = part + box(sx, sy, h, x, y, BOARD_T)

    mesh = part.to_mesh()
    verts = np.asarray(mesh.vert_properties[:, :3], dtype=np.float64)
    tris = np.asarray(mesh.tri_verts, dtype=np.int64)
    write_stl(STL, verts, tris, b"POV3D zynq_board photo")
    lo, hi = verts.min(0), verts.max(0)
    print(f"tris={len(tris)}  bbox X[{lo[0]:.1f},{hi[0]:.1f}] "
          f"Y[{lo[1]:.1f},{hi[1]:.1f}] Z[{lo[2]:.2f},{hi[2]:.2f}]")
    for name, hd in HEADERS.items():
        print(f"  {name}: 2x{hd['n']} @2.54, cols X={hd['cols']}")
    render(verts, tris)


def write_stl(path, verts, tris, header):
    n = len(tris); tv = verts[tris]
    a, b = tv[:, 1] - tv[:, 0], tv[:, 2] - tv[:, 0]
    nrm = np.cross(a, b); ln = np.linalg.norm(nrm, axis=1, keepdims=True)
    nrm = np.divide(nrm, ln, out=np.zeros_like(nrm), where=ln != 0)
    with open(path, "wb") as f:
        f.write(header.ljust(80, b" ")[:80]); f.write(np.uint32(n).tobytes())
        buf = bytearray()
        for i in range(n):
            buf += nrm[i].astype("<f4").tobytes()
            buf += tv[i].astype("<f4").tobytes(); buf += b"\x00\x00"
        f.write(buf)
    assert 84 + n*50 == path.stat().st_size


def render(verts, tris):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    tv = verts[tris]
    th = np.linspace(0, 2*np.pi, 48)
    fig = plt.figure(figsize=(13, 6))
    for i, (e, a, t) in enumerate([(90, -90, "top (+Z), Φ7 keep-out"), (28, -60, "iso (headers down)")]):
        ax = fig.add_subplot(1, 2, i+1, projection="3d")
        ax.add_collection3d(Poly3DCollection(tv, facecolor="#2f7d32", edgecolor="none", alpha=0.97))
        for (hx, hy) in HOLES:                       # Φ7 keep-out rings
            ax.plot(hx + KEEPOUT_D/2*np.cos(th), hy + KEEPOUT_D/2*np.sin(th),
                    BOARD_T + 0.2, color="red", lw=1.3)
        ax.set_xlim(-30, 30); ax.set_ylim(-45, 45); ax.set_zlim(-10, 16)
        ax.set_box_aspect((60, 90, 26)); ax.view_init(elev=e, azim=a)
        ax.set_title(t); ax.set_xlabel("X"); ax.set_ylabel("Y")
    fig.tight_layout(); fig.savefig(PNG, dpi=110)
    print(f"wrote {PNG}")


if __name__ == "__main__":
    main()
