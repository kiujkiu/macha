# -*- coding: utf-8 -*-
"""玻璃下 上段 + 下段 组合 2D 图 (11-16): 过螺丝孔 22.5° 的竖剖面 (整宽 + 局部放大) + 俯视孔位。
读 models/*/STEP (装配坐标), 不 import build_v1_2 (太慢); 螺丝/螺母按参数画。
    cd v1.2/scripts && ../../.venv/bin/python drawing_glass_split_asm_v1_2.py
→ models/glass_shroud_upper_v1_2/glass_split_组合图.{pdf,png}"""
import math, re
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle, Polygon, Circle
from matplotlib.collections import PolyCollection
from OCP.STEPControl import STEPControl_Reader
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
font_manager.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.family'] = 'SimHei'; plt.rcParams['axes.unicode_minus'] = False

V12 = Path(__file__).resolve().parents[1]
src = (V12 / 'scripts' / 'build_v1_2.py').read_text(encoding='utf-8')
def num(name):
    m = re.search(rf'^{name}\s*=\s*([^#\n]+)', src, re.M); return m.group(1).strip()
Z_G = 53.08; Z_VIEW0 = 73.08; SPLIT_Z = 32.0
JN_R, ANG = 98.5, 22.5
JN_D, JN_CB = 4.5, 8.8; JN_L, JN_HH = 50.0, 1.8
JN_BEAR = Z_G - float(num('JN_BEAR').split('-')[1]); JN_TIP = JN_BEAR - JN_L
JN_NUT_FD, JN_NUT_FZ, JN_NUT_AF, JN_NUT_H = 10.1, 1.8, 7.1, 4.3; JN_NUT_Z1 = 0.3 + JN_NUT_H

def load(p):
    r = STEPControl_Reader(); r.ReadFile(str(p)); r.TransferRoots(); return r.OneShape()

def section(shape, ang):
    a = math.radians(ang); n = gp_Dir(-math.sin(a), math.cos(a), 0)
    f = BRepBuilderAPI_MakeFace(gp_Pln(gp_Pnt(0, 0, 0), n), -400, 400, -400, 400).Face()
    c = BRepAlgoAPI_Common(shape, f); c.Build(); s = c.Shape()
    BRepMesh_IncrementalMesh(s, 0.05)
    tris = []; e = TopExp_Explorer(s, TopAbs_FACE)
    while e.More():
        fc = TopoDS.Face(e.Current()); loc = TopLoc_Location(); t = BRep_Tool.Triangulation_s(fc, loc)
        if t is not None:
            tr = loc.Transformation()
            P = [t.Node(i).Transformed(tr) for i in range(1, t.NbNodes() + 1)]
            U = [(p.X() * math.cos(a) + p.Y() * math.sin(a), p.Z()) for p in P]
            for i in range(1, t.NbTriangles() + 1):
                i1, i2, i3 = t.Triangle(i).Get(); tris.append([U[i1 - 1], U[i2 - 1], U[i3 - 1]])
        e.Next()
    return tris

M = V12 / 'models'
parts = [('下段 glass_shroud_lower_v1_2', M / 'glass_shroud_lower_v1_2/glass_shroud_lower_v1_2.step', '#E8C99A'),
         ('上段 glass_shroud_upper_v1_2', M / 'glass_shroud_upper_v1_2/glass_shroud_upper_v1_2.step', '#A9CCE3'),
         ('外卡环 glass_clamp_ring_v1_2', M / 'glass_clamp_ring_v1_2/glass_clamp_ring_v1_2.step', '#CFD8DC'),
         ('底盘 base_disc', M / 'base_disc_v1_2/base_disc_v1_2.step', '#E0E0E0')]
secs = [(n, section(load(p), ANG), c) for n, p, c in parts if p.exists()]

