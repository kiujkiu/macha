"""V2 转子电路 (占位, 用户 11-13 晚; 11-16 晚改读底板 r3): 转接板 POV3D_V2_BaseBoard r3 (多边形, x −51.2..40, y 14..80.4) + MLK CZ06 核心板 + V2 灯板 LED_V0.2.0 (11-13)。
只给结构看位置/限高, 不是电路模型:
  - 转接板: 板框 + 每个器件按 F.CrtYd 外框 × 限高做方块 (限高按转接板 README「做矮」表 + 常见规格书, 偏保守)。
    器件全在顶面; 长边 (140) 平行屏面 = 世界 X; KiCad (150,100) = 转子中心, 世界 Y = −(ky−100)。
  - CZ06: DF40 座 (合高 3.0) + 60×35 板 + 顶面件, 整体按 6.6 包络; r3: 中心 (0, 48.5), 长边沿 x (x ±30, y 31..66)。
  - 灯板: kicad-cli 导出的整板 STEP (boards/led_v0.2.0_2026-11-13.step, 板心原点), 竖起来放在 XZ 面, LED 面 (B 面) 朝 +Y,
    板背面贴 Y=0 (只 1 块; 两块背靠背的间距/偏心 V2 还没定)。
高度全从 build_v1_2 读: Z_BB0 (转接板底) / BB_T / CZ06_H / Z_SCR0 (灯板下沿)。
"""
import math, re
from pathlib import Path
from OCP.gp import gp_Pnt, gp_Trsf, gp_Ax1, gp_Dir, gp_Vec
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
from helpers import read_step

BB_PCB = Path('/mnt/d/claude_workspace/pov3d/pcb/projects/POV3D_V2_BaseBoard/layout/r4e_pads/POV3D_V2_BaseBoard_r4e.kicad_pcb')   # 11-16 晚 r4d (96 11234291): 板框同 r4c (角 r81.69), 四角矩形孔, J8/J10/J9 改焊盘, J11/J12 测试点, C13 换聚合物
BB_STEP = Path('/mnt/d/claude_workspace/pov3d/pcb/projects/POV3D_V2_BaseBoard/review/结构交付/POV3D_V2_BaseBoard_r4e.step')   # 原点 = 转轴, z0 = 板底
# 板框 (世界坐标); _arc = 以转轴为心的圆弧 (r4c 五边形不用, 留着)
def _arc(p0, p1, r=81.7, n=12):                       # 11-16 晚 改回 Φ170: r81.7 (罩内壁 r82, 罩内件 ≤ r81.7; Φ175 时曾 r84.2)
    a0, a1 = math.atan2(p0[1], p0[0]), math.atan2(p1[1], p1[0])
    return [(r * math.cos(a0 + (a1 - a0) * k / n), r * math.sin(a0 + (a1 - a0) * k / n)) for k in range(1, n)]
# 11-16 晚 用户 (Φ175, 再改): 底板改窄长条 x ±64, y 0.5–42 (128×41.5, 上两角 r76.55), pov3d-96 出板中 ⇒ 结构侧先用占位;
#   原 r3 rev c 多边形 (板角 r81.7) 及 104×65.5 长方形 作废; 长条 / r4b 也已作废 (见下)
#   11-16 晚 改回 Φ170: r4c 五边形 x −51.2…47.3, y 8.6–66.6, 左上角切 (−51.2, 63.6)–(−47.3, 66.6); 顶点最远 r81.69 (罩内壁 r82)
def _fillet_rect(x0, y0, x1, y1, r, n=8):
    """四角 R 圆角矩形 (逆时针), 每角 n 段折线"""
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        pts += [(cx + r * math.cos(math.radians(a0 + 90 * k / n)), cy + r * math.sin(math.radians(a0 + 90 * k / n))) for k in range(n + 1)]
    return pts
