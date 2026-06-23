"""
Photo-interrupter MODULE model (the actual PCB component, for stacking) —
"宽体对射式计数模块 / LM393, 槽宽10mm".

NOT a printed part — the bought component, modelled so it can be placed in
assembly_stack.py and cradled by sensor_mount.

CORRECT topology (fixed 2026-06-15 per user): the PCB lies FLAT; the slotted
optocoupler STANDS UP perpendicular to the board (slot opening faces +Z, away
from the board); the 3-pin header is on one board EDGE. The slot's through-
channel is horizontal (±Y, parallel to the board, well above the board top so
a thin vane passes clear of the PCB).

Local frame: origin = PCB centre on its bottom face.
  X = board width (23),  Y = board depth (20),  Z = up (board thickness 1.4).
  optocoupler at the +Y (back) edge, arms split along X (10 mm gap), slot
  opens +Z, through-channel ±Y.

Dims: PCB 23×20×1.4 (confirmed); fork 16.3 tall, slot 10w×13d, arms 4 wide,
fork depth (Y) 6.  [ARM_W / FORK_DY / hole / header read from the drawing —
adjust if the real part differs.]
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

PCB_W, PCB_D, PCB_T = 20.0, 23.0, 1.4        # X (along fork/slot) , Y (depth) , Z
FORK_H, ARM_W, SLOT_W, SLOT_D = 16.3, 4.0, 10.0, 13.0
FORK_DY = 6.0                                # opto depth along Y
FORK_Y0 = PCB_D - FORK_DY                    # opto footprint at the back edge (Y17..23)
BASE_H  = FORK_H - SLOT_D                     # 3.3 closed base
HOLE_D  = 3.2                                 # 2× M3 through-holes
CORNER  = 3.0                                 # hole centre 3mm from nearest corner (x & y)
HOLES   = [(-(PCB_W/2 - CORNER), CORNER), (PCB_W/2 - CORNER, CORNER)]   # (±7, 3) front corners
PIN_D, PIN_L, PIN_PITCH = 0.7, 8.0, 2.54     # header centred between the holes


def box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))

# PCB (flat), 2× M3 mount holes through Z at the front corners
part = box(-PCB_W/2, PCB_W/2, 0.0, PCB_D, 0.0, PCB_T)
for (hx, hy) in HOLES:
    part = part - m3d.Manifold.cylinder(PCB_T + 2, HOLE_D/2, HOLE_D/2, 32, False)\
        .translate((hx, hy, -1.0))

# optocoupler STANDS UP perpendicular to the board (slot opens +Z, through ±Y)
opto = box(-(SLOT_W/2 + ARM_W), (SLOT_W/2 + ARM_W), FORK_Y0, PCB_D,
           PCB_T, PCB_T + FORK_H)
slot = box(-SLOT_W/2, SLOT_W/2, FORK_Y0 - 1, PCB_D + 1,
           PCB_T + BASE_H, PCB_T + FORK_H + 1)          # open +Z + through ±Y
opto = opto - slot
part = part + opto
# emitter/detector ridges on the inner arm faces (cosmetic beam markers)
for sx in (-SLOT_W/2, SLOT_W/2 - 0.6):
    part = part + box(sx, sx + 0.6, FORK_Y0 + 1.5, PCB_D - 1.5,
                      PCB_T + BASE_H + 2.0, PCB_T + BASE_H + 4.0)

# components on the board top (LM393 + trimpot), in the mid area
part = part + box(-6.0, 1.0, 8.0, 13.0, PCB_T, PCB_T + 2.0)    # chip
part = part + box(2.5, 7.5, 8.0, 13.0, PCB_T, PCB_T + 3.5)     # blue trimpot

# 3-pin header CENTRED between the 2 holes, pins out -Y. Moved 1mm INWARD
# (+Y) per user — base set back from the edge, pins protrude 1mm less.
HDR_X = [-PIN_PITCH, 0.0, PIN_PITCH]
HDR_Y = 1.0                                   # header inward offset (+Y)
part = part + box(HDR_X[0] - 1.3, HDR_X[-1] + 1.3, HDR_Y - 1.0, HDR_Y + 1.5,
                  PCB_T, PCB_T + 2.5)         # housing
for hx in HDR_X:
    pin = m3d.Manifold.cylinder(PIN_L, PIN_D/2, PIN_D/2, 12, False).rotate((-90, 0, 0))
    part = part + pin.translate((hx, HDR_Y - PIN_L, PCB_T + 1.0))

# SOLDER LEADS protruding the BACK (-Z) face: 1.5 long × Φ1 (soldered part).
# 4 opto legs under the arms + 3 header tails — the bracket MUST clear these
# (hold the PCB ≥1.5 off the backing or recess these spots).
LEAD_L, LEAD_D = 1.5, 1.0
BACK_LEADS = [(-7.0, 19.0), (-7.0, 21.5), (7.0, 19.0), (7.0, 21.5)] \
           + [(hx, HDR_Y + 0.8) for hx in HDR_X]
for (px, py) in BACK_LEADS:
    lead = m3d.Manifold.cylinder(LEAD_L, LEAD_D/2, LEAD_D/2, 12, False)
    part = part + lead.translate((px, py, -LEAD_L))

# ---- export ----
mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("sensor_module.stl")
with out.open("wb") as f:
    f.write(b"POV3D sensor_module".ljust(80, b" "))
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
print(f"sensor_module.stl  {len(tris)} tris  "
      f"X {v[:,0].min():.2f}..{v[:,0].max():.2f}  "
      f"Y {v[:,1].min():.2f}..{v[:,1].max():.2f}  "
      f"Z {v[:,2].min():.2f}..{v[:,2].max():.2f}  vol {part.volume()/1000:.2f}cm³")
print(f"PCB flat {PCB_W}(X,叉向)×{PCB_D}(Y,深)×{PCB_T}; opto stands UP +Z (slot +Z, through ±Y); "
      f"2×M3 Φ{HOLE_D} @ corners (±{PCB_W/2-CORNER:g},{CORNER:g}); header centred between them, pins -Y")