def draw_hw(ax, sgn):
    r = sgn * JN_R
    ax.add_patch(Rectangle((r - JN_D / 2 + 0.25, JN_TIP), JN_D - 0.5, JN_L, color='#455A64', zorder=5))
    ax.add_patch(Rectangle((r - 8.5 / 2, JN_BEAR), 8.5, JN_HH, color='#263238', zorder=6))
    z0 = JN_NUT_Z1 - JN_NUT_H
    ax.add_patch(Rectangle((r - 9.7 / 2, z0), 9.7, 1.2, color='#616161', zorder=6))
    ax.add_patch(Rectangle((r - 6.9 / 2 * 1.155 / 1.155, z0 + 1.2), 6.9, JN_NUT_H - 1.2, color='#757575', zorder=6))
    ax.add_patch(Rectangle((r * 1 - 0 + (95 - JN_R if sgn > 0 else -100 + JN_R) * 0 + (95 if sgn > 0 else -100) - r, Z_G), 5, 30, color='#D6EAF8', ec='#5DADE2', zorder=4))

fig = plt.figure(figsize=(16.54, 11.69))   # A3
fig.suptitle(f'玻璃下 上段 + 下段 组合图 (V1.2, 11-16)  —  8× M4×{JN_L:g} 超薄头 (头 Φ8.5×1.8) 穿通 + 下段底面 M4 法兰螺母', fontsize=15, y=0.975)
# 整宽剖面
ax = fig.add_axes([0.04, 0.52, 0.92, 0.40])
for n, tris, c in secs:
    ax.add_collection(PolyCollection(tris, facecolors=c, edgecolors=c, linewidths=0.2))
for s in (1, -1): draw_hw(ax, s)
ax.set_xlim(-115, 115); ax.set_ylim(-8, 80); ax.set_aspect('equal'); ax.grid(alpha=0.25)
ax.set_title(f'剖面 A-A (过 {ANG:g}° / {ANG + 180:g}° 两个螺丝孔的竖剖面, 1:1 比例按图宽缩放)', fontsize=12)
ax.axhline(SPLIT_Z, color='r', ls='--', lw=0.8); ax.text(-112, SPLIT_Z + 0.8, f'分缝 Z{SPLIT_Z:g}', color='r', fontsize=9)
ax.axhline(Z_G, color='#1F77B4', ls=':', lw=0.8); ax.text(-112, Z_G + 0.8, f'玻璃底 Z{Z_G:g}', color='#1F77B4', fontsize=9)
ax.text(-60, 10, '下段 Z0→32 (浅黄)', fontsize=11); ax.text(-60, 42, f'上段 Z32→{Z_G:g} (+ 内卡到 Z{Z_VIEW0:g}) (浅蓝)', fontsize=11)
ax.text(30, -5.5, '底盘', fontsize=10)
ax.set_xlabel('r (mm, 剖面内, 中心 = 转轴)'); ax.set_ylabel('Z (mm)')
# 局部放大
bx = fig.add_axes([0.04, 0.05, 0.45, 0.42])
for n, tris, c in secs:
    bx.add_collection(PolyCollection(tris, facecolors=c, edgecolors=c, linewidths=0.3))
draw_hw(bx, 1)
bx.set_xlim(86, 112); bx.set_ylim(-7, 60); bx.set_aspect('equal'); bx.grid(alpha=0.3)
bx.set_title('局部 B (放大, 一个螺丝孔)', fontsize=12)
def dim(ax_, x0, x1, y, t, vert=False):
    if vert:
        ax_.annotate('', xy=(y, x0), xytext=(y, x1), arrowprops=dict(arrowstyle='<->', lw=0.8)); ax_.text(y + 0.4, (x0 + x1) / 2, t, fontsize=8.5, va='center')
    else:
        ax_.annotate('', xy=(x0, y), xytext=(x1, y), arrowprops=dict(arrowstyle='<->', lw=0.8)); ax_.text((x0 + x1) / 2, y + 0.5, t, fontsize=8.5, ha='center')
