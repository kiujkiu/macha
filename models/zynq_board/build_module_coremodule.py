#!/usr/bin/env python3
"""
ZYNQ7000_10_20 core board (鹿小班 ZYNQ-7010/7020 核心板) — DETAILED digital twin.
BOUGHT board, NOT printed.  Real component geometry is loaded from the seller's
own STEP models and placed exactly as the KiCad PCB positions them:
  src PCB : .../ZYNQ7000_10_20_core/ZYNQ7000_10_20_core.kicad_pcb
  src 3D  : .../ZYNQ7000_10_20_core/3D/*.stp

Output frame  (matches KiCad's 3-D viewer = right-handed, recentred on the
board centre (80, 93.25) of the KiCad sheet):
  • X right, Y up, Z up.
  • board bottom = Z 0, board top (F.Cu) = Z 1.6.
  • top-side parts sit on Z 1.6 and grow +Z.
  • the two bottom-side mezzanine connectors J1/J2 hang DOWN to Z ≈ -3.75
    (this is the board-to-board mating interface to a carrier).

Only the 17 components that ship with a real local STEP model are placed
(the big silicon + connectors + power inductors); 0402/0603 passives are
omitted — they carry no meaningful height for a fit-check twin.

A box-only earlier version is kept as build_module_box.py.
This file writes the SAME output path (zynq_board.stl) as a drop-in upgrade.
"""
import re
import math
from pathlib import Path
import numpy as np
import cadquery as cq

HERE = Path(__file__).parent
STL = HERE / "zynq_board.stl"
PNG = HERE / "zynq_board_preview.png"

PCB = Path("/mnt/d/工程项目/硬件/pov/zynq/ZYNQ7000_10_20_core_v1.0_20221204_LE/"
           "ZYNQ7000_10_20_core/ZYNQ7000_10_20_core.kicad_pcb")
MODEL_DIR = PCB.parent / "3D"

CX, CY = 80.0, 93.25          # KiCad board centre
BD_T = 1.6                    # FR4 thickness; bottom Z 0, top Z BD_T
TESS = 0.1                    # tessellation tolerance (mm)
# Some seller STEP models are pathologically dense (the BGA packages model
# every solder ball -> 0.8..3.2 M triangles each, all hidden UNDER the chip
# against the board).  Any component whose mesh exceeds this many triangles is
# replaced by its package bounding box (visually identical from outside).
BOX_THRESH = 60_000


# ---------------------------------------------------------------- KiCad parse
def footprint_blocks(s, key="(footprint "):
    out, i = [], 0
    while True:
        j = s.find(key, i)
        if j < 0:
            break
        depth, k = 0, j
        while k < len(s):
            c = s[k]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    break
            k += 1
        out.append(s[j:k + 1])
        i = k + 1
    return out


def parse_components(txt):
    """Return list of dicts for footprints carrying a ${KIPRJMOD}/3D STEP model."""
    comps = []
    for b in footprint_blocks(txt):
        layer = re.search(r'\(layer "([^"]+)"', b).group(1)
        at = re.search(r'\n\s*\(at ([\-0-9.]+) ([\-0-9.]+)(?:\s+([\-0-9.]+))?\)', b)
        px, py = float(at.group(1)), float(at.group(2))
        rot = float(at.group(3)) if at.group(3) else 0.0
        ref_m = re.search(r'\(fp_text reference "([^"]+)"', b)
        ref = ref_m.group(1) if ref_m else "?"
        mdl = re.search(
            r'\(model "([^"]+)"\s*\n\s*\(offset \(xyz ([\-0-9. ]+)\)\)'
            r'\s*\n\s*\(scale \(xyz ([\-0-9. ]+)\)\)'
            r'\s*\n\s*\(rotate \(xyz ([\-0-9. ]+)\)\)', b)
        if not (mdl and 'KIPRJMOD' in mdl.group(1)):
            continue
        off = [float(v) for v in mdl.group(2).split()]
        scl = [float(v) for v in mdl.group(3).split()]
        mrot = [float(v) for v in mdl.group(4).split()]
        comps.append(dict(ref=ref, layer=layer, px=px, py=py, rot=rot,
                          model=mdl.group(1).split('/')[-1],
                          off=off, scale=scl, mrot=mrot))
    return comps


def parse_mounting_holes(txt):
    holes = []
    for b in footprint_blocks(txt):
        name = re.search(r'\(footprint "([^"]+)"', b).group(1)
        if "MountingHole" not in name:
            continue
        at = re.search(r'\n\s*\(at ([\-0-9.]+) ([\-0-9.]+)', b)
        d = re.search(r'(\d\.\d)mm', name)
        dia = float(d.group(1)) if d else 2.2
        holes.append((float(at.group(1)), float(at.group(2)), dia))
    return holes


