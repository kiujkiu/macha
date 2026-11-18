"""V1.2 桥板真模型 + 两根桥 FPC 实体 + 三个 FPC 座真外形 (11-16 晚, G 做; 不改现有脚本, 由主线合并)。
    cd v1.2/scripts && ../../.venv/bin/python fpc_v1_2.py          (import 也可: 只建几何, 不导出不校核)
输入:
  桥板 STEP  pov3d/POV3D_V2桥_结构STEP与质量_2026-11-11/V2桥_3D_结构简版.step (+ mass.json 11.0 g, 重心 (0.21, −0.37, 0.77))
             坐标: 原点 = 板框中心, z=0 = B 面 (板体 z 0…1.53, F 面件从 z1.62 起, B 面件到 z−0.08 止), FPC1 在 F 面 +y 板边。
             B 面两个 AXK6A2337YG 插头 J1/J2 中心 (∓28.8, 0), 长边沿 STEP y; STEP 里 FPC1 是 40×5×1.2 占位方块 ⇒ 去掉, 换成按封装 Fab 建的座子。
  桥板 PCB   POV3D_GW5A_Bridge_V2.0/hw_1110/pcb_v1 (user origin 132,118): FPC1 (132,104.4) 转 180°, 脚 1 在 STEP x+17.25 / y10.775 (信号脚一排在板里侧),
             两只固定脚在板边侧 ⇒ 插口朝板边 (STEP +y); Fab 本体 x±19.975, y11.337…17.887 (口边离板边 0.11)。
  灯板 STEP  v1.2/boards/led_v0.2.0_2026-11-13.step: LED 面 (B 面) 两个 AXK 插座 J1/J2 x±28.8, STEP y −102.61…−69.40 (中心 −86.0)。
  底板       r4d PCB / STEP (V.BB_PCB / V.BB_STEP): STEP 里 J5/J6 没 3D ⇒ 按封装 Fab (= CrtYd 内缩 0.2) 建; 两座都插口朝 −y, 脚 1 在 x+17.25。
桥板摆法 (同 led_support 方块的位置, 用 AXK 对齐):
  STEP (bx, by, bz) → 板 A 局部 (bx, Y_LED + 3.0 + bz, ZC − by): B 面贴灯板 LED 面, AXK 合高 3.0; STEP +y (FPC 边) 朝下; 右手系 ⇒ bx 不翻。
  ZC 由两对 AXK 中心对齐求 (灯板 J1 ↔ 桥板 J2 同在 x+28.8), 再 pair 同法: 板 B = 绕局部原点转 180°, 两块再平移 ECC。
FPC (11-16 晚 桥板窗口定规格): 单层铜, 弯曲区 0.15 厚, 两端补强/金手指区 0.3 厚; 宽 35.5 = 70×0.5 + 0.5, 插入深 4.0, 补强 5.0 (B 根 J6 端 4.0)。
  在 YZ 面内画中线 (直段 + 圆弧), 两侧各偏 t/2 成截面, 沿 x 拉伸 ±17.75; 两端补强段另加 0.3 厚直段。弯起点离补强边 ≥1。
  B 根: 桥板 B 座口 (Z37.11 朝下) 下到毂盘顶 (实测 Z30.5, 双面胶 0.1 上平铺) → 穿过灯板组下方 → 在 桥板 A 座 与 底板下沿 y8.6 之间的竖槽上来 → 进 J6。
  A 根: 桥板 A 座口出来 2.0 后 180° 回弯 (在 B 根竖段的 −y 侧) 竖直往上 → 过 J6 顶 → 贴 CZ06 顶 (双面胶) → 过 y53.3 外沿再 S 弯折下 → 进 J5。
  竖槽 (桥 A 座口 y4.71 → J6 口 y8.945) 只 4.24: A 的 180° 回弯和 B 进 J6 的 90° 弯 中线 R1.0 / 内 0.925 (6.2T, IPC-2223 单层静态 ≥6T), 不挪底板 (11-16 晚定);
  脚序: 两根都 1↔1 直通; B 根配底板 J6 网络镜像 (pin k ↔ 71−k)。
"""
import io, contextlib, math, json, re, os
from pathlib import Path
_f = io.StringIO()
with contextlib.redirect_stdout(_f):
    import build_v1_2 as B
    import led_support_v1_2 as L
import v2_boards_v1_2 as V
from helpers import write_doc, solids
from OCP.gp import gp_Pnt, gp_Trsf, gp_Vec
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDataStd import TDataStd_Name
from OCP.collections import Sequence_TDF_Label as _Seq
from OCP.IFSelect import IFSelect_RetDone
from OCP.GC import GC_MakeSegment, GC_MakeArcOfCircle
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer

gbox, cut, fuse, xf, rotz, vol, bbox, cyl = B.gbox, B.cut, B.fuse, B.xf, B.rotz, B.vol, B.bbox, B.cyl
tr, comp, cog = L.tr, L.comp, L.cog
# 11-16 22:4x 用户定桥板最终装法 (= 新朝向, 默认): 桥板按 PCB 正放 (KiCad +y 朝转子盘), FPC 座在上沿插口朝下 (r11 P0: FPC1 原地转 180°, 中心 (132,104.4) 不变),
#   FPC 贴 FPGA 面往下过桥板下沿去底板; J1/J2 与灯板逐脚对应 (桥 J1 插灯板 J1, 1 脚都在上端 Z70)。旧朝向 (FPC 在下沿, 与 PCB 电气差 180°) 留开关: FPC_BRIDGE_FLIP=0
#   新朝向的插口位置是假设: FPC1 本体 (Fab) 位置不动, 只是口边从板边侧 (STEP y17.887) 换到板内侧 (y11.337), 转 180° 后座子在桥板上沿, 口朝下 (Z≈66.3)。等新桥板 STEP 再核。
BRIDGE_FLIP = os.environ.get('FPC_BRIDGE_FLIP', '1') == '1'
# 11-17 用户: 底板 J5/J6 插口朝向方案 (同型座, 只改位置/朝向; 板框 r4f 和 CZ06 不动), 环境变量 FPC_BB_SEAT_MODE:
#   same = r4f 现状 (两口都朝 −y); out = 两口朝外 (J6 −y 不变, J5 转 180° 口朝 +y 板外沿); in = 面对面朝内 (J6 转 180° 口朝 +y 朝 CZ06, J5 −y 不变)
BB_SEAT_MODE = os.environ.get('FPC_BB_SEAT_MODE', 'out')   # 11-17 用户定两口朝外 (r4i); r4h = in
assert BB_SEAT_MODE in ('same', 'out', 'in'), BB_SEAT_MODE
OUT = B.V12 / 'models' / 'fpc_v1_2' / ('新朝向_桥板转180' if BRIDGE_FLIP else '')
if BB_SEAT_MODE != 'same': OUT = B.V12 / 'models' / 'fpc_v1_2' / '底板座反向方案' / BB_SEAT_MODE
if BB_SEAT_MODE == 'out' and BRIDGE_FLIP: OUT = B.V12 / 'models' / 'fpc_v1_2' / 'r4i_定稿'   # 11-17 默认 = r4i 两口朝外

# ---------------- 资料 ----------------
BR_DIR = Path('/mnt/d/claude_workspace/pov3d/POV3D_V2桥_结构STEP与质量_2026-11-11')
BR_STEP = BR_DIR / 'V2桥_3D_结构简版.step'
BR_MASS = json.load(open(BR_DIR / 'mass.json', encoding='utf-8'))
BR_G = round(BR_MASS['total_g'], 2)               # 11.0 g (计算值, 未称重, ±10%)
BR_COM = tuple(BR_MASS['com_mm'])                 # STEP 坐标 (0.21, −0.36, 0.77)
BR_PCB_OLD = Path('/mnt/d/claude_workspace/pov3d/pcb/projects/POV3D_GW5A_Bridge_V2.0/hw_1110/pcb_v1/ProPrj_ICN2260转接板_V2_2026-11-10.kicad_pcb')
# r11 P0 (FPC1 朝内): 只动 FPC1 (转 180°, 中心不变), 其余同 pcb_v1; 它的 STEP (P0_FPC朝内.step) 只有板 + U52, 原点 = KiCad 原点 ⇒ 器件仍取 11-11 结构简版 STEP, FPC1 座按 r11 封装建
BR_R11 = Path('/mnt/d/claude_workspace/pov3d/pcb/projects/POV3D_GW5A_Bridge_V2.0/layout/r11/P0')
BR_PCB = BR_R11 / 'ProPrj_ICN2260转接板_V2_2026-11-10.kicad_pcb' if BRIDGE_FLIP else BR_PCB_OLD
LED_PCB = Path('/mnt/d/claude_workspace/_led_v020_1113/src/LED_V0.2.0/LED_V0.2.0.kicad_pcb')   # 灯板 V0.2.0 (11-13, 同 MIP json 出处); 板心 KiCad (175, 62)
LED_C = (175.0, 62.0)
BR_ORG = (132.0, 118.0)                           # kicad-cli --user-origin 132x118mm ⇒ STEP (x, y) = (kx − 132, 118 − ky)

# ---------------- 尺寸 ----------------
ECC, Y_LED, Z0 = L.ECC, L.Y_LED, L.Z0
T_ECC = L.T_ECC
AXK_H = 3.0                                       # AXK5A2137YG (灯板) + AXK6A2337YG (桥板) 合高 = 两板面距
BR_F = 1.6                                        # 桥板 F 面 (STEP z, 名义板厚)
ZT = B.Z_BB0 + B.BB_T                             # 底板顶 36.6
CZ06_TOP = ZT + B.CZ06_H                          # 43.2
# 11-17 96 选项: J6 再往 +y 挪 (焊盘离板边 ≥ 铣边余量), CZ06 整组可跟着往 +y 挪 (环境变量, 默认 0)
J6_DY_EXTRA = float(os.environ.get('FPC_J6_DY_EXTRA', '0'))   # 只 in 方案用 (r4h 时 +0.3)
CZ06_DY = float(os.environ.get('FPC_CZ06_DY', '0'))   # r4h 的 +0.3 已写进 led_support ENV, 这里只放额外偏移
CZ06_BOX = list(L.ENV['CZ06 (DF40+板+件)']); CZ06_BOX[1] += CZ06_DY; CZ06_BOX[3] += CZ06_DY   # (x0, y0, x1, y1, h)
CZ06_ENV = gbox(CZ06_BOX[0], CZ06_BOX[1], ZT, CZ06_BOX[2], CZ06_BOX[3], ZT + CZ06_BOX[4])     # 保守包络 (整块)
# 按实物: DF40 合高 3.0 区 (四边各内缩 2, 同 v2_boards) + CZ06 板体及顶面件 Z ZT+3.0 … 43.2
CZ06_REAL = fuse(gbox(CZ06_BOX[0] + 2, CZ06_BOX[1] + 2, ZT, CZ06_BOX[2] - 2, CZ06_BOX[3] - 2, ZT + V.DF40_H),
                 gbox(CZ06_BOX[0], CZ06_BOX[1], ZT + V.DF40_H, CZ06_BOX[2], CZ06_BOX[3], ZT + CZ06_BOX[4]))
CZ06_Y1 = CZ06_BOX[3]                                # 53.3 (+CZ06_DY) CZ06 外沿
# FPC 座 (XW0525512-702R-001, 70P 0.5, 翻盖; 高按底板需求表 "约 2" 取 2.0 偏保守, 桥板 STEP 占位是 1.2 — 都待规格书核)
SEAT_H = float(os.environ.get("FPC_SEAT_H", "2.55"))   # 11-17 96: XW0525512-702R-001 实高 2.55 (LCSC C49392770)
SLOT_W, SLOT_H, SLOT_Z, SLOT_D = 36.0, 0.5, 0.7, 5.0   # 插口: 宽 36 / 高 0.5 / 中心离 PCB 面 0.7 / 深 5 (FPC 插 4.0, 留 1.0)
BR_SEAT = dict(xh=19.975, mouth=17.887, depth=6.55)    # 桥板 FPC1 Fab (STEP 坐标), 本体从口边往 −y
# 11-16 晚 桥板窗口定 FPC 规格: 单层铜 (信号+GND 同层), 弯曲区总厚 ≤0.15 (PI+铜+覆盖膜), 只有两端补强/金手指区 0.3;
#   补强长 = 插入 4.0 + 1.0 = 5.0; 弯起点离补强边 ≥1 (离端头 ≥6); 一次预成形装好不再动, 弯曲处不贴胶 (IPC-2223 单层静态安装弯 ≥6×厚 = 0.9)
FPC_T, FPC_W, FPC_INS = 0.15, 35.5, 4.0            # 弯曲区厚 / 宽 (70×0.5+0.5) / 插入深 (口边 → FPC 端)
FPC_T_STF = 0.3                                    # 补强区总厚 (补强 PI 贴在金手指背面)
STF_L = 5.0                                        # 补强长 (插入 4.0 + 1.0)
STF_L_J6 = 4.0                                     # ⚠ B 根 J6 端补强只能缩到 = 插入 4.0 (见 R_CH)
BEND_GAP = 1.0                                     # 弯起点离补强边 ≥1
FINGER_L = 3.5                                     # 金手指长 (端头起, 按 XW0525512 规格书核)
def _hub_top():
    """毂盘顶实测: B 根平铺带 (|x|≤18, y −14…10) 里毂盘最高点 (L.HUB_TOP 写 30.4, 实测 30.5)"""
    o = BRepAlgoAPI_Common(B.hub, gbox(-18, -14, 25, 18, 10, 32)); o.Build(); return round(bbox(o.Shape())[5], 3)