dim(bx, JN_R - JN_CB / 2, JN_R + JN_CB / 2, Z_G + 1.2, f'沉孔 Φ{JN_CB:g} 深 {Z_G - JN_BEAR:.1f}')
dim(bx, JN_R - JN_NUT_FD / 2, JN_R + JN_NUT_FD / 2, -5.5, f'法兰窝 Φ{JN_NUT_FD:g} 深 {JN_NUT_FZ:g}')
dim(bx, 0, JN_NUT_Z1, 105.5, f'螺母窝深 {JN_NUT_Z1:g}\n(六角对边 {JN_NUT_AF:g})', vert=True)
dim(bx, JN_TIP, JN_BEAR, 88.5, f'M4×{JN_L:g}\n支承 Z{JN_BEAR:.2f}\n尾 Z{JN_TIP:.2f}', vert=True)
bx.text(JN_R + 5, 20, f'通孔 Φ{JN_D:g}\n(上下段)', fontsize=9)
bx.text(96, 56.5, '玻璃 (r95–100)', fontsize=9, color='#2874A6')
bx.set_xlabel('r (mm)'); bx.set_ylabel('Z (mm)')
# 俯视孔位 + 说明
cx = fig.add_axes([0.53, 0.05, 0.22, 0.42]); cx.set_aspect('equal'); cx.axis('off')
cx.set_title('俯视: 8 孔位置', fontsize=12)
cx.add_patch(Circle((0, 0), 110, fill=False, lw=1)); cx.add_patch(Circle((0, 0), 90.8, fill=False, lw=1, ls='--'))
cx.add_patch(Circle((0, 0), 97.5, fill=False, lw=6, color='#D6EAF8'))
for k in range(8):
    a = math.radians(ANG + 45 * k); x, y = JN_R * math.cos(a), JN_R * math.sin(a)
    cx.add_patch(Circle((x, y), JN_CB / 2, color='#263238')); cx.text(1.18 * x, 1.18 * y, f'{ANG + 45 * k:g}°', ha='center', va='center', fontsize=8)
cx.plot([0, 120 * math.cos(math.radians(ANG))], [0, 120 * math.sin(math.radians(ANG))], 'r-.', lw=0.8); cx.text(70, 45, 'A', color='r')
cx.text(0, 0, f'r{JN_R:g}\n22.5°+45°×k\n(+X = XT60 侧)', ha='center', va='center', fontsize=9)
cx.set_xlim(-135, 135); cx.set_ylim(-135, 135)
dx = fig.add_axes([0.77, 0.05, 0.21, 0.42]); dx.axis('off')
txt = f'''紧固件 (按用户实物):
 · M4×{JN_L:g} 超薄头内六角 ×8
   头 Φ8.5×1.8, 2.5 六角扳手
 · M4 法兰螺母 304 ×8
   法兰 Φ9.7, 对边 6.9, 厚 4.3

尺寸:
 · 上段: Φ{JN_D:g} 通, 顶面沉孔 Φ{JN_CB:g} 深 {Z_G - JN_BEAR:.1f}
   头顶 Z{JN_BEAR + JN_HH:.2f}, 玻璃端面下 {Z_G - JN_BEAR - JN_HH:.1f}
 · 下段: Φ{JN_D:g} 通, 底面法兰圆窝
   Φ{JN_NUT_FD:g} 深 {JN_NUT_FZ:g} + 六角窝 {JN_NUT_AF:g} 到深 {JN_NUT_Z1:g}
   螺母 Z0.3..{JN_NUT_Z1:g} (法兰朝下, 防转)
 · 尾 Z{JN_TIP:.2f}, 啮合 {JN_NUT_Z1 - JN_TIP:.2f}

装配顺序:
 1. 8 个法兰螺母法兰朝下放进下段底面窝
 2. 下段放上底盘 (底盘托住螺母)
 3. 上段扣上 (止口凸筋 r104–106 对位)
 4. 从上段顶面拧 8 颗 M4×{JN_L:g}
 5. 放玻璃, 装外卡环

注: 沉孔 Φ{JN_CB:g} 下切内卡根 0.7 (只在玻璃座下 {Z_G - JN_BEAR:.1f}),
    离外卡环槽 0.9。'''
dx.text(0, 1, txt, va='top', fontsize=10, family='SimHei')
out = M / 'glass_shroud_upper_v1_2' / 'glass_split_组合图'
fig.savefig(str(out) + '.pdf'); fig.savefig(str(out) + '.png', dpi=110)
print(out)
