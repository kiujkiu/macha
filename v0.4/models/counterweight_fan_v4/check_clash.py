"""counterweight_fan_v4 干涉校核: 件 + 五金包络 (M6 螺母叠 Φ12.6×30, 微调 Φ6.6×12, 锁紧头 Φ7×3)
快照 vs 转子件, 全周扫掠 vs 静止件。用法: python check_clash.py [--ecc]"""
import sys, runpy, io, contextlib, numpy as np, manifold3d as m3d
from pathlib import Path
HERE = Path(__file__).parent; V4 = HERE.parents[1]
sys.path.insert(0, str(HERE)); import build_stl as B
ecc = "--ecc" in sys.argv
sys.argv = ["assembly_v4.py"] + (["--ecc"] if ecc else [])
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(str(V4 / "assembly_v4.py"), run_name="asm")
parts = g["parts"]; ROT = g["ROTOR_ROT"] + g["V3_SCR_ROT"]; ZT = g["DISC_TOP"] + 50.0
def to_man(tris):
    v = tris.reshape(-1, 3); uv, inv = np.unique(np.round(v, 5), axis=0, return_inverse=True)
    f = inv.reshape(-1, 3).astype(np.uint32)
    m = m3d.Manifold(m3d.Mesh(vert_properties=uv.astype(np.float32), tri_verts=f))
    if m.volume() < 0 or m.status() != m3d.Error.NoError:
        m = m3d.Manifold(m3d.Mesh(vert_properties=uv.astype(np.float32), tri_verts=f[:, ::-1].copy()))
    return m
T = B.T; mv = B.build()
for x, y in B.M6: mv += B.cyl(12.6, x, y, T, T + 30)
for x, y in B.TRIM: mv += B.cyl(6.6, x, y, T, T + 12)
for x, y in B.LOCK: mv += B.cyl(7.0, x, y, T, T + 3)
mv = mv.translate((0, 0, ZT)).rotate((0, 0, ROT))
kw = ("post", "frame", "vane", "688")
stat = [(n, to_man(t)) for n, t in parts if any(k in n for k in kw)]
rot = [(n, to_man(t)) for n, t in parts if not any(k in n for k in kw) and n != "counterweight_fan_v4"]
snap = [(n, round((mv ^ m).volume(), 3)) for n, m in rot]; snap = [x for x in snap if x[1] > 1e-3]
sw = max((mv.rotate((0, 0, k)) ^ m).volume() for k in range(0, 360, 3) for _, m in stat)
r = np.hypot(*np.asarray(mv.to_mesh().vert_properties)[:, :2].T).max()
probe = B.build().translate((0, 0, ZT)).rotate((0, 0, ROT + 30.0))   # 转 30° → 端头压进屏
hit = sum((probe ^ m).volume() for n, m in rot if "screen" in n)
print(f"{'偏心' if ecc else '居中'}: 快照 {snap or 0}; 全周扫掠最差 {sw:.3f}; r_max {r:.2f}; 探针(转30°) vs 屏 {hit:.1f} (应>0)")
