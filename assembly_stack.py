"""
Stack the POV3D parts into one assembly STL for visual inspection.

Assembly frame = rim_ring build frame (center at origin, Z up):
  • rim_ring        — as built, Z = 0 .. 9 (base annulus 0..3.5, wall to 9)
  • hub_disc        — FLIPPED upside down (180° about X: (x,y,z)→(x,−y,9−z))
    and nested INSIDE the ring, Z = 0 .. 9:
      Φ60 upper boss drops into the ring's ID60 bore (flush at Z = 0),
      Φ80 boss + Φ145-165 rim boss rest on the ring base top (Z = 3.5),
      Φ165 base fits inside the ring wall ID165, flush at Z = 9.
    The hub rim-boss cutout (0°..5°, mirrored to −5°..0° by the flip)
    aligns with the ring wall cutout at −5°..0° — they interlock.
  • rim_top_disc    — +9 (rests on ring wall top AND hub base, both at 9;
    disc 9 .. 15, ribs to 45)
  • l_bracket_170x60 — print frame rotated -90° about Y, then placed:
        (x, y, z)_print  →  (-z - 14.3,  y - 45,  x + 15)
    vleg flat on the disc top (Z = 15 .. 19), hleg fin vertical at
    X = -18.3 .. -14.3, clamped between the disc ribs.
  • pi2hub75e PCB (placeholder plate 82 × 62 × 1.6 with the 6 Φ3.3 holes)
    resting on the 6 boss tops at Z = 18 .. 19.6.
hub + ring + disc share the 16 × M3 pattern (PCD Φ70 + Φ155, 22.5° + k·45°,
self-symmetric about X so the flip keeps it aligned) — screw holes line up.

Output: assembly_stack.stl (+ assembly_stack_preview.png isometric render).
NOT printable — for fit checking only.
"""
import math
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

ROOT = Path(__file__).parent

STL_TRI = np.dtype([
    ("normal", "<f4", 3), ("verts", "<f4", (3, 3)), ("attr", "<u2"),
])

def read_stl(path):
    raw = path.read_bytes()
    n = struct.unpack_from("<I", raw, 80)[0]
    tris = np.frombuffer(raw, dtype=STL_TRI, count=n, offset=84)
    return tris["verts"].astype(np.float64)        # (n, 3, 3)

# ===== load + transform =====
# STATOR group (Z 0..28): baseplate + ring_collar + flange_disc +
# flipped mounting_flange. The baseplate boss (OD65/ID55, Z 5..28) carries:
# collar (5..18, rotated +75° so its 0-30° notch aligns with the boss
# 75-105° notch), flange_disc (18..25), flipped mounting_flange (wall 18..25
# wrapping the flange OD165, base 25..28). Boss top flush at Z=28.
# ROTOR group (hub+ring+disc+bracket+PCB) at Z = 31.7: the motor (Φ50 ×
# 26.7) stands on the baseplate top (Z=5) inside the boss bore (ID55);
# its rotor face at Z=31.7 bolts to the hub's 4 diamond holes. This leaves
# a 3.7 mm axial air gap between the stator top (28) and the rotor bottom.
MOTOR_D, MOTOR_H, MOTOR_Z0 = 50.0, 26.7, 5.0
ROTOR_Z0 = MOTOR_Z0 + MOTOR_H   # 31.7
DISC_Z0 = ROTOR_Z0 + 9.0         # disc on ring wall top / hub base top
VLEG_Z0 = DISC_Z0 + 6.0          # vleg on disc top
parts = []

# metal breadboard (洞洞板) placeholder: 300 × 300 × 12, top face at Z=0,
# 12 × 12 M6 (Φ6) holes on a 25 mm grid (spans ±137.5). The baseplate's
# 4 × M6 (75 × 75 = 3 grid pitches) bolt onto it, centered.
BB_T = 12.0
bb = m3d.Manifold.cube((300.0, 300.0, BB_T), False).translate((-150.0, -150.0, -BB_T))
for i in range(12):
    for j in range(12):
        bx, by = -137.5 + 25.0*i, -137.5 + 25.0*j
        h = m3d.Manifold.cylinder(BB_T + 2, 3.0, 3.0, 16, False)
        bb = bb - h.translate((bx, by, -BB_T - 1.0))
