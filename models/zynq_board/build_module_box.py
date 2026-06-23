#!/usr/bin/env python3
"""
ZYNQ7000_10_20 core board (鹿小班 ZYNQ-7010/7020 核心板) — simplified digital-twin model.
BOUGHT board, NOT printed. Geometry parsed from the seller's KiCad source:
  /mnt/d/工程项目/硬件/pov/zynq/ZYNQ7000_10_20_core_v1.0_20221204_LE/.../ZYNQ7000_10_20_core.kicad_pcb

Local frame: PCB centred on XY origin, board occupies Z 0..1.6 (component/top side = +Z).
  - Top components (F.Cu) sit above the board (Z 1.6..).
  - The two board-to-board mezzanine connectors J1/J2 are on the BOTTOM (B.Cu) and
    hang DOWN to Z = -4.25 (this is the mating interface to a carrier board).
  - 4 x M2 mounting holes Φ2.2 at (±27, ±22); the top-right hole (H4) is 0.25 low
    (design quirk in the original board) -> kept exactly.

KiCad board centre = (80, 93.25); all positions below are board-local (centred).
"""
import math
from pathlib import Path
import numpy as np
import manifold3d as m3d

HERE = Path(__file__).parent
STL = HERE / "zynq_board.stl"

# --- board ---
BD_X, BD_Y, BD_T = 60.0, 50.0, 1.6      # 60 x 50, 1.6 thick (4-layer FR4)
CORNER_R = 2.0                           # rounded corners R2 (from Edge.Cuts arcs)

# --- mounting holes Φ2.2 (M2), board-local; H4 is 0.25 low ---
MH_D = 2.2
HOLES = [(-27.0, -22.0), (27.0, -22.0), (27.0, 21.75), (-27.0, 22.0)]

# --- top-side components (x, y, sx, sy, h) board-local, after rotation already applied ---
# big chips only (placeholder identification); heights from BGA lib names (..X160 = 1.6mm etc)
TOP_PARTS = [
    ("U5_ZYNQ",  3.20,  1.75, 17.0, 17.0, 1.60),   # XC7Z020 BGA400 17x17x1.6
    ("U6_DDR",  -9.35, -17.15, 13.0, 11.5, 0.80),   # BGA153 (ang90 -> 13x11.5)
    ("U10_DDR", -17.92, -4.04, 14.0,  8.0, 1.20),   # BGA96 (ang-90 -> 14x8)
    ("U11_DDR", -17.92,  7.38, 14.0,  8.0, 1.20),   # BGA96
    ("U7_FLASH",-20.00,-18.45,  5.3,  5.3, 1.00),   # W25Q256 SOP-8
    ("U8_QFN",   2.80, -17.80,  6.0,  6.0, 1.00),   # QFN40 6x6
]

# --- bottom-side board-to-board connectors J1/J2 (TE 5177983-4): 45.8 x 6 x 4.25, hang down ---
CON_X, CON_Y, CON_Z = 45.8, 6.0, 4.25
CONNS = [(0.0, -20.75), (0.0, 20.75)]


def rounded_plate(sx, sy, t, r):
    inner = m3d.CrossSection.square((sx - 2*r, sy - 2*r), center=True)
    prof = inner.offset(r, m3d.JoinType.Round, circular_segments=48)
    return prof.extrude(t)


def box(sx, sy, sz, cx, cy, z0):
    return m3d.Manifold.cube((sx, sy, sz), False).translate((cx - sx/2, cy - sy/2, z0))


def main():
    # board slab, Z 0..1.6
    part = rounded_plate(BD_X, BD_Y, BD_T, CORNER_R)

    # mounting holes
    for (hx, hy) in HOLES:
        h = m3d.Manifold.cylinder(BD_T + 2, MH_D/2, MH_D/2, 32, False).translate((hx, hy, -1.0))
        part = part - h

    # top components (Z 1.6 up)
    for (_n, x, y, sx, sy, h) in TOP_PARTS:
        part = part + box(sx, sy, h, x, y, BD_T)

    # bottom mezzanine connectors (Z 0 down to -4.25)
    for (x, y) in CONNS:
        part = part + box(CON_X, CON_Y, CON_Z, x, y, -CON_Z)

    # --- export binary STL ---
    mesh = part.to_mesh()
    verts = np.asarray(mesh.vert_properties[:, :3], dtype=np.float64)
    tris = np.asarray(mesh.tri_verts, dtype=np.int64)
    write_stl(STL, verts, tris, b"POV3D zynq_board")

    lo = verts.min(0); hi = verts.max(0)
    print(f"tris={len(tris)}  bbox X[{lo[0]:.1f},{hi[0]:.1f}] "
          f"Y[{lo[1]:.1f},{hi[1]:.1f}] Z[{lo[2]:.1f},{hi[2]:.1f}]  vol={part.volume()/1000:.1f} cm3")


def write_stl(path, verts, tris, header):
    n = len(tris)
    tv = verts[tris]                          # (n,3,3)
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
    assert 84 + n * 50 == path.stat().st_size, "STL size mismatch (header > 80 bytes?)"


if __name__ == "__main__":
    main()
