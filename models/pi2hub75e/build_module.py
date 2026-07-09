"""
pi2hub75e 数字孪生 (BOUGHT PCB, 不打印) — 从 'Copy of pi2hub75e.step' (2026-07-03 新版)
抠出的几何。板 100×75×1.6, 7×Φ3.3 安装孔, 顶部连接器 (排座) 供米联派下插。
居中坐标系: 原点 = 4 图案孔 (±39.5,±25) 中心 = STEP 原始坐标平移 (−50, −28)。
  板外形 X −50..50, Y −28..47 ; 板 Z 0..1.6。
  7 孔 = 4 图案孔 (±39.5,±25) + 顶边 3 孔 (−47,44)(0,44)(47,44)。
  STEP 里板体只有 0.411 厚 (导出退化), 按实际 1.6 建模; 底面无元件体
  (仅 119 个 Φ0.9/Φ1.1 通孔的焊脚突出, 用承载盘凸台高 5 避空)。
  连接器无 3D 体, 按排针孔群 bbox±1.27 推出: P3 顶左 2×15, P1 顶右 2×15,
  P2 底 2×25, J1 2p / J2 3p 小排针。另建 3 个 >3mm 高的顶面元件块。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

BW_X, BW_Y, T = 100.0, 75.0, 1.6
X0, Y0 = -50.0, -28.0                    # board min corner (centred on 4-pattern holes)
HOLES = [(-47.0, 44.0), (0.0, 44.0), (47.0, 44.0),
         (-39.5, 25.0), (39.5, 25.0), (-39.5, -25.0), (39.5, -25.0)]
HOLE_D = 3.3
SOCK_H = 8.5                             # 排座高度 (米联派插上来的间隙, 估值)
JUMP_H = 6.0                             # 小排针(带跳线帽)高度估值, 低于排座避免假碰撞
# connectors on TOP (name, x0, x1, y0, y1, h) — pin-hole cluster bbox ± 1.27
CONN = [("P3", -46.2,  -8.1,  32.1,  37.2, SOCK_H),   # top-left  2×15
        ("P1",   8.2,  46.2,  32.1,  37.2, SOCK_H),   # top-right 2×15
        ("P2", -31.7,  31.7, -26.7, -21.6, SOCK_H),   # bottom    2×25
        ("J1",  -2.5,   2.6,  34.2,  36.7, JUMP_H),   # 2p header @ y35.4
        ("J2",  -3.8,   3.9,  28.9,  31.5, JUMP_H)]   # 3p header @ y30.2
# tall top-side components (>3 mm) from STEP, (x0,x1,y0,y1,z0,z1) above board top
COMP = [( 34.5, 40.9, -12.4,  -6.1, 0.0, 7.7),        # 电解电容
        ( 41.5, 46.6,   1.6,   6.7, 0.0, 5.4),
        ( 37.1, 43.8,  12.4,  19.1, 0.0, 3.3)]

def _box(x0, x1, y0, y1, z0, z1):
    return m3d.Manifold.cube((x1-x0, y1-y0, z1-z0), False).translate((x0, y0, z0))
def _cyl(d, x, y, z0, z1):
    return m3d.Manifold.cylinder(z1-z0, d/2, d/2, 32, False).translate((x, y, z0))

part = _box(X0, X0+BW_X, Y0, Y0+BW_Y, 0.0, T)
for (x, y) in HOLES:
    part = part - _cyl(HOLE_D, x, y, -1, T+1)
for (_n, x0, x1, y0, y1, h) in CONN:
    part = part + _box(x0, x1, y0, y1, T, T+h)
for (x0, x1, y0, y1, z0, z1) in COMP:
    part = part + _box(x0, x1, y0, y1, T+z0, T+z1)

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
print(f"  board X{X0:g}..{X0+BW_X:g} Y{Y0:g}..{Y0+BW_Y:g} Z0..{T:g}; {len(HOLES)}×Φ{HOLE_D:g} holes @ {HOLES}")
print(f"  connectors +{SOCK_H:g} on top; bbox Z {verts[:,2].min():.1f}..{verts[:,2].max():.1f}")
print(f"  bbox X {verts[:,0].min():.1f}..{verts[:,0].max():.1f}  Y {verts[:,1].min():.1f}..{verts[:,1].max():.1f}  vol {part.volume():.0f}")