_bm = bb.to_mesh()
_bv = np.asarray(_bm.vert_properties)[:, :3]
_bt = np.asarray(_bm.tri_verts)
parts.append(("breadboard (placeholder)", _bv[_bt]))

# 4 corner standoff posts: Φ8 × 400 mm, M6 stud ends screwed into the
# breadboard's 4 corner holes (±137.5, ±137.5), standing up from Z = 0.
for px in (-137.5, 137.5):
    for py in (-137.5, 137.5):
        post = m3d.Manifold.cylinder(400.0, 4.0, 4.0, 24, False)
        post = post.translate((px, py, 0.0))
        _pm = post.to_mesh()
        _pv = np.asarray(_pm.vert_properties)[:, :3]
        _pt = np.asarray(_pm.tri_verts)
        parts.append((f"post @({px:+.0f},{py:+.0f})", _pv[_pt]))

# baseplate — as is
base = read_stl(ROOT / "models/baseplate/baseplate.stl")
parts.append(("baseplate", base))

# ring_collar — +5 Z, rotated +75° about Z (notch 0-30° → 75-105°)
col = read_stl(ROOT / "models/ring_collar/ring_collar.stl")
c75, s75 = math.cos(math.radians(75)), math.sin(math.radians(75))
cx, cy = col[..., 0].copy(), col[..., 1].copy()
col[..., 0] = c75 * cx - s75 * cy
col[..., 1] = s75 * cx + c75 * cy
col[..., 2] += 5.0
parts.append(("ring_collar", col))

# flange_disc — +18 Z, upright
fd = read_stl(ROOT / "models/flange_disc/flange_disc.stl")
fd = fd + np.array([0.0, 0.0, 18.0])
parts.append(("flange_disc", fd))

# mounting_flange — flipped 180° about X, capping the flange_disc (18..28)
mf = read_stl(ROOT / "models/mounting_flange/mounting_flange.stl")
mf[..., 1] = -mf[..., 1]
mf[..., 2] = 28.0 - mf[..., 2]
mf = mf[:, ::-1, :].copy()
parts.append(("mounting_flange", mf))

# rim_ring — rotor group bottom
ring = read_stl(ROOT / "models/rim_ring/rim_ring.stl")
ring = ring + np.array([0.0, 0.0, ROTOR_Z0])
parts.append(("rim_ring", ring))

# hub_disc — flipped 180° about X, nested inside the ring (Z 0..9).
# Flip reverses triangle winding; swap two vertices to restore orientation.
hub = read_stl(ROOT / "models/hub_disc/hub_disc.stl")
hub[..., 1] = -hub[..., 1]
hub[..., 2] = ROTOR_Z0 + 9.0 - hub[..., 2]
hub = hub[:, ::-1, :].copy()
parts.append(("hub_disc", hub))

# rim_top_disc — +9 Z
disc = read_stl(ROOT / "models/rim_top_disc/rim_top_disc.stl")
disc = disc + np.array([0.0, 0.0, DISC_Z0])
parts.append(("rim_top_disc", disc))

# l_bracket — rotate -90° about Y then translate
br = read_stl(ROOT / "models/l_bracket_170x60/l_bracket_170x60.stl")
x, y, z = br[..., 0].copy(), br[..., 1].copy(), br[..., 2].copy()
br_t = np.empty_like(br)
br_t[..., 0] = -z - 14.3
br_t[..., 1] = y - 45.0
br_t[..., 2] = x + VLEG_Z0
parts.append(("l_bracket_170x60", br_t))

# motor placeholder cylinder (Φ50 × 26.7) on the baseplate top
motor = m3d.Manifold.cylinder(MOTOR_H, MOTOR_D/2, MOTOR_D/2, 64, False)
motor = motor.translate((0.0, 0.0, MOTOR_Z0))
_mm = motor.to_mesh()
_mv = np.asarray(_mm.vert_properties)[:, :3]
_mt = np.asarray(_mm.tri_verts)
parts.append(("motor (placeholder)", _mv[_mt]))