HUB_TOP = _hub_top()
FPC_RHO = 1.8e-3                                  # g/mm³ (PI + 铜 + 补强, 估)
TAPE_T = 0.1                                      # 聚酰亚胺双面胶
R_STD = 3.15                                      # 空间够处: 中线 R3.15 = 内 R3.0 = 10T (静态下限)
R_J5 = 1.6                                        # CZ06 外沿 y53.3 → J5 口 y58.575 只 5.275, 减去口外直段 2.0 (补强 1 + 隙 1) ⇒ S 弯两个 90° 中线 R1.6 (内 1.525 ≥ 6T)
R_CH = 1.0                                        # 竖槽里 A 的 180° 回弯 + B 进 J6 的 90° 弯 (中线; 内 0.925 = 6.2T ≥ IPC 6T)
# 11-17 96 问 V1 排线 (双层铜, 弯曲区 ≥0.2, IPC 双层静态 ~10T ⇒ 内 R ≥2–2.5): 环境变量 FPC_T_BEND / FPC_R_MIN 覆盖厚度和最小内弯 (默认不变)
FPC_T = float(os.environ.get('FPC_T_BEND', FPC_T))
R_MIN_IN = float(os.environ.get('FPC_R_MIN', '0'))
def _rr(r): return max(r, R_MIN_IN + FPC_T / 2)
R_STD, R_J5, R_CH = _rr(R_STD), _rr(R_J5), _rr(R_CH)
#   竖槽: 桥 A 座口 y4.708 → J6 口 y8.945 只 4.24, 要放 A 的 2R + B 的 R + B 口外直段 + 两层厚 + 隙;
#   B 在 J6 口外留 2.0 直段 (补强 5.0) 时 2R_A + R_B ≤ 2.04 ⇒ 内 R 只有 ~0.6 ⇒ 改成 J6 端补强缩到 4.0 (= 插入, 不能再缩), 口外直段 1.0, R 中线 1.0
CH_GAP = 0.05                                     # 竖槽里 A 竖段 ↔ B 竖段 最小间隙 (算出 0.187)


# ---------------- 读 STEP (带名字) ----------------
def read_named(p):
    """→ [(名字, 已定位形状)] (装配叶子)"""
    doc = TDocStd_Document(TCollection_ExtendedString('XmlOcaf'))
    r = STEPCAFControl_Reader(); r.SetNameMode(True)
    assert r.ReadFile(str(p)) == IFSelect_RetDone
    r.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    q = _Seq(); st.GetFreeShapes(q); out = []
    def nm(lab):
        a = TDataStd_Name()
        return a.Get().ToExtString() if lab.FindAttribute(TDataStd_Name.GetID_s(), a) else '?'
    def rec(lab):
        q2 = _Seq()
        if st.IsAssembly_s(lab): st.GetComponents_s(lab, q2)
        if q2.Length() == 0: out.append((nm(lab), st.GetShape_s(lab)))
        for i in range(q2.Length()): rec(q2.Value(i + 1))
    for i in range(q.Length()): rec(q.Value(i + 1))
    return out


def kicad_pad(pcb, ref, pad):
    """kicad_pcb 里某件某脚的板坐标 (kx, ky)"""
    s = Path(pcb).read_text(encoding='utf-8')
    for m in re.finditer(r'\n\t\(footprint "([^"]+)"', s):
        b = s[m.start():s.find('\n\t)', m.start())]
        if f'(property "Reference" "{ref}"' not in b: continue
        at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', b).groups()
        ax, ay, a = float(at[0]), float(at[1]), math.radians(float(at[2] or 0))
        p = re.search(r'\(pad "%s" \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+)' % pad, b)
        x, y = float(p.group(1)), float(p.group(2))
        return ax + x * math.cos(a) + y * math.sin(a), ay - x * math.sin(a) + y * math.cos(a)
    raise KeyError(ref)


def bbc(s):
    b = bbox(s); return ((b[0] + b[3]) / 2, (b[1] + b[4]) / 2, (b[2] + b[5]) / 2)


# ---------------- 桥板: 读 STEP, 用 AXK 对齐灯板 ----------------
_br_parts = read_named(BR_STEP)
_br_parts = [('桥板 PCB' if n.startswith('=>') else n, s) for n, s in _br_parts]
_br_axk = {n: s for n, s in _br_parts if n in ('J1', 'J2')}
_led_axk = {n: s for n, s in read_named(V.LED_STEP) if n in ('J1', 'J2')}
# 灯板 STEP (x, y) → 世界 (x, Z = Z0 + LED_HALF_H + y); 桥板 STEP (x, y) → (x, ZC − y) ⇒ 每对 ZC = Z0 + LED_HALF_H + y灯 + y桥, x 残差 = x桥 − x灯
AXK_PAIR = []
for nl, sl in _led_axk.items():
    _sg = -1 if BRIDGE_FLIP else 1                  # 转 180°: 桥板 STEP (x, y) → (−x, −y)
    cl = bbc(sl); nb, sb = min(_br_axk.items(), key=lambda kv: abs(_sg * bbc(kv[1])[0] - cl[0])); cb = bbc(sb)
    AXK_PAIR.append(dict(led=nl, bridge=nb, x_led=round(cl[0], 3), x_br=round(_sg * cb[0], 3), dx=round(_sg * cb[0] - cl[0], 3),
                         zc=Z0 + V.LED_HALF_H + cl[1] + _sg * cb[1]))
ZC = round(sum(p['zc'] for p in AXK_PAIR) / len(AXK_PAIR), 3)   # ≈ 55.0 (方块 Z0+18 = 55.0)
assert max(abs(p['dx']) for p in AXK_PAIR) < 0.2 and max(abs(p['zc'] - ZC) for p in AXK_PAIR) < 0.2, AXK_PAIR


def T_BR():
    """桥板 STEP → 板 A 局部 (灯板组中面 y=0): (bx, by, bz) → (bx, Y_LED + AXK_H + bz, ZC − by), det = +1"""
    t = gp_Trsf()
    if BRIDGE_FLIP: t.SetValues(-1, 0, 0, 0, 0, 0, 1, Y_LED + AXK_H, 0, 1, 0, ZC)     # 先绕 STEP z 转 180°: (−bx, Y_LED+3+bz, ZC + by)
    else: t.SetValues(1, 0, 0, 0, 0, 0, 1, Y_LED + AXK_H, 0, -1, 0, ZC)
    return t


def seat_box(xh, mouth, depth, dirn, z0, h=SEAT_H):
    """FPC 座: 本体 x±xh, 从口边 y=mouth 往 dirn (±1) 方向 depth, z0…z0+h; 口边开插口 (宽 SLOT_W, 高 SLOT_H, 中心 z0+SLOT_Z, 深 SLOT_D)"""
    ya, yb = sorted((mouth, mouth + dirn * depth))
    s = gbox(-xh, ya, z0, xh, yb, z0 + h)
    sa, sb = sorted((mouth - dirn * 0.01, mouth + dirn * SLOT_D))
    return cut(s, gbox(-SLOT_W / 2, sa, z0 + SLOT_Z - SLOT_H / 2, SLOT_W / 2, sb, z0 + SLOT_Z + SLOT_H / 2))


def pairw(s_loc):
    """板 A 局部 → (A 世界, B 世界) (同 L.pair, 但 s_loc 已含 Y_LED)"""
    return xf(s_loc, T_ECC), xf(xf(s_loc, rotz(180)), T_ECC)


_t = T_BR()
# r11: FPC1 (132,104.4) 转 0° ⇒ Fab 本体 KiCad y 102.137…108.687, 固定脚在 ky107.225 (板内侧) ⇒ 口边 ky108.687 朝板内 (朝 BGA); STEP y = 118 − ky
BR_MOUTH = (BR_ORG[1] - (104.4 + 4.287)) if BRIDGE_FLIP else BR_SEAT['mouth']   # 新: 9.313 (口朝 STEP −y) / 旧: 17.887 (口朝 +y)
_seat_step = seat_box(BR_SEAT['xh'], BR_MOUTH, BR_SEAT['depth'], 1 if BRIDGE_FLIP else -1, BR_F)
if BRIDGE_FLIP: assert abs(kicad_pad(BR_PCB, 'FPC1', '71')[1] - 107.225) < 0.01 and abs(kicad_pad(BR_PCB, 'FPC1', '1')[1] - 101.575) < 0.01
BR_LOC = [(n, xf(s, _t)) for n, s in _br_parts if n != 'FPC1'] + [('FPC1 座 (XW0525512 按 Fab, 高 2.0)', xf(_seat_step, _t))]
_br_loc = comp([s for _, s in BR_LOC])
_axk_loc = comp([xf(s, _t) for s in _br_axk.values()])
_nonaxk_loc = comp([s for n, s in BR_LOC if n not in ('J1', 'J2')])
bridge_a, bridge_b = pairw(_br_loc)                 # 世界 (含座子)
axk_a, axk_b = pairw(_axk_loc)                      # AXK 插头 (与灯板插座本来就套合, 校核另算)
br_rest_a, br_rest_b = pairw(_nonaxk_loc)
seat_a, seat_b = pairw(xf(_seat_step, _t))


def _wp(p_step, which):
    """桥板 STEP 点 → 世界 (板 A/B)"""
    q = gp_Pnt(*p_step).Transformed(_t)
    if which == 'b': q = q.Transformed(rotz(180))
    q = q.Transformed(T_ECC); return (q.X(), q.Y(), q.Z())


_mouth_c = (0.0, BR_MOUTH, BR_F + SLOT_Z)
MOUTH_A, MOUTH_B = _wp(_mouth_c, 'a'), _wp(_mouth_c, 'b')   # 桥板座口中线 (世界): A (0, 4.71, 37.11) / B (0, −13.43, 37.11)
COM_A, COM_B = _wp(BR_COM, 'a'), _wp(BR_COM, 'b')
_k1 = kicad_pad(BR_PCB, 'FPC1', '1')
_p1 = (_k1[0] - BR_ORG[0], BR_ORG[1] - _k1[1], BR_F)
PIN1_BR = dict(step=(round(_p1[0], 3), round(_p1[1], 3)), a_world_x=round(_wp(_p1, 'a')[0], 2), b_world_x=round(_wp(_p1, 'b')[0], 2))


def axk_check():
    """桥 J1/J2 (插头) 与灯板 J1/J2 (插座) 脚 1/2/119/120 的世界坐标 (板 A): 同号脚 x/Z 应重合 (行距不同: 插头 4.05 / 插座 5.0, 中心同)"""
    out = {}
    for ref in ('J1', 'J2'):
        row = {}
        for pin in ('1', '2', '119', '120'):
            kb = kicad_pad(BR_PCB, ref, pin); wb = _wp((kb[0] - BR_ORG[0], BR_ORG[1] - kb[1], 0.0), 'a')
            kl = kicad_pad(LED_PCB, ref, pin); wl = (kl[0] - LED_C[0], Z0 + V.LED_HALF_H - (kl[1] - LED_C[1]))
            row[pin] = dict(bridge_xz=(round(wb[0], 2), round(wb[2], 2)), led_xz=(round(wl[0], 2), round(wl[1], 2)))
        out[ref] = row
    mids = {r: abs((v['1']['bridge_xz'][0] + v['2']['bridge_xz'][0]) / 2 - (v['1']['led_xz'][0] + v['2']['led_xz'][0]) / 2) + abs(v['1']['bridge_xz'][1] - v['1']['led_xz'][1]) for r, v in out.items()}
    out['ok_1to1'] = all(m < 0.1 for m in mids.values())
    return out

# ---------------- 底板 FPC 座 J5 / J6 (r4d) ----------------
_bbp = {r: bb for r, fp, bb, h in V.baseboard_parts()[0]}
def _fp_at(pcb, ref):
    s_ = Path(pcb).read_text(encoding='utf-8')
    for m in re.finditer(r'\n\t\(footprint "([^"]+)"', s_):
        b = s_[m.start():s_.find('\n\t)', m.start())]
        if f'(property "Reference" "{ref}"' in b:
            at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', b).groups(); return float(at[0]), float(at[1]), float(at[2] or 0)
    raise KeyError(ref)


