"""V1.2 底座玻纤板 base_fr4_v1_2 (用户 11-18): 打印底盘顶上加 FR4 (11-25 起 2 mm, 原 3), 板顶 = 装配 Z0, 板 Z-2..0。
孔形 = 底盘 (build_v1_2.disc) 在 Z-0.1 的截面: 所有通孔 + 原顶面槽 (电容槽/控制板背面让位/电机中央 Φ12 …) 全部做成通孔;
底面沉孔 / 铜螺母孔不进玻纤板。输出 models/base_fr4_v1_2/: STEP + DXF (板厂) + 图纸 PDF/PNG。

    cd v1.2/scripts && ../../.venv/bin/python fr4_base_v1_2.py
"""
import math, sys, collections
from pathlib import Path
import build_v1_2 as B
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.gp import gp_Vec, gp_Trsf
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE, TopAbs_WIRE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCP.BRepTools import BRepTools_WireExplorer
from OCP.GeomAbs import GeomAbs_Plane, GeomAbs_Circle, GeomAbs_Line
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
import ezdxf
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

OUT = Path(__file__).resolve().parent.parent / 'models' / 'base_fr4_v1_2'
OUT.mkdir(parents=True, exist_ok=True)

# 1 玻纤板形体 / 底面截面 都在 build_v1_2 里拆好 (fr4, FR4_FACE)
FR4_T = B.FR4_T
face, fr4 = B.FR4_FACE, B.fr4
p = GProp_GProps(); BRepGProp.VolumeProperties_s(fr4, p); VOL = p.Mass()

# 2 轮廓分类: 外圆 / 圆孔 / 其它开口 (槽)
from OCP.BRepTools import BRepTools
outer_wire = BRepTools.OuterWire_s(face)


def wire_edges(w):
    we = BRepTools_WireExplorer(TopoDS.Wire(w)); out = []
    while we.More():
        out.append(we.Current()); we.Next()
    return out


def edge_pts(e, n=None):
    from OCP.TopAbs import TopAbs_REVERSED
    c = BRepAdaptor_Curve(e); u0, u1 = c.FirstParameter(), c.LastParameter()
    if n is None: n = 1 if c.GetType() == GeomAbs_Line else max(8, int(abs(u1 - u0) * 60))
    P = [(c.Value(u0 + (u1 - u0) * i / n).X(), c.Value(u0 + (u1 - u0) * i / n).Y()) for i in range(n + 1)]
    return P[::-1] if e.Orientation() == TopAbs_REVERSED else P


holes, slots, loops = [], [], []
wx = TopExp_Explorer(face, TopAbs_WIRE)
while wx.More():
    w = wx.Current(); es = wire_edges(w)
    pts = []
    for e in es: pts += edge_pts(e)
    is_outer = w.IsSame(outer_wire)
    loops.append((is_outer, pts))
    if not is_outer:
        c0 = BRepAdaptor_Curve(es[0])
        if len(es) <= 2 and all(BRepAdaptor_Curve(e).GetType() == GeomAbs_Circle for e in es):
            ci = c0.Circle(); holes.append((round(ci.Location().X(), 2), round(ci.Location().Y(), 2), round(2 * ci.Radius(), 2)))
        else:
            xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
            slots.append((min(xs), min(ys), max(xs), max(ys)))
    wx.Next()

# 3 STEP
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
w = STEPControl_Writer(); w.Transfer(fr4, STEPControl_AsIs); w.Write(str(OUT / 'base_fr4_v1_2.step'))
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
BRepMesh_IncrementalMesh(fr4, 0.02, False, 0.2, True); _w = StlAPI_Writer(); _w.ASCIIMode = False; _w.Write(fr4, str(OUT / 'base_fr4_v1_2.stl'))

# 4 DXF (板顶面视图, 1:1 mm; 外形层 OUTLINE, 孔/槽层 CUT)
doc = ezdxf.new('R2010', setup=True); doc.units = ezdxf.units.MM; msp = doc.modelspace()
doc.layers.add('OUTLINE', color=7); doc.layers.add('CUT', color=1)
wx = TopExp_Explorer(face, TopAbs_WIRE)
while wx.More():
    wr = wx.Current(); lay = 'OUTLINE' if wr.IsSame(outer_wire) else 'CUT'
    for e in wire_edges(wr):
        c = BRepAdaptor_Curve(e); ty = c.GetType(); u0, u1 = c.FirstParameter(), c.LastParameter()
        if ty == GeomAbs_Line:
            a, b = c.Value(u0), c.Value(u1); msp.add_line((a.X(), a.Y()), (b.X(), b.Y()), dxfattribs=dict(layer=lay))
        elif ty == GeomAbs_Circle:
            ci = c.Circle(); cx, cy, r = ci.Location().X(), ci.Location().Y(), ci.Radius()
            if abs(u1 - u0 - 2 * math.pi) < 1e-6:
                msp.add_circle((cx, cy), r, dxfattribs=dict(layer=lay))
            else:
                a, b = c.Value(u0), c.Value(u1)
                if ci.Axis().Direction().Z() < 0: a, b = b, a
                a0 = math.degrees(math.atan2(a.Y() - cy, a.X() - cx)); a1 = math.degrees(math.atan2(b.Y() - cy, b.X() - cx))
                msp.add_arc((cx, cy), r, a0, a1, dxfattribs=dict(layer=lay))
        else:
            msp.add_lwpolyline(edge_pts(e, 64), dxfattribs=dict(layer=lay))
    wx.Next()
doc.saveas(OUT / 'base_fr4_v1_2.dxf')

