# -*- coding: utf-8 -*-
"""灯板焊铜螺柱托条 (POV3D V1.2, 2026-11-26)
    cd v1.2/scripts && ../../.venv/bin/python led_solder_bar_v1_2.py
输出 v1.2/models/led_solder_bar_v1_2/: .step / .stl / _drawing.pdf / _drawing_preview.png

用户 11-26: 参考 models/screen_solder_jig_bar (7 月老屏 L 形底条: 墙 4 × 高 18 + 底唇 6 宽 × 3 厚, 孔心 Z9.6),
「按照我们 V2 灯板」「pcb 厚度先做一个 1.6 的试试」「用这个 bar 夹住这个屏幕, 然后用这个 bar 上的孔锁住一个六边形铜螺母,
然后把这个铜螺母焊接到灯板」「需要这个形状托住, 这个托的部分长度做到 30」(原话 30cm, 按 30 mm 做: 底唇宽 6 → 30)。
⇒ L 形截面同老 bar (墙 4, 高 18, 底唇厚 3), 底唇伸进板下 30 托住灯板; 两端封口壁 (同老 jig 侧壁) 给板 x 向定位。
   灯板 (按 1.6) 平放在底唇上, 板边顶墙; 墙上 3×M3 Φ3.2 横孔沿板高方向, 螺丝穿墙伸到板面上,
   M3 六角铜螺柱 (对边 4.6 × 长 5) 拧在螺丝上, 平面贴板面开窗 → 焊。
   孔心 = 底唇顶 3 + 板 1.6 + 4.6/2 = Z6.9 (老 bar 是 Z9.6, 按 V2 灯板重算)。孔 X = 开窗中心 −78.88 / 0 / +78.88。
   一条托上沿、一条托下沿 (同件 ×2)。
局部系: X 沿板宽居中; Y: 墙内面 (= 板边) y=0, 底唇向 +y; Z 床面 0 向上。不 import build_v1_2。
"""
import sys
from pathlib import Path

from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp

V12 = Path(__file__).resolve().parents[1]
CODE = 'led_solder_bar_v1_2'

# ===== 参数 =====
BW = 163.76        # 灯板宽 (LED_V0.2.0 板框 163.7575)
PCB = 1.6          # 板厚 (用户 11-26 先按 1.6)
X_CLR = 0.2        # 两端封口每边间隙
END = 4.0          # 两端封口壁厚 (同老 jig 壁 4)
WALL = 4.0         # 墙厚 (同老 bar)
H = 18.0           # 总高 (同老 bar)
FLOOR = 3.0        # 底唇厚 (同老 bar)
LIP = 30.0         # 底唇伸进板下 (用户 11-26: 6 → 30)
SO_AF = 4.6        # 六角铜螺柱对边
HOLE_D = 3.2
HOLE_XS = (-78.88, 0.0, 78.88)   # 开窗中心: 左/中/右

PX = BW / 2 + X_CLR                 # 内腔半长 82.08
L = 2 * (PX + END)                  # 总长 172.16
Y0, Y1 = -WALL, LIP                 # −4 .. 30
Z_F = FLOOR + PCB                   # 板面 4.6
Z_HOLE = Z_F + SO_AF / 2            # 孔心 6.9


def box(x0, y0, z0, x1, y1, z1):
    return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()


def make():
    s = box(-L / 2, Y0, 0, L / 2, Y1, H)
    s = BRepAlgoAPI_Cut(s, box(-PX, 0, FLOOR, PX, Y1 + 1, H + 1)).Shape()
    for x in HOLE_XS:
        c = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, Y0 - 1, Z_HOLE), gp_Dir(0, 1, 0)), HOLE_D / 2, WALL + 2).Shape()
        s = BRepAlgoAPI_Cut(s, c).Shape()
    assert BRepCheck_Analyzer(s).IsValid()
    return s


