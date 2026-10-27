import sys, runpy, io, contextlib, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pathlib import Path
from matplotlib import font_manager as _fm; _fm.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.sans-serif']=['SimHei']; plt.rcParams['axes.unicode_minus']=False
V4 = Path("/mnt/d/claude_workspace/macha/pov3d/v0.4")
sys.path.insert(0, str(V4/"models/top_balance_bar_v4")); import build_stl as B
sys.argv=["a","--ecc"]
with contextlib.redirect_stdout(io.StringIO()): g = runpy.run_path(str(V4/"assembly_v4.py"), run_name="asm")
ROT = g["ROTOR_ROT"]+g["V3_SCR_ROT"]
def tris(m):
    mm=m.to_mesh(); v=np.asarray(mm.vert_properties)[:,:3]; return v[np.asarray(mm.tri_verts)]
def unrot(t):  # 回到压条零件系看
    a=np.radians(-ROT); c,s=np.cos(a),np.sin(a); t=t.copy(); x,y=t[...,0].copy(),t[...,1].copy(); t[...,0]=c*x-s*y; t[...,1]=s*x+c*y; return t
show = {"top_cap_v3_1_1 (rotor)":"#bbbbbb","sensor_module":"#4a90d9","vane_slider_v4":"#d0a020","standoff Φ8×40 (rotor)":"#888888"}
fig = plt.figure(figsize=(15,7))
for i,(el,az,title) in enumerate(((90,-90,"俯视 (压条零件系, +X=屏偏心侧)"),(22,-60,"轴测"))):
    ax = fig.add_subplot(1,2,i+1,projection="3d")
    for n,t in g["parts"]:
        if n in show:
            ax.add_collection3d(Poly3DCollection(unrot(t),facecolor=show[n],edgecolor="none",alpha=.6))
    bt = tris(B.build())
    ax.add_collection3d(Poly3DCollection(bt,facecolor="#e8702a",edgecolor="none",alpha=.95))
    th=np.linspace(0,2*np.pi,200)
    for r,c in ((42.43,"#d0a020"),(45.41,"#d0a020"),(85,"k")):
        ax.plot(r*np.cos(th),r*np.sin(th),np.full_like(th,B.Z0),c,lw=.8,ls="--")
    for (x,y) in B.CW_XY:
        ax.plot(x+6.25*np.cos(th),y+6.25*np.sin(th),np.full_like(th,B.Z0+B.T+.1),"r",lw=1)
    ax.set_xlim(-90,90); ax.set_ylim(-90,90); ax.set_zlim(230,310); ax.set_box_aspect((180,180,80))
    ax.view_init(el,az); ax.set_title(title, fontname="SimHei" if False else None)
plt.tight_layout(); out=V4/"models/top_balance_bar_v4/top_balance_bar_v4_preview.png"; plt.savefig(out,dpi=110); print(out)