# 5 图纸 (A3 横): 左 俯视 + 孔标号, 右 孔表 / 槽表 / 技术要求
FP = FontProperties(fname='/mnt/c/Windows/Fonts/simhei.ttf') if Path('/mnt/c/Windows/Fonts/simhei.ttf').exists() else None
fig = plt.figure(figsize=(16.54, 11.69))
ax = fig.add_axes([0.03, 0.06, 0.55, 0.86])
for is_outer, pts in loops:
    ax.plot([q[0] for q in pts], [q[1] for q in pts], 'k-', lw=1.0 if is_outer else 0.7)
ax.axhline(0, color='#c00', lw=0.4, ls='-.'); ax.axvline(0, color='#c00', lw=0.4, ls='-.')
groups = collections.OrderedDict()
for x, y, d in sorted(holes, key=lambda h: (-h[2], math.atan2(h[1], h[0]))):
    groups.setdefault(d, []).append((x, y))
tags = {}
for k, d in enumerate(groups):
    tg = chr(ord('A') + k); tags[d] = tg
    for x, y in groups[d]:
        ax.text(x + d / 2 + 0.6, y + d / 2 + 0.3, tg, fontsize=6.5, color='#1f4e9a')
def slot_name(x0, y0, x1, y1):
    w, h = x1 - x0, y1 - y0; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if abs(max(w, h) - 40) < 0.5 and abs(min(w, h) - 20) < 0.5: return '散热片槽 (线圈驱动板)' if cy < 30 else '散热片槽 (电机控制板)'
    if abs(w - 8) < 0.5 and abs(h - 3) < 0.5: return '下载排针口'
    if cx > 45 and cy < -20: return '电容弧形槽'
    if cx < -45 and abs(cy) < 10: return 'MR30 护套让位'
    return '控制板背面元件让位'
for k, (x0, y0, x1, y1) in enumerate(slots):
    ax.text(x1 + 0.8, y1 + 0.3, f'S{k + 1}', fontsize=6.5, color='#9a1f1f')
R = B.DISC_D / 2
ax.annotate('', xy=(-R, -R - 8), xytext=(R, -R - 8), arrowprops=dict(arrowstyle='<->', lw=0.7))
ax.text(0, -R - 7, f'Φ{B.DISC_D:g}', ha='center', fontsize=9)
ax.set_xlim(-R - 12, R + 12); ax.set_ylim(-R - 14, R + 10); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('俯视 (板顶面 = 装配 Z0, 看向 -Z)  1:1 坐标 mm, 原点 = 轴心', fontproperties=FP, fontsize=11)

tx = fig.add_axes([0.60, 0.04, 0.39, 0.92]); tx.axis('off')
L = [f'POV3D V1.2 — base_fr4_v1_2  底座玻纤板 FR4 Φ{B.DISC_D:g}×{FR4_T:g}', '',
     f'材料 FR4 (玻纤环氧板) 厚 {FR4_T:g}, 无铜, 数量 1;  全部通孔/通槽; 外形 Φ{B.DISC_D:g}',
     f'位置: 打印底盘 ({B.PRINT_T:g} 厚, Z{-B.DISC_T:g}..{-B.FR4_T:g}) 之上, 板顶 Z0 = 原底盘顶面 (上面所有件 Z 不变)',
     '加工: 按 DXF (base_fr4_v1_2.dxf, 层 OUTLINE 外形 / CUT 孔槽) 铣; 孔径公差 +0.1/-0', '',
     f'圆孔 {len(holes)} 个:']
for d, pts in groups.items():
    _u = {12.0: '电机中央凸台让位', 6.4: 'M6 外圈固定孔', 3.4: 'M3 (MR30 座 / 线夹)', 3.2: 'M3 通孔 (电机/线圈环/中央/下罩/控制板/XT60/按键/驱动板)'}.get(d, '')
    L.append(f'  {tags[d]}  Φ{d:g} ×{len(pts)}  {_u}')
    s = '     ' + '  '.join(f'({x:g},{y:g})' for x, y in pts)
    while len(s) > 92:
        cut_ = s.rfind('  ', 0, 92); L.append(s[:cut_]); s = '     ' + s[cut_:].strip()
    L.append(s)
L += ['', f'异形开口 {len(slots)} 个 (外包框 x0..x1, y0..y1; 精确形状见 DXF):']
for k, (x0, y0, x1, y1) in enumerate(slots):
    L.append(f'  S{k + 1}  {slot_name(x0, y0, x1, y1)}:  x {x0:.2f}..{x1:.2f}  y {y0:.2f}..{y1:.2f}  ({x1 - x0:.2f}×{y1 - y0:.2f})')
L += ['', '说明:', '  · 孔形取自打印底盘 Z-0.1 截面: 原底盘顶面 3 深的槽 (电容弧形槽 / 控制板背面让位 /',
      '    电机中央 Φ12) 在玻纤板上都做成通孔 (还进打印底盘顶面 1); 底面沉孔与铜螺母孔只在打印底盘上',
      '  · 2026-11-25 夜: 板厚 3 → 2 (轮廓/孔位/DXF 不变); 打印底盘 5.5 (底座 2+5.5=7.5), 螺丝长度不变',
      '  · 2026-11-25 版: 电机控制板整组 (4 孔 / S2 / S3 / S4 / S6) 往 +Y (向外) 挪 1, 其余不变',
      f'  · 体积 {VOL / 1000:.1f} cm3']
tx.text(0, 1, '\n'.join(L), va='top', fontproperties=FP, fontsize=8.2, linespacing=1.45)
fig.savefig(OUT / 'base_fr4_v1_2_drawing.pdf'); fig.savefig(OUT / 'base_fr4_v1_2_drawing_preview.png', dpi=110)
print('FR4 圆孔', len(holes), {tags[d]: (d, len(p)) for d, p in groups.items()}, '异形', len(slots), 'vol', round(VOL))