def drawing(OUT):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Polygon, Circle
    from matplotlib import font_manager; font_manager.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.family'] = 'SimHei'
    plt.rcParams['axes.unicode_minus'] = False
    fig = plt.figure(figsize=(16.54, 11.69))  # A3
    fig.suptitle(f'POV3D V1.2 — {CODE}  灯板焊铜螺柱托条 {L:.2f} × {WALL + LIP:g} × {H:g}  (底唇 {LIP:g}, 3×M3 孔)', fontsize=15)

    def dim_v(ax, x, z0, z1, txt, side=1):
        ax.annotate('', (x, z0), (x, z1), arrowprops=dict(arrowstyle='<->', lw=0.8))
        ax.text(x + side * 0.5, (z0 + z1) / 2, txt, va='center', ha='left' if side > 0 else 'right', fontsize=9)

    def dim_h(ax, z, y0, y1, txt, dz):
        ax.annotate('', (y0, z), (y1, z), arrowprops=dict(arrowstyle='<->', lw=0.8))
        ax.text((y0 + y1) / 2, z + dz, txt, ha='center', va='bottom' if dz > 0 else 'top', fontsize=9)

    # --- 剖视 (YZ, 过孔) ---
    bx = fig.add_axes([0.03, 0.36, 0.47, 0.52]); bx.set_aspect('equal'); bx.axis('off')
    bx.set_title('A-A 剖视 (过 M3 孔)  尺寸单位: mm')
    poly = [(Y0, 0), (Y1, 0), (Y1, FLOOR), (0, FLOOR), (0, H), (Y0, H)]
    bx.add_patch(Polygon(poly, fc='#ccc', ec='k', hatch='//', lw=1.2))
    bx.add_patch(Rectangle((Y0, Z_HOLE - HOLE_D / 2), WALL, HOLE_D, fc='w', ec='k', lw=0.8))
    bx.plot([Y0 - 2, 24], [Z_HOLE, Z_HOLE], 'b-.', lw=0.6)
    bx.add_patch(Rectangle((0, FLOOR), 36, PCB, fc='#7a7', ec='g', lw=0.6, alpha=0.6))
    bx.text(31, FLOOR + PCB + 0.4, '灯板', fontsize=8, va='bottom')
    bx.add_patch(Rectangle((10, Z_F), 5, SO_AF, fc='#f2b56b', ec='#c60', lw=0.8))
    bx.text(12.5, Z_F + SO_AF + 0.5, '六角铜螺柱 (示意, 前后靠拧)', fontsize=8, ha='center', va='bottom')
    bx.text(24.3, Z_HOLE, 'M3 螺丝轴线', fontsize=8, va='center', color='b')
    zs = [0, FLOOR, Z_F, Z_HOLE]
    lbl = [f'底唇 {FLOOR:g}', f'板 {PCB:g}', f'{SO_AF / 2:g}']
    for a, b, t in zip(zs[:-1], zs[1:], lbl):
        dim_v(bx, Y0 - 1.2, a, b, t, side=-1)
    dim_v(bx, Y0 - 7, 0, Z_HOLE, f'孔心 {Z_HOLE:g}', side=-1)
    dim_v(bx, Y0 - 13, 0, H, f'总高 {H:g}', side=-1)
    dim_h(bx, -1.5, Y0, 0, f'墙 {WALL:g}', -0.3)
    dim_h(bx, -1.5, 0, Y1, f'底唇 {LIP:g}', -0.3)
    dim_h(bx, -5, Y0, Y1, f'总宽 {WALL + LIP:g}', -0.3)
    bx.text(Y0 + WALL / 2, Z_HOLE + HOLE_D / 2 + 0.5, f'Φ{HOLE_D:g}', ha='center', va='bottom', fontsize=8)
    bx.set_xlim(Y0 - 20, 38); bx.set_ylim(-8, H + 3)

    # --- 俯视 (XY) ---
    ax = fig.add_axes([0.05, 0.05, 0.90, 0.30]); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title('俯视 (墙在下, 底唇朝上)  尺寸单位: mm')
    ax.add_patch(Rectangle((-L / 2, Y0), L, WALL + LIP, fc='#ddd', ec='k', lw=1.2))
    ax.add_patch(Rectangle((-PX, 0), 2 * PX, LIP, fc='#f4f4f4', ec='k', lw=0.8))
    for x in HOLE_XS:
        ax.add_patch(Rectangle((x - HOLE_D / 2, Y0), HOLE_D, WALL, fc='w', ec='k', ls='--', lw=0.6))
    dim_h(ax, Y0 - 4, -L / 2, L / 2, f'总长 {L:.2f}', -0.8)
    dim_h(ax, Y1 + 3, -PX, PX, f'内长 {2 * PX:.2f} (板宽 {BW:g} + 2×{X_CLR:g})', 0.8)
    for xa, xb in ((HOLE_XS[0], HOLE_XS[1]), (HOLE_XS[1], HOLE_XS[2])):
        dim_h(ax, 4, xa, xb, f'孔距 {xb - xa:g}', 0.6)
    ax.plot([HOLE_XS[0]] * 2 + [None] + [HOLE_XS[2]] * 2, [Y0, 4, None, Y0, 4], 'k:', lw=0.5)
    ax.annotate('', (PX, 15), (L / 2, 15), arrowprops=dict(arrowstyle='<->', lw=0.8)); ax.text(L / 2 + 1, 15, f'封口 {END:g}', va='center', fontsize=9)
    ax.set_xlim(-L / 2 - 6, L / 2 + 16); ax.set_ylim(Y0 - 9, Y1 + 9)

    notes = [
        '用途: LED_V0.2.0 灯板平放在底唇上, 板边顶墙; 上沿 / 下沿各托一条 (同件 ×2)',
        'M3 螺丝从外侧穿墙伸到板面上, 六角铜螺柱 (对边 4.6×5) 拧上去, 平面贴开窗 → 焊',
        f'截面同老 screen_solder_jig_bar (墙 {WALL:g} / 高 {H:g} / 底唇厚 {FLOOR:g}), 底唇宽 6 → {LIP:g} (用户 11-26)',
        f'孔心 Z{Z_HOLE:g} = 底唇 {FLOOR:g} + 板 {PCB:g} + 螺柱半对边 {SO_AF / 2:g} (老 bar 是 9.6)',
        '孔 X = 开窗中心 -78.88 / 0 / +78.88; 两端封口给板左右定位',
        '螺柱在开窗里前后位置靠拧进多少调; 中部开窗 (离板边约 100) 够不着',
        '打印: 底面 (Z0) 贴床, 无需支撑; PLA/PETG',
    ]
    fig.text(0.53, 0.85, '说明', fontsize=12)
    for i, t in enumerate(notes):
        fig.text(0.53, 0.82 - i * 0.045, '· ' + t, fontsize=9.5)
    fig.text(0.05, 0.015, f'{CODE}  数量 2/板  材料 PLA/PETG  单位 mm  2026-11-26  POV3D V1.2  (参考 models/screen_solder_jig_bar)', fontsize=10)
    try: fig.savefig(OUT / f'{CODE}_drawing.pdf')
    except PermissionError: fig.savefig(OUT / f'{CODE}_drawing.NEW.pdf')
    fig.savefig(OUT / f'{CODE}_drawing_preview.png', dpi=90)


if __name__ == '__main__':
    from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer
    OUT = V12 / 'models' / CODE; OUT.mkdir(parents=True, exist_ok=True)
    s = make()
    w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs); w.Write(str(OUT / f'{CODE}.step'))
    BRepMesh_IncrementalMesh(s, 0.01, False, 0.1, True)
    sw = StlAPI_Writer(); sw.ASCIIMode = False; assert sw.Write(s, str(OUT / f'{CODE}.stl'))
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g)
    print(f'{CODE}: {L:.2f} × {WALL + LIP:g} × {H:g}; 板面 Z{Z_F:g}, 孔心 Z{Z_HOLE:g}; 体积 {g.Mass() / 1000:.2f} cm3')
    if '--no-drawing' not in sys.argv:
        drawing(OUT)
