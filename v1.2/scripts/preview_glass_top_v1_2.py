"""玻璃上 (顶盖) 预览 PNG: 过轴剖面 (玻璃罩 / 玻璃上环 / 圆环玻璃 / 中心堵头) + 等轴测 (切掉 1/4)。
    cd v1.2/scripts && ../../.venv/bin/python preview_glass_top_v1_2.py
输出 models/glass_top_v1_2/glass_top_v1_2_{section,iso}.png (只读 build_v1_2, 不改模型)。"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import build_v1_2 as B
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS

from matplotlib import font_manager
font_manager.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.family'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = False
OUT = B.V12 / 'models' / 'glass_top_v1_2'; OUT.mkdir(parents=True, exist_ok=True)
C = dict(tube='#BFE3F5', ring='#7FB3D5', disc='#D6EAF8', hub='#2E86C1')

# ---------- 剖面 (旋转体, 直接用 r-z 轮廓; 堵头 0° 剖在爪上不在槽上) ----------
def rect(r0, r1, z0, z1): return [(r0, z0), (r1, z0), (r1, z1), (r0, z1)]
items = [('玻璃罩 OD200×5', rect(B.GL_OD / 2 - B.GL_T, B.GL_OD / 2, B.Z_GT - 25, B.Z_GT), C['tube'], '#5D8AA8'),
         ('玻璃上 glass_top_v1_2', B.GT_RZ, C['ring'], '#1B4F72'),
         (f'圆环玻璃 OD{B.GD_OD:g}×ID{B.GD_ID:g}×{B.GD_T:g}', rect(B.GD_ID / 2, B.GD_OD / 2, B.GD_Z0, B.GD_Z1), C['disc'], '#5D8AA8'),
         ('中心堵头 glass_top_hub_v1_2', B.GH_RZ, C['hub'], '#0B3C5D')]
fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.25])
axes = [fig.add_subplot(gs[0, :]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])]
wins = [(-115, 115, B.Z_GT - 25, B.GT_Z1 + 6), (80, 113, B.GT_Z0 - 3, B.GT_Z1 + 3), (-2, 20, B.GT_Z0 - 1, B.GD_Z1 + B._fl_t + 2)]
for k, ax in enumerate(axes):
    for name, rz, fc, ec in items:
        for s in (1, -1):
            if k == 0 or s == 1:
                ax.add_patch(Polygon([(s * r, z) for r, z in rz], closed=True, fc=fc, ec=ec, lw=0.8, label=name if s == 1 else None, hatch='//' if 'glass_top' in name and k else None))
    ax.axvline(0, color='k', lw=0.5, ls='-.')
    ax.axhline(B.Z_GT, color='#999', lw=0.4, ls=':')
    ax.set_xlim(*wins[k][:2]); ax.set_ylim(*wins[k][2:]); ax.set_aspect('equal'); ax.grid(alpha=0.25)
    ax.set_xlabel('r / mm'); ax.set_ylabel('Z / mm')
axes[0].set_title(f'POV3D V1.2 玻璃上 过轴剖面 (玻璃上端 Z{B.Z_GT:g}; 环 Z{B.GT_Z0:g}–{B.GT_Z1:g}; 玻璃 Z{B.GD_Z0:g}–{B.GD_Z1:g}; 堵头{" 带 688 轴承窝" if B.GT_BEARING else " 实心 (无轴承)"})')
axes[0].legend(loc='lower center', ncol=4, fontsize=9)
a = axes[1]; a.set_title('外缘: 内卡 / 外卡 / 玻璃窝 + 托台')
for txt, xy in [(f'内卡 r{B._gin:g}–{B.gi:g}\n深 {B.GT_DEPTH:g}', (B.gi - 2, B.GT_Z0 + 3)), (f'外卡 r{B.go:g}–{B.SH_OUT:g}\n斜面 {B.GT_CONE_DEG:.0f}°', (B.go + 2.5, B.GT_Z0 + 2)),
                (f'窝 r{B.GD_POCKET_R:g}\n托台 r{B.GT_LEDGE_R:g}', (B.GT_LEDGE_R - 4.8, B.GD_Z0 - 4.6)), (f'玻璃顶低 {B.GD_RECESS:g}', (B.GD_POCKET_R - 9, B.GT_Z1 + 1))]:
    a.annotate(txt, xy, fontsize=8)
a = axes[2]; a.set_title(f'中心: 堵头 6 爪 (爪长 {B.GH_L:.1f}, 倒钩 {B.GH_BARB:g}, 应变≈{B.GH_STRAIN * 100:.1f}%)')
a.annotate(f'Φ{B.GH_FL_D:g} 法兰压玻璃顶', (6, B.GD_Z1 + B._fl_t + 0.5), fontsize=8)
a.annotate(f'30° 倒钩 r{B._rb:g}\n钩玻璃下面', (11.3, B._zc - 1.5), fontsize=8)
a.annotate(f'爪 r{B.GH_R0:g}–{B.GH_R1:g}\n(孔 r{B.GD_ID / 2:g})', (0.5, B.GD_Z0 + 4), fontsize=8)
fig.tight_layout(); fig.savefig(OUT / 'glass_top_v1_2_section.png', dpi=130); plt.close(fig)

# ---------- 等轴测 (切掉 +X+Y 1/4) ----------
def mesh(sh, defl=0.3):
    BRepMesh_IncrementalMesh(sh, defl, False, 0.4, True)
    tris = []; e = TopExp_Explorer(sh, TopAbs_FACE)
    while e.More():
        f = TopoDS.Face(e.Current()); L = TopLoc_Location(); tr = BRep_Tool.Triangulation_s(f, L)
        if tr is not None:
            t = L.Transformation()
            V = np.array([[p.X(), p.Y(), p.Z()] for p in (tr.Node(i).Transformed(t) for i in range(1, tr.NbNodes() + 1))])
            T = np.array([[tr.Triangle(i).Value(j) for j in (1, 2, 3)] for i in range(1, tr.NbTriangles() + 1)]) - 1
            if f.Orientation() == TopAbs_REVERSED: T = T[:, [0, 2, 1]]
            tris.append(V[T])
        e.Next()
    return np.vstack(tris)
q = B.gbox(0, 0, 0, 200, 200, 400)
tube_top = B.op(B.BRepAlgoAPI_Common, B.tube, B.cyl(0, 0, 400, B.Z_GT - 40, B.Z_GT + 1))
parts = [(B.cut(tube_top, q), C['tube'], 0.35), (B.cut(B.glass_top, q), C['ring'], 1.0), (B.cut(B.glass_disc, q), C['disc'], 0.55), (B.cut(B.glass_top_hub, q), C['hub'], 1.0)]
fig = plt.figure(figsize=(12, 10)); ax = fig.add_subplot(111, projection='3d')
light = np.array([0.3, -0.5, 0.8]); light /= np.linalg.norm(light)
for sh, col, al in parts:
    T = mesh(sh)
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    sh_ = 0.45 + 0.55 * np.clip(n @ light, 0, 1)
    rgb = np.array(matplotlib.colors.to_rgb(col))
    pc = Poly3DCollection(T, facecolors=np.clip(rgb[None] * sh_[:, None], 0, 1), alpha=al, linewidths=0)
    ax.add_collection3d(pc)
ax.set_xlim(-110, 110); ax.set_ylim(-110, 110); ax.set_zlim(B.Z_GT - 40, B.Z_GT + 10)
ax.set_box_aspect((220, 220, 50), zoom=1.35); ax.view_init(elev=28, azim=-60); ax.set_axis_off()
ax.set_title('POV3D V1.2 玻璃上 (切 1/4): 玻璃罩上端 + 玻璃上环 + 圆环玻璃 + 中心堵头')
fig.tight_layout(); fig.savefig(OUT / 'glass_top_v1_2_iso.png', dpi=110, bbox_inches='tight'); plt.close(fig)
print('wrote', OUT / 'glass_top_v1_2_section.png', OUT / 'glass_top_v1_2_iso.png')