# LED screen placeholder: 2 × HUB75 modules 128(W) × 256(H) × 14.3(T)
# side by side (total 256 wide), back face against the fin's axis-side face
# (X = -14.3) so the LED front face lies exactly ON the rotation axis plane
# (X = 0) — this is why HLEG_DIST_FROM_CENTER is 14.3.
# Vertical position approximated from the assembly photo: bottom ~90
# (clears the disc ribs at 76.7), top ~346 (overhangs the fin top ~100).
# TWO separate screens; each has 8 mounting holes but only 3 are engaged
# (via the fin's M3 pairs C/A/B). The +Y screen sits +1 outward (+Y) and
# +1 up (+Z) relative to the -Y screen — this is WHY the fin's bottom-row
# holes carry the (+1, +1) shift (and pair C's bottom an extra +1 Y).
# Each module's 8 M3 holes form a 井 (#) pattern (user-measured 2026-06-12,
# module-local, center origin): vertical strokes x=±30 with end holes at
# y=±120 (top pair 60 apart, 240 vertical, edge margin 8); horizontal
# strokes y=±33 with end holes at x=±54 (66 apart, side margin 10,
# left-right span 108). The fin engages 3 per screen: inner vertical
# stroke's BOTTOM hole (= pair C) + the inner side edge's two holes
# (= pairs A & B, exact match). Screen bottom = rib top = DISC_Z0+36
# (the ribs support the panels' bottom edges).
SCR_W, SCR_H, SCR_T = 128.0, 256.0, 14.3
SCR_HOLES = [(sx, sy) for sx in (-30.0, 30.0) for sy in (-120.0, 120.0)] + \
            [(sx, sy) for sx in (-54.0, 54.0) for sy in (-33.0, 33.0)]
SCR_Z0 = DISC_Z0 + 36.0          # -Y screen bottom = rib top (76.7 tower)
for yc, dz, tag in ((-SCR_W/2, 0.0, "-Y"), (SCR_W/2 + 1.0, 1.0, "+Y (+1,+1)")):
    scr = m3d.Manifold.cube((SCR_T, SCR_W, SCR_H), False)
    scr = scr.translate((-SCR_T, yc - SCR_W/2, SCR_Z0 + dz))
    zc = SCR_Z0 + dz + SCR_H/2
    for (hx, hy) in SCR_HOLES:           # drill the 8 M3 holes (along X)
        h = m3d.Manifold.cylinder(SCR_T + 2, 1.6, 1.6, 16, False)
        h = h.rotate((0, 90, 0))
        h = h.translate((-SCR_T - 1.0, yc + hx, zc + hy))
        scr = scr - h
    _sm = scr.to_mesh()
    _sv = np.asarray(_sm.vert_properties)[:, :3]
    _st = np.asarray(_sm.tri_verts)
    parts.append((f"LED module {tag}", _sv[_st]))

# Daygreen B10-1224-05 DC-DC power module (50W, 12/24V→5V 10A) placeholder,
# modelled from the listing drawing (63 × 53 × 20 overall incl. ears):
#   • body 50(Y) × 38(X) × 20(Z), terminal end facing −X (toward the PCB)
#   • base-plate front strip 15(X) × 50(Y) carrying the terminal block,
#     with two 3.2 × 6.4 slots (R1.6 ends, lengthwise along X), centers
#     7.5 in from the front edge, 42 apart → land on disc holes (62, ±21)
#   • two side ears with Φ3.2 holes 57 apart (drawing: ±28.5; disc pair is
#     (88, ±28.5) → exact match), hole line 19 in from
#     the rear edge, ear tips at ±31.5 (63 overall)
#   • base-plate / ear thickness 3.0 (not dimensioned; assumed)
#   • terminal block ≈ 38(Y) × 12(X) × 12(Z) step on the front face (approx.)
# The round ear holes pin X: rear edge = 88 + 19 = 107, body front face 69,
# strip front edge 54. Slots (6.4 long) then cover the (62, ±21) holes from
# center 61.5. Body front face at 69 clears the pi2hub75e plate (X ≤ 53.8);
# the 3-thick strip tops out at the plate's bottom plane (Z 49.7) with a
# 0.2 X gap. Rear corners (107, ±25) nominally overhang the Φ200 disc.
PSU_Z0 = DISC_Z0 + 6.0             # disc top face = 46.7
PSU_TAB_X = 88.0                   # ear-hole line on the disc pair (88, ±28.5)
PSU_X1 = PSU_TAB_X + 19.0          # rear edge, 107
PSU_BX0 = PSU_X1 - 38.0            # body front face, 69
PSU_X0 = PSU_X1 - 53.0             # strip front edge, 54
PSU_T = 3.0                        # base-plate / ear thickness (assumed)
psu = m3d.Manifold.cube((38.0, 50.0, 20.0), False).translate(
    (PSU_BX0, -25.0, PSU_Z0))                      # body
