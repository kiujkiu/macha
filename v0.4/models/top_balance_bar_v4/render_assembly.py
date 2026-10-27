import sys, runpy, io, contextlib, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fm.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.sans-serif']=['SimHei']; plt.rcParams['axes.unicode_minus']=False
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pathlib import Path
V4 = Path("/mnt/d/claude_workspace/macha/pov3d/v0.4")
sys.path.insert(0, str(V4/"models/top_balance_bar_v4")); import build_stl as B
sys.argv=["a","--ecc"]
with contextlib.redirect_stdout(io.StringIO()): g = runpy.run_path(str(V4/"assembly_v4.py"), run_name="asm")
ROT = g["ROTOR_ROT"]+g["V3_SCR_ROT"]
def tris(m):
    mm=m.to_mesh(); v=np.asarray(mm.vert_properties)[:,:3]; return v[np.asarray(mm.tri_verts)]
Z1=B.Z0+B.T
bar = B.build()
hw = None
for (x,y) in B.MOUNT_XY:      # 安装: 大扁头在压条底, 杆, 螺母在横梁顶
    for m in (B.cyl(12.5,x,y,258.45,260.95), B.cyl(6,x,y,260.95,Z1+7), B.cyl(11.5,x,y,Z1,Z1+5,6)):
        hw = m if hw is None else hw + m
cw = None                     # 示例配重: -X 外孔 M6×30 + 4 螺母 (往下叠)
x,y = -78.0, 0.0
for m in [B.cyl(12.5,x,y,Z1,Z1+2.5), B.cyl(6,x,y,Z1-30+2.5,Z1)] + [B.cyl(11.5,x,y,B.Z0-5*(k+1),B.Z0-5*k,6) for k in range(4)]:
    cw = m if cw is None else cw + m
extra = [(bar,"#e8702a",1.0),(hw,"#606060",1.0),(cw,"#c02020",1.0)]
extra = [(tris(m.rotate((0,0,ROT))),c,a) for m,c,a in extra]
def col(n):
    if n.startswith("post") or "frame" in n or "688" in n: return "#9aa0a6",.35
    if "screen" in n.lower() or "屏" in n: return "#2b2b2b",.25
    if "shroud" in n: return "#7fb3d5",.25
    if "top_cap" in n: return "#c8c8c8",.9
    if "sensor" in n: return "#4a90d9",.9
    if "vane" in n: return "#d0a020",.9
    return "#b0b0b0",.25
fig = plt.figure(figsize=(16,9))
views = [((-110,110),(-110,110),(0,320),15,40,"整机 (V0.4 偏心装 + 顶部配重横梁)"),
         ((-95,95),(-95,95),(200,310),22,40,"顶部特写: 橙=横梁 / 灰=安装 M6 / 红=示例配重 (r78, M6×30+4 螺母往下叠)")]
for i,(xl,yl,zl,el,az,title) in enumerate(views):
    ax = fig.add_subplot(1,2,i+1,projection="3d")
    for n,t in g["parts"]:
        if i==1:
            c = t.reshape(-1,3); 
            if c[:,2].max() < zl[0]: continue
            t = t[(t[...,2].max(1) > zl[0])]
        cc,a = col(n)
        ax.add_collection3d(Poly3DCollection(t,facecolor=cc,edgecolor="none",alpha=a))
    for t,c,a in extra:
        if i==1: t = t[(t[...,2].max(1) > zl[0])]
        ax.add_collection3d(Poly3DCollection(t,facecolor=c,edgecolor="none",alpha=a))
    ax.set_xlim(*xl); ax.set_ylim(*yl); ax.set_zlim(*zl)
    ax.set_box_aspect((xl[1]-xl[0], yl[1]-yl[0], zl[1]-zl[0])); ax.view_init(el,az); ax.set_title(title, fontsize=11)
    ax.set_axis_off()
plt.tight_layout(); out=V4/"models/top_balance_bar_v4/top_balance_bar_v4_assembly_preview.png"; plt.savefig(out,dpi=110); print(out)
