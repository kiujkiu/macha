"""
screen_150x169_t13 — 双面屏模组数字孪生 (2026-07-22 深夜 v2, 外购不打印)。

用户澄清: "两个屏幕一起" = **一个双面屏模组 13.4(厚)×150(宽)×168.75(高)**,
正反两面都是 LED 发光面 (各占 6.7 厚, 合为一体)。固定孔:
**底面 (13.4×150 端面) 3×M3, 居中 (厚度中线上), 沿宽度间距 64 (−64/0/64);
顶面同样 3 个** —— 与 screen_solder_jig 定位孔同套系 (M3 通孔, 深度未实测,
占位 Φ3.2×10 盲)。

局部系: 厚度居中 X ±6.7 (LED 面 = ±6.7 两外侧面), 宽 Y ±75, 高 Z 0..168.75。
装配只做 +Z 平移 + 组旋转 (无 X 偏移)。
"""
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

T, W, H = 13.4, 150.0, 168.75
EDGE_HOLE_YS = (-64.0, 0.0, 64.0)   # 沿宽度, 间距 64
EDGE_HOLE_D, EDGE_HOLE_DEEP = 3.2, 10.0   # M3 通孔占位 (深度未实测)

part = m3d.Manifold.cube((T, W, H), False).translate((-T / 2, -W / 2, 0.0))
for y in EDGE_HOLE_YS:              # 底面 3 + 顶面 3, 全部居中 X=0
    for (z0, up) in ((0.0, True), (H, False)):
        h = m3d.Manifold.cylinder(EDGE_HOLE_DEEP + 0.1, EDGE_HOLE_D / 2,
                                  EDGE_HOLE_D / 2, 24, False)
        if up:
            h = h.translate((0.0, y, -0.1))
        else:
            h = h.translate((0.0, y, H - EDGE_HOLE_DEEP))
        part = part - h

mesh = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris = np.asarray(mesh.tri_verts)
out = Path(__file__).with_name("screen_150x169_t13.stl")
with out.open("wb") as f:
    f.write(b"POV3D dual screen 13.4x150x168.75 (bought)".ljust(80, b" ")[:80])
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1 - v0, v2 - v0); L = float(np.linalg.norm(n))
        if L > 0: n = n / L
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0)); f.write(struct.pack("<3f", *v1)); f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))
assert 84 + len(tris) * 50 == out.stat().st_size
print(f"wrote {out} ({len(tris)} tris)  vol {part.volume()/1000:.1f} cm3")
print(f"  双面屏模组 {T:g}×{W:g}×{H:g}, LED 面 = X ±{T/2:g} 两外侧, Y ±{W/2:g}, Z 0..{H:g}")
print(f"  底面/顶面各 3×M3 @ Y {EDGE_HOLE_YS} (间距 64), 厚度居中 X=0, 占位 Φ{EDGE_HOLE_D:g}×{EDGE_HOLE_DEEP:g}")
