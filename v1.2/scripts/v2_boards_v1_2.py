"""V2 转子电路 (占位, 用户 11-13 晚): 转接板 POV3D_V2_BaseBoard 140×80 + MLK CZ06 核心板 + V2 灯板 LED_V0.2.0 (11-13)。
只给结构看位置/限高, 不是电路模型:
  - 转接板: 板框 + 每个器件按 F.CrtYd 外框 × 限高做方块 (限高按转接板 README「做矮」表 + 常见规格书, 偏保守)。
    器件全在顶面; 长边 (140) 平行屏面 = 世界 X; KiCad (150,100) = 转子中心, 世界 Y = −(ky−100)。
  - CZ06: DF40 座 (合高 3.0) + 60×35 板 + 顶面件, 整体按 6.6 包络。
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

BB_PCB = Path('/mnt/d/claude_workspace/pov3d/pcb/projects/POV3D_V2_BaseBoard/kicad/POV3D_V2_BaseBoard.kicad_pcb')
BB_C = (150.0, 100.0)                                # 转接板中心 (KiCad)
# 限高 (板顶以上, mm); 没列的 = 1.2 (0402~0805 / SOT / QFN 一类)
H_BY_FP = {
    'BL-M7921AU1': 3.7, 'CP_EIA-7343-20_Kemet-V': 2.0, 'CP_Elec_10x10.5': 10.8, 'C_1210_3225Metric': 2.5, 'D_SMB': 2.3,
    'FPC_72P_0.5mm_XW0525512': 2.0, 'Fuse_1812_4532Metric': 1.6, 'IDC-Header_2x05_P2.54mm_Vertical': 9.0,
    'JST_VH_B2PS-VH_1x02_P3.96mm_Horizontal': 10.0, 'JST_VH_B4PS-VH_1x04_P3.96mm_Horizontal': 10.0,
    'JST_XH_S3B-XH-A_1x03_P2.50mm_Horizontal': 7.0, 'L_Bourns_SRP1038C_10.0x10.0mm': 3.8, 'L_Bourns_SRP7028A_7.3x6.6mm': 2.8,
    'L_Taiyo-Yuden_NR-40xx': 2.0, 'SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm': 1.75, 'SOIC-8_3.9x4.9mm_P1.27mm': 1.75,
    'SSOP-10_3.9x4.9mm_P1.00mm': 1.75, 'SW_SPST_TL3342': 2.5, 'USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal': 3.3,
    'microSD_HC_Hirose_DM3AT-SF-PEJM5': 2.0, 'SW_DIP_SPSTx03_Slide_6.7x9.18mm_W6.73mm_P2.54mm_LowProfile_JPin': 2.0,
}
SKIP_FP = ('MountingHole', 'DF40HC')                 # 孔不建; DF40 归 CZ06
CZ06_W, CZ06_D, DF40_H, CZ06_PCB_T = 60.0, 35.0, 3.0, 1.6
LED_STEP = Path(__file__).resolve().parent.parent / 'boards' / 'led_v0.2.0_2026-11-13.step'
LED_HALF_H = 104.004                                 # STEP 里板 y −104.004..104.004


def _box(x0, y0, z0, x1, y1, z1): return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()


def _comp(shapes):
    b = BRep_Builder(); c = TopoDS_Compound(); b.MakeCompound(c)
    for s in shapes: b.Add(c, s)
    return c


def _w(kx, ky): return kx - BB_C[0], -(ky - BB_C[1])


def baseboard_parts():
    """→ list of (ref, fp, (x0,y0,x1,y1) 世界, h) 及板框 (x0,y0,x1,y1)"""
    s = BB_PCB.read_text(encoding='utf-8')
    ex = []
    for m in re.finditer(r'\n\t\(gr_(?:line|rect)(.*?)\n\t\)', s, re.S):
        if 'Edge.Cuts' in m.group(1):
            ex += [(float(a), float(b)) for a, b in re.findall(r'\((?:start|end) ([-\d.]+) ([-\d.]+)\)', m.group(1))]
    (ax, ay), (bx, by) = _w(min(p[0] for p in ex), min(p[1] for p in ex)), _w(max(p[0] for p in ex), max(p[1] for p in ex))
    outline = (min(ax, bx), min(ay, by), max(ax, bx), max(ay, by))
    parts = []
    for m in re.finditer(r'\n\t\(footprint "([^"]+)"', s):
        st = m.start(); b = s[st:s.find('\n\t)', st)]
        fp = m.group(1).split(':')[-1]
        if fp.startswith(SKIP_FP): continue
        ref = re.search(r'\(property "Reference" "([^"]+)"', b).group(1)
        at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', b).groups()
        fx, fy, fa = float(at[0]), float(at[1]), math.radians(float(at[2] or 0))
        pts = []
        for g in re.finditer(r'\(fp_(?:line|rect|poly|circle)(.*?)\n\t\t\)', b, re.S):
            if 'F.CrtYd' not in g.group(1): continue
            pts += [(float(a), float(c)) for a, c in re.findall(r'\((?:start|end|xy|center|mid) ([-\d.]+) ([-\d.]+)\)', g.group(1))]
        if not pts: continue
        wp = [_w(fx + x * math.cos(fa) + y * math.sin(fa), fy - x * math.sin(fa) + y * math.cos(fa)) for x, y in pts]
        xs, ys = [p[0] for p in wp], [p[1] for p in wp]
        parts.append((ref, fp, (min(xs), min(ys), max(xs), max(ys)), H_BY_FP.get(fp, 1.2)))
    return parts, outline


def make(B):
    """→ dict(baseboard, bb_parts, cz06, led, info)"""
    z0 = B.Z_BB0; zt = z0 + B.BB_T
    parts, (x0, y0, x1, y1) = baseboard_parts()
    pcb = _box(x0, y0, z0, x1, y1, zt)
    comps = [_box(a, b_, zt, c, d, zt + h) for _, _, (a, b_, c, d), h in parts]
    cz = _comp([_box(-CZ06_W / 2, -CZ06_D / 2, zt + DF40_H, CZ06_W / 2, CZ06_D / 2, zt + B.CZ06_H)] +
               [_box(-CZ06_W / 2 + 2, -CZ06_D / 2 + 2, zt, CZ06_W / 2 - 2, CZ06_D / 2 - 2, zt + DF40_H)])   # DF40 合高区 (简化成一块)
    led = read_step(LED_STEP)
    t = gp_Trsf(); t.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi / 2)    # (x,y,z) → (x, −z, y): LED 面 (STEP z<0) 朝 +Y
    t2 = gp_Trsf(); t2.SetTranslation(gp_Vec(0, 0, B.Z_SCR0 + LED_HALF_H))
    led = BRepBuilderAPI_Transform(BRepBuilderAPI_Transform(led, t, True).Shape(), t2, True).Shape()
    tall = sorted(((h, ref, fp, bb) for ref, fp, bb, h in parts), reverse=True)[:8]
    return dict(baseboard=pcb, bb_parts=_comp(comps), cz06=cz, led=led,
                info=dict(outline=(x0, y0, x1, y1), n_parts=len(parts), tall=[(ref, fp, round(h, 2), tuple(round(v, 1) for v in bb)) for h, ref, fp, bb in tall]))