def _bb_seat(ref, rot=False, dy=0.0):
    """rot = 绕封装原点 (KiCad at) 转 180° (口 −y → +y, 脚 1 x 反号); dy = 世界 y 平移"""
    x0, y0, x1, y1 = _bbp[ref]                      # CrtYd; Fab = CrtYd 内缩 0.2
    xh, mouth, depth = (x1 - x0) / 2 - 0.2, y0 + 0.2, (y1 - y0) - 0.4
    assert abs((x0 + x1) / 2) < 0.05, (ref, x0, x1)
    k = kicad_pad(V.BB_PCB, ref, '1'); kc = V._w(*k)
    sig_y = kc[1]
    kx, ky, ka = _fp_at(V.BB_PCB, ref); oy = V._w(kx, ky)[1]
    face, px = -1, kc[0]
    if sig_y < (y0 + y1) / 2:                       # 11-17 r4h: PCB 里 J6 已掉头 (0°, 口朝 +y) ⇒ 原样读, 不再转/平移
        assert rot, (ref, '板上座子已朝 +y, 但方案要求朝 −y')
        mouth, face, rot, dy = y1 - 0.2, 1, False, 0.0
    else:
        assert sig_y > mouth + 3, (ref, sig_y, mouth)   # r4f 现状: 信号脚在 +y 侧 ⇒ 插口朝 −y
    if rot: mouth, face, px, sig_y = 2 * oy - mouth, 1, -kc[0], 2 * oy - sig_y
    mouth += dy; sig_y += dy
    back = mouth - face * depth
    kic = (kx, round(ky - dy, 3), (ka + (180 if rot else 0)) % 360)
    return seat_box(xh, mouth, depth, -face, ZT), dict(xh=round(xh, 3), mouth_y=round(mouth, 3), back_y=round(back, 3), face=face, z=(ZT, ZT + SEAT_H),
                                                       slot_z=ZT + SLOT_Z, pin1_x=round(px, 2), sig_row_y=round(sig_y, 3), kicad_at=kic,
                                                       origin_world_y=round(oy + dy, 3), rot=rot, dy=dy)
# in: J6 转 180° 后口朝 +y, B 要从 J6 顶上翻过来 U 形回弯 (中线 R1.0) 再朝 −y 进口, 口外要 OUT_J6 + R + t/2 = 2.075 到 CZ06 外沿 y18.3 之前
#     ⇒ J6 本体 (Fab) 贴到板下沿 y8.6 (CrtYd 出板边 0.2), 口边 y16.2, U 弯最外 y18.275 (离 CZ06 包络 0.025)
J6_DY_IN = 8.6 - 9.345                               # 转 180° 后 Fab 后沿 9.345 → 8.6
seat_j6, J6 = _bb_seat('J6', rot=BB_SEAT_MODE == 'in', dy=(J6_DY_IN + J6_DY_EXTRA) if BB_SEAT_MODE == 'in' else 0.0)
if CZ06_DY or J6_DY_EXTRA: OUT = OUT.parent / f'{OUT.name}_J6{J6_DY_EXTRA:+g}_CZ06{CZ06_DY:+g}'
J5_DY = float(os.environ.get('FPC_J5_DY', '0'))       # 11-17: 按 96 的口边口径 (r4g: CZ06 外沿 → J5 口 4.73 ⇒ 口 y58.33) 可把 J5 整体往 −y 让 (偏保守)
seat_j5, J5 = _bb_seat('J5', rot=BB_SEAT_MODE == 'out', dy=J5_DY)
# 底板交付 STEP 可用环境变量换版 (默认 = v2_boards 里的 BB_STEP); r4g = J6 掉头 + CZ06 上移 0.3
_bbs = os.environ.get('FPC_BB_STEP')
if _bbs:
    from helpers import read_step
    BB_STEP_USED = xf(read_step(_bbs), tr(0, 0, B.Z_BB0)); BB_STEP_NAME = Path(_bbs).stem
else:
    BB_STEP_USED = L.bb_step; BB_STEP_NAME = Path(str(V.BB_STEP)).stem
if _bbs or J5_DY: OUT = OUT.parent / (OUT.name + (f'_{BB_STEP_NAME.split("_")[-1]}' if _bbs else '') + (f'_J5{J5_DY:+g}' if J5_DY else ''))
if R_MIN_IN or SEAT_H != 2.55 or FPC_T != 0.15: OUT = OUT.parent / f'{OUT.name}_T{FPC_T:g}_Rmin{R_MIN_IN:g}_座高{SEAT_H:g}'   # 11-17 V1 双层排线核算, 不覆盖定稿


# ---------------- FPC 中线 (YZ 面) ----------------
class Path2:
    """YZ 面内中线: 直段 + 圆弧; 角度 a = 方向 (cos a, sin a) 在 (y, z) 里; arc da>0 = 逆时针 (左转)"""
    def __init__(s, y, z, a_deg):
        s.p = (y, z); s.a = math.radians(a_deg); s.segs = []; s.L = 0.0; s.marks = []
    @staticmethod
    def n(a): return (-math.sin(a), math.cos(a))
    def line(s, d, tag=''):
        p0 = s.p; p1 = (p0[0] + d * math.cos(s.a), p0[1] + d * math.sin(s.a))
        s.segs.append(('L', p0, p1, s.a)); s.p = p1; s.L += d; s.marks.append((tag, round(d, 3)))
        return s
    def arc(s, R, da_deg, tag=''):
        sg = 1 if da_deg > 0 else -1; n0 = s.n(s.a)
        c = (s.p[0] + sg * R * n0[0], s.p[1] + sg * R * n0[1])
        a0, a1 = s.a, s.a + math.radians(da_deg)
        n1 = s.n(a1); p1 = (c[0] - sg * R * n1[0], c[1] - sg * R * n1[1])
        s.segs.append(('A', s.p, p1, a0, a1, c, R, sg)); s.p, s.a = p1, a1
        L_ = R * abs(math.radians(da_deg)); s.L += L_; s.marks.append((tag, round(L_, 3), f'R{R:g}'))
        return s
    def side(s, o):
        """偏 o (左 +) 的边线: [(类型, 点...)]"""
        out = []
        for g in s.segs:
            if g[0] == 'L':
                _, p0, p1, a = g; nn = s.n(a)
                out.append(('L', (p0[0] + o * nn[0], p0[1] + o * nn[1]), (p1[0] + o * nn[0], p1[1] + o * nn[1])))
            else:
                _, p0, p1, a0, a1, c, R, sg = g
                pts = []
                for a in (a0, (a0 + a1) / 2, a1):
                    nn = s.n(a); pts.append((c[0] - sg * R * nn[0] + o * nn[0], c[1] - sg * R * nn[1] + o * nn[1]))
                out.append(('A', *pts))
        return out
    def solid(s, w=FPC_W, t=FPC_T):
        """截面 (中线两侧各 t/2) 在 x = −w/2 面上, 沿 +x 拉伸 w"""
        x0 = -w / 2; P = lambda q: gp_Pnt(x0, q[0], q[1])
        lft, rgt = s.side(t / 2), s.side(-t / 2)
        mw = BRepBuilderAPI_MakeWire()
        def add_seg(g, rev=False):
            pts = list(g[1:])
            if rev: pts = pts[::-1]
            if g[0] == 'L': e = BRepBuilderAPI_MakeEdge(GC_MakeSegment(P(pts[0]), P(pts[1])).Value()).Edge()
            else: e = BRepBuilderAPI_MakeEdge(GC_MakeArcOfCircle(P(pts[0]), P(pts[1]), P(pts[2])).Value()).Edge()
            mw.Add(e)
        for g in lft: add_seg(g)
        mw.Add(BRepBuilderAPI_MakeEdge(GC_MakeSegment(P(lft[-1][-1]), P(rgt[-1][-1])).Value()).Edge())
        for g in reversed(rgt): add_seg(g, rev=True)
        mw.Add(BRepBuilderAPI_MakeEdge(GC_MakeSegment(P(rgt[0][1]), P(lft[0][1])).Value()).Edge())
        f = BRepBuilderAPI_MakeFace(mw.Wire(), True).Face()
        return BRepPrimAPI_MakePrism(f, gp_Vec(w, 0, 0)).Shape()
    def min_r(s): return min([g[6] for g in s.segs if g[0] == 'A'] or [999])


# B 根: 桥板 B 座 (FPC 端在口内 4.0) 朝下出 → 毂盘顶平铺 → 竖槽上来 → 进 J6
Z_FLAT_B = HUB_TOP + TAPE_T + FPC_T / 2            # 30.675
Z_FLAT_A = CZ06_TOP + TAPE_T + FPC_T / 2           # 43.375
yA, zM = MOUTH_A[1], MOUTH_A[2]
yB = MOUTH_B[1]
assert abs(MOUTH_B[2] - zM) < 1e-6
OUT_A = STF_L - FPC_INS + BEND_GAP                  # 2.0 口外直段 (补强露出 1.0 + 隙 1.0)
OUT_J6 = STF_L_J6 - FPC_INS + BEND_GAP              # 1.0 (J6 端补强 4.0)
Y_RB = (J6['mouth_y'] if J6['face'] < 0 else 8.945) - OUT_J6 - R_CH   # B 竖段 y 6.945 (in 方案沿用同一竖槽位置)
Y_RA = yA + 2 * R_CH                                # A 竖段 y 6.708 (旧朝向)
assert BRIDGE_FLIP or Y_RB - Y_RA - FPC_T >= CH_GAP, (Y_RA, Y_RB)
# 新朝向: 座口在桥板上沿 (Z≈66.3) 朝下, FPC 沿桥板 F 面往下要先外移 JOG 躲开 F 面器件 (BGA/SOT23-5 高 ≤1.57), 出桥板下沿后再接旧走线
_fpart_h = max(bbox(s_)[5] for n_, s_ in _br_parts if n_ not in ('FPC1', '桥板 PCB') and bbox(s_)[2] > BR_F - 0.1
               and bbox(s_)[3] > -FPC_W / 2 - 0.5 and bbox(s_)[0] < FPC_W / 2 + 0.5) - BR_F
JOG = round(_fpart_h + 0.1 + FPC_T / 2 - SLOT_Z, 3) if BRIDGE_FLIP else 0.0   # 1.045
R_JOG = 1.0                                         # 外移 S 弯 (中线, 内 0.925)
R_JOG = _rr(R_JOG)
BR_BOT = ZC - 18.0                                  # 桥板下沿 Z37.0


def _jog(p, d, sgn, tag):
    """S 弯侧移 d (在 YZ 面, 当前方向朝下; sgn=+1 往 +y)"""
    phi = math.degrees(math.acos(1 - d / (2 * R_JOG)))
    return p.arc(R_JOG, sgn * phi, tag).arc(R_JOG, -sgn * phi, tag)


pb = Path2(yB, zM + FPC_INS, -90)
if BRIDGE_FLIP:
    pb.line(FPC_INS + OUT_A, '插入 桥板 B 座 + 口外直段'); _jog(pb, JOG, -1, '外移躲 F 面器件')
    pb.line(pb.p[1] - (R_STD + Z_FLAT_B), '沿桥板 B F 面下'); pb.arc(R_STD, 90, '弯 → 平铺')
else:
    pb.line(FPC_INS, '插入 桥板 B 座').line(zM - R_STD - Z_FLAT_B, '桥板 B 座口 → 下').arc(R_STD, 90, '弯 → 平铺')
R_U = 1.0                                           # 进 +y 向口的 180° 回弯 (中线, 内 0.925)
R_U = _rr(R_U)
if J6['face'] < 0:
    pb.line((Y_RB - R_STD) - pb.p[0], '毂盘顶平铺').arc(R_STD, 90, '弯 → 竖槽')
    pb.line((J6['slot_z'] - R_CH) - pb.p[1], '竖槽竖段').arc(R_CH, -90, '弯 → 进 J6').line(OUT_J6 + FPC_INS, 'J6 口外直段 + 插入')
else:   # in: 竖槽上来 → 翻过 J6 顶 (Z = 口高 + 2R_U) → 180° 回弯朝 −y 进口
    _zo = J6['slot_z'] + 2 * R_U
    assert _zo - FPC_T / 2 >= ZT + SEAT_H + 0.1, _zo
    pb.line((Y_RB - R_STD) - pb.p[0], '毂盘顶平铺').arc(R_STD, 90, '弯 → 竖槽')
    pb.line((_zo - R_STD) - pb.p[1], '竖槽竖段').arc(R_STD, -90, '弯 → 过 J6 顶')
    pb.line((J6['mouth_y'] + OUT_J6) - pb.p[0], 'J6 顶上平段').arc(R_U, -180, '180° 回弯 → 进 J6').line(OUT_J6 + FPC_INS, 'J6 口外直段 + 插入')
# A 根: 桥板 A 座朝下出 2.0 → 180° 回弯 → 竖直往上 (B 竖段的 −y 侧) → 过 J6 顶 → 贴 CZ06 顶 → 外沿 (过了 y53.3 才弯) 折下 → 进 J5
pa = Path2(yA, zM + FPC_INS, -90)
if BRIDGE_FLIP:
    # 下行段贴 F 面器件外 (y yA+JOG) 下到桥板下沿以下, 往 −y 内收 (灯板组下面是空的), 180° 回弯, 竖段从下行段外侧 (+y) 上来过 J6 顶
    Y_RA = yA + JOG + FPC_T + CH_GAP / 2            # A 竖段 (在下行段外侧, 层叠)
    _yd = Y_RA - 2 * R_CH                           # 回弯起点 y
    pa.line(FPC_INS + OUT_A, '插入 桥板 A 座 + 口外直段'); _jog(pa, JOG, 1, '外移躲 F 面器件')
    pa.line(pa.p[1] - (BR_BOT - 0.3), '沿桥板 A F 面下'); _jog(pa, yA + JOG - _yd, -1, '出桥板下沿后内收')
    pa.arc(R_CH, 180, '180° 回弯')
    assert abs(pa.p[0] - Y_RA) < 1e-6 and Y_RB - Y_RA - FPC_T >= CH_GAP, (pa.p, Y_RA, Y_RB)
