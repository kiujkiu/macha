import sys, runpy, math, numpy as np, manifold3d as m3d
from pathlib import Path
V4 = Path("/mnt/d/claude_workspace/macha/pov3d/v0.4")
sys.path.insert(0, str(V4/"models/top_balance_bar_v4"))
import build_stl as B
sys.argv = ["assembly_v4.py", "--ecc"]
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(str(V4/"assembly_v4.py"), run_name="asm")
parts = g["parts"]; ROT = g["ROTOR_ROT"] + g["V3_SCR_ROT"]

def to_man(tris):
    v = tris.reshape(-1,3)
    uv, inv = np.unique(np.round(v,5), axis=0, return_inverse=True)
    m = m3d.Manifold(m3d.Mesh(vert_properties=uv.astype(np.float32), tri_verts=inv.reshape(-1,3).astype(np.uint32)))
    if m.volume() < 0 or m.status() != m3d.Error.NoError:
        m = m3d.Manifold(m3d.Mesh(vert_properties=uv.astype(np.float32), tri_verts=inv.reshape(-1,3)[:, ::-1].astype(np.uint32)))
    return m

cyl = B.cyl
Z1 = B.Z0 + B.T
bar = B.build()
hw = []
for (x,y) in B.MOUNT_XY:
    hw.append(("mount head", cyl(12.6,x,y,258.45,260.95)))
    hw.append(("mount nut+tail", cyl(11.6,x,y,Z1,Z1+7)))
for (x,y) in B.CW_XY:
    hw.append(("cw stack above", cyl(12.6,x,y,Z1,Z1+14)))
    hw.append(("cw stack below", cyl(12.6,x,y,Z1-6-60,B.Z0)))
mov = [("bar", bar)] + hw
mov = [(n, m.rotate((0,0,ROT))) for n,m in mov]

static_kw = ("post", "frame", "vane", "688")
stat, rot = [], []
for n,t in parts:
    (stat if any(k in n for k in static_kw) else rot).append((n, to_man(t)))
print("static:", [n for n,_ in stat])
# snapshot vs rotor parts
worst = 0
for mn, mm in mov:
    for rn, rm in rot:
        v = (mm ^ rm).volume()
        if v > 1e-3:
            print(f"  CLASH snapshot {mn} x {rn}: {v:.2f} mm3"); worst = max(worst, v)
# hardware vs bar itself is intended contact; skip. sweep vs static
mov_u = mov[0][1]
for _,m in mov[1:]: mov_u += m
smax = 0; sarg = None
for k in range(180):
    mr = mov_u.rotate((0,0,2.0*k))
    for sn, sm in stat:
        v = (mr ^ sm).volume()
        if v > smax: smax, sarg = v, (2.0*k, sn)
print(f"snapshot worst {worst:.3f}; sweep 2deg x180 worst {smax:.3f} {sarg}")
# min gap: vane radial band / frame bottom
for sn, sm in stat:
    bb = sm.bounding_box()
    print(f"  {sn:28s} Z {bb[2]:.2f}..{bb[5]:.2f}")
# 灵敏度探针: r44 处的螺母叠高应扫到刀片; 横梁顶 +17 应扫到架子
for tag, probe in (("r44 叠高14", cyl(11.6,-44,0,Z1,Z1+14)), ("r66 叠高17", cyl(11.6,-66,0,Z1,Z1+17))):
    pm = probe.rotate((0,0,ROT)); hit = 0
    for k in range(180):
        pr = pm.rotate((0,0,2.0*k))
        hit = max(hit, max((pr ^ sm).volume() for _, sm in stat))
    print(f"probe {tag}: max {hit:.2f} mm3 (应 >0)")
# 余量: 螺母外角到刀片内缘, 叠层顶到架底
print(f"nut corner r {min(B.CW_RS)-6.25:.1f} vs vane r 45.41; stack top {Z1+14:.2f} vs frame 290 / vane tip 280")
