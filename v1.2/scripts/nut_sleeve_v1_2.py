# -*- coding: utf-8 -*-
"""法兰螺母定位套 (POV3D V1.2, 2026-11-20 起)
    cd v1.2/scripts && ../../.venv/bin/python nut_sleeve_v1_2.py [m3|m4 ...]   (缺省两件都出)
输出 v1.2/models/<code>/: <code>.step / .stl / _drawing.pdf / _drawing_preview.png

nut_sleeve_v1_2 (M3):
  用户 11-20「应该是一个外径8mm的件，直径要紧配，就做8mm不要留余量」:
  M3 法兰螺母坐在 Φ8×3.7 圆窝里会转/会掉 ⇒ 圆窝与六角之间塞一个套: 外圆 Φ8 (= 窝径, 零余量紧配), 内六角对边 5.4 (11-23 用户「5.4吧」, 先说 5.3; 原 5.9),
  高 2.0 (11-23 用户; 原 2.7 = 螺母六角段 3.7 − 法兰 1.0): 套坐在法兰上, 顶低于盘顶 0.7。
  用户 11-20「就做转子盘这个就行」: 只用在承载盘 rim_ring_v1_2b 顶面内圈 R34 ×8 (法兰在窝底 Z26.8):
  先放螺母, 再把套压在六角外, 套 Z27.8..29.8。每台 8 个。(打印底盘底 G 8 不用)
nut_sleeve_m4_v1_2 (M4):
  用户 11-23「在做一个M4的法兰托，外径是10mm，对边6.9，厚度2.5mm」。用在哪处用户未说 (现存 M4 法兰螺母: 分体玻璃下底座底面 8 个 Φ10.2 圆窝)。
不 import build_v1_2。
"""
import math
import sys
from pathlib import Path

from OCP.gp import gp_Pnt, gp_Vec
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp

V12 = Path(__file__).resolve().parents[1]

VARIANTS = {
    'm3': dict(CODE='nut_sleeve_v1_2', M='M3', OD=8.0, AF=5.4, H=2.0, QTY='8/台', DATE='2026-11-23',
               notes=['材料 PLA, 每台 8 个 (承载盘 rim_ring_v1_2b 顶面内圈 R34 ×8); 打印: 端面贴床, 竖放',
                      '用途: M3 法兰螺母 (法兰 Φ7.6×1.0, 厚 3.7) 坐 Φ8×3.7 圆窝时会转/会掉, 用本件套住六角段, 外圆紧配窝壁',
                      '高 2 (用户 11-23; 原 2.7 = 螺母六角段): 套坐在法兰上, 顶面低于盘顶 0.7',
                      '装法: 承载盘顶面内圈 R34 8 个 Φ8×3.7 窝 (法兰在窝底 Z26.8): 先放螺母, 再把套压在六角外, 套 Z27.8..29.8',
                      '外径 Φ8 0 余量 (用户 11-20), 内六角对边 5.4 (用户 11-23)']),
    'm4': dict(CODE='nut_sleeve_m4_v1_2', M='M4', OD=10.0, AF=6.9, H=2.5, QTY='按需', DATE='2026-11-23',
               notes=['材料 PLA; 打印: 端面贴床, 竖放',
                      '用途: M4 法兰螺母 (对边 6.9) 定位套, 套住六角段、外圆卡窝壁, 防转防掉',
                      '尺寸按用户 11-23: 外径 Φ10, 内六角对边 6.9, 厚 2.5 (均为名义尺寸, 不另加余量)',
                      '现存 M4 法兰螺母窝: 分体玻璃下底座底面 8 个 Φ10.2 圆窝 (二合一件无)']),
}


def make(P):
    OD, AF, H = P['OD'], P['AF'], P['H']; AC = AF / math.cos(math.radians(30))
    c = BRepPrimAPI_MakeCylinder(OD / 2, H).Shape()
    poly = BRepBuilderAPI_MakePolygon()
    for k in range(6):
        a = math.radians(30 + 60 * k)
        poly.Add(gp_Pnt(AC / 2 * math.cos(a), AC / 2 * math.sin(a), -1))
    poly.Close()
    hx = BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(poly.Wire()).Face(), gp_Vec(0, 0, H + 2)).Shape()
    s = BRepAlgoAPI_Cut(c, hx).Shape()
    assert BRepCheck_Analyzer(s).IsValid()
    return s