else:
    pa.line(FPC_INS + OUT_A, '插入 桥板 A 座 + 口外直段').arc(R_CH, 180, '座口下 180° 回弯')
pa.line((Z_FLAT_A - R_STD) - pa.p[1], '竖段 (竖槽 −y 侧)').arc(R_STD, -90, '弯 → 过 J6 顶')
if J5['face'] < 0:
    _rmax = (J5['mouth_y'] - OUT_A - CZ06_Y1 - 0.075) / 2     # S 弯起点在 CZ06 外沿以外 ≥0.075 (r4f 现状正好 R1.6)
    if _rmax < R_J5 - 1e-9: R_J5 = math.floor(_rmax * 20 + 1e-6) / 20   # CZ06 外移时 S 弯收小 (取 0.05 档)
    assert R_J5 - FPC_T / 2 >= 0.925, R_J5
    _y1 = J5['mouth_y'] - OUT_A - 2 * R_J5
    assert _y1 >= CZ06_Y1, _y1                      # S 弯从 CZ06 外沿以外开始 (不压棱)
    pa.line(_y1 - pa.p[0], 'CZ06 顶平铺').arc(R_J5, -90, 'CZ06 外沿折下')
    pa.line(pa.p[1] - (J5['slot_z'] + R_J5), '竖段').arc(R_J5, 90, '弯 → 进 J5').line(OUT_A + FPC_INS, 'J5 口外直段 + 插入')
else:   # out: CZ06 顶平铺过 J5 顶伸出板外沿 → 180° 回弯 (直径 = 平铺高 − 口高) 朝 −y 进口
    _ru = (Z_FLAT_A - J5['slot_z']) / 2
    pa.line((J5['mouth_y'] + OUT_A) - pa.p[0], 'CZ06/J5 顶平铺 (伸出板外沿)').arc(_ru, -180, '板外 180° 回弯 → 进 J5').line(OUT_A + FPC_INS, 'J5 口外直段 + 插入')
for _p, _j in ((pb, J6), (pa, J5)):
    assert abs(_p.p[0] - (_j['mouth_y'] - _j['face'] * FPC_INS)) < 1e-6 and abs(_p.p[1] - _j['slot_z']) < 1e-6, (_p.p, _j)
assert all(m[1] >= -1e-9 for m in pa.marks + pb.marks), (pa.marks, pb.marks)
STF = dict(A=(STF_L, STF_L), B=(STF_L, STF_L_J6))   # (桥板端, 底板端) 补强长


def _stf(p, L0, L1, t=FPC_T_STF):
    """两端补强段 (0.3 厚, 直段) 实体"""
    g0, g1 = p.segs[0], p.segs[-1]
    assert g0[0] == 'L' and g1[0] == 'L'
    a0, a1 = g0[3], g1[3]
    s0 = Path2(*g0[1], math.degrees(a0)).line(L0).solid(t=t)
    q = (g1[2][0] - L1 * math.cos(a1), g1[2][1] - L1 * math.sin(a1))
    s1 = Path2(*q, math.degrees(a1)).line(L1).solid(t=t)
    return s0, s1


def bends(p, stf):
    """各弯在展开长度上的位置 (从桥板端量) + 离两端距离; 核 弯起点 ≥ 补强 + BEND_GAP"""
    out, s_ = [], 0.0
    for g, m in zip(p.segs, p.marks):
        L_ = m[1]
        if g[0] == 'A':
            out.append(dict(tag=m[0], R_center=g[6], R_inner=round(g[6] - FPC_T / 2, 3), ang=round(math.degrees(abs(g[4] - g[3]))),
                            s=(round(s_, 2), round(s_ + L_, 2)), from_end0=round(s_, 2), from_end1=round(p.L - s_ - L_, 2)))
        s_ += L_
    first, last = out[0]['from_end0'], out[-1]['from_end1']
    return dict(list=out, first_from_bridge_end=first, last_from_board_end=last,
                ok_bridge=first >= stf[0] + BEND_GAP - 1e-6, ok_board=last >= stf[1] + BEND_GAP - 1e-6,
                need=(stf[0] + BEND_GAP, stf[1] + BEND_GAP))


def contact(p, pcb_y0, pcb_dz1):
    """同面 / 异面: 两端各看 PCB 在 FPC 哪一侧 (左 = 中线行进方向的左法线 n, 沿全长连续); 两座同型号 ⇒ 接触面同在 PCB 侧或同在背侧"""
    a0 = p.segs[0][3]; n0 = Path2.n(a0); y0 = p.segs[0][1][0]
    side0 = 'L' if n0[0] * (pcb_y0 - y0) > 0 else 'R'
    a1 = p.segs[-1][3]; n1 = Path2.n(a1)
    side1 = 'L' if n1[1] * pcb_dz1 > 0 else 'R'
    return dict(bridge_end_pcb_side=side0, board_end_pcb_side=side1, same=side0 == side1, kind='同面' if side0 == side1 else '异面')


_fa, _fb = pa.solid(), pb.solid()
fpc_a = fuse(_fa, *_stf(pa, *STF['A']))
fpc_b = fuse(_fb, *_stf(pb, *STF['B']))

# ---------------- 防离心固定: 聚酰亚胺双面胶 0.1 (薄片表示) ----------------
# 胶只贴平直段, 不进弯曲区: B 毂盘顶平铺段 (y −10.28…3.80) 里 y −8…3 一片 (r≤19.9, 都在毂盘顶 r<24.5 区); A CZ06 顶平铺段 (y9.86…53.38) 里 y21…51 一片
tape_b = gbox(-FPC_W / 2, -8.0, HUB_TOP, FPC_W / 2, 3.0, HUB_TOP + TAPE_T)
tape_a = gbox(-FPC_W / 2, 21.0, CZ06_TOP, FPC_W / 2, 51.0, CZ06_TOP + TAPE_T)
FIX = dict(tape_b=tape_b, tape_a=tape_a)


def fpc_len():
    """中线长 (两座口之间) + 两端插入段 + 建议下料"""
    out = {}
    for nm, p in (('A', pa), ('B', pb)):
        mid = p.L - 2 * FPC_INS
        cut_len = math.ceil((p.L + 3.0) * 2) / 2     # 余量 +3 (装配拉直/公差), 取到 0.5
        out[nm] = dict(centerline_mm=round(mid, 1), insert_mm=(FPC_INS, FPC_INS), total_mm=round(p.L, 1), cut_mm=cut_len,
                       min_R_centerline=p.min_r(), min_R_inner=round(p.min_r() - FPC_T / 2, 3), segs=p.marks,
                       stiffener_mm=STF[nm], finger_mm=FINGER_L, t_bend=FPC_T, t_stiff=FPC_T_STF, bends=bends(p, STF[nm]),
                       contact=CONTACT[nm], wiring='直通 (导体 x 不变), 底板按物理 x 分网')
    return out


# 接触面: 桥板端 PCB = 桥板 F 面 (座在 F 面上), 底板端 PCB 在 FPC 下方
_brF = Y_LED + AXK_H + BR_F
CONTACT = dict(A=contact(pa, ECC + _brF, ZT - J5['slot_z']), B=contact(pb, ECC - _brF, ZT - J6['slot_z']))


def tape_check():
    """胶片 y 范围要落在平铺直段里 (不进弯曲区)"""
    def flat(p, z):
        return [(min(g[1][0], g[2][0]), max(g[1][0], g[2][0])) for g in p.segs if g[0] == 'L' and abs(g[1][1] - z) < 1e-6 and abs(g[2][1] - z) < 1e-6]
    out = {}
    for nm, t, p, z in (('tape_a', tape_a, pa, Z_FLAT_A), ('tape_b', tape_b, pb, Z_FLAT_B)):
        b = bbox(t); fl = flat(p, z)
        out[nm] = dict(tape_y=(round(b[1], 2), round(b[4], 2)), flat_y=[tuple(round(v, 2) for v in f) for f in fl],
                       ok=any(f[0] <= b[1] + 1e-6 and b[4] <= f[1] + 1e-6 for f in fl))
    return out


# ---------------- 校核 ----------------
def _solids_bb(s):
    return [(q, bbox(q)) for q in (solids(s) or [s])]
def _hit(a, b):
    return not (a[3] < b[0] or b[3] < a[0] or a[4] < b[1] or b[4] < a[1] or a[5] < b[2] or b[5] < a[2])
def interf(a, b, _cache={}):
    """相交体积 (逐实体 + 包围盒预筛)"""
    ka, kb = id(a), id(b)
    sa = _cache.setdefault(ka, _solids_bb(a)); sb = _cache.setdefault(kb, _solids_bb(b))
    v = 0.0
    for x, bx in sa:
        for y, by in sb:
            if _hit(bx, by):
                o = BRepAlgoAPI_Common(x, y); o.Build(); v += vol(o.Shape())
    return v
def dist(a, b):
    d = BRepExtrema_DistShapeShape(a, b); d.Perform(); return round(d.Value(), 3)


def balance(br_g, com_a, com_b, extra=()):
    """同 led_support report() 的质量平衡 (支撑件/螺丝/灯板/桥板/底板/无线), 桥板换成 br_g @ com; extra = [(名, g, (x,y,z))]"""
    RHO, RHO_ST = 1.27e-3, 7.85e-3
    Ux = Uy = Mx = My = 0.0
    def add(g, c):
        nonlocal Ux, Uy, Mx, My
        Ux += g * c[0]; Uy += g * c[1]; Mx += g * c[0] * c[2]; My += g * c[1] * c[2]
    if B.ROTOR_B:   # 11-18 转子盘B: 立板 → 屏幕固定件 (耳朵螺丝没了); 另把承载盘 / 玻纤板 / 罩子 2 片也算进来 (罩子沿 y=ECC 分, 两半不等重)
        with contextlib.redirect_stdout(io.StringIO()):
            import rotor_shroud_b_v1_2 as RSB
        RB = RSB.RB
        sup = [s for k, s in L.SUP.items() if k not in ('post_a', 'post_b')] + [RB.hold_a, RB.hold_b, RB.rim, RSB.shr_a, RSB.shr_b]
        for s in sup:
            m, c = cog(s); add(m * RHO, c)
        m, c = cog(RB.fr4); add(m * 1.85e-3, c)
        scr = L.bar_scr + L.h1 + L.comb_scr
    else:
        for s in L.SUP.values():
            m, c = cog(s); add(m * RHO, c)
        scr = L.foot_scr + L.bar_scr + L.h1 + L.comb_scr
    for _, s in scr:
        m, c = cog(s); add(m * RHO_ST, c)
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_SOLID
    e = TopExp_Explorer(L.led_a, TopAbs_SOLID); vmax = 0.0
    while e.More(): vmax = max(vmax, vol(e.Current())); e.Next()
    led_g = round(vmax * 1.9e-3 + 30.0, 1)
    for s in (L.led_a, L.led_b): add(led_g, cog(s)[1])
    add(br_g, com_a); add(br_g, com_b)
    _bb = bbox(L.VB['baseboard']); add(44.5, ((_bb[0] + _bb[3]) / 2, (_bb[1] + _bb[4]) / 2, ZT + 3.0))
    try:
        wb = json.load(open(B.V12 / 'models' / 'wireless_holder_v1_2' / 'wireless_holder_report.json', encoding='utf-8'))['balance']; add(wb['total_g'], wb['total_cog'])
    except Exception:
        add(39.2, (0.04, -60.69, 39.5))
    for _, g, c in extra: add(g, c)
    U = math.hypot(Ux, Uy)
    z_lo, z_hi, r_lo, r_hi = 45.0, L.COMB_Z1 - 2, 83.0, 40.0
    Ulo = [(-(M_ - z_hi * U_)) / (z_lo - z_hi) for U_, M_ in ((Ux, Mx), (Uy, My))]
    Uhi = [-U_ - l for U_, l in zip((Ux, Uy), Ulo)]
    return dict(U_gmm=(round(Ux, 1), round(Uy, 1)), U_abs=round(U, 1), cw_g_r83=round(U / r_lo, 2),
                cw_ang_deg=round(math.degrees(math.atan2(-Uy, -Ux)) % 360, 1), z_eff=round(math.hypot(Mx, My) / max(U, 1e-9), 1),
                two_plane=dict(lo_g_r83=round(math.hypot(*Ulo) / r_lo, 2), lo_ang=round(math.degrees(math.atan2(Ulo[1], Ulo[0])) % 360, 1),
                               hi_g_r40=round(math.hypot(*Uhi) / r_hi, 2), hi_ang=round(math.degrees(math.atan2(Uhi[1], Uhi[0])) % 360, 1)))


