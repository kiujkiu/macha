"""top_cap_v4 干涉校核: 压条+配重五金 快照 vs 转子件, 全周扫掠 vs 静止件 (挡片/架/柱/688)。
用法: python check_clash.py [--ecc]"""
import sys, runpy, io, contextlib, numpy as np, manifold3d as m3d
from pathlib import Path
V4 = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent))
with contextlib.redirect_stdout(io.StringIO()):
    import build_stl as B
ecc = "--ecc" in sys.argv
sys.argv = ["assembly_v4.py"] + (["--ecc"] if ecc else [])
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(str(V4 / "assembly_v4.py"), run_name="asm")
parts = g["parts"]; ROT = g["ROTOR_ROT"] + g["V3_SCR_ROT"]

def to_man(tris):
    v = tris.reshape(-1, 3)
    uv, inv = np.unique(np.round(v, 5), axis=0, return_inverse=True)
    f = inv.reshape(-1, 3).astype(np.uint32)
    m = m3d.Manifold(m3d.Mesh(vert_properties=uv.astype(np.float32), tri_verts=f))
    if m.volume() < 0 or m.status() != m3d.Error.NoError:
        m = m3d.Manifold(m3d.Mesh(vert_properties=uv.astype(np.float32), tri_verts=f[:, ::-1].copy()))
    return m

cyl = B.cyl; Z0, Z1 = B.BAR_Z0, B.BAR_Z1
STACK_UP = 290.0 - 2.0 - Z1          # 往上叠到架臂底留 2
NUT_D = float(next((a.split("=")[1] for a in sys.argv if a.startswith("--nut=")), 12.6))  # 五金外接圆径
hw = []
for y in B.WING_CW_YS:
    hw.append(("cw up", cyl(NUT_D, B.WING_CW_X, y, Z1, Z1 + STACK_UP)))
    hw.append(("cw down", cyl(NUT_D, B.WING_CW_X, y, Z0 - 40, Z0)))
cap = [n for n in parts if n[0].startswith("top_cap_v4")][0]
capm = to_man(cap[1])
hwm = m3d.Manifold()
for _, m in hw: hwm += m.rotate((0, 0, ROT))
stat_kw = ("post", "frame", "vane", "688")
stat = [(n, to_man(t)) for n, t in parts if any(k in n for k in stat_kw)]
rot = [(n, to_man(t)) for n, t in parts if not any(k in n for k in stat_kw) and not n.startswith("top_cap_v4")]
worst = 0
for rn, rm in rot:
    for tag, mm in (("cap", capm), ("hw", hwm)):
        v = (mm ^ rm).volume()
        if v > 1e-3 and not (tag == "cap" and ("M6x20" in rn or "standoff" in rn or "sensor" in rn)):
            print(f"  CLASH snapshot {tag} x {rn}: {v:.2f}"); worst = max(worst, v)
mov = capm + hwm
smax, sarg = 0, None
for k in range(180):
    mr = mov.rotate((0, 0, 2.0 * k))
    for sn, sm in stat:
        v = (mr ^ sm).volume()
        if v > smax: smax, sarg = v, (2.0 * k, sn)
print(f"{'偏心' if ecc else '居中'}: 快照最差 {worst:.3f} mm3; 全周扫掠(2°×180) 最差 {smax:.3f} {sarg}; 五金上叠到 Z{Z1+STACK_UP:.2f}")
# 探针: 草图原位 r46.6 叠高 10 应扫到挡片 (证明检测有效)
pm = cyl(12.6, -46.6, 0, Z1, Z1 + 13).rotate((0, 0, ROT)); hit = 0
vane = [sm for sn, sm in stat if "vane" in sn][0]
for k in range(180): hit = max(hit, (pm.rotate((0, 0, 2.0 * k)) ^ vane).volume())
print(f"探针 r46.6 头叠高13 vs 挡片: {hit:.2f} mm3 (应 >0)")