def drawing(P, OUT):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, Polygon, Rectangle
    from matplotlib import font_manager; font_manager.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.family'] = 'SimHei'
    plt.rcParams['axes.unicode_minus'] = False
    CODE, OD, AF, H = P['CODE'], P['OD'], P['AF'], P['H']
    AC = AF / math.cos(math.radians(30)); WF, WC = (OD - AF) / 2, (OD - AC) / 2
    R = OD / 2; m = R * 1.6
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.suptitle(f'POV3D V1.2 — {CODE}  {P["M"]} 法兰螺母定位套 Φ{OD:g} × {H:g} (内六角对边 {AF:g})', fontsize=14)
    hexp = [(AC / 2 * math.cos(math.radians(30 + 60 * k)), AC / 2 * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    ax = fig.add_axes([0.05, 0.30, 0.42, 0.58]); ax.set_aspect('equal'); ax.axis('off'); ax.set_title('俯视图 (示意)  尺寸单位: mm')
    ax.add_patch(Circle((0, 0), R, fc='#ddd', ec='k', lw=1.5)); ax.add_patch(Polygon(hexp, fc='w', ec='k', lw=1.5))
    ax.annotate('', (-R, -R * 1.3), (R, -R * 1.3), arrowprops=dict(arrowstyle='<->')); ax.text(0, -R * 1.4, f'Φ{OD:g}', ha='center', va='top')
    ax.annotate('', (-AF / 2, R * 1.2), (AF / 2, R * 1.2), arrowprops=dict(arrowstyle='<->')); ax.text(0, R * 1.25, f'内六角对边 {AF:g}', ha='center', va='bottom')
    ax.plot([-AF / 2, -AF / 2], [0, R * 1.2], 'k:', lw=0.6); ax.plot([AF / 2, AF / 2], [0, R * 1.2], 'k:', lw=0.6)
    ax.text(0, 0, f'对角 {AC:.2f}', ha='center', va='center', fontsize=9)
    ax.set_xlim(-m, m); ax.set_ylim(-m * 1.1, m)
    bx = fig.add_axes([0.55, 0.45, 0.40, 0.40]); bx.set_aspect('equal'); bx.axis('off'); bx.set_title('剖视 (过对边)  示意')
    bx.add_patch(Rectangle((-R, 0), WF, H, fc='#bbb', ec='k', hatch='//')); bx.add_patch(Rectangle((AF / 2, 0), WF, H, fc='#bbb', ec='k', hatch='//'))
    bx.annotate('', (R + 0.8, 0), (R + 0.8, H), arrowprops=dict(arrowstyle='<->')); bx.text(R + 1.0, H / 2, f'{H:g}', va='center')
    bx.annotate('', (AF / 2, -0.6), (R, -0.6), arrowprops=dict(arrowstyle='<->')); bx.text(R + 0.2, -0.9, f'壁 {WF:.2f} (对边) / {WC:.2f} (对角)', va='top', fontsize=9)
    bx.set_xlim(-R - 1.5, R + 6); bx.set_ylim(-2.5, H + 1.5)
    fig.text(0.06, 0.24, '说明', fontsize=12)
    for i, t in enumerate(P['notes']): fig.text(0.07, 0.21 - i * 0.03, '· ' + t, fontsize=9.5)
    fig.text(0.06, 0.03, f'{CODE}  数量 {P["QTY"]}  材料 PLA  单位 mm  {P["DATE"]}  POV3D V1.2', fontsize=10)
    try: fig.savefig(OUT / f'{CODE}_drawing.pdf')
    except PermissionError: fig.savefig(OUT / f'{CODE}_drawing.NEW.pdf')
    fig.savefig(OUT / f'{CODE}_drawing_preview.png', dpi=110)


if __name__ == '__main__':
    from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer
    for key in (sys.argv[1:] or list(VARIANTS)):
        P = VARIANTS[key]; CODE = P['CODE']; OUT = V12 / 'models' / CODE; OUT.mkdir(parents=True, exist_ok=True)
        s = make(P)
        w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs); w.Write(str(OUT / f'{CODE}.step'))
        BRepMesh_IncrementalMesh(s, 0.005, False, 0.1, True)
        sw = StlAPI_Writer(); sw.ASCIIMode = False; assert sw.Write(s, str(OUT / f'{CODE}.stl'))
        g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g)
        AC = P['AF'] / math.cos(math.radians(30))
        print(f"{CODE}: Φ{P['OD']:g}×{P['H']:g}, 内六角 {P['AF']:g} (对角 {AC:.2f}), 壁 {(P['OD'] - P['AF']) / 2:.2f}/{(P['OD'] - AC) / 2:.2f}, 体积 {g.Mass():.1f} mm3")
        drawing(P, OUT)