def report():
    """干涉 / 间隙 / 长度 / 平衡 (几分钟)"""
    with contextlib.redirect_stdout(io.StringIO()):
        import rotor_shroud_v1_2 as RS
    mip = comp(list(L.pair(gbox(-74.88, 0.0, 75.0, 74.88, V.MIP_H, 243.5))))   # MIP 两万颗太慢 ⇒ 每板一块包络 (同 assembly_noglass 绘图)
    env = {k: v for k, v in L.env.items() if k not in ('J5', 'J6', '底面件 (r2 B.CrtYd × 限高)', 'CZ06 (DF40+板+件)')}   # J5/J6 方块包络换成真座子
    env['CZ06 (DF40+板+件)'] = CZ06_ENV
    env['底板器件 CrtYd×限高 (除 J5/J6)'] = comp([gbox(a, b_, ZT, c, d, ZT + h) if h > 0 else gbox(a, b_, B.Z_BB0 + h, c, d, B.Z_BB0)
                                         for r, _, (a, b_, c, d), h in V.baseboard_parts()[0] if r not in ('J5', 'J6')])
    OBJ = dict(led_a=L.led_a, led_b=L.led_b, mip_env=mip, bar=L.bar_s, post_a=L.post_a, post_b=L.post_b, ant_a=L.ant_a, ant_b=L.ant_b,
               bb_step=BB_STEP_USED, bb_pcb=L.VB['baseboard'], hub=B.hub, rim=B.rim, wireless_holder=L.wl, top=L.top,
               shroud_a=RS.shr_a, shroud_b=RS.shr_b, lid_a=RS.lid_a, lid_b=RS.lid_b, **{f'env {k}': v for k, v in env.items()})
    RIM_, HUB_, LID_A, LID_B = B.rim, B.hub, RS.lid_a, RS.lid_b
    if B.ROTOR_B:   # 11-18 整机换成转子盘B: hub → 玻纤板, rim → 承载盘单件, 立板 → 屏幕固定件, 罩子/顶盖 → 罩子 2 片 (含顶盖)
        import io as _io, contextlib as _cl
        with _cl.redirect_stdout(_io.StringIO()):
            import rotor_shroud_b_v1_2 as RSB
        RB = RSB.RB
        RIM_, HUB_, LID_A, LID_B = RB.rim, RB.fr4, RSB.shr_a, RSB.shr_b
        for k in ('post_a', 'post_b', 'hub', 'rim', 'shroud_a', 'shroud_b', 'lid_a', 'lid_b'): OBJ.pop(k)
        OBJ.update(holder_a=RB.hold_a, holder_b=RB.hold_b, fr4=RB.fr4, rim_b=RB.rim, shroud_b_a=RSB.shr_a, shroud_b_b=RSB.shr_b)
    NEW = dict(fpc_a=fpc_a, fpc_b=fpc_b, tape_a=tape_a, tape_b=tape_b, seat_j5=seat_j5, seat_j6=seat_j6,
               bridge_a=br_rest_a, bridge_b=br_rest_b)
    rep = dict(interf={}, axk_mate={}, gap={})
    for a, sa in NEW.items():
        for b, sb in OBJ.items():
            if a.startswith('bridge') and b in ('led_a', 'led_b'): continue      # 另算 (去掉 AXK 后)
            v = interf(sa, sb)
            if v > 1e-4: rep['interf'][f'{a} × {b}'] = round(v, 4)
    ks = list(NEW)
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            v = interf(NEW[a], NEW[b])
            if v > 1e-4: rep['interf'][f'{a} × {b}'] = round(v, 4)
    for a in ('fpc_a', 'fpc_b'):                                                     # FPC × 桥板 AXK (含在桥板里)
        for b, s in (('axk_a', axk_a), ('axk_b', axk_b)):
            v = interf(NEW[a], s)
            if v > 1e-4: rep['interf'][f'{a} × {b}'] = round(v, 4)
    # 桥板 (除 AXK) × 灯板 应 0; AXK 插头 × 灯板 = 与 AXK 插座套合 (两边都是长方体占位, 预期非 0)
    for nm, s_rest, s_axk in (('bridge_a', br_rest_a, axk_a), ('bridge_b', br_rest_b, axk_b)):
        for b in ('led_a', 'led_b'):
            v = interf(s_rest, OBJ[b])
            if v > 1e-4: rep['interf'][f'{nm}(除 AXK) × {b}'] = round(v, 4)
            v = interf(s_axk, OBJ[b])
            if v > 1e-4: rep['axk_mate'][f'{nm} AXK × {b}'] = round(v, 3)
    rep['interf']['_checked'] = f'{len(NEW)} 新件 × {len(OBJ)} 对象 + 新件互查; 只列非 0 (FPC 插入段在座子插口里, 本体留缝不碰)'
    # 关键间隙
    G = rep['gap']
    G['fpc_a × fpc_b'] = dist(fpc_a, fpc_b)
    for nm, f in (('fpc_a', fpc_a), ('fpc_b', fpc_b)):
        for b, s in (('seat_a', seat_a), ('seat_b', seat_b), ('bridge_a', br_rest_a), ('bb_pcb', L.VB['baseboard']), ('seat_j6', seat_j6), ('seat_j5', seat_j5),
                     ('cz06', CZ06_ENV), ('cz06_real', CZ06_REAL), ('led_a', L.led_a), ('led_b', L.led_b), ('hub' if not B.ROTOR_B else 'fr4', HUB_), ('rim' if not B.ROTOR_B else 'rim_b', RIM_), ('bar', L.bar_s)):
            G[f'{nm} × {b}'] = dist(f, s)
    G['bridge_a × lid_a'] = dist(bridge_a, LID_A); G['bridge_b × lid_b'] = dist(bridge_b, LID_B)   # 转子盘B: lid = 罩子半片 (含顶盖)
    G['bridge_a × bar'] = dist(br_rest_a, L.bar_s)
    rep['fpc'] = fpc_len()
    rep['tape'] = tape_check()
    # 顶盖 (Z≥LID_Z0) 处桥板实际外伸: 方块按 F 面 (局部 Y_LED+4.6) +0.4 开槽; 真模型 F 面器件 (U56 等 高 1.57) 伸得更外
    o = BRepAlgoAPI_Common(_br_loc, gbox(-40, 0, RS.LID_Z0 - 0.4, 40, 30, 80)); o.Build(); yl = bbox(o.Shape())[4]
    rep['axk'] = axk_check()
    if BRIDGE_FLIP:
        # FPC 出口净空 (给桥板挪件, KiCad 坐标): 区 1 = 座口 → 口外直段 + 外移 S 弯走完; 区 2 = 之后到桥板下沿 (FPC 已在外移后的平面)
        jl = 2 * R_JOG * math.sin(math.acos(1 - JOG / (2 * R_JOG)))
        ky0 = BR_ORG[1] - BR_MOUTH; ky1 = ky0 + OUT_A + jl
        xz = (round(132 - FPC_W / 2 - 0.5, 2), round(132 + FPC_W / 2 + 0.5, 2))
        h1 = round(SLOT_Z - FPC_T_STF / 2 - 0.1, 2); h2 = round(SLOT_Z + JOG - FPC_T / 2 - 0.1, 2)
        viol = []
        for n_, s_ in _br_parts:
            if n_ in ('FPC1', '桥板 PCB'): continue
            b = bbox(s_)
            if b[2] < BR_F - 0.1 or b[3] < xz[0] - 132 or b[0] > xz[1] - 132: continue
            kya, kyb = BR_ORG[1] - b[4], BR_ORG[1] - b[1]; h = round(b[5] - BR_F, 2)
            if kyb > ky0 and kya < ky1 and h > h1: viol.append((n_, '区1', (round(b[0] + 132, 2), round(b[3] + 132, 2)), (round(kya, 2), round(kyb, 2)), h))
            elif kyb > ky1 and h > h2: viol.append((n_, '区2', (round(b[0] + 132, 2), round(b[3] + 132, 2)), (round(kya, 2), round(kyb, 2)), h))
        hit = {}
        _brw = [(n_, xf(s_, T_ECC)) for n_, s_ in BR_LOC]          # 先留住 (interf 按 id 缓存, 临时对象 id 会复用)
        for n_, s_ in _brw:
            v = interf(s_, fpc_a)
            if v > 1e-4: hit[n_] = round(v, 3)
        rep['keepout'] = dict(zone1=dict(kx=xz, ky=(round(ky0, 3), round(ky1, 3)), h_max_from_F=h1, note='座口外 2.0 直段 (补强露 1.0 + 隙 1.0) + 外移 S 弯 (中线 R%.1f, 侧移 %.3f, 长 %.2f)' % (R_JOG, JOG, jl)),
                              zone2=dict(kx=xz, ky=(round(ky1, 3), 136.0), h_max_from_F=h2, note='FPC 外移后贴 F 面器件外走 (平面离 F 面 %.3f)' % (SLOT_Z + JOG)),
                              violators=viol, fpc_a_hits=hit,
                              alt_no_jog=dict(kx=xz, ky=(round(ky0, 3), 136.0), h_max_from_F=round(SLOT_Z - FPC_T / 2 - 0.1, 2), note='不外移 (FPC 一直在插口高度) 时整条带的限高'))
    rep['lid_pocket'] = dict(lid_z0=RS.LID_Z0, bridge_local_y_max=round(yl, 3), pocket_now=RS.BR_POCKET,
                             pocket_need={'a': round(ECC + yl + 0.4, 3), 'b': round(ECC - yl - 0.4, 3)},
                             note='rotor_shroud BR_POCKET 槽外边 Y_LED0+4.6+0.4 → Y_LED0+%.2f+0.4 (局部), 否则顶盖压桥板 F 面器件' % (yl - Y_LED))
    rep['seats'] = dict(J5=J5, J6=J6, bridge=dict(mouth_a=tuple(round(v, 3) for v in MOUTH_A), mouth_b=tuple(round(v, 3) for v in MOUTH_B),
                                                   step_fab=BR_SEAT, z_world=(round(zM, 3), round(ZC - (BR_SEAT['mouth'] - BR_SEAT['depth']), 3))),
                        pin1=dict(bridge=PIN1_BR, J5_x=J5['pin1_x'], J6_x=J6['pin1_x'],
                                  A_direct=PIN1_BR['a_world_x'] == J5['pin1_x'], B_direct=PIN1_BR['b_world_x'] == J6['pin1_x'],
                                  note='FPC 弯都绕 x 轴, 导体 x 位置全程不变: A 根 桥A 脚1 x%+.2f → J5 脚1 x%+.2f (%s); B 根 桥B 脚1 x%+.2f → J6 脚1 x%+.2f (%s)'
                                       % (PIN1_BR['a_world_x'], J5['pin1_x'], '1↔1 直通' if PIN1_BR['a_world_x'] == J5['pin1_x'] else '反序 ⇒ 需 J5 网络镜像',
                                          PIN1_BR['b_world_x'], J6['pin1_x'], '1↔1 直通' if PIN1_BR['b_world_x'] == J6['pin1_x'] else '反序 ⇒ 需 J6 网络镜像')))
    # 11-17: 底板座朝向方案汇总 + 等长 (同一料号) 评估
    Lf = rep['fpc']; la, lb = Lf['A']['total_mm'], Lf['B']['total_mm']; slack = round(abs(la - lb), 1)
    flat_b = [g for g in pb.segs if g[0] == 'L' and abs(g[1][1] - Z_FLAT_B) < 1e-6]
    fl = max(abs(g[2][0] - g[1][0]) for g in flat_b)
    rep['bb_seat_mode'] = dict(mode=BB_SEAT_MODE, J5=dict(kicad_at=J5['kicad_at'], face='+y' if J5['face'] > 0 else '-y', mouth_y=J5['mouth_y'], body_y=sorted((J5['mouth_y'], J5['back_y']))),
                               J6=dict(kicad_at=J6['kicad_at'], face='+y' if J6['face'] > 0 else '-y', mouth_y=J6['mouth_y'], body_y=sorted((J6['mouth_y'], J6['back_y']))),
                               pins=dict(A=rep['seats']['pin1']['A_direct'], B=rep['seats']['pin1']['B_direct']),
                               contact=dict(A=CONTACT['A']['kind'], B=CONTACT['B']['kind'], same_kind=CONTACT['A']['kind'] == CONTACT['B']['kind']),
                               length=dict(A=la, B=lb, diff=slack, unified_cut=max(Lf['A']['cut_mm'], Lf['B']['cut_mm']),
                                           take_up=dict(where='短的那根 (B) 毂盘顶平铺段 (y %.1f…%.1f, Z%.3f) 做一个 Z 形叠折: 两个 180° 折 (中线 R1.0, 内 0.925), 三层叠高 Z%.2f…%.2f (< 桥板/夹条下沿 Z37)'
                                                              % (min(min(g[1][0], g[2][0]) for g in flat_b), max(max(g[1][0], g[2][0]) for g in flat_b), Z_FLAT_B,
                                                                 Z_FLAT_B - FPC_T / 2, Z_FLAT_B + 4 * 1.0 + FPC_T / 2),
                                                        fold_layer_len=round(slack / 2, 2), flat_len=round(fl, 2),
                                                        ok=slack / 2 + 2 * 1.0 <= fl - 2.0 and Z_FLAT_B + 4.0 + FPC_T / 2 < Z0 - 0.5,
                                                        note='叠折段不贴胶 (胶只贴最下层平直段两端); 叠层间留 1.85 空隙')))
    rep['bridge'] = dict(zc=ZC, axk=AXK_PAIR, bbox_a=[round(v, 2) for v in bbox(bridge_a)], bbox_b=[round(v, 2) for v in bbox(bridge_b)],
                         vs_block=dict(block_seat=dict(x=20.75, y_local=(round(Y_LED + 4.6, 3), round(Y_LED + 6.6, 3)), z=(Z0 + 2.0, Z0 + 6.4), mouth_z=Z0 + 2.0, fpc_plane_y_local=round(Y_LED + 5.6, 3)),
                                       real_seat=dict(x=BR_SEAT['xh'], y_local=(round(Y_LED + AXK_H + BR_F, 3), round(Y_LED + AXK_H + BR_F + SEAT_H, 3)),
                                                      z=(round(zM, 3), round(ZC - BR_SEAT['mouth'] + BR_SEAT['depth'], 3)), mouth_z=round(zM, 3), fpc_plane_y_local=round(Y_LED + AXK_H + BR_F + SLOT_Z, 3))))
    # 平衡
    old_a = cog(L.br_a)[1]; old_b = cog(L.br_b)[1]
    fx = [('FPC A', vol(fpc_a) * FPC_RHO, cog(fpc_a)[1]), ('FPC B', vol(fpc_b) * FPC_RHO, cog(fpc_b)[1]),
          ('胶 A', vol(tape_a) * 1.1e-3, cog(tape_a)[1]), ('胶 B', vol(tape_b) * 1.1e-3, cog(tape_b)[1])]
    rep['balance'] = dict(old_12g_block=balance(12.0, old_a, old_b), new_11g_real=balance(BR_G, COM_A, COM_B),
                          new_plus_fpc=balance(BR_G, COM_A, COM_B, fx),
                          bridge=dict(g=BR_G, com_a=tuple(round(v, 2) for v in COM_A), com_b=tuple(round(v, 2) for v in COM_B),
                                      old_com_a=tuple(round(v, 2) for v in old_a), old_com_b=tuple(round(v, 2) for v in old_b)),
                          fpc_g={n: round(g, 2) for n, g, _ in fx},
                          note='其余件同 led_support report() (底板仍 44.5 g 估 @ 板框中心); 两面配平按 Z45/r83 + 梳齿 r40')
    # 竖槽 (11-16 晚定: 接受小 R, 不挪底板): J6 端补强 5.0 (口外直段 2.0) 时 2R_A + R_B 可用多少
    def r_eq(out_j6):
        av = J6['mouth_y'] - out_j6 - yA - FPC_T - CH_GAP; return round(av / 3, 3), round(av / 3 - FPC_T / 2, 3)
    rep['channel'] = dict(mouth_A_y=round(yA, 3), J6_mouth_y=J6['mouth_y'], gap_A_B=round(Y_RB - Y_RA - FPC_T, 3),
                          stf_J6_5mm=dict(R_center_inner=r_eq(STF_L - FPC_INS + BEND_GAP), note='J6 端补强 5.0 ⇒ 内 R 只 ~0.6 < 6T, 不取'),
                          stf_J6_4mm=dict(R_center_inner=r_eq(OUT_J6), used=(R_CH, round(R_CH - FPC_T / 2, 3)), note='J6 端补强缩到 4.0 (= 插入, 最小) ⇒ 取中线 R1.0 / 内 0.925 (6.2T)'),
                          need_R3_inner_J6_mouth=round(yA + 3 * (3.0 + FPC_T / 2) + FPC_T + CH_GAP + OUT_J6, 2))
    return rep