strip = m3d.Manifold.cube((15.0, 50.0, PSU_T), False).translate(
    (PSU_X0, -25.0, PSU_Z0))                       # front base strip
_scx = PSU_X0 + 7.5                # slot centers at X = 61.5
for _sy in (21.0, -21.0):          # 3.2 × 6.4 slots (R1.6 ends, along X)
    _sl = m3d.Manifold.cube((3.2, 3.2, PSU_T + 2.0), False).translate(
        (_scx - 1.6, _sy - 1.6, PSU_Z0 - 1.0))
    for _ex in (_scx - 1.6, _scx + 1.6):
        _sl = _sl + m3d.Manifold.cylinder(PSU_T + 2.0, 1.6, 1.6, 24, False
                                          ).translate((_ex, _sy, PSU_Z0 - 1.0))
    strip = strip - _sl
psu = psu + strip
for _sgn in (1.0, -1.0):           # side ears with Φ3.2 holes at (88, ±28.5)
    _ear = m3d.Manifold.cube((12.0, 6.5, PSU_T), False).translate(
        (PSU_TAB_X - 6.0, min(_sgn * 25.0, _sgn * 31.5), PSU_Z0))
    _hole = m3d.Manifold.cylinder(PSU_T + 2.0, 1.6, 1.6, 24, False).translate(
        (PSU_TAB_X, _sgn * 28.5, PSU_Z0 - 1.0))
    psu = psu + (_ear - _hole)
psu = psu + m3d.Manifold.cube((12.0, 38.0, 12.0), False).translate(
    (PSU_BX0 - 12.0, -19.0, PSU_Z0))               # terminal block step
_qm = psu.to_mesh()
_qv = np.asarray(_qm.vert_properties)[:, :3]
_qt = np.asarray(_qm.tri_verts)
parts.append(("DC-DC PSU (B10-1224-05)", _qv[_qt]))
print(f"PSU body  X {PSU_BX0:.1f}..{PSU_X1:.1f}  Y ±25.0  "
      f"Z {PSU_Z0:.1f}..{PSU_Z0 + 20.0:.1f}")
print(f"PSU strip X {PSU_X0:.1f}..{PSU_BX0:.1f}  Z {PSU_Z0:.1f}.."
      f"{PSU_Z0 + PSU_T:.1f}; ears X {PSU_TAB_X - 6.0:.1f}..{PSU_TAB_X + 6.0:.1f}"
      f"  Y ±25.0..±31.5")
print(f"PSU→PCB plate (X ≤ 53.8): body gap {PSU_BX0 - 53.8:.1f}, "
      f"terminal-block gap {PSU_BX0 - 12.0 - 53.8:.1f}, strip gap "
      f"{PSU_X0 - 53.8:.1f} (strip top {PSU_Z0 + PSU_T:.1f} = plate bottom)")
print(f"PSU vs disc R100: rear corner r = {math.hypot(PSU_X1, 25.0):.1f} "
      f"(overhang {math.hypot(PSU_X1, 25.0) - 100.0:.1f}), ear corner r = "
      f"{math.hypot(PSU_TAB_X + 6.0, 31.5):.1f}")

