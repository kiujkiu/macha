"""
螺纹试打件 threaded_post_d50x70_thread_test (2026-09-14 建, 用户要求先单独试打螺纹效果; 2026-09-15 一度同时出间隙 0 / 0.4 两个, 试打确认 0 可用后只出 0)

= 母件 threaded_post_d50x70 在顶板底面 Z = BASE_H − PLATE_T 横切, 只留上面:
  - 螺纹柱整段 (Z 70–85): 牙型 / 顶端倒角 / 内孔 与母件一致
  - 下部圆柱留 BASE_KEEP = 母件顶板厚 PLATE_T (随母件, 改⑥ 后 2.52; 保证贴床面是实心 Φ50 整圆)
几何直接复用母件 build_stl.py (exec 到临时目录, 母件的全部 assert 照跑, 它自己的 STL 写进临时目录后丢弃),
母件参数改了这里重跑即同步。
2026-09-15: 配合的是塑料/打印内螺纹; 用户已试打确认间隙 0 (凸起 Φ27.5 / 凹陷 Φ24.5) 可拧上 ⇒ 只出母件自身间隙一个。
  需要再比较间隙时把 EXTRA_CLEARANCES 设为 (0.4,) 等, 会另出 _c0.4 后缀的 STL
  (额外间隙版只在 exec 时替换母件源码里的 THR_CLEAR 行, 母件文件不动; 同目录 SCAD 只对应母件自身间隙)
坐标: 切面平移到 Z=0 贴床, 螺纹朝上 (与母件同一打印方向)。
"""
import contextlib
import io
import re
import struct
import tempfile
from pathlib import Path

import numpy as np
import manifold3d as m3d

PARENT = Path(__file__).resolve().parent.parent / "threaded_post_d50x70" / "build_stl.py"
STEM = "threaded_post_d50x70_thread_test"
EXTRA_CLEARANCES = ()          # 额外出的螺纹间隙 (直径), 如 (0.4,) 会另出 _c0.4 后缀; 2026-09-15 用户试打确认间隙 0 可用, 不再出

SRC = PARENT.read_text(encoding="utf-8")
_m = re.search(r"^THR_CLEAR\s*=\s*([0-9.]+)", SRC, flags=re.M)
assert _m, "母件 build_stl.py 里找不到 THR_CLEAR 参数行"
PARENT_CLEAR = float(_m.group(1))


def intersect(a, b):
    return m3d.Manifold.batch_boolean([a, b], m3d.OpType.Intersect)


def build(clear):
    if clear == PARENT_CLEAR:
        src = SRC
    else:
        src, n = re.subn(r"^THR_CLEAR\s*=\s*[^#\n]*", f"THR_CLEAR = {clear!r}  ", SRC, count=1, flags=re.M)
        assert n == 1
    with tempfile.TemporaryDirectory() as td, contextlib.redirect_stdout(io.StringIO()):
        ns = {"__file__": str(Path(td) / "build_stl.py"), "__name__": "__parent__"}
        exec(compile(src, str(PARENT), "exec"), ns)
    assert abs(ns["THR_CLEAR"] - clear) < 1e-9, "间隙替换没生效"

    parent = ns["part"]
    BASE_H, Z_TOP, R_BASE = ns["BASE_H"], ns["Z_TOP"], ns["R_BASE"]
    BASE_KEEP = ns["PLATE_T"]           # 下部圆柱保留高度 = 母件顶板厚 (再厚会切进腔/45° 过渡区)
    Z_CUT = BASE_H - BASE_KEEP
    H = Z_TOP - Z_CUT

    _big = 2 * R_BASE + 10
    keep = m3d.Manifold.cube((_big, _big, H + 5)).translate((-_big / 2, -_big / 2, Z_CUT))
    coupon = intersect(parent, keep).translate((0, 0, -Z_CUT))

    # ===== 校核 =====
    assert coupon.status() == m3d.Error.NoError, f"试打件非流形: {coupon.status()}"
    assert len(coupon.decompose()) == 1, "件不是一整块"
    for z in (BASE_H + 1.0, ns["z_mid"], Z_TOP - ns["CHAMFER"] / 2):      # 螺纹段截面与母件同高度处逐一相同
        a_c, a_p = coupon.slice(z - Z_CUT).area(), parent.slice(z).area()
        assert abs(a_c - a_p) < 1e-6, f"Z={z} 截面与母件不一致 {a_c} vs {a_p}"
    a_bed = coupon.slice(1e-3).area()
    a_disk = ns["poly_area"](R_BASE, ns["BASE_SEG"])
    assert abs(a_bed - a_disk) < 1e-2, f"贴床面应为实心 Φ{2*R_BASE:g} 圆 {a_bed} vs {a_disk}"
    assert len(coupon.slice(1e-3).to_polygons()) == 1, "贴床面应为整圆 (不应有孔)"
    lower = intersect(parent, m3d.Manifold.cube((_big, _big, Z_CUT + 1)).translate((-_big / 2, -_big / 2, -1)))
    assert abs(coupon.volume() + lower.volume() - parent.volume()) < 1e-3 * parent.volume(), "切分体积对不上"

    # ===== 导出 STL (float32 合并顶点、丢掉退化碎三角; 函数来自母件) =====
    verts, tris, n_degen = ns["float32_clean_mesh"](coupon)
    suffix = "" if clear == PARENT_CLEAR else f"_c{clear:g}"
    out = Path(__file__).with_name(f"{STEM}{suffix}.stl")
    _hdr = f"thread_test of threaded_post_d50x70 clr{clear:g} cut Z{Z_CUT:g} H{H:g}".encode("ascii")
    assert len(_hdr) <= 80, f"STL 头 {len(_hdr)} 字节 > 80"
    with out.open("wb") as f:
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
    assert out.stat().st_size == 84 + len(tris) * 50, "STL 大小不对"

    vol = coupon.volume()
    _vf = verts.astype(float)
    print(f"wrote {out}  ({len(tris)} triangles; float32 清理丢掉退化碎三角 {n_degen})")
    print(f"  bbox Z: {verts[:,2].min():.3f} .. {verts[:,2].max():.3f};  外轮廓最大半径 {np.hypot(_vf[:, 0], _vf[:, 1]).max():.6f}")
    print(f"  母件切于 Z={Z_CUT:g}: 圆片 Φ{2*R_BASE:g}×{BASE_KEEP:g} + 螺纹柱高 {Z_TOP-BASE_H:g}")
    print(f"  螺纹: 间隙 {clear:g} ⇒ 建模大径 Φ{2*ns['R_MAJ']:.2f} / 小径 Φ{2*ns['R_MIN']:.2f}, P{ns['PITCH']:g}, "
          f"顶倒角 C{ns['CHAMFER']:g}, " + (f"内孔 Φ{2*ns['R_BORE']:g}" if ns["R_BORE"] > 0 else "螺纹柱实心"))
    print(f"  volume {vol:.2f} mm^3, PETG 实心约 {vol*1.27e-3:.1f} g")


for c in (PARENT_CLEAR,) + tuple(x for x in EXTRA_CLEARANCES if x != PARENT_CLEAR):
    build(c)
