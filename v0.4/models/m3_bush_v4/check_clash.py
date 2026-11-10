"""m3_bush_v4 干涉: 4 个孔位各放 上法兰+头 (条顶上 Φ12×6) / 下法兰+螺母 (条底下 Φ12×6), 快照 vs 转子件, 全周扫掠 vs 静止件。
用法: python check_clash.py [--ecc]"""
import sys, runpy, io, contextlib, numpy as np, manifold3d as m3d
from pathlib import Path
V4 = Path(__file__).resolve().parents[2]
ecc = "--ecc" in sys.argv
sys.argv = ["assembly_v4.py"] + (["--ecc"] if ecc else [])
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(str(V4 / "assembly_v4.py"), run_name="asm")
parts = g["parts"]; ROT = g["ROTOR_ROT"] + g["V3_SCR_ROT"]
Z0, Z1 = 260.95, 267.95
def to_man(tris):
    v = tris.reshape(-1, 3)
    uv, inv = np.unique(np.round(v, 5), axis=0, return_inverse=True)
    f = inv.reshape(-1, 3).astype(np.uint32)
    m = m3d.Manifold(m3d.Mesh(vert_properties=uv.astype(np.float32), tri_verts=f))
    if m.volume() < 0 or m.status() != m3d.Error.NoError:
        m = m3d.Manifold(m3d.Mesh(vert_properties=uv.astype(np.float32), tri_verts=f[:, ::-1].copy()))
    return m
cyl = lambda d, x, y, z0, z1: m3d.Manifold.cylinder(z1 - z0, d / 2, d / 2, 48, False).translate((x, y, z0))
HOLES = [(-11, 56), (-11, -56), (-55, 14), (-55, -14)]
hw = m3d.Manifold()
for x, y in HOLES:
    hw += cyl(12.0, x, y, Z1, Z1 + 6) + cyl(12.0, x, y, Z0 - 6, Z0)
hw = hw.rotate((0, 0, ROT))
stat_kw = ("post", "frame", "vane", "688")
stat = [(n, to_man(t)) for n, t in parts if any(k in n for k in stat_kw)]
rot = [(n, to_man(t)) for n, t in parts if not any(k in n for k in stat_kw)]
worst = []
for rn, rm in rot:
    v = (hw ^ rm).volume()
    if v > 1e-3: worst.append((rn, round(v, 2)))
smax, sarg = 0, None
for k in range(180):
    mr = hw.rotate((0, 0, 2.0 * k))
    for sn, sm in stat:
        v = (mr ^ sm).volume()
        if v > smax: smax, sarg = v, (2.0 * k, sn)
print(f"{'偏心' if ecc else '居中'}: 快照撞转子件 {worst or 0}; 全周扫掠最差 {smax:.3f} {sarg}")
# 探针: 同样五金放 r43 (−11,42) 应扫到挡片
pm = (cyl(12.0, -11, 42, Z1, Z1 + 13)).rotate((0, 0, ROT)); hit = 0
vane = [sm for sn, sm in stat if "vane" in sn][0]
for k in range(180): hit = max(hit, (pm.rotate((0, 0, 2.0 * k)) ^ vane).volume())
print(f"探针 (−11,42) 叠高 13 vs 挡片: {hit:.2f} mm3 (应 >0)")