# pi2hub75e placeholder plate on the boss tops
PCB_T = 1.6
PCB_HOLES = [( 3.2, 58.8), ( 3.2, 48.8), (79.0, 58.8), (79.0, 48.8),
             ( 3.5,  3.1), (78.4,  3.0)]
PCB_OFF_X, PCB_OFF_Y = 53.8, 41.0
plate = m3d.Manifold.cube((62.0, 82.0, PCB_T), False)       # X = 62 (pcb_y), Y = 82 (pcb_x)
plate = plate.translate((PCB_OFF_X - 62.0, PCB_OFF_Y - 82.0, 0.0))
for (px, py) in PCB_HOLES:   # component side up: disc_Y = pcb_x − PCB_OFF_Y
    h = m3d.Manifold.cylinder(PCB_T + 2, 1.65, 1.65, 24, False)
    h = h.translate((PCB_OFF_X - py, px - PCB_OFF_Y, -1.0))
    plate = plate - h
plate = plate.translate((0.0, 0.0, VLEG_Z0 + 3.0))           # boss tops
mesh = plate.to_mesh()
pv = np.asarray(mesh.vert_properties)[:, :3]
pt = np.asarray(mesh.tri_verts)
pcb_tris = pv[pt]                                            # (n, 3, 3)
parts.append(("pi2hub75e (plate)", pcb_tris))

# Top steady-bearing module v3 (models/top_bearing/): rotating top_cap with
# a Φ26 reinforcement column; M6×40 screw up through it into a Φ8×50
# standoff threaded onto the screw (asm 366.4..416.4); the standoff body
# rides in TWO 688 bearings press-fit (Φ15.8) in the frame_A/B hubs.
capm = read_stl(ROOT / "models/top_bearing/top_cap.stl")
ct = capm.copy()
ct[..., 1] = -capm[..., 1]
ct[..., 2] = 342.7 - capm[..., 2]
ct = ct[:, ::-1, :].copy()
parts.append(("top_cap (rotor)", ct))
fa = read_stl(ROOT / "models/top_bearing/frame_A.stl")
c135, s135 = math.cos(math.radians(135)), math.sin(math.radians(135))
fax, fay = fa[..., 0].copy(), fa[..., 1].copy()
fa[..., 0] = c135*fax - s135*fay
fa[..., 1] = s135*fax + c135*fay
fa[..., 2] += 400.0
parts.append(("frame_A SW+NW", fa))
fb = read_stl(ROOT / "models/top_bearing/frame_B.stl")
fb[..., 1] = -fb[..., 1]
fb[..., 2] = 416.0 - fb[..., 2]
fb = fb[:, ::-1, :].copy()
cm45, sm45 = math.cos(math.radians(-45)), math.sin(math.radians(-45))
fbx, fby = fb[..., 0].copy(), fb[..., 1].copy()
fb[..., 0] = cm45*fbx - sm45*fby
fb[..., 1] = sm45*fbx + cm45*fby
parts.append(("frame_B NE+SE", fb))
# M6×40 screw shank (visible span column top 342.7 -> standoff bottom 366.4)
scr = m3d.Manifold.cylinder(40.0, 3.0, 3.0, 32, False).translate((0, 0, 336.4))
_sc = scr.to_mesh()
_scv = np.asarray(_sc.vert_properties)[:, :3]
_sct = np.asarray(_sc.tri_verts)
parts.append(("M6x40 screw (rotor)", _scv[_sct]))
sto = m3d.Manifold.cylinder(50.0, 4.0, 4.0, 48, False).translate((0, 0, 366.4))
_st = sto.to_mesh()
_sv2 = np.asarray(_st.vert_properties)[:, :3]
_st2 = np.asarray(_st.tri_verts)
parts.append(("standoff Φ8×50 (rotor)", _sv2[_st2]))
for bz, tag in ((403.0, "688 lower (frame_A)"), (411.0, "688 upper (frame_B)")):
    brg = (m3d.Manifold.cylinder(5.0, 8.0, 8.0, 64, False)
           - m3d.Manifold.cylinder(7.0, 4.0, 4.0, 64, False).translate((0, 0, -1.0)))
    brg = brg.translate((0.0, 0.0, bz))
    _bg = brg.to_mesh()
    _bgv = np.asarray(_bg.vert_properties)[:, :3]
    _bgt = np.asarray(_bg.tri_verts)
    parts.append((tag, _bgv[_bgt]))

