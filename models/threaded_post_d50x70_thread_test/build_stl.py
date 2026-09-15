"""
螺纹试打件 threaded_post_d50x70_thread_test (2026-09-14, 用户要求: 先单独试打螺纹效果)

= 母件 threaded_post_d50x70 在 Z_CUT 处横切, 只留上面:
  - 螺纹柱整段 (Z 70–85): 牙型 / 打印间隙 / 顶端倒角 / 内孔 与母件完全一致
  - 下部圆柱留 BASE_KEEP = 母件顶板厚 PLATE_T (2026-09-15 定稿 3.36; 保证贴床面是实心 Φ50 整圆)
几何直接复用母件 build_stl.py (exec 到临时目录, 母件的全部 assert 照跑, 它自己的 STL 写进临时目录后丢弃),
母件参数改了这里重跑即同步。
坐标: 切面平移到 Z=0 贴床, 螺纹朝上 (与母件同一打印方向)。
"""
import contextlib
import io
import struct
import tempfile
from pathlib import Path

import numpy as np
import manifold3d as m3d

PARENT = Path(__file__).resolve().parent.parent / "threaded_post_d50x70" / "build_stl.py"

# ===== 复用母件几何 =====
with tempfile.TemporaryDirectory() as td, contextlib.redirect_stdout(io.StringIO()):
    ns = {"__file__": str(Path(td) / "build_stl.py"), "__name__": "__parent__"}
    exec(compile(PARENT.read_text(encoding="utf-8"), str(PARENT), "exec"), ns)

parent = ns["part"]
BASE_H, Z_TOP, R_BASE = ns["BASE_H"], ns["Z_TOP"], ns["R_BASE"]
BASE_KEEP = ns["PLATE_T"]           # 下部圆柱保留高度 = 母件顶板厚 (再厚会切进腔/45° 过渡区)
Z_CUT = BASE_H - BASE_KEEP
H = Z_TOP - Z_CUT                                   # 试打件总高 20

def intersect(a, b):
    return m3d.Manifold.batch_boolean([a, b], m3d.OpType.Intersect)

_big = 2 * R_BASE + 10
keep = m3d.Manifold.cube((_big, _big, H + 5)).translate((-_big / 2, -_big / 2, Z_CUT))
coupon = intersect(parent, keep).translate((0, 0, -Z_CUT))

# ===== 校核 =====
assert len(coupon.decompose()) == 1, "件不是一整块"
# 螺纹段截面与母件同高度处逐一相同
for z in (BASE_H + 1.0, ns["z_mid"], Z_TOP - ns["CHAMFER"] / 2):
    a_c, a_p = coupon.slice(z - Z_CUT).area(), parent.slice(z).area()
    assert abs(a_c - a_p) < 1e-6, f"Z={z} 截面与母件不一致 {a_c} vs {a_p}"
# 贴床面: 保留高度不超过顶板厚时应是实心整圆
a_bed = coupon.slice(1e-3).area()
if BASE_KEEP <= ns["PLATE_T"]:
    a_disk = ns["poly_area"](R_BASE, ns["BASE_SEG"])
    assert abs(a_bed - a_disk) < 1e-2, f"贴床面应为实心 Φ{2*R_BASE:g} 圆 {a_bed} vs {a_disk}"
# 体积 = 母件 − 切掉的下半
lower = intersect(parent, m3d.Manifold.cube((_big, _big, Z_CUT + 1)).translate((-_big / 2, -_big / 2, -1)))
assert abs(coupon.volume() + lower.volume() - parent.volume()) < 1e-3 * parent.volume(), "切分体积对不上"

# ===== 导出 STL =====
mesh  = coupon.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("threaded_post_d50x70_thread_test.stl")
with out.open("wb") as f:
    _hdr = f"thread_test of threaded_post_d50x70 cut Z{Z_CUT:g} H{H:g}".encode("ascii")
    f.write(_hdr.ljust(80, b" ")[:80])
    f.write(struct.pack("<I", len(tris)))
    v0 = verts[tris[:, 0]]; v1 = verts[tris[:, 1]]; v2 = verts[tris[:, 2]]
    n = np.cross(v1 - v0, v2 - v0)
    L = np.linalg.norm(n, axis=1, keepdims=True)
    n = np.where(L > 0, n / np.where(L > 0, L, 1), 0)
    rec = np.zeros(len(tris), dtype=[("n", "<f4", 3), ("v0", "<f4", 3), ("v1", "<f4", 3),
                                     ("v2", "<f4", 3), ("attr", "<u2")])
    rec["n"], rec["v0"], rec["v1"], rec["v2"] = n, v0, v1, v2
    f.write(rec.tobytes())

expected = 84 + len(tris) * 50
assert out.stat().st_size == expected, f"STL 大小不对: {out.stat().st_size} != {expected}"

vol = coupon.volume()
print(f"wrote {out}  ({len(tris)} triangles)")
print(f"  bbox X: {verts[:,0].min():8.3f} .. {verts[:,0].max():8.3f}")
print(f"  bbox Y: {verts[:,1].min():8.3f} .. {verts[:,1].max():8.3f}")
print(f"  bbox Z: {verts[:,2].min():8.3f} .. {verts[:,2].max():8.3f}")
print(f"  母件切于 Z={Z_CUT:g}: 圆片 Φ{2*R_BASE:g}×{BASE_KEEP:g} (贴床面 {a_bed:.1f} mm²) + 螺纹柱高 {Z_TOP-BASE_H:g}")
print(f"  螺纹 (同母件): 建模大径 Φ{2*ns['R_MAJ']:.2f} / 小径 Φ{2*ns['R_MIN']:.2f} (名义 Φ{ns['THR_MAJ']:g}/Φ{ns['THR_MIN']:g}, "
      f"间隙 {ns['THR_CLEAR']:g}), P{ns['PITCH']:g} {'右' if ns['RIGHT_HAND'] else '左'}旋, 顶倒角 C{ns['CHAMFER']:g}, "
      + (f"内孔 Φ{2*ns['R_BORE']:g}" if ns["R_BORE"] > 0 else "螺纹柱实心"))
print(f"  volume {vol:.2f} mm^3 (母件 {parent.volume():.2f}), PLA 实心约 {vol*1.24e-3:.1f} g")