BB_POLY = _fillet_rect(-51.2, 8.6, 47.3, 66.6, 6.0)   # 11-16 晚 r4e (96 31676a1a): 外接 x −51.2…47.3 y 8.6…66.6 四角 R6, 最远 r81.60 (r4c/r4d 左上斜切作废)
BB_R = 81.7                                          # 11-16 晚 改回 Φ170: 底板外接限 r81.7 (Φ175 时曾 r84.2; 原 r83)
BB_C = (150.0, 100.0)                                # 转轴 (KiCad); r2: 世界 (x, y) = (kx − 150, 100 − ky), 已与 bbox_r2.json 核对
# 限高 (板顶以上, mm); 没列的 = 1.2 (0402~0805 / SOT / QFN 一类)
H_BY_FP = {
    'BL-M7921AU1': 3.7, 'CP_EIA-7343-20_Kemet-V': 2.0, 'CP_Elec_10x10.5': 10.8, 'C_1210_3225Metric': 2.5, 'D_SMB': 2.3,
    'FPC_72P_0.5mm_XW0525512': 2.0, 'Fuse_1812_4532Metric': 1.6, 'IDC-Header_2x05_P2.54mm_Vertical': 9.0,
    'JST_VH_B2PS-VH_1x02_P3.96mm_Horizontal': 10.0, 'JST_VH_B4PS-VH_1x04_P3.96mm_Horizontal': 10.0,
    'JST_XH_S3B-XH-A_1x03_P2.50mm_Horizontal': 7.0, 'L_Bourns_SRP1038C_10.0x10.0mm': 3.8, 'L_Bourns_SRP7028A_7.3x6.6mm': 2.8,
    'L_Taiyo-Yuden_NR-40xx': 2.0, 'SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm': 1.75, 'SOIC-8_3.9x4.9mm_P1.27mm': 1.75,
    'SSOP-10_3.9x4.9mm_P1.00mm': 1.75, 'SW_SPST_TL3342': 2.5, 'USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal': 3.3,
    'microSD_HC_Hirose_DM3AT-SF-PEJM5': 2.0, 'SW_DIP_SPSTx03_Slide_6.7x9.18mm_W6.73mm_P2.54mm_LowProfile_JPin': 2.0,
    # r2 新封装
    'JST_VH_B2P-VH_1x02_P3.96mm_Vertical': 10.0, 'JST_XH_B3B-XH-AM_1x03_P2.50mm_Vertical': 7.0, 'microSD_HC_Molex_47219-2001': 2.0,
    'Molex_PicoBlade_53398-0471_1x04-1MP_P1.25mm_Vertical': 4.8, 'L_Sunlord_MWSA1204S-3R3': 4.2, 'PinHeader_1x06_P1.27mm_Vertical': 4.5,
    'PinHeader_1x03_P1.27mm_Vertical': 4.5, 'QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm': 1.0, 'SOT-583-8': 0.6,
    'Crystal_SMD_3225-4Pin_3.2x2.5mm': 0.9, 'Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm': 1.3, 'PWR_PADS_24V_2xD3.0': 1.5,
}
SKIP_FP = ('MountingHole', 'DF40HC')                 # 孔不建; DF40 归 CZ06
CZ06_W, CZ06_D, DF40_H, CZ06_PCB_T = 60.0, 35.0, 3.0, 1.6
CZ06_C = (0.0, 48.32)                                # 11-16 r3 rev c: CZ06 中心 (板体 x±30 y30.82–65.82, 转 180°), 长边 60 沿 x
LED_STEP = Path(__file__).resolve().parent.parent / 'boards' / 'led_v0.2.0_2026-11-13.step'
LED_HALF_H = 104.004                                 # STEP 里板 y −104.004..104.004


def _box(x0, y0, z0, x1, y1, z1): return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()


def _comp(shapes):
    b = BRep_Builder(); c = TopoDS_Compound(); b.MakeCompound(c)
    for s in shapes: b.Add(c, s)
    return c


def _w(kx, ky): return kx - BB_C[0], -(ky - BB_C[1])


def baseboard_parts():
    """→ list of (ref, fp, (x0,y0,x1,y1) 世界, h; h<0 = 底面件) 及板框外接框 (x0,y0,x1,y1)"""
    s = BB_PCB.read_text(encoding='utf-8')
    ex = []
    for m in re.finditer(r'\n\t\(gr_(?:line|rect|arc)(.*?)\n\t\)', s, re.S):
        if 'Edge.Cuts' in m.group(1):
            ex += [(float(a), float(b)) for a, b in re.findall(r'\((?:start|end|mid) ([-\d.]+) ([-\d.]+)\)', m.group(1))]
    (ax, ay), (bx, by) = _w(min(p[0] for p in ex), min(p[1] for p in ex)), _w(max(p[0] for p in ex), max(p[1] for p in ex))
    outline = (min(ax, bx), min(ay, by), max(ax, bx), max(ay, by))
    parts = []
    for m in re.finditer(r'\n\t\(footprint "([^"]+)"', s):
        st = m.start(); b = s[st:s.find('\n\t)', st)]
        fp = m.group(1).split(':')[-1]
        if fp.startswith(SKIP_FP): continue
        side = 'B' if re.search(r'\n\t\t\(layer "B\.Cu"\)', b) else 'F'
        ref = re.search(r'\(property "Reference" "([^"]+)"', b).group(1)
        at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', b).groups()
        fx, fy, fa = float(at[0]), float(at[1]), math.radians(float(at[2] or 0))
        pts = []
        for g in re.finditer(r'\(fp_(?:line|rect|poly|circle)(.*?)\n\t\t\)', b, re.S):
            if f'{side}.CrtYd' not in g.group(1): continue
            pts += [(float(a), float(c)) for a, c in re.findall(r'\((?:start|end|xy|center|mid) ([-\d.]+) ([-\d.]+)\)', g.group(1))]
        if not pts: continue
        wp = [_w(fx + x * math.cos(fa) + y * math.sin(fa), fy - x * math.sin(fa) + y * math.cos(fa)) for x, y in pts]
        xs, ys = [p[0] for p in wp], [p[1] for p in wp]
        parts.append((ref, fp, (min(xs), min(ys), max(xs), max(ys)), H_BY_FP.get(fp, 1.2) * (1 if side == 'F' else -1)))   # h<0 = 底面件 (板底往下)
    return parts, outline


