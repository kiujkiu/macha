"""
pi2hub75e 数字孪生 (BOUGHT PCB, 不打印) — 从 'Copy of pi2hub75e.step' 抠出的几何
(2026-07-01)。板 100×100×1.6, 6×Φ3.3 安装孔, 顶部连接器 (排座) 供米联派下插。
居中坐标系: 4 图案孔在 (±39.5,±25) 与盘/米联派对齐; 原点=4图案孔中心。
  板外形 X -50..50, Y -58..42 ; 板 Z 0..1.6 ; 板底件≈1.2 (未逐个建模, 用凸台2mm避空)。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

BW_X, BW_Y, T = 100.0, 100.0, 1.6
X0, Y0 = -50.0, -58.0                    # board min corner (centred on 4-pattern holes)
HOLES = [(-39.5, 25.0), (39.5, 25.0), (-39.5, -25.0), (39.5, -25.0), (-39.5, -55.0), (39.5, -55.0)]
HOLE_D = 3.3
SOCK_H = 8.5                             # 排座高度 (米联派插上来的间隙, 估值)
# connectors on TOP (x0,x1,y0,y1)
CONN = [("P3", -45, -9, 34, 40), ("P1", -1, 45, 34, 40), ("P2", -31, 30, -26, -21)]

def _box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))
def _cyl(d, x, y, z0, z1):
    return m3d.Manifold.cylinder(z1-z0, d/2, d/2, 32, False).translate((x, y, z0))

part = _box(X0, X0+BW_X, Y0, Y0+BW_Y, 0.0, T)
for (x, y) in HOLES:
    part = part - _cyl(HOLE_D, x, y, -1, T+1)
for (_n, x0, x1, y0, y1) in CONN:
    part = part + _box(x0, x1, y0, y1, T, T+SOCK_H)

mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("pi2hub75e.stl")
_hdr = b"POV3D pi2hub75e twin"
with out.open("wb") as f:
    f.write(_hdr.ljust(80, b" ")[:80]); f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1-v0, v2-v0); L = float(np.linalg.norm(n))
        if L > 0: n = n/L
        f.write(struct.pack("<3f", *n)); f.write(struct.pack("<3f", *v0))
        f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2)); f.write(struct.pack("<H", 0))
assert 84 + len(tris)*50 == out.stat().st_size
print(f"wrote {out} ({len(tris)} tris)")
print(f"  board X{X0:g}..{X0+BW_X:g} Y{Y0:g}..{Y0+BW_Y:g} Z0..{T:g}; 6×Φ{HOLE_D:g} holes; connectors +{SOCK_H:g} on top")
print(f"  bbox Z {verts[:,2].min():.1f}..{verts[:,2].max():.1f}")