def export():
    OUT.mkdir(parents=True, exist_ok=True)
    COL = dict(bridge_a='#1E8449', bridge_b='#1E8449', fpc_a='#E67E22', fpc_b='#D35400', fpc_fix='#F4D03F', bb_fpc_seats='#555555')
    items = dict(bridge_a=bridge_a, bridge_b=bridge_b, fpc_a=fpc_a, fpc_b=fpc_b, fpc_fix=comp([tape_a, tape_b]), bb_fpc_seats=comp([seat_j5, seat_j6]))
    for k, s in items.items():
        nm = f'{k}_v1_2'
        write_doc([(nm, s, COL[k], None, False)], OUT / f'{nm}.step', nm)
        BRepMesh_IncrementalMesh(s, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(s, str(OUT / f'{nm}.stl'))
    # 看走线用 3MF: 转子盘 + 灯板 + 桥板 + 底板 + FPC + 夹条 + 立板 (不带罩子)
    from mf3_v1_2 import write3mf
    parts = [('转子毂盘 hub_disc_v1_2', B.hub, '#4F86C6', 0.05), ('承载盘 rim_ring', B.rim, '#6AA84F', 0.05),
             ('灯板 A (+y)', L.led_a, '#145A32', 0.05), ('灯板 B (-y)', L.led_b, '#0E3B22', 0.05),
             ('桥板 A (真模型)', bridge_a, '#27AE60', 0.03), ('桥板 B (真模型)', bridge_b, '#229954', 0.03),
             (f'底板 {BB_STEP_NAME} (交付 STEP)', BB_STEP_USED, '#1E8449', 0.05), ('CZ06 包络', CZ06_ENV, '#7D8C8E', 0.05),
             ('底板 FPC 座 J5/J6 (Fab 外形)', comp([seat_j5, seat_j6]), '#555555', 0.03),
             ('FPC A (桥A→J5)', fpc_a, '#E67E22', 0.02), ('FPC B (桥B→J6)', fpc_b, '#D35400', 0.02), ('双面胶 ×2', comp([tape_a, tape_b]), '#F4D03F', 0.02),
             ('灯板夹条 led_bar', L.bar_s, '#8E7CC3', 0.03), ('立板 +x led_post_a', L.post_a, '#F1C232', 0.03), ('立板 -x led_post_b', L.post_b, '#E69138', 0.03)]
    if B.ROTOR_B:   # 11-18 转子盘B
        import io as _io, contextlib as _cl
        with _cl.redirect_stdout(_io.StringIO()):
            import rotor_b_v1_2 as RB
        parts = [('玻纤板 fr4_plate_v1_2b', RB.fr4, '#C9B458', 0.05), ('承载盘 rim_ring_v1_2b', RB.rim, '#6AA84F', 0.05)] + \
                [p for p in parts if not p[0].startswith(('转子毂盘', '承载盘', '立板'))] + \
                [('屏幕固定件 +x screen_holder_v1_2b_a', RB.hold_a, '#F1C232', 0.03), ('屏幕固定件 −x screen_holder_v1_2b_b', RB.hold_b, '#E69138', 0.03)]
    write3mf(str(B.V12 / ('assembly_v1_2_FPC走线.3mf' if BRIDGE_FLIP else 'assembly_v1_2_FPC走线_旧朝向.3mf')), parts)


def _sample(p, n=24):
    """中线折线点 (YZ)"""
    P = []
    for g in p.segs:
        if g[0] == 'L': P += [g[1], g[2]]
        else:
            _, p0, p1, a0, a1, c, R, sg = g
            for k in range(n + 1):
                a = a0 + (a1 - a0) * k / n; nn = Path2.n(a); P.append((c[0] - sg * R * nn[0], c[1] - sg * R * nn[1]))
    return P


def drawing():
    """FPC 规格图 (A3 横, 中文): 展开外形 / 叠层 / 补强 + 金手指 / 弯曲位置 / 走线侧视 / 安装说明 → models/fpc_v1_2/FPC_规格图_v1_2.{pdf,png}"""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    from matplotlib.patches import Rectangle
    font_manager.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.family'] = 'SimHei'; plt.rcParams['axes.unicode_minus'] = False
    PW, PH = 420.0, 297.0
    fig = plt.figure(figsize=(PW / 25.4, PH / 25.4)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, PW); ax.set_ylim(0, PH); ax.axis('off')
    T = lambda x, y, t, sz=7, **k: ax.text(x, y, t, fontsize=sz, **k)
    ax.add_patch(Rectangle((5, 5), PW - 10, PH - 10, fill=False, lw=0.8))
    L_ = fpc_len()
    T(PW / 2, PH - 14, 'POV3D V1.2 — 桥 FPC 规格 (A: 桥板 A → 底板 J5 / B: 桥板 B → 底板 J6)', 13, ha='center')
    T(PW / 2, PH - 20, '70P  0.5 节距  宽 35.5  单层铜  弯曲区 ≤0.15 / 补强区 0.3  一次预成形静态安装 (IPC-2223)', 8, ha='center')

    # ---- 展开外形 (2:1) ----
    sc = 1.5
    def plan(x0, y0, nm):
        d = L_[nm]; p = pa if nm == 'A' else pb; Lt = p.L; W = FPC_W; s0, s1 = STF[nm]
        X = lambda s: x0 + s * sc; Y = lambda w: y0 + (w + W / 2) * sc
        T(x0, Y(W / 2) + 9, f'FPC {nm}  展开 (1.5:1)  —  {"桥板 A → 底板 J5 (外座)" if nm == "A" else "桥板 B → 底板 J6 (内座)"}', 9)
        for b in d['bends']['list']:                                         # 弯曲区
            ax.add_patch(Rectangle((X(b['s'][0]), Y(-W / 2)), (b['s'][1] - b['s'][0]) * sc, W * sc, fc='#D6EAF8', ec='#2E86C1', lw=0.4, ls='--'))
            T(X((b['s'][0] + b['s'][1]) / 2), Y(-W / 2) - 4.5, f"内R{b['R_inner']:g}\n{b['ang']}°", 5.6, ha='center', va='top', color='#1F618D')
            T(X((b['s'][0] + b['s'][1]) / 2), Y(W / 2) + 1.2, f"{b['s'][0]:.1f}–{b['s'][1]:.1f}", 5.0, ha='center', color='#1F618D')
        for sa, sb, txt in ((0, s0, f'补强 {s0:g}'), (Lt - s1, Lt, f'补强 {s1:g}')):   # 补强 (背面)
            ax.add_patch(Rectangle((X(sa), Y(-W / 2)), (sb - sa) * sc, W * sc, fc='none', ec='#7D3C98', hatch='////', lw=0.5))
            T(X((sa + sb) / 2), Y(-W / 2) - 13, txt, 6, ha='center', color='#7D3C98')
        ax.add_patch(Rectangle((X(0), Y(-W / 2)), Lt * sc, W * sc, fill=False, lw=0.9))
        same = d['contact']['same']
        for e, (sa, sb) in enumerate(((0, FINGER_L), (Lt - FINGER_L, Lt))):  # 金手指 70 根 (0.5 节距, 宽 0.3)
            ls = '-' if (e == 0 or same) else (0, (2, 1.2))
            for k in range(70):
                w = -17.25 + 0.5 * k
                ax.plot([X(sa), X(sb)], [Y(w), Y(w)], color='#B7950B', lw=0.35, ls=ls)
        ax.plot([X(0) - 2, X(Lt) + 2], [Y(-17.25)] * 2, color='r', lw=0.4, ls=(0, (6, 2, 1, 2)))
        T(X(0) - 3, Y(-17.25), '1', 7, color='r', ha='right', va='center'); T(X(Lt) + 3, Y(-17.25), '1', 7, color='r', va='center')
        T(X(0) - 3, Y(17.25), '70', 6, ha='right', va='center'); T(X(Lt) + 3, Y(17.25), '70', 6, va='center')
        T(X(0), Y(-W / 2) - 19, '← 桥板端', 6.5); T(X(Lt), Y(-W / 2) - 19, ('底板 J5 端 →' if nm == 'A' else '底板 J6 端 →'), 6.5, ha='right')
        yd = Y(W / 2) + 5.5                                                   # 总长尺寸
        ax.annotate('', (X(0), yd), (X(Lt), yd), arrowprops=dict(arrowstyle='<->', lw=0.5))
        T(X(0), yd + 0.8, f"下料长 {d['cut_mm']:g}  (模型展开 {d['total_mm']:.1f} = 两端插入 4.0×2 + 口间中线 {d['centerline_mm']:.1f}; 余量在桥板端平直段)", 6.5)
        xd = X(Lt) + 9
        ax.annotate('', (xd, Y(-W / 2)), (xd, Y(W / 2)), arrowprops=dict(arrowstyle='<->', lw=0.5)); T(xd + 1, Y(0), '35.5', 6.5, va='center', rotation=90)
        T(X(0), Y(-W / 2) - 24, f"金手指 {FINGER_L:g} (0.5 节距 ×70, 宽 0.3); 接触面: {d['contact']['kind']} "
                                f"({'两端金手指在同一面' if same else '两端金手指在相反面: 右端虚线 = 在背面'}); {d['wiring'].replace('↔', '<->').replace('−', '-')}", 6.2)
    plan(15, 214, 'A')
    plan(15, 110, 'B')

    # ---- 叠层 ----
    x0, y0 = 222, 268
    T(x0, y0, '叠层 (单层铜, 信号与 GND 同层)', 9)
    rows = [('覆盖膜 PI 12.5 um + 胶 15 um', '0.028'), ('铜 1/3 oz 12 um (压延铜, 线宽/距 0.15/0.10)', '0.012'), ('基材 PI 25 um + 胶 (或无胶单面 FCCL)', '0.040–0.065'),
            ('弯曲区合计', '≤ 0.15  (按 0.15 建模)'), ('补强 PI (只在两端, 贴金手指背面)', '+0.15'), ('补强区合计 (= ZIF 座要求 FPC 厚)', '0.30 ± 0.03')]
    for i, (a, b) in enumerate(rows):
        y = y0 - 6 - 5 * i
        T(x0, y, a, 6.5); T(x0 + 120, y, b, 6.5, ha='right')
    T(x0, y0 - 39, '金手指: 镀金 (ENIG 或电镀硬金 ≥0.1 um), 端头起 3.5; 外形公差 宽 35.5 ±0.05, 端头倒角 0.3', 6.2)

    # ---- 走线侧视 (YZ, 2:1) ----
    sx, ox, oz = 2.0, 222.0, 165.0
    Pz = lambda y, z: (ox + (y + 14.5) * sx, oz + (z - 29.5) * sx)
    def box(y0_, z0_, y1_, z1_, **k):
        a_, b_ = Pz(y0_, z0_); c_, d_ = Pz(y1_, z1_); ax.add_patch(Rectangle((a_, b_), c_ - a_, d_ - b_, **k))
    T(ox, Pz(0, 49.5)[1] + 4, '走线侧视 (x=0 剖, 从 +x 看; 2:1; Y →, Z ↑)', 9)
    box(-14.5, 29.5, 60, HUB_TOP, fc='#D5DBDB', ec='none'); T(*Pz(-12, 29.9), '毂盘顶 Z%.1f' % HUB_TOP, 5.5)
    box(V.BB_POLY[0][1], B.Z_BB0, 60, ZT, fc='#A9DFBF', ec='k', lw=0.3); T(*Pz(20, 35.3), '底板 r4d', 5.5)
    cz = CZ06_BOX; box(cz[1], ZT, min(cz[3], 60), CZ06_TOP, fc='#E5E8E8', ec='k', lw=0.3); T(*Pz(30, 39.5), 'CZ06', 6)
    for j in (J6, J5):
        if j['mouth_y'] < 60: box(j['mouth_y'], ZT, min(j['back_y'], 60), ZT + SEAT_H, fc='#566573', ec='k', lw=0.3)
    for sgn, nm in ((1, 'A'), (-1, 'B')):
        yb0 = ECC + sgn * (Y_LED + AXK_H); yb1 = ECC + sgn * (Y_LED + AXK_H + BR_F); ys0 = ECC + sgn * (Y_LED + AXK_H + BR_F + SEAT_H)
        box(min(yb0, yb1), ZC - 18, max(yb0, yb1), 49.5, fc='#58D68D', ec='k', lw=0.3)
        box(min(yb1, ys0), zM, max(yb1, ys0), ZC - BR_SEAT['mouth'] + BR_SEAT['depth'], fc='#566573', ec='k', lw=0.3)
        yl0 = ECC + sgn * L.GAP_HALF; yl1 = ECC + sgn * Y_LED
        box(min(yl0, yl1), Z0, max(yl0, yl1), 49.5, fc='#145A32', ec='none')
        T(*Pz((yb0 + yb1) / 2, 48), f'桥板{nm}', 5.5, ha='center')
    box(ECC - L.GAP_HALF, Z0, ECC + L.GAP_HALF, 46, fc='#D2B4DE', ec='none'); T(*Pz(ECC, 44), '夹条', 5.5, ha='center')
    for p, col in ((pa, '#E67E22'), (pb, '#C0392B')):
        Q = [Pz(*q) for q in _sample(p)]; ax.plot([q[0] for q in Q], [q[1] for q in Q], color=col, lw=1.0)
    for nm, p in (('A', pa), ('B', pb)):
        for g, b in zip([g for g in p.segs if g[0] == 'A'], L_[nm]['bends']['list']):
            c = Pz(*g[5]); T(c[0], c[1], f"{nm}:R{b['R_inner']:g}", 5, color='#1F618D', ha='center', va='center')
    for t_, nm in ((tape_a, '胶'), (tape_b, '胶')):
        b = bbox(t_); box(b[1], b[2], b[4], b[5] + 0.25, fc='#F4D03F', ec='none')
    T(*Pz(-14, 27.0), '橙 = FPC A, 红 = FPC B, 黄 = 双面胶; 圆心处标内 R', 5.5)

    # ---- 竖槽局部 (6:1) ----
    s6, ox6, oz6 = 6.0, 222.0, 52.0
    Pd = lambda y, z: (ox6 + (y - 3.0) * s6, oz6 + (z - 33.0) * s6)
    def boxd(y0_, z0_, y1_, z1_, **k):
        y0_, y1_ = max(y0_, 3.0), min(y1_, 10.5); z0_, z1_ = max(z0_, 33.0), min(z1_, 41.0)
        if y1_ <= y0_: return
        a_, b_ = Pd(y0_, z0_); c_, d_ = Pd(y1_, z1_); ax.add_patch(Rectangle((a_, b_), c_ - a_, d_ - b_, **k))
    T(ox6, oz6 + 8 * s6 + 4, '局部 I: 竖槽 (6:1) — 桥板 A 座口 <-> 底板 J6 口', 8)
    boxd(ECC + Y_LED + AXK_H + BR_F, zM, ECC + Y_LED + AXK_H + BR_F + SEAT_H, 50, fc='#566573', ec='k', lw=0.3)
    boxd(ECC + Y_LED + AXK_H, ZC - 18, ECC + Y_LED + AXK_H + BR_F, 50, fc='#58D68D', ec='k', lw=0.3)
    boxd(V.BB_POLY[0][1], B.Z_BB0, 12, ZT, fc='#A9DFBF', ec='k', lw=0.3); boxd(J6['mouth_y'], ZT, 12, ZT + SEAT_H, fc='#566573', ec='k', lw=0.3)
    import matplotlib.path as mpath
    from matplotlib.patches import PathPatch
    for p, col in ((pa, '#E67E22'), (pb, '#C0392B')):
        Q = [q for q in _sample(p, 48) if 3.0 <= q[0] <= 10.5 and 33.0 <= q[1] <= 41.0]
        Q = [Pd(*q) for q in Q]; ax.plot([q[0] for q in Q], [q[1] for q in Q], color=col, lw=FPC_T * s6 * 2.83, solid_capstyle='butt')
    for nm, p, i in (('A', pa, 0), ('B', pb, -1)):
        g = [g for g in p.segs if g[0] == 'A'][i]; c = Pd(*g[5]); T(c[0], c[1], f'{nm} 内R{g[6] - FPC_T / 2:g}', 5.5, ha='center', va='center', color='#1F618D')
    T(ox6, oz6 - 5, f"A 座口下直段 {OUT_A:g} 后 180° 回弯; B 进 J6 前直段 {OUT_J6:g} (J6 端补强缩到 4.0); A/B 竖段间隙 {Y_RB - Y_RA - FPC_T:.3f}", 5.8)

    # ---- 技术要求 ----
    bA, bB = L_['A']['bends'], L_['B']['bends']
    notes = ['技术要求 / 安装:',
             ('1. 两根同一种做法: 导体直通, 世界 x 不变 (FPC 内不交叉, 弯都绕 x 轴), 只是长度不同; '
              + '底板 J5 座 k 脚 ↔ 桥 A FPC1 第 %s 脚, J6 座 k 脚 ↔ 桥 B FPC1 第 %s 脚 (按模型 1 脚世界 x 自动判: 桥A 脚1 x%+.2f / J5 脚1 x%+.2f, 桥B 脚1 x%+.2f / J6 脚1 x%+.2f)。'
              % ('k' if PIN1_BR['a_world_x'] == J5['pin1_x'] else '71−k', 'k' if PIN1_BR['b_world_x'] == J6['pin1_x'] else '71−k',
                 PIN1_BR['a_world_x'], J5['pin1_x'], PIN1_BR['b_world_x'], J6['pin1_x'])),   # 11-18 底板窗口要求: 删 r4h 旧文字「座 pin k = 桥板 pin k, 不镜像」
             '   核对口径: 桥 A 世界 x = -(kx-132), 桥 B 世界 x = +(kx-132), 按物理 x 对脚 (例: 桥 A pin1 TCK 在 kx114.75 -> 世界 x+17.25)。',
             f"2. 接触面: A {L_['A']['contact']['kind']}, B {L_['B']['contact']['kind']} (按走线几何: 两座同型号 XW0525512, 判 PCB 在 FPC 哪一面; 座子上/下接触以规格书为准, 同/异面结论不变)。",
             f"3. 补强 PI 贴金手指背面: A 两端 {STF['A'][0]:g}/{STF['A'][1]:g}; B 桥板端 {STF['B'][0]:g}, J6 端 {STF['B'][1]:g} (= 插入深 4.0, 竖槽放不下 5.0 + 1 隙)。",
             f"4. 弯起点离补强边 ≥1: A 首弯离桥板端 {bA['first_from_bridge_end']:.1f} / 末弯离 J5 端 {bA['last_from_board_end']:.1f}; B 首弯 {bB['first_from_bridge_end']:.1f} / 末弯离 J6 端 {bB['last_from_board_end']:.1f}。",
             f"5. 最小内弯半径 {min(L_['A']['min_R_inner'], L_['B']['min_R_inner']):g} (竖槽两处) ≥ IPC-2223 单层静态安装 6×厚 = {6 * FPC_T:g}; 其余 内R ≥ {R_J5 - FPC_T / 2:g}。弯曲区不得有过孔/补强/焊盘, 线垂直于弯折线。",
             '6. 一次预成形 (按侧视图弯好再插), 装好后不再动; 弯曲处不贴胶。',
             f"7. 防离心: 聚酰亚胺双面胶 0.1 只贴平直段 — B: 毂盘顶 y -8~3 (35.5×11); A: CZ06 顶 y 21~51 (35.5×30, 贴在平整面上)。",
             '8. 依据 IPC-2223 (柔性板设计): 单层静态弯曲 ≥6T; 补强边与弯曲起点 ≥1 mm。模型: v1.2/scripts/fpc_v1_2.py, models/fpc_v1_2/fpc_{a,b}_v1_2.step']
    for i, t in enumerate(notes):
        T(15, 82 - 4.6 * i, t, 6.2)
    # ---- 标题栏 (同 drawing_v1_2) ----
    ax.add_patch(Rectangle((10, 10), PW - 20, 24, fill=False, lw=0.8)); ax.plot([10, PW - 10], [22, 22], 'k', lw=0.4)
    for xx in (110, 180, 236, 276): ax.plot([xx, xx], [10, 34], 'k', lw=0.4)
    T(14, 26, 'FPC_A / FPC_B', 11); T(14, 14, '桥 FPC 70P 0.5 (桥板 <-> 底板)', 7.5)
    T(114, 26, '数量: A×1, B×1 / 台', 7.5); T(114, 14, '材料: PI 单层铜 + PI 补强', 7.5)
    T(184, 26, '展开 1.5:1 / 侧视 2:1 / 局部 6:1', 7.5); T(184, 14, '单位 mm', 7.5)
    T(240, 26, '2026-11-17 (底板 r4h)', 7.5); T(240, 14, 'POV3D V1.2', 7.5)
    T(280, 26, f"A 下料 {L_['A']['cut_mm']:g} / B 下料 {L_['B']['cut_mm']:g}", 7.5); T(280, 14, '桥板窗口 11-16 晚定规格 (G 出图)', 7.0)
    T(PW / 2, PH / 2, '草稿 - 待桥板 8 层 STEP 复核 (U52)' if BRIDGE_FLIP else '草稿 - 旧桥板朝向 (作废待重算)', 46, ha='center', va='center', color='red', alpha=0.18, rotation=20)
    T(PW - 15, PH - 14, '草稿', 16, ha='right', color='red')
    out = OUT / 'FPC_规格图_v1_2'
    fig.savefig(f'{out}.pdf'); fig.savefig(f'{out}.png', dpi=130); plt.close(fig)
    return out


def combo():
    """组合图 (新装法): 桥板 + 灯板 + FPC + 底板 + 转子盘; 正视 (看桥板 A FPGA 面, KiCad 视向) + 侧视 + 出口局部 → OUT/组合图_桥板FPC_v1_2.{pdf,png}"""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    from matplotlib.patches import Rectangle, FancyArrow
    font_manager.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.family'] = 'SimHei'; plt.rcParams['axes.unicode_minus'] = False
    PW, PH = 420.0, 297.0
    fig = plt.figure(figsize=(PW / 25.4, PH / 25.4)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, PW); ax.set_ylim(0, PH); ax.axis('off')
    T = lambda x, y, t, sz=7, **k: ax.text(x, y, t, fontsize=sz, **k)
    ax.add_patch(Rectangle((5, 5), PW - 10, PH - 10, fill=False, lw=0.8))
    T(PW / 2, PH - 13, 'POV3D V1.2 — 桥板 (最终装法) + 灯板 + 桥 FPC + 底板 + 转子盘  组合图', 13, ha='center')
    T(PW / 2, PH - 19, ('新装法: 桥板按 PCB 正放 (KiCad +y 朝转子盘), FPC 座在上沿插口朝下, FPC 贴 FPGA 面往下; 桥 J1<->灯板 J1, 桥 J2<->灯板 J2' if BRIDGE_FLIP else '旧朝向 (作废)'), 8, ha='center')
    T(PW - 15, PH - 13, '草稿 - 待桥板 6 层重布后复核', 9, ha='right', color='r')
    BRS = [(n, xf(s_, T_ECC)) for n, s_ in BR_LOC]
    def rect(P, b, **k):
        a_ = P(b[0], b[1]); c_ = P(b[2], b[3]); ax.add_patch(Rectangle((min(a_[0], c_[0]), min(a_[1], c_[1])), abs(c_[0] - a_[0]), abs(c_[1] - a_[1]), **k))
    # ---- 正视: 从 +y 看桥板 A 的 FPGA 面 (= KiCad 视向: 右 = KiCad +x = 世界 −x, 下 = KiCad +y = 世界 −Z), 1.5:1 ----
    sf, ox, oz = 1.5, 145.0, 172.0
    P = lambda x, z: (ox - x * sf, oz + (z - 28.0) * sf)
    T(ox - 90 * sf, P(0, 82)[1] + 3, '正视 (从 +y 看桥板 A 的 FPGA 面 = KiCad 视向; 1.5:1)', 9)
    rect(P, (-81.88, 28.0, 81.88, 30.5), fc='#AF9B6E', ec='none'); T(*P(80, 29), '转子盘 (毂盘顶 Z%.1f / 承载盘顶 Z32)' % HUB_TOP, 5.5, va='center')
    rect(P, (-81.88, Z0, 81.88, 82), fc='#145A32', ec='none'); T(*P(78, 79), '灯板 A (看插座面)', 6, color='w')
    bb = bbox(bridge_a); rect(P, (bb[0], ZC - 18, bb[3], ZC + 18), fc='#28B463', ec='k', lw=0.5)
    for n_, s_ in BRS:
        b = bbox(s_)
        if n_ in ('J1', 'J2'):
            rect(P, (b[0], b[2], b[3], b[5]), fc='none', ec='#BBBBBB', lw=0.6, ls='--')
        elif n_ == 'U52':
            rect(P, (b[0], b[2], b[3], b[5]), fc='#333333', ec='k', lw=0.4); T(*P((b[0] + b[3]) / 2, (b[2] + b[5]) / 2), 'U52 FPGA', 6, color='w', ha='center', va='center')
        elif n_.startswith('FPC1'):
            rect(P, (b[0], b[2], b[3], b[5]), fc='#1B1B1B', ec='k', lw=0.4); T(*P(-22, (b[2] + b[5]) / 2), 'FPC1 座 (插口朝下)', 6, va='center', color='#C0392B')
    ax_ = axk_check()
    for ref in ('J1', 'J2'):
        bx_, bz_ = ax_[ref]['1']['bridge_xz']; lx_, lz_ = ax_[ref]['1']['led_xz']
        ax.plot(*P(bx_, bz_), 'o', ms=4, color='#F1C40F'); ax.plot(*P(lx_, lz_), 'x', ms=5, color='#E74C3C')
        T(*P(bx_ + (6 if bx_ < 0 else -6), bz_ - 3), f'桥 {ref} <-> 灯板 {ref}\n(黄点 桥脚 1 / 红叉 灯板脚 1)', 5.5, ha='center')
    fp = bbox(fpc_a); u0 = P(FPC_W / 2, 0)[0]
    zt_ = MOUTH_A[2]
    ax.add_patch(Rectangle((u0, P(0, 30.6)[1]), FPC_W * sf, (zt_ - 30.6) * sf, fc='#E67E22', alpha=0.55, ec='#D35400', lw=0.5))
    ax.add_patch(FancyArrow(P(0, zt_ - 1)[0], P(0, zt_ - 1)[1], 0, -12, width=1.2, head_width=4, head_length=4, color='#C0392B'))
    T(*P(-19, 45), 'FPC A 贴 FPGA 面往下\n(过桥板下沿 → 底板 J5)', 6, color='#A04000')
    rect(P, (-51.2, B.Z_BB0, 47.3, ZT), fc='none', ec='#1E8449', lw=0.7, ls='--'); T(*P(-50, ZT + 0.6), '底板 r4d (在前方 y8.6–66.6, 虚线)', 5.5, color='#1E8449')
    for j, nm in ((J6, 'J6'), (J5, 'J5')):
        rect(P, (-j['xh'], ZT, j['xh'], ZT + SEAT_H), fc='none', ec='#555', lw=0.5, ls=':')
    ax.annotate('', P(-70, 70), P(-80, 70), arrowprops=dict(arrowstyle='->', lw=0.6)); T(*P(-70, 71.5), 'KiCad +x', 5.5)
    ax.annotate('', P(-82, 60), P(-82, 70), arrowprops=dict(arrowstyle='->', lw=0.6)); T(*P(-83, 63), 'KiCad +y\n(朝转子盘)', 5.5)
    # ---- 侧视: YZ (从 +x 看), 1.6:1 ----
    sv, oy, oz2 = 1.6, 30.0, 40.0
    Q = lambda y, z: (oy + (y + 16.0) * sv, oz2 + (z - 28.0) * sv)
    T(oy, Q(0, 82)[1] + 3, '侧视 (x=0 剖, 从 +x 看; 1.6:1) — 橙 A 根 (桥 A→J5), 红 B 根 (桥 B→J6), 黄 = 双面胶', 9)
    rect(Q, (-16, 28.0, 68, HUB_TOP), fc='#AF9B6E', ec='none')
    for sg in (1, -1):
        yl0, yl1 = ECC + sg * L.GAP_HALF, ECC + sg * Y_LED
        rect(Q, (min(yl0, yl1), Z0, max(yl0, yl1), 82), fc='#145A32', ec='none')
        yb0, yb1 = ECC + sg * (Y_LED + AXK_H), ECC + sg * (Y_LED + AXK_H + BR_F)
        rect(Q, (min(yb0, yb1), ZC - 18, max(yb0, yb1), ZC + 18), fc='#28B463', ec='k', lw=0.3)
        T(*Q((yb0 + yb1) / 2, ZC + 19.5), '桥板 A' if sg > 0 else '桥板 B', 6, ha='center')
    for s_ in (seat_a, seat_b):
        b = bbox(s_); rect(Q, (b[1], b[2], b[4], b[5]), fc='#1B1B1B', ec='none')
    for nm in ('U52',):
        for s_ in [xf(x_, T_ECC) for n_, x_ in BR_LOC if n_ == nm] + [xf(xf(x_, rotz(180)), T_ECC) for n_, x_ in BR_LOC if n_ == nm]:
            b = bbox(s_); rect(Q, (b[1], b[2], b[4], b[5]), fc='#333333', ec='none'); T(*Q(b[4] + 0.5 if b[1] > 0 else b[1] - 3, (b[2] + b[5]) / 2), 'U52', 5)
    rect(Q, (ECC - L.GAP_HALF, Z0, ECC + L.GAP_HALF, Z0 + 9), fc='#D2B4DE', ec='none')
    rect(Q, (V.BB_POLY[0][1], B.Z_BB0, V.BB_POLY[2][1], ZT), fc='#A9DFBF', ec='k', lw=0.3); T(*Q(56, 35.3), '底板 r4d', 5.5)
    cz = CZ06_BOX; rect(Q, (cz[1], ZT, cz[3], CZ06_TOP), fc='#E5E8E8', ec='k', lw=0.3); T(*Q(35, 39.5), 'CZ06', 6, ha='center')
    for j, nm in ((J6, 'J6 (口朝 %s)' % ('+y' if J6['face'] > 0 else '-y')), (J5, 'J5 (口朝 %s)' % ('+y' if J5['face'] > 0 else '-y'))):
        rect(Q, (j['mouth_y'], ZT, j['back_y'], ZT + SEAT_H), fc='#566573', ec='k', lw=0.3); T(*Q(min(j['mouth_y'], j['back_y']), ZT - 2.2), nm, 5.5)
    for p_, col in ((pa, '#E67E22'), (pb, '#C0392B')):
        q = [Q(*t) for t in _sample(p_)]; ax.plot([t[0] for t in q], [t[1] for t in q], color=col, lw=1.1)
    for t_ in (tape_a, tape_b):
        b = bbox(t_); rect(Q, (b[1], b[2], b[4], b[5] + 0.3), fc='#F4D03F', ec='none')
    T(*Q(MOUTH_A[1] + 2.5, MOUTH_A[2] + 1), '座口 (朝下)', 5.5, color='#C0392B'); T(*Q(MOUTH_B[1] - 7, MOUTH_B[2] + 1), '座口 (朝下)', 5.5, color='#C0392B')
    # ---- 出口局部 (桥板 A 座口下, 8:1) ----
    s8, ox8, oz8 = 8.0, 215.0, 45.0
    Rz = lambda y, z: (ox8 + (y - 1.5) * s8, oz8 + (z - 57.5) * s8)
    T(ox8, oz8 + 10.5 * s8 + 3, '局部: 桥板 A 座口出口 (8:1) — 2.0 直段 + 外移 S 弯 躲 FPGA', 8)
    def rr(b):
        y0_, z0_, y1_, z1_ = max(b[0], 1.5), max(b[1], 57.5), min(b[2], 9.0), min(b[3], 68.0)
        if y1_ > y0_ and z1_ > z0_: rect(Rz, (y0_, z0_, y1_, z1_), **b[4])
    yb0 = ECC + Y_LED + AXK_H
    rr((yb0, ZC - 18, yb0 + BR_F, ZC + 18, dict(fc='#28B463', ec='k', lw=0.3)))
    for n_, s_ in BRS:
        b = bbox(s_)
        if b[1] > yb0 + BR_F - 0.2 and abs(b[0] + b[3]) / 2 < 20:
            rr((b[1], b[2], b[4], b[5], dict(fc='#1B1B1B' if n_.startswith('FPC1') else '#555555', ec='none')))
    q = [Rz(*t) for t in _sample(pa, 60)]
    cp = Rectangle(Rz(1.5, 57.5), 7.5 * s8, 10.5 * s8, fc='none', ec='#999', lw=0.4); ax.add_patch(cp)
    ln, = ax.plot([t[0] for t in q], [t[1] for t in q], color='#E67E22', lw=FPC_T * s8 * 2.83, solid_capstyle='butt'); ln.set_clip_path(cp)
    T(*Rz(MOUTH_A[1] + 0.3, MOUTH_A[2] + 0.3), '座口', 6, color='#C0392B')
    kz = rep_keep = None
    T(ox8, oz8 - 6, f'FPC 平面: 插口 F+{SLOT_Z:g} → 外移 {JOG:.3f} 到 F+{SLOT_Z + JOG:.3f}; S 弯中线 R{R_JOG:g} (内 {R_JOG - FPC_T / 2:g}); 灰 = 桥板 F 面器件 (x 投影全叠)', 5.8)
    # ---- 说明 ----
    L_ = fpc_len(); pin = PIN1_BR
    notes = ['说明:', f"1. 桥 J1/J2 与灯板逐脚对应: 脚 1 都在上端 Z{ax_['J1']['1']['bridge_xz'][1]:.1f}, 桥 J1 在 x{ax_['J1']['1']['bridge_xz'][0]:+.1f} 侧 = 灯板 J1 ({'OK' if ax_['ok_1to1'] else '不对!'})",
             f"2. FPC1 座在桥板上沿 (Z{MOUTH_A[2]:.2f}–{ZC + BR_MOUTH + BR_SEAT['depth']:.2f}), 插口朝下 (板内, 朝 FPGA)",
             f"3. 线序: 桥 A 脚 1 x{pin['a_world_x']:+.2f} -> J5 脚 1 x{J5['pin1_x']:+.2f} ({'直通' if pin['a_world_x'] == J5['pin1_x'] else '反 => J5 镜像'});",
             f"   桥 B 脚 1 x{pin['b_world_x']:+.2f} -> J6 脚 1 x{J6['pin1_x']:+.2f} ({'直通' if pin['b_world_x'] == J6['pin1_x'] else '反 => 底板 J6 镜像 (pin k <-> 71-k)'})",
             f"4. FPC 长 (展开/下料): A {L_['A']['total_mm']:.1f}/{L_['A']['cut_mm']:g}, B {L_['B']['total_mm']:.1f}/{L_['B']['cut_mm']:g}; 最小内 R {min(L_['A']['min_R_inner'], L_['B']['min_R_inner']):g}",
             '5. 双面胶: B 根贴毂盘顶平铺段, A 根贴 CZ06 顶; 弯曲处不贴', '6. 模型: v1.2/scripts/fpc_v1_2.py (BRIDGE_FLIP=True 默认)']
    for i, t in enumerate(notes):
        T(300, 140 - 6 * i, t, 5.8)
    out = OUT / '组合图_桥板FPC_v1_2'
    fig.savefig(f'{out}.pdf'); fig.savefig(f'{out}.png', dpi=130); plt.close(fig)
    return out


if __name__ == '__main__':
    export()
    drawing()
    combo()
    rep = report()
    json.dump(rep, open(OUT / 'fpc_report.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    print(json.dumps(rep, indent=1, ensure_ascii=False))