def _common(a, b):
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
    o = BRepAlgoAPI_Common(a, b); o.Build(); return o.Shape()


def make(B):
    """→ dict(baseboard, bb_parts, cz06, led, bb_step, info); 灯板仍按 B.Z_SCR0 摆, 底板按 B.Z_BB0 / B.BB_T"""
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2
    z0 = B.Z_BB0; zt = z0 + B.BB_T
    parts, (x0, y0, x1, y1) = baseboard_parts()
    rr = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, z0 - 20), gp_Dir(0, 0, 1)), BB_R, 40).Shape()
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    pg = BRepBuilderAPI_MakePolygon()
    for x, y in BB_POLY: pg.Add(gp_Pnt(x, y, z0))
    pg.Close()
    pcb = BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(0, 0, B.BB_T)).Shape()   # r4d 板框
    pcb = B.cut(pcb, *[B.cyl(x, y, 3.2, z0 - 1, z0 + B.BB_T + 1) for x, y in B.BB_HOLES])   # 11-16 晚: 4 个 M3 安装孔 Φ3.2 (原板框实心, 尼龙螺丝误报 11.3 mm3)
    comps = [_box(a, b_, zt, c, d, zt + h) if h > 0 else _box(a, b_, z0 + h, c, d, z0) for _, _, (a, b_, c, d), h in parts]
    # r2: CZ06 中心 (0, 53.5), 长边 60 沿 x (r2_说明 §4)
    (cx, cy), w_, d_ = CZ06_C, CZ06_W, CZ06_D
    cz = _comp([_box(cx - w_ / 2, cy - d_ / 2, zt + DF40_H, cx + w_ / 2, cy + d_ / 2, zt + B.CZ06_H)] +
               [_box(cx - w_ / 2 + 2, cy - d_ / 2 + 2, zt, cx + w_ / 2 - 2, cy + d_ / 2 - 2, zt + DF40_H)])   # DF40 合高区 (简化成一块)
    led = read_step(LED_STEP)
    t = gp_Trsf(); t.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi / 2)    # (x,y,z) → (x, −z, y): LED 面 (STEP z<0) 朝 +Y
    t2 = gp_Trsf(); t2.SetTranslation(gp_Vec(0, 0, B.Z_SCR0 + LED_HALF_H))
    led = BRepBuilderAPI_Transform(BRepBuilderAPI_Transform(led, t, True).Shape(), t2, True).Shape()
    t3 = gp_Trsf(); t3.SetTranslation(gp_Vec(0, 0, z0))
    bb_step = BRepBuilderAPI_Transform(read_step(BB_STEP), t3, True).Shape()     # r2 交付 STEP (z0 = 板底) → 世界
    tall = sorted(((h, ref, fp, bb) for ref, fp, bb, h in parts), reverse=True)[:8]
    return dict(baseboard=pcb, bb_parts=_comp(comps), cz06=cz, led=led, bb_step=bb_step,
                info=dict(outline=(x0, y0, x1, y1), outline_r=BB_R, n_parts=len(parts), n_bottom=sum(1 for p in parts if p[3] < 0),
                          tall=[(ref, fp, round(h, 2), tuple(round(v, 1) for v in bb)) for h, ref, fp, bb in tall]))

# ---- 11-16 用户: 灯板 STEP 里没有 LED, 按灯板 PCB 真实坐标贴上 MIP-CIMD07TN 4 合 1 (国星, 1.32×1.32×0.59, 2×2 像素 0.781) ----
MIP_JSON = Path(__file__).resolve().parent.parent / 'boards' / 'led_v0.2.0_mip_xy.json'   # 10368 颗, B.Cu (从 LED_V0.2.0.kicad_pcb 提)
MIP_W, MIP_BASE, MIP_H = 1.32, 0.29, 0.59      # 外形 / 底部白漆+绿漆基板厚 / 总厚 (规格书 p6 侧视图)


def led_mip(B):
    """→ (基板部分 compound, 发光面部分 compound), 坐标系同 make()['led'] (B 面 y=0, LED 朝 +y; 世界 x = kx−cx, z = −(ky−cy) + Z_SCR0 + LED_HALF_H)"""
    import json as _j
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    d = _j.load(open(MIP_JSON, encoding='utf-8')); cx, cy = d['center_kicad']
    zc = B.Z_SCR0 + LED_HALF_H; h = MIP_W / 2
    base, top = [], []
    for kx, ky in d['xy_kicad']:
        x, z = kx - cx, -(ky - cy) + zc
        base.append(BRepPrimAPI_MakeBox(gp_Pnt(x - h, 0.0, z - h), gp_Pnt(x + h, MIP_BASE, z + h)).Shape())
        top.append(BRepPrimAPI_MakeBox(gp_Pnt(x - h, MIP_BASE, z - h), gp_Pnt(x + h, MIP_H, z + h)).Shape())
    return _comp(base), _comp(top)