# ---------------------------------------------------------------- geometry
def rot_mat(rx, ry, rz):
    """KiCad model rotation: negate angles, apply Rz·Ry·Rx (X first)."""
    rx, ry, rz = (math.radians(-a) for a in (rx, ry, rz))
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def rz(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def box_mesh(lo, hi):
    """12-triangle axis-aligned box spanning lo..hi (each length 3)."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                  [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]],
                 dtype=np.float64)
    t = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7],
                  [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5],
                  [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]], dtype=np.int64)
    return v, t


_cache = {}
def load_mesh(fname):
    """Tessellate a STEP once -> (verts Nx3 float64, tris Mx3 int, boxed:bool).
    Pathologically dense models (BGA ball arrays) collapse to a package box."""
    if fname in _cache:
        return _cache[fname]
    shp = cq.importers.importStep(str(MODEL_DIR / fname)).val()
    vtx, tri = shp.tessellate(TESS)
    verts = np.array([[v.x, v.y, v.z] for v in vtx], dtype=np.float64)
    tris = np.array(tri, dtype=np.int64)
    boxed = len(tris) > BOX_THRESH
    if boxed:
        verts, tris = box_mesh(verts.min(0), verts.max(0))
    _cache[fname] = (verts, tris, boxed)
    return verts, tris, boxed


def place_component(c):
    """Return world-frame (verts, tris, boxed) for one component."""
    verts, tris, boxed = load_mesh(c["model"])
    v = verts.copy()
    v *= np.array(c["scale"])                       # model scale
    v = v @ rot_mat(*c["mrot"]).T                   # model rotate
    v += np.array(c["off"])                         # model offset (mm)

    if c["layer"] == "B.Cu":                        # bottom: flip 180° about X
        v[:, 1] *= -1.0
        v[:, 2] *= -1.0
        v = v @ rz(c["rot"]).T                       # footprint rotation
        v[:, 2] += 0.0                               # contact plane = board bottom Z0
        flip = True
    else:                                            # top: sits on board top
        v = v @ rz(c["rot"]).T
        v[:, 2] += BD_T
        flip = False

    # in-plane placement (board Y-down -> world Y-up)
    v[:, 0] += c["px"] - CX
    v[:, 1] += CY - c["py"]

    if flip:                                         # restore winding after mirror
        tris = tris[:, ::-1]
    return v, tris, boxed


def board_slab(holes):
    """Rounded-rect FR4 slab (60×50, R2) minus the mounting holes."""
    slab = (cq.Workplane("XY")
            .box(60.0, 50.0, BD_T, centered=(True, True, False))
            .edges("|Z").fillet(2.0))
    for (px, py, dia) in holes:
        slab = (slab.faces(">Z").workplane(origin=(px - CX, CY - py, 0))
                .circle(dia / 2).cutThruAll())
    v, t = slab.val().tessellate(TESS)
    return (np.array([[p.x, p.y, p.z] for p in v]), np.array(t, dtype=np.int64))


# ---------------------------------------------------------------- STL writer
def write_stl(path, blocks, header=b"POV3D zynq_board detailed"):
    tri_list = []
    for verts, tris in blocks:
        tri_list.append(verts[tris])                 # (n,3,3)
    tv = np.concatenate(tri_list, axis=0)
    n = len(tv)
    a = tv[:, 1] - tv[:, 0]
    b = tv[:, 2] - tv[:, 0]
    nrm = np.cross(a, b)
    ln = np.linalg.norm(nrm, axis=1, keepdims=True)
    nrm = np.divide(nrm, ln, out=np.zeros_like(nrm), where=ln != 0)
    with open(path, "wb") as f:
        f.write(header.ljust(80, b" ")[:80])
        f.write(np.uint32(n).tobytes())
        buf = bytearray()
        for i in range(n):
            buf += nrm[i].astype("<f4").tobytes()
            buf += tv[i].astype("<f4").tobytes()
            buf += b"\x00\x00"
        f.write(buf)
    assert 84 + n * 50 == path.stat().st_size, "STL size mismatch"
    return n, tv


# ---------------------------------------------------------------- main
def main():
    txt = PCB.read_text()
    comps = parse_components(txt)
    holes = parse_mounting_holes(txt)
    print(f"components with STEP: {len(comps)}   mounting holes: {len(holes)}")

    blocks = [board_slab(holes)]
    for c in sorted(comps, key=lambda x: x["ref"]):
        v, t, boxed = place_component(c)
        blocks.append((v, t))
        lo, hi = v.min(0), v.max(0)
        print(f"  {c['ref']:4} {c['model']:24} {c['layer']:5} "
              f"X[{lo[0]:6.1f},{hi[0]:6.1f}] Y[{lo[1]:6.1f},{hi[1]:6.1f}] "
              f"Z[{lo[2]:6.2f},{hi[2]:6.2f}] {len(t):>7}t"
              f"{'  [BOX]' if boxed else ''}")

    n, tv = write_stl(STL, blocks)
    allv = tv.reshape(-1, 3)
    lo, hi = allv.min(0), allv.max(0)
    print(f"\nwrote {STL}  ({n} tris)")
    print(f"bbox  X[{lo[0]:.1f},{hi[0]:.1f}] Y[{lo[1]:.1f},{hi[1]:.1f}] "
          f"Z[{lo[2]:.2f},{hi[2]:.2f}]")
    render(blocks)


def render(blocks):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    fig = plt.figure(figsize=(15, 6))
    for i, (elev, azim, title) in enumerate(
            [(32, -60, "iso (top)"), (90, -90, "top (+Z)"), (-12, -90, "edge / bottom")]):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        for k, (verts, tris) in enumerate(blocks):
            col = "#2f7d32" if k == 0 else "#bbbbbb"
            pc = Poly3DCollection(verts[tris], facecolor=col,
                                  edgecolor="none", alpha=0.95)
            ax.add_collection3d(pc)
        ax.set_xlim(-32, 32); ax.set_ylim(-27, 27); ax.set_zlim(-8, 8)
        ax.set_box_aspect((64, 54, 16))
        ax.view_init(elev=elev, azim=azim)
        ax.set_title(title); ax.set_xlabel("X"); ax.set_ylabel("Y")
    fig.tight_layout()
    fig.savefig(PNG, dpi=110)
    print(f"wrote {PNG}")


if __name__ == "__main__":
    main()
