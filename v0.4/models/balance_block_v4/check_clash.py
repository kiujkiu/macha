"""balance_block_v4 干涉校核: 9 个可放位置 × (块 + 五金包络) vs 转子件快照, 全周扫掠 vs 静止件。
五金包络: M6 螺母/垫圈叠 Φ12.6 往上 STACK6, 微调 M3 螺母 Φ6.6 往上 STACK3, 锁紧头 Φ7.5 在沉孔里。
用法: python check_clash.py [--ecc]"""
import sys, runpy, io, contextlib, math, numpy as np, manifold3d as m3d
from pathlib import Path
HERE = Path(__file__).parent; V4 = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import build_stl as B, balance_params_v4 as BP
ecc = "--ecc" in sys.argv
STACK6, STACK3 = 30.0, 12.0
sys.argv = ["assembly_v4.py", "--blk", "none"] + (["--ecc"] if ecc else [])
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(str(V4 / "assembly_v4.py"), run_name="asm")
parts = g["parts"]; ROT = g["ROTOR_ROT"] + g["V3_SCR_ROT"]; ZT = g["DISC_TOP"] + 50.0

def to_man(tris):
    v = tris.reshape(-1, 3)
    uv, inv = np.unique(np.round(v, 5), axis=0, return_inverse=True)
    f = inv.reshape(-1, 3).astype(np.uint32)
    m = m3d.Manifold(m3d.Mesh(vert_properties=uv.astype(np.float32), tri_verts=f))
    if m.volume() < 0 or m.status() != m3d.Error.NoError:
        m = m3d.Manifold(m3d.Mesh(vert_properties=uv.astype(np.float32), tri_verts=f[:, ::-1].copy()))
    return m

T = B.T
blk = B.build()
for x, y in B.M6: blk += B.cyl(12.6, x, y, T, T + STACK6)
for x, y in B.TRIM: blk += B.cyl(6.6, x, y, T, T + STACK3)
blk = blk.translate((0, 0, ZT))
stat_kw = ("post", "frame", "vane", "688")
stat = [(n, to_man(t)) for n, t in parts if any(k in n for k in stat_kw)]
rot = [(n, to_man(t)) for n, t in parts if not any(k in n for k in stat_kw)]
bad = 0
for c in BP.BLK_CENTERS:
    m = blk.rotate((0, 0, c + ROT))
    snap = [(n, (m ^ rm).volume()) for n, rm in rot]
    snap = [(n, v) for n, v in snap if v > 1e-3]
    sw = 0.0
    for k in range(0, 360, 3):
        mr = m.rotate((0, 0, k))
        sw = max([sw] + [(mr ^ sm).volume() for _, sm in stat])
    r = np.hypot(*np.asarray(m.to_mesh().vert_properties)[:, :2].T).max()
    ok = not snap and sw < 1e-3 and r <= 85.001
    bad += not ok
    print(f"  中心 零件 {c:5.1f}° / 装配 {(c + ROT) % 360:5.1f}°: r_max {r:6.2f}  快照 {snap or '0'}  扫掠 {sw:.3f}  {'✓' if ok else '★'}")
# 探针: 块放 90° (屏缝上) 应该撞屏, 证明检测有效
pm = B.build().translate((0, 0, ZT)).rotate((0, 0, 90 + ROT))
hit = sum((pm ^ rm).volume() for n, rm in rot if "screen" in n)
print(f"{'偏心' if ecc else '居中'}: {len(BP.BLK_CENTERS) - bad}/{len(BP.BLK_CENTERS)} 位置通过; 探针 90° vs 屏 {hit:.1f} mm3 (应 >0)")