# once-per-rev optical index (models/photo_sensor/): sensor_bracket is a 5mm
# plate bolted UNDER the disc at (−92.5,±20); the sensor_module hangs from it
# (flipped: slot opens DOWN, leads UP), placed so the beam is RADIAL through
# the centre (−R_SLOT,0,25.7) and the slot through-channel is TANGENTIAL.
R_SLOT = 112.0
brk = read_stl(ROOT / "models/photo_sensor/sensor_bracket.stl")   # assembly frame
parts.append(("sensor_bracket (rotor)", brk))
mod = read_stl(ROOT / "models/photo_sensor/sensor_module.stl")
mod[..., 1] = -mod[..., 1]                       # flip 180° about X (slot down)
mod[..., 2] = -mod[..., 2]                       # (2 axis-flips = rotation, winding kept)
mod = mod + np.array([-R_SLOT, 20.0, 46.7])
parts.append(("photo sensor module", mod))
# index_vane — STATIC flag bolted to the breadboard (M6), blade in the slot
vane = read_stl(ROOT / "models/photo_sensor/index_vane.stl")
parts.append(("index_vane (static)", vane))

# ===== merge + export =====
all_tris = np.concatenate([t for (_, t) in parts], axis=0)
out = ROOT / "assembly_stack.stl"
_header = b"POV3D assembly_stack"
assert len(_header) <= 80
with out.open("wb") as f:
    f.write(_header.ljust(80, b" "))
    f.write(struct.pack("<I", len(all_tris)))
    for t in all_tris:
        v0, v1, v2 = t
        n = np.cross(v1 - v0, v2 - v0)
        L = float(np.linalg.norm(n))
        if L > 0:
            n = n / L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0))
        f.write(struct.pack("<3f", *v1))
        f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))

_expected = 84 + len(all_tris) * 50
assert _expected == out.stat().st_size, "STL size mismatch"
print(f"wrote {out}  ({len(all_tris)} triangles)")
for name, t in parts:
    v = t.reshape(-1, 3)
    print(f"  {name:22s} X {v[:,0].min():7.2f}..{v[:,0].max():7.2f}  "
          f"Y {v[:,1].min():7.2f}..{v[:,1].max():7.2f}  "
          f"Z {v[:,2].min():7.2f}..{v[:,2].max():7.2f}")

# ===== isometric preview render =====
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

fig = plt.figure(figsize=(14, 7))
COLORS = {"M6x40 screw (rotor)": "#888888", "top_cap (rotor)": "#cc8888", "frame_A SW+NW": "#5577aa",
          "frame_B NE+SE": "#5577aa", "688 lower (frame_A)": "#999999", "688 upper (frame_B)": "#999999",
          "standoff Φ8×50 (rotor)": "#666666",
          "DC-DC PSU (B10-1224-05)": "#bb6633",
          "breadboard (placeholder)": "#333333",
          "motor (placeholder)": "#444444", "baseplate": "#777777", "ring_collar": "#bb88bb",
          "flange_disc": "#88aacc", "mounting_flange": "#cccc77",
          "hub_disc": "#ccaa55", "rim_ring": "#9999bb", "rim_top_disc": "#88bb88",
          "l_bracket_170x60": "#cc8888", "pi2hub75e (plate)": "#3a6b35"}
for i, (elev, azim, title) in enumerate([(28, -60, "iso"), (8, -90, "front (-Y)")]):
    ax = fig.add_subplot(1, 2, i + 1, projection="3d")
    for name, t in parts:
        pc = Poly3DCollection(t, facecolor=COLORS.get(name, "#222222"),
                              edgecolor="none", alpha=0.95)
        ax.add_collection3d(pc)
    ax.set_xlim(-150, 150); ax.set_ylim(-150, 150); ax.set_zlim(0, 425)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title)
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
fig.tight_layout()
png = ROOT / "assembly_stack_preview.png"
fig.savefig(png, dpi=110)
print(f"wrote {png}")
