"""
index_vane — the STATIC light-blocking flag that mates with the rotor's
photo-interrupter. Bolts to the metal breadboard (洞洞板) with M6.

Built in the ASSEMBLY frame (θ=180, −X side). The rotor sensor sweeps past
once per rev; the blade sits in the slot's path so its beam (radial, at
(−105, 0, 25.7)) is blocked at exactly θ=180.

  • foot: a 5 mm plate on the breadboard, 2× Φ6.5 M6 clearance holes on the
    25 mm grid at (−112.5, ±12.5) (straddle Y0, fix orientation).
  • blade: rises into the fork slot gap (R100..110), crossing the beam.
    Lower part (below the slot, Z<16) is 8 mm thick for stiffness; the part
    INSIDE the slot (Z16..28) is 4 mm thick (the pulse width) so it sweeps
    cleanly through the slot's ±Y through-channel (opto depth ≈6 mm).

The breadboard M6 holes are tapped; the M6 screw heads sit on the foot top
(Z5), well clear of the rotor module above (Z≥16).
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

BEAM = (-112.0, 0.0, 38.7)
FOOT_Z = 5.0
M6_GRID = [(-112.5, 12.5), (-112.5, -12.5)]   # breadboard grid (still under R112 index)
M6_CLEAR = 6.5
# blade reshaped per user: NARROW radial (left-right), LONG tangential (up-down).
# Radial 4mm (R103..107) → 3mm clearance to each arm (R100/R110); tangential
# long for blocking area/stiffness. The broad face is ⊥ the radial beam.
BLADE_X0, BLADE_X1 = -114.0, -110.0            # 4mm radial, centred R112
SLOT_BOT = 29.0                                # module slot mouth (raised: plate on disc top)
BLADE_TOP = 40.0                               # > beam 38.7, < slot base 42
LOW_HALF, UP_HALF = 5.0, 4.0                   # tangential half-thickness (below 10 / in slot 8)


def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))

def zcyl(z0, z1, r, x, y, seg=32):
    return m3d.Manifold.cylinder(z1-z0, r, r, seg, False).translate((x, y, z0))

# foot
vane = box(-119.0, -99.0, -18.0, 18.0, 0.0, FOOT_Z)
for (x, y) in M6_GRID:
    vane = vane - zcyl(-1, FOOT_Z + 1, M6_CLEAR/2, x, y)
# blade: stout lower part (Z4..16) + thin upper part in the slot (Z16..28)
vane = vane + box(BLADE_X0, BLADE_X1, -LOW_HALF, LOW_HALF, FOOT_Z - 1, SLOT_BOT)
vane = vane + box(BLADE_X0, BLADE_X1, -UP_HALF, UP_HALF, SLOT_BOT, BLADE_TOP)

# ---- export ----
mesh = vane.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("index_vane.stl")
with out.open("wb") as f:
    f.write(b"POV3D index_vane".ljust(80, b" "))
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1 - v0, v2 - v0); L = float(np.linalg.norm(n))
        if L > 0: n = n / L
        f.write(struct.pack("<3f", *n)); f.write(struct.pack("<3f", *v0))
        f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(tris)*50 == out.stat().st_size
v = verts
print(f"index_vane.stl  {len(tris)} tris  X {v[:,0].min():.2f}..{v[:,0].max():.2f}  "
      f"Y {v[:,1].min():.2f}..{v[:,1].max():.2f}  Z {v[:,2].min():.2f}..{v[:,2].max():.2f}  "
      f"vol {vane.volume()/1000:.2f}cm³")
print(f"foot 2×M6 @ {M6_GRID}; blade X[{BLADE_X1:g},{BLADE_X0:g}] (narrow radial) × "
      f"tang {2*UP_HALF:g} to Z{BLADE_TOP} crosses beam Z{BEAM[2]}")
