"""
Build POV 3D PCB test-jig (治具) STL.

Solid block with a top pocket precisely matching the PCB outline
(loaded from STEP), depth 3 mm so the wall around the pocket rises
3 mm above the pocket floor (= 1.4 mm above the seated PCB top face).
Four finger cutouts at the cardinal mid-edges remove the wall locally
so the PCB can be pinched and lifted out from above.

Source PCB:
  /mnt/c/Users/kiujkiu/Downloads/3D_ClipRec_BTW_2026-06-09(1).step
  - outline bbox 57.52 × 45.37 mm, irregular (45-edge perimeter)
  - thickness 1.6 mm

Final orientation: print flat on bed, jig bottom at Z=0.
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d
import cadquery as cq

# ===== Parameters =====
PCB_STEP_PATH = '/mnt/c/Users/kiujkiu/Downloads/3D_ClipRec_BTW_2026-06-09(1).step'

PCB_THICK     = 1.6      # for reference / drawing only

PCB_CLEARANCE = 0.30     # pocket offset OUTWARD from PCB outline
POCKET_DEPTH  = 2.0      # corner-boss height above floor (was 3 — reduced per spec)
FLOOR_THICK   = 3.0      # solid base thickness below pocket floor (was 5)

JIG_BORDER    = 7.0      # extra material around PCB bbox on each side
JIG_R_CORNER  = 3.0      # outer rounded-rect corner radius

# Only KEEP the wall material inside 4 corner squares (size CORNER_SIZE),
# anchored to the jig outer corners. Everywhere else the wall is removed →
# the PCB is located only by the 4 L-shaped corner cups, and the 4 mid-edges
# are fully open for finger access.
CORNER_SIZE   = 18.0

# Top + bottom mid scallops: shape FOLLOWS the PCB outline (offset INWARD by
# SCALLOP_REACH mm so the scallop reaches 2 mm into the PCB material along
# the entire perimeter). X extent is bounded so the scallop stays clear of
# the corner-wall x range (corner walls at |x| > JIG_HX - CORNER_SIZE = 17.76).
SCALLOP_W       = 34.0   # width along X (stays clear of corner walls at ±17.76)
SCALLOP_REACH   = 2.0    # 2 mm inward offset of PCB outline → scallop inner edge
SCALLOP_DEPTH   = 2.0    # 2 mm scoop into base top (1 mm floor remains)

# 4 × M3 mounting through-holes at the 4 jig corners (inside the corner-wall
# material). MOUNT_OFFSET = distance from each jig outer edge to hole center.
MOUNT_DIAM    = 3.2      # M3 clearance
MOUNT_OFFSET  = 4.0
MOUNT_SEG     = 24

# Probe holes at every PCB M0.8 hole position. The jig is drilled through
# (top↔bottom) with Φ1.0 mm holes — clearance for spring-loaded test probes
# contacting the PCB from below.
PROBE_DIAM         = 1.0
PROBE_PCB_HOLE_R   = 0.40    # match inner wires with this radius (= Φ0.8 holes)
PROBE_R_TOL        = 0.02    # tolerance when matching the radius
PROBE_HOLE_SEG     = 16

# ===== Extract PCB outline from STEP =====
print(f"reading {PCB_STEP_PATH}")
shape = cq.importers.importStep(PCB_STEP_PATH)
faces = shape.val().Faces()
top_face = max(faces, key=lambda f: f.Area())
bb = top_face.BoundingBox()
PCB_CX = (bb.xmin + bb.xmax) / 2
PCB_CY = (bb.ymin + bb.ymax) / 2
PCB_DX = bb.xlen
PCB_DY = bb.ylen
print(f"  PCB bbox {PCB_DX:.2f} × {PCB_DY:.2f} mm @ centroid ({PCB_CX:.2f}, {PCB_CY:.2f})")

def sample_edge(e, n_per_mm=2.5):
    """Return points along edge in PCB-local coords (centered at origin).
    Includes the start point but NOT the end (next edge supplies it)."""
    if e.geomType() == 'LINE':
        s = e.startPoint()
        return [(s.x - PCB_CX, s.y - PCB_CY)]
    # Arc: sample n points
    L = e.Length()
    n = max(4, int(L * n_per_mm))
    pts = []
    for i in range(n):
        t = i / n
        p = e.positionAt(t)
        pts.append((p.x - PCB_CX, p.y - PCB_CY))
    return pts

outer = top_face.outerWire()
pcb_pts = []
for e in outer.Edges():
    pcb_pts.extend(sample_edge(e))
print(f"  outline sampled to {len(pcb_pts)} points")

# Extract M0.8 PCB hole centers (inner wires with two CIRCLE edges of R≈0.40)
m08_holes = []
for w in top_face.innerWires():
    eds = w.Edges()
    if len(eds) != 2:
        continue
    if not all(e.geomType() == 'CIRCLE' for e in eds):
        continue
    r = eds[0].radius()
    if abs(r - PROBE_PCB_HOLE_R) > PROBE_R_TOL:
        continue
    c = eds[0].arcCenter()
    m08_holes.append((c.x - PCB_CX, c.y - PCB_CY))
print(f"  found {len(m08_holes)} M0.8 (Φ0.8) PCB hole positions to drill as Φ{PROBE_DIAM:g} probes")

def signed_area(pts):
    s = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        s += (x1 * y2 - x2 * y1)
    return s / 2

A = signed_area(pcb_pts)
if A < 0:
    pcb_pts = pcb_pts[::-1]
    A = -A
    print("  reversed outline to CCW")
print(f"  outline area: {A:.2f} mm²")

# ===== 2D cross-sections =====
pcb_cs = m3d.CrossSection([pcb_pts])

# Pocket: PCB outline + clearance, rounded joins to swallow concave corners safely
pocket_cs = pcb_cs.offset(PCB_CLEARANCE, join_type=m3d.JoinType.Round, circular_segments=24)

# Jig outline: rounded rectangle covering PCB bbox + border
JIG_DX = PCB_DX + 2 * JIG_BORDER
JIG_DY = PCB_DY + 2 * JIG_BORDER
print(f"  jig outline: {JIG_DX:.2f} × {JIG_DY:.2f} mm")

def rounded_rect_cs(dx, dy, r, n_seg=16):
    pts = []
    hx, hy = dx / 2 - r, dy / 2 - r
    centers_starts = [
        ( hx, -hy, -math.pi / 2),
        ( hx,  hy,  0.0),
        (-hx,  hy,  math.pi / 2),
        (-hx, -hy,  math.pi),
    ]
    for cx, cy, a0 in centers_starts:
        for i in range(n_seg + 1):
            a = a0 + (math.pi / 2) * i / n_seg
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return m3d.CrossSection([pts])

jig_outline_cs = rounded_rect_cs(JIG_DX, JIG_DY, JIG_R_CORNER)

# ===== Build 3D =====
TOTAL_H = FLOOR_THICK + POCKET_DEPTH      # 5 mm  (3 base + 2 corner-boss)
print(f"  jig height: {TOTAL_H:g} mm  (floor {FLOOR_THICK:g} + boss {POCKET_DEPTH:g})")

PCB_HX = PCB_DX / 2
PCB_HY = PCB_DY / 2
JIG_HX = JIG_DX / 2
JIG_HY = JIG_DY / 2

# Base plate (full rounded rect)
base = jig_outline_cs.extrude(FLOOR_THICK)

# Wall material = jig outline minus the PCB pocket (PCB outline + clearance)
wall_full_cs = jig_outline_cs - pocket_cs

# Keep only material inside the 4 corner squares (anchored to JIG outer corners)
def corner_sq_cs(sx, sy):
    cx = sx * (JIG_HX - CORNER_SIZE / 2)
    cy = sy * (JIG_HY - CORNER_SIZE / 2)
    h = CORNER_SIZE / 2
    return m3d.CrossSection([[
        (cx - h, cy - h), (cx + h, cy - h),
        (cx + h, cy + h), (cx - h, cy + h),
    ]])

corners_union = (corner_sq_cs( 1,  1) + corner_sq_cs(-1,  1)
               + corner_sq_cs(-1, -1) + corner_sq_cs( 1, -1))

# Intersection via identity A ∩ B = A − (A − B)
corner_walls_cs = wall_full_cs - (wall_full_cs - corners_union)

corner_walls = corner_walls_cs.extrude(POCKET_DEPTH).translate((0, 0, FLOOR_THICK))

jig = base + corner_walls

# Top + bottom mid scallops — shape = (top/bottom half rectangle) - (PCB
# outline offset INWARD by SCALLOP_REACH). The scallop follows the PCB
# contour naturally at the recess/tab area; on the straight bottom edge it
# is a clean strip 2 mm into the PCB.
pcb_inset_cs = pcb_cs.offset(-SCALLOP_REACH,
                             join_type=m3d.JoinType.Round,
                             circular_segments=24)

SC_HX = SCALLOP_W / 2
top_rect_cs = m3d.CrossSection([[
    (-SC_HX, 0.0), (SC_HX, 0.0),
    (SC_HX, JIG_HY + 1.0), (-SC_HX, JIG_HY + 1.0),
]])
bot_rect_cs = m3d.CrossSection([[
    (-SC_HX, -JIG_HY - 1.0), (SC_HX, -JIG_HY - 1.0),
    (SC_HX, 0.0), (-SC_HX, 0.0),
]])
top_scallop_cs = top_rect_cs - pcb_inset_cs
bot_scallop_cs = bot_rect_cs - pcb_inset_cs

def to_scallop_solid(cs):
    cutter_h = SCALLOP_DEPTH + 1.0
    return cs.extrude(cutter_h).translate(
        (0.0, 0.0, FLOOR_THICK - SCALLOP_DEPTH - 0.5))

jig = jig - to_scallop_solid(top_scallop_cs) - to_scallop_solid(bot_scallop_cs)

# ===== 4 × M3 mounting through-holes (jig corners) =====
mount_positions = [(sx * (JIG_HX - MOUNT_OFFSET), sy * (JIG_HY - MOUNT_OFFSET))
                   for sx in (-1, 1) for sy in (-1, 1)]
mount_h = TOTAL_H + 2.0
for (hx, hy) in mount_positions:
    h = m3d.Manifold.cylinder(mount_h, MOUNT_DIAM / 2, MOUNT_DIAM / 2,
                              MOUNT_SEG, False)
    h = h.translate((hx, hy, -1.0))
    jig = jig - h

# ===== Drill Φ1.0 probe through-holes at every M0.8 PCB hole position =====
probe_h = TOTAL_H + 2.0
for (hx, hy) in m08_holes:
    h = m3d.Manifold.cylinder(probe_h, PROBE_DIAM / 2, PROBE_DIAM / 2,
                              PROBE_HOLE_SEG, False)
    h = h.translate((hx, hy, -1.0))
    jig = jig - h

# ===== Export STL =====
mesh  = jig.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("pcb_tray.stl")
_header = b"POV3D pcb_tray"
assert len(_header) <= 80
with out.open("wb") as f:
    f.write(_header.ljust(80, b" "))
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1 - v0, v2 - v0)
        L = float(np.linalg.norm(n))
        if L > 0:
            n = n / L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0))
        f.write(struct.pack("<3f", *v1))
        f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))

print(f"\nwrote {out}  ({len(tris)} triangles, {len(verts)} vertices)")
print(f"  bbox X: {verts[:,0].min():7.2f} .. {verts[:,0].max():7.2f}")
print(f"  bbox Y: {verts[:,1].min():7.2f} .. {verts[:,1].max():7.2f}")
print(f"  bbox Z: {verts[:,2].min():7.2f} .. {verts[:,2].max():7.2f}")
print(f"  volume: {jig.volume():.2f} mm³")

# STL size sanity check
_expected = 84 + len(tris) * 50
_actual = out.stat().st_size
assert _expected == _actual, f"STL size mismatch: {_expected} vs {_actual}"
print(f"  STL size OK: {_actual} bytes")

# Save outline points for SCAD / drawing reuse
out_pts = Path(__file__).with_name("pcb_outline_points.json")
import json
with out_pts.open("w") as f:
    json.dump({
        "pcb_pts_local": pcb_pts,
        "pcb_bbox": [PCB_DX, PCB_DY],
        "m08_holes": m08_holes,
        "mount_holes": mount_positions,
        "params": {
            "PCB_CLEARANCE": PCB_CLEARANCE,
            "POCKET_DEPTH": POCKET_DEPTH,
            "FLOOR_THICK": FLOOR_THICK,
            "JIG_BORDER": JIG_BORDER,
            "JIG_R_CORNER": JIG_R_CORNER,
            "CORNER_SIZE": CORNER_SIZE,
            "SCALLOP_W": SCALLOP_W,
            "SCALLOP_REACH": SCALLOP_REACH,
            "SCALLOP_DEPTH": SCALLOP_DEPTH,
            "MOUNT_DIAM": MOUNT_DIAM,
            "MOUNT_OFFSET": MOUNT_OFFSET,
            "PROBE_DIAM": PROBE_DIAM,
            "JIG_DX": JIG_DX,
            "JIG_DY": JIG_DY,
            "TOTAL_H": TOTAL_H,
        }
    }, f)
print(f"  saved outline points to {out_pts}")
