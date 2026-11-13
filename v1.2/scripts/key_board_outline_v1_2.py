# -*- coding: utf-8 -*-
"""按键板板框 (V1.2, 用户 11-13): 2 按键 + 1 三色 LED + 3 单色 LED (全贴片), 40 x 22.5 板, 竖放在 +Y 下罩墙里, 正面朝外。
固定 (11-13 前面平板): 板左右 2×M3 安装孔 Φ3.2 @ (3.5, 13) / (36.5, 13) (11-13 (五) 中线); 支架 (scripts/key_bracket_v1_2.py) 前面是一整块平板 压住板**正面** (整板覆盖),
  M3×8 超薄头埋进平板前面沉孔往里穿平板 + 板 1.6, **背面上 M3 法兰螺母** (Φ7.6×3.7) ⇒ 背面每孔 Φ8 禁布; 正面孔周 Φ4.8 禁布 (平板压板环)。
  平板背面只在元件处开: 按键本体 + 脚让位腔, 每颗 LED 一个 Φ3.2 隔光通道 (导光柱从外皮外面插进来)。其余平板背面全贴板。
  板下沿坐支架底条 (Z3); 支架脚 2×M3 从底盘下往上, 法兰螺母坐脚顶。下罩从上罩下来; 按键 = 下罩外皮 H 形缝舌片 (外皮不开按键孔)。
11-13 (三) 用户新定元件: 按键 6×6×7.5 贴片 ZX-QC66-7.5TP ×2 @ (11, 18.5) / (11, 7.5) (11-13 (四) 间距 11, 板高 22.5); 三色 1615 (XL-1615RGBC) @ (17, 10); 单色 0603 ×3 @ (22 / 26.5 / 31, 10)。
11-13 (五) 用户: 按键转 90° (焊盘外包 5.6×9.5 竖), 按键 / 螺丝 / LED 行对板水平中线对称: 板高 22.5 → 26 (中线 Y13), 螺丝 (3.5 / 36.5, 13), LED 行 Y13 @ X 17 / 21.5 / 26 / 30.5; 按键仍 (11, 18.5 / 7.5) ⇒ 整机 Z 不变, 舌片 / 力不变;
  R1–R6 / C1 搬正面 (单面贴), 一行 Y19.5 节距 2.0。
输出 models/key_board_v1_2/key_board_outline_v1_2.dxf (板框 + 安装孔 + 禁布 + 推荐元件位 + 焊盘外包, 给画 PCB 用) + _layout.png
坐标: 板正视 (从外面看), 原点 = 板左下角, X 向右 (= 整机 -X, 整机 x = 20 − X), Y 向上 (= 整机 Z = 3 + Y)。
本文件只在 __main__ 出图; 常数给 key_bracket_v1_2.py import。"""
import math
from pathlib import Path

V12 = Path(__file__).resolve().parents[1]
OUT = V12 / 'models' / 'key_board_v1_2'

W, H, T = 40.0, 26.0, 1.6          # 板框 / 板厚 (11-13 (四): 按键拉开到间距 11, 板高 20 → 22.5; 11-13 (五) 用户: 按键 / 螺丝 / LED 对板水平中线对称 ⇒ 22.5 → 26, 中线 Y13, 下沿仍 Z3)
YC = H / 2                         # 板水平中线 Y13 (= 整机 Z16)
EDGE_KO = 1.0                      # 四边禁布
BACK_MAX = 6.0                     # 背面元件最高 (含插座)
MH = [(3.5, YC), (W - 3.5, YC)]    # M3 安装孔 Φ3.2 (用户 11-13; 11-13 (五) 移到中线 Y13, 左右对称)
MH_D = 3.2
BACK_KO_D = 8.0                    # 背面法兰螺母 Φ7.6 禁布 Φ8
FRONT_KO_D = 4.8                   # 正面孔周禁布 (平板压板环; 按键焊盘外包离孔心只 2.75, 放不下 Φ8)
# 按键: 6×6×7.5 贴片轻触 ZX-QC66-7.5TP (用户 11-13 (三)); 脚沿板 X 方向伸出 (Y 向两键间距只有 7, 放不下 9.5)
BTN = [(11.0, YC + 5.5), (11.0, YC - 5.5)]  # (11-13 (五) 对中线 Y13 对称, 仍 = 板 Y18.5 / 7.5, 整机 Z21.5 / Z10.5 ⇒ 舌片 / 力不变) 中心 (上 / 下); 11-13 (四) 间距 7 → 11 (= 整机 Z21.5 / Z10.5; 两舌片悬臂各 8.5, 弹性力 ≤4 N 定的上限 ≈11.3)
BTN_BODY, BTN_BODY_H, BTN_H, BTN_STEM_D = 6.0, 3.45, 7.5, 3.5   # 本体 6×6 高 3.45, 杆 Φ3.5, 板面到杆顶 7.5
BTN_TRAVEL = 0.2                   # 行程
BTN_LEG_W = 8.6                    # 脚外宽 (11-13 (五) 转 90° 后沿 Y)
BTN_PAD_OUT = (5.6, 9.5)           # 焊盘外包 (X, Y) (11-13 (五) 用户: 按键转 90°, 长向竖 (板 Y): 5.6 宽 × 9.5 高 ⇒ 外包 Y 2.75–12.25 / 13.75–23.25)
BTN_PAD_C = (4.5, 8.0)             # 焊盘中心距 (X, Y) ⇒ 每焊盘 1.5 × 1.1, 中心 (±4.0, ±2.25) (11-13 晚 封装 agent 更正: 原 (6.5, 3.4) 是焊盘内边距, 不是中心距; 外包 9.5×5.6 不变)
BTN_PAD = (BTN_PAD_OUT[0] - BTN_PAD_C[0], BTN_PAD_OUT[1] - BTN_PAD_C[1])
BTN_LEG_H = 1.0                    # 脚 + 焊锡高度 (估, 平板背面脚让位按这个 +0.5)
RGB = (17.0, YC)                   # 三色 LED 1615 (XL-1615RGBC) 中心 (11-13 (五) LED 行上中线 Y13, 按键右边, 节距 4.5)
RGB_W, RGB_L, RGB_H = 1.6, 1.5, 0.6     # X × Y × 高
LED = [(21.5, YC), (26.0, YC), (30.5, YC)]   # 单色 0603 中心 (节距 4.5; 末颗隔光通道离右螺丝沉孔 Φ7.4 留 0.7)
LED_W, LED_L, LED_H = 1.6, 0.8, 0.8     # 0603 (高按 0.8 算)

# 背面 J1 = JST GH 1.25 12P 卧贴 SM12B-GHS-TB (用户 11-13 晚), 插头 GHR-12V-S 从板下沿方向 (整机 Z 向下) 插, 线往下出再弯向 −Y 走底盘面到电机控制板 U24
#   封装 Connector_JST:JST_GH_SM12B-GHS-TB_1x12-1MP_P1.25mm_Horizontal: 原点 = 12 脚焊盘行中点往前 1.85; 封装 +y = 插口方向;
#   JST eGH.pdf: 座 B = 18.25 (含固定脚) × 高 4.25, 本体 y −1.6..2.45 (深 4.05), 信号脚 y −1.85 (0.6×1.7), 固定脚 (±8.725, 1.35) 1×2.7
#   插头 GHR-12V-S: 宽 16.25 (B), 长 5.7 / 高 4.15 (表图); 插合后露出插口按 5.0 算 (保守), 宽按 17.25 (+锁扣/手指余量), 厚按座高 4.25
J1_X = 20.0                        # 板系 X (= 整机 x 0, 两 M3 中间)
J1_MATE_Y = 6.0                    # 插口面板系 Y (= 整机 Z9); 插头端 Y 1.0 (Z4) ⇒ 插头下面到底盘 4.0 给线弯 (≥3)
J1_ORG_Y = J1_MATE_Y + 2.45        # 封装原点 (封装 +y 2.45 = 插口面, 朝板系 −Y)
J1_W, J1_BODY_Y, J1_H = 18.25, (-1.6, 2.45), 4.25
J1_PIN_Y, J1_PIN_TIP = -1.85, -2.7  # 信号焊盘中心 / 外端 (封装 y)
J1_PITCH, J1_N = 1.25, 12
J1_CRT = (9.73, 3.2)               # 封装 courtyard 半宽 / 半深 (±9.73 × ±3.2)
PLUG_W, PLUG_L, PLUG_T = 17.25, 5.0, 4.25
BEND = 3.0                         # 插头端以外留线弯
CABLE_W, CABLE_T = 14.0, 1.6       # 12 根 AWG30 (外径 ≈0.6–0.8) 压扁 / 两层的外包
BACK_R_MAX = 1.0                   # (11-13 晚 原背面贴片区限高; 11-13 单面贴后背面只剩 J1, 留着给以后加件)

# 正面贴片阻容 (用户 11-13 单面贴: JLC 只贴顶面更便宜 ⇒ R1–R6 / C1 由背面搬到正面 LED 行上方; J1 留背面手焊, 平板盖着正面贴不了)
#   竖放 (焊盘沿 Y), 管脚 1 (LED 侧) 朝下; 按 LED 顺序左→右, C1 最左 (靠 J1 pin8 +3V3)
#   11-13 (五): 一行等距 2.0 (同向), LED 行上方; C1 在左端 (靠 J1 pin8 +3V3 进线 X18.1), 整行对 LED 行居中 (中点 X23.75)
SMD_Y, SMD_PITCH = 19.5, 2.0
SMD_F = {r: (RGB[0] + 0.75 + i * SMD_PITCH, SMD_Y) for i, r in enumerate(('C1', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6'))}
SMD_ENV = (0.95, 2.45)             # 0603 外包 X × Y (竖放; 焊盘 0.95 宽 / 两焊盘外端 2.45 ⊇ 本体 0.8×1.6), R 和 C 同
SMD_H = {'R': 0.7, 'C': 1.0}       # 离板高 (0603 R 标称 0.45–0.55 / 100nF 0.8±0.1, 都按上限再 +0.1)
SMD_CLR = 0.3                      # 平板背面让位腔: 外包 +0.3 每边, 深 = 最高件 +0.3 (一个共用腔)
TUNNEL_D = 3.2                     # LED 隔光通道 (= key_bracket PL_LED_D)
CB_D = 7.4                         # 板螺丝头沉孔 (平板前面; = key_bracket CB_D)


def smd_env(ref):
    """正面贴片件外包 (X0, Y0, X1, Y1) 板系"""
    X, Y = SMD_F[ref]; w, l = SMD_ENV
    return (X - w / 2, Y - l / 2, X + w / 2, Y + l / 2)


def smd_pocket():
    """平板背面共用让位腔 (X0, Y0, X1, Y1, 深) 板系"""
    e = [smd_env(r) for r in SMD_F]
    return (min(a[0] for a in e) - SMD_CLR, min(a[1] for a in e) - SMD_CLR, max(a[2] for a in e) + SMD_CLR, max(a[3] for a in e) + SMD_CLR,
            round(max(SMD_H[r[0]] for r in SMD_F) + SMD_CLR, 3))


def _rc_gap(r, c, d):
    """矩形 (X0,Y0,X1,Y1) 到圆 (c, 直径 d) 边的距离"""
    dx = max(r[0] - c[0], 0, c[0] - r[2]); dy = max(r[1] - c[1], 0, c[1] - r[3]); return math.hypot(dx, dy) - d / 2


def _rr_gap(a, b):
    return max(b[0] - a[2], a[0] - b[2], b[1] - a[3], a[1] - b[3])


def btn_reliefs():
    """平板背面按键让位 (本体 +0.3 / 焊盘外包 +0.3) 矩形 板系"""
    out = []
    for X, Y in BTN:
        h = BTN_BODY / 2 + 0.3; px, py = BTN_PAD_OUT[0] / 2 + 0.3, BTN_PAD_OUT[1] / 2 + 0.3
        out += [(X - h, Y - h, X + h, Y + h), (X - px, Y - py, X + px, Y + py)]
    return out


def smd_check():
    """正面贴片件 / 让位腔间距 (自检 + 报告): 件离 LED 通道 ≥3, 离按键让位 / 螺丝禁布 (Φ4.8 及平板沉孔 Φ7.4) ≥1; 腔离 LED 通道壁 ≥0.8"""
    env = [smd_env(r) for r in SMD_F]; pk = smd_pocket()[:4]
    tun = [(X, Y) for _, X, Y, *_ in leds()]
    d = dict(件_LED通道=min(_rc_gap(e, t, TUNNEL_D) for e in env for t in tun),
             件_按键让位=min(_rr_gap(e, b) for e in env for b in btn_reliefs()),
             件_螺丝禁布=min(_rc_gap(e, m, max(FRONT_KO_D, CB_D)) for e in env for m in MH),
             件_板边=min(min(e[0], e[1], W - e[2], H - e[3]) for e in env) - EDGE_KO,
             件间=min(_rr_gap(a, b) for i, a in enumerate(env) for b in env[i + 1:]),
             腔壁_LED通道=min(_rc_gap(pk, t, TUNNEL_D) for t in tun),
             腔壁_按键让位=min(_rr_gap(pk, b) for b in btn_reliefs()),
             腔壁_沉孔=min(_rc_gap(pk, m, CB_D) for m in MH))
    d = {k: round(v, 3) for k, v in d.items()}
    assert d['件_LED通道'] >= 3.0 - 1e-9 and d['件_按键让位'] >= 1.0 - 1e-9 and d['件_螺丝禁布'] >= 1.0 - 1e-9 and d['件_板边'] >= 0, d
    assert d['腔壁_LED通道'] >= 0.8 - 1e-9 and d['腔壁_按键让位'] >= 0.8 - 1e-9 and d['件间'] >= 0.3, d
    return d


def j1_fp_to_board(x, y):
    """J1 封装坐标 (未翻面, KiCad +y 朝下的封装定义) → 板系正视。B.Cu 翻面 = 封装 x 取反; 封装 +y (插口) → 板系 −Y"""
    return J1_X - x, J1_ORG_Y - y


# 整机里的位置 (key_bracket_v1_2 按这个做)
Y_BOARD_FRONT = 100.6              # 板正面 y (用户 11-13)
Y_BOARD_BACK = Y_BOARD_FRONT - T   # 99.0
Y_BACK_MAX = Y_BOARD_BACK - BACK_MAX   # 93.0
Z0 = 3.0                           # 板下沿离底盘顶 (支架底条)


def to_global(X, Y):
    """板系 (X, Y) → 整机 (x, Z)"""
    return 20.0 - X, Z0 + Y


def btn_pads(X, Y):
    """按键 4 个焊盘矩形 (x0, y0, w, h) 板系"""
    pw, ph = BTN_PAD
    return [(X + sx * BTN_PAD_C[0] / 2 - pw / 2, Y + sy * BTN_PAD_C[1] / 2 - ph / 2, pw, ph) for sx in (1, -1) for sy in (1, -1)]


def leds():
    """[(名, X, Y, 宽X, 长Y, 高)] 板系"""
    return [('RGB 1615', *RGB, RGB_W, RGB_L, RGB_H)] + [(f'单色{i} 0603', X, Y, LED_W, LED_L, LED_H) for i, (X, Y) in enumerate(LED, 1)]


def j1_geom():
    """J1 板系几何 (正视): 本体 / 焊盘 / courtyard / 插头 / pin1"""
    X0, X1 = J1_X - J1_W / 2, J1_X + J1_W / 2
    by = sorted(j1_fp_to_board(0, y)[1] for y in J1_BODY_Y)
    cy = sorted(j1_fp_to_board(0, y)[1] for y in (-J1_CRT[1], J1_CRT[1]))
    pins = [(n, *j1_fp_to_board(-(J1_N - 1) / 2 * J1_PITCH + (n - 1) * J1_PITCH, J1_PIN_Y)) for n in range(1, J1_N + 1)]
    return dict(body=(X0, by[0], X1, by[1]), crt=(J1_X - J1_CRT[0], cy[0], J1_X + J1_CRT[0], cy[1]),
                plug=(J1_X - PLUG_W / 2, J1_MATE_Y - PLUG_L, J1_X + PLUG_W / 2, J1_MATE_Y), pins=pins,
                mp=[j1_fp_to_board(sx * 8.725, 1.35) for sx in (-1, 1)], pad_tip_Y=j1_fp_to_board(0, J1_PIN_TIP)[1])


def circ(c, d, n=24):
    return [[round(c[0] + d / 2 * math.cos(2 * math.pi * k / n), 3), round(c[1] + d / 2 * math.sin(2 * math.pi * k / n), 3)] for k in range(n)]


def rectp(x0, y0, x1, y1):
    return [[round(x0, 3), round(y0, 3)], [round(x1, 3), round(y0, 3)], [round(x1, 3), round(y1, 3)], [round(x0, 3), round(y1, 3)]]


def mech_constraints():
    """给画 PCB 的 agent: v1.2/pcb/key_board_v1_2/mech_constraints.json"""
    g = j1_geom(); E = EDGE_KO
    nut_r = BACK_KO_D / 2
    pz = (g['plug'][0] - 0.25, 0.0, g['plug'][2] + 0.25, J1_MATE_Y)
    return {
        "_generated_by": "v1.2/scripts/key_board_outline_v1_2.py (mechanical agent 维护; 改这里不要手改 JSON)",
        "_date": "2026-11-13",
        "coords": "板系 = 正视 (从机器外面看板正面 F.Cu), 原点板左下角, X 右, Y 上, mm. 整机 x = 20 - X, Z = 3 + Y. "
                  "KiCad 若板框左上角为原点且 Y 向下: x_kicad = X, y_kicad = H - Y (H = %g). 背面件也用这个正视坐标 (KiCad 里就是翻面后在顶视图看到的位置)" % H,
        "board": {"W": W, "H": H, "T": T, "edge_keepout": E,
                  "mount_holes": [{"XY": list(m), "d": MH_D, "note": "M3 NPTH/PTH Φ3.2; 背面 M3 法兰螺母 Φ7.6×3.7, 螺丝尾端到背面外 3.7"} for m in MH]},
        "connector": {
            "ref": "J1", "part": "JST SM12B-GHS-TB (GH 1.25mm 12P SMD 卧式/侧插)", "mate": "GHR-12V-S + SSHL-002T-P0.2 (插头从板下沿方向插入)",
            "footprint": "Connector_JST:JST_GH_SM12B-GHS-TB_1x12-1MP_P1.25mm_Horizontal (KiCad 库, 原点 = 信号焊盘行往插口方向 1.85 处)",
            "side": "back (B.Cu)",
            "origin_board_XY": [J1_X, round(J1_ORG_Y, 3)],
            "rotation": "B.Cu 上 rotation 0 (KiCad 默认左右翻面): 封装插口 (+y, 固定脚那侧) 朝板下沿 (板系 −Y / KiCad 屏幕向下), 信号焊盘行在上",
            "rotation_check": f"翻面后 pin1 在 板系 X {g['pins'][0][1]:.3f} (正视偏右, 整机 x {20 - g['pins'][0][1]:+.3f}), pin12 在 X {g['pins'][-1][1]:.3f}; 焊盘中心 Y {g['pins'][0][2]:.2f}",
            "pin1_board_XY": [round(g['pins'][0][1], 3), round(g['pins'][0][2], 3)],
            "pin12_board_XY": [round(g['pins'][-1][1], 3), round(g['pins'][-1][2], 3)],
            "mounting_pads_board_XY": [[round(x, 3), round(y, 3)] for x, y in g['mp']],
            "mating_face_board_Y": J1_MATE_Y, "body_board": {"X": [g['body'][0], g['body'][2]], "Y": [round(g['body'][1], 3), round(g['body'][3], 3)], "height": J1_H},
            "pin1_side_note": "pin1 在正视右侧 (整机 −x 侧). 机械上与 U24 线序见 cable_note",
        },
        "cable_note": "插头端 Y=1.0 (Z4), 线往下 3–4 mm 弯向机器内侧 (−Y), 贴底盘面从下罩内壁 r90.8 底部缺口 (x ±9, Z0–3) 出去, 到电机控制板 U24. "
                      "U24 与 J1 的插头锁扣在不扭的扁平走线下同在一面 ⇒ 不扭的线 = 同向线 = J1 pin k ↔ U24 pin 13−k; "
                      "要 pin1↔pin1 用 反向线 (两端锁扣在扁平线两面, 走线里拧半圈). 由原理图 agent 决定线序后选线.",
        "keepouts_back": [
            *[{"name": f"nut_M3_{i}", "type": "no_component", "max_height": 0.0, "circle": {"c": list(m), "d": BACK_KO_D}, "polygon": circ(m, BACK_KO_D),
               "note": "法兰螺母 Φ7.6 + 螺丝尾; 允许走线 (螺母压阻焊, 建议孔周 Φ8 不走线 / 铺地)"} for i, m in enumerate(MH)],
            {"name": "J1_courtyard", "type": "J1_only", "max_height": J1_H, "polygon": rectp(*g['crt'])},
            {"name": "plug_and_cable", "type": "no_component", "max_height": 0.0, "polygon": rectp(*pz),
             "note": "GHR 插头 (宽 17.25 保守, 露出插口 5.0, 厚 4.25 贴板背) + 插拔方向; 只能走线/铺铜, 不放件不放测试点"},
            {"name": "edge", "type": "no_component", "max_height": 0.0, "note": f"四边 {E:g} mm 禁布 (下沿 Y=0 坐支架底条)"},
        ],
        "back_component_zones": [],
        "back_note": "11-13 单面贴: 背面只放 J1 (手焊, JLC 不贴, CPL 不含 J1); R1–R6 / C1 已搬正面 (见 front_smd)",
        "back_mech_limit": "背面让位腔到 y93 (离板背 6.0); 除上面禁布外机械上允许 ≤5.5 高; 本版贴片区限 1.0 (0603)",
        "bracket_contact": {"back": "无 (支架只压正面; 底条 y98–100.6 托板下沿, 背面只在板外 1.0)", "bottom_edge": "下沿 Y=0 全宽坐支架底条 ⇒ 下沿 1 mm 不放件",
                            "front": "支架前面平板压整板正面, 只在下面 front_cavities 开让位"},
        "keepouts_front": [
            {"name": "edge", "type": "no_component", "max_height": 0.0, "note": f"四边 {E:g}"},
            *[{"name": f"MH_ring_{i}", "type": "no_component", "max_height": 0.0, "circle": {"c": list(m), "d": FRONT_KO_D}, "polygon": circ(m, FRONT_KO_D), "note": "平板压板环 (螺丝头埋平板沉孔, 板正面无头)"} for i, m in enumerate(MH)],
            {"name": "plate_pressed", "type": "no_component", "max_height": 0.0, "note": "正面除 front_cavities 外全被平板压住: 不放件 / 测试点 / 厚丝印凸起"},
            {"name": "SMD_pocket_only", "type": "smd_0603_only", "max_height": smd_pocket()[4] - SMD_CLR, "polygon": rectp(*smd_pocket()[:4]),
             "note": "正面 0603 R1–R6 / C1 只能放在这个腔里 (外包离腔边 ≥0.3, 高 ≤%.1f)" % (smd_pocket()[4] - SMD_CLR)},
        ],
        "front_smd": {r: dict(XY=list(SMD_F[r]), env_board_XY=[round(v, 3) for v in smd_env(r)], height=SMD_H[r[0]], rot="竖放, 脚 1 (LED 侧 / C1 +3V3) 朝下") for r in SMD_F},
        "front_smd_check": smd_check(),
        "front_cavities": [
            {"name": "SMD_pocket", "max_height": smd_pocket()[4], "polygon": rectp(*smd_pocket()[:4]),
             "note": "R1–R6 / C1 共用让位腔 (外包 +%g 每边, 深 %g); 与 LED 隔光通道之间壁 ≥%.2f, 不连通" % (SMD_CLR, smd_pocket()[4], smd_check()['腔壁_LED通道'])},
            *[{"name": f"SW{i + 1}_body", "max_height": 3.75, "polygon": rectp(X - BTN_BODY / 2 - 0.3, Y - BTN_BODY / 2 - 0.3, X + BTN_BODY / 2 + 0.3, Y + BTN_BODY / 2 + 0.3), "note": f"按键 ZX-QC66-7.5TP 本体 6×6×3.45, 杆 Φ{BTN_STEM_D:g} 穿平板 Φ4.0"} for i, (X, Y) in enumerate(BTN)],
            *[{"name": f"SW{i + 1}_pads", "max_height": 1.5, "polygon": rectp(X - BTN_PAD_OUT[0] / 2 - 0.3, Y - BTN_PAD_OUT[1] / 2 - 0.3, X + BTN_PAD_OUT[0] / 2 + 0.3, Y + BTN_PAD_OUT[1] / 2 + 0.3), "note": "脚/焊盘让位 (焊盘 1.5×1.1 @ (±4.0, ±2.25))"} for i, (X, Y) in enumerate(BTN)],
            *[{"name": nm, "max_height": 5.0, "circle": {"c": [X, Y], "d": 3.2}, "polygon": circ((X, Y), 3.2), "note": "LED 隔光通道 Φ3.2 (LED 本体须在圆内)"} for nm, X, Y, *_ in leds()],
        ],
    }


def main():
    import ezdxf
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    from matplotlib import font_manager as fm
    OUT.mkdir(parents=True, exist_ok=True)
    KO_E = [(0, 0, W, EDGE_KO), (0, H - EDGE_KO, W, EDGE_KO), (0, 0, EDGE_KO, H), (W - EDGE_KO, 0, EDGE_KO, H)]
    # 自检 (11-13 (三) 贴片件): 本体 / 焊盘外包 不出四边禁布, 离正面孔周禁布 ≥0.3, 互相 ≥0.3
    def rect_gap(a, b):
        return max(b[0] - (a[0] + a[2]), a[0] - (b[0] + b[2]), b[1] - (a[1] + a[3]), a[1] - (b[1] + b[3]))
    def circ_gap(r, c, d):   # 矩形 r 到圆 (c, d) 的距离
        dx = max(r[0] - c[0], 0, c[0] - r[0] - r[2]); dy = max(r[1] - c[1], 0, c[1] - r[1] - r[3]); return math.hypot(dx, dy) - d / 2
    btn_out = [(X - BTN_PAD_OUT[0] / 2, Y - BTN_PAD_OUT[1] / 2, *BTN_PAD_OUT) for X, Y in BTN]       # 焊盘外包 9.5×5.6
    btn_body = [(X - BTN_BODY / 2, Y - BTN_BODY / 2, BTN_BODY, BTN_BODY) for X, Y in BTN]
    led_r = [(X - w / 2, Y - l / 2, w, l) for _, X, Y, w, l, _ in leds()]
    comps = btn_out + btn_body + led_r
    assert all(c[0] >= EDGE_KO and c[1] >= EDGE_KO and c[0] + c[2] <= W - EDGE_KO and c[1] + c[3] <= H - EDGE_KO for c in comps), '元件出四边禁布'
    assert min(circ_gap(c, m, FRONT_KO_D) for c in comps for m in MH) >= 0.3 - 1e-9, "元件离正面孔周禁布 <0.3"
    assert rect_gap(btn_body[0], btn_body[1]) >= 0.5 - 1e-9 and rect_gap(btn_out[0], btn_out[1]) >= 0.3 - 1e-9, '两按键太近'
    assert all(rect_gap(b, l) >= 0.3 - 1e-9 for b in btn_out for l in led_r), '按键焊盘离 LED <0.3'
    assert all(rect_gap(a, b) >= 0.3 - 1e-9 for i, a in enumerate(led_r) for b in led_r[i + 1:])
    gap_rgb = min(rect_gap(b, led_r[0]) for b in btn_out)
    sc = smd_check(); pk = smd_pocket()

    doc = ezdxf.new('R2000'); msp = doc.modelspace()
    for n, c in (('Edge_Cuts', 7), ('KeepOut_F', 1), ('KeepOut_B', 6), ('Holes', 4), ('Comp', 3), ('Pads', 2), ('Text', 5)): doc.layers.add(n, color=c)
    msp.add_lwpolyline([(0, 0), (W, 0), (W, H), (0, H)], close=True, dxfattribs={'layer': 'Edge_Cuts'})
    def rect(x, y, w, h, layer):
        msp.add_lwpolyline([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], close=True, dxfattribs={'layer': layer})
    for x, y in MH:
        msp.add_circle((x, y), MH_D / 2, dxfattribs={'layer': 'Holes'})
        msp.add_circle((x, y), BACK_KO_D / 2, dxfattribs={'layer': 'KeepOut_B'})
        msp.add_circle((x, y), FRONT_KO_D / 2, dxfattribs={'layer': 'KeepOut_F'})
    for r in KO_E: rect(*r, 'KeepOut_F')
    for (X, Y), b, o in zip(BTN, btn_body, btn_out):
        rect(*b, 'Comp'); rect(*o, 'Pads'); msp.add_circle((X, Y), BTN_STEM_D / 2, dxfattribs={'layer': 'Comp'})
        for pd in btn_pads(X, Y): rect(*pd, 'Pads')
    for r in led_r: rect(*r, 'Comp')
    for ref in SMD_F:
        e = smd_env(ref); rect(e[0], e[1], e[2] - e[0], e[3] - e[1], 'Comp')
    doc.layers.add('Cavity_F', color=140); rect(pk[0], pk[1], pk[2] - pk[0], pk[3] - pk[1], 'Cavity_F')
    doc.layers.add('Comp_B', color=30)
    g = j1_geom()
    rect(g['body'][0], g['body'][1], g['body'][2] - g['body'][0], g['body'][3] - g['body'][1], 'Comp_B')
    rect(g['crt'][0], g['crt'][1], g['crt'][2] - g['crt'][0], g['crt'][3] - g['crt'][1], 'KeepOut_B')
    rect(g['plug'][0], g['plug'][1], g['plug'][2] - g['plug'][0], g['plug'][3] - g['plug'][1], 'KeepOut_B')
    for n, X, Y in g['pins']:
        rect(X - 0.3, Y - 0.85, 0.6, 1.7, 'Comp_B')
    msp.add_text('J1 pin1', dxfattribs={'layer': 'Text', 'height': 0.6}).set_placement((g['pins'][0][1] - 0.5, g['pins'][0][2] + 1.2))
    doc.saveas(OUT / 'key_board_outline_v1_2.dxf')
    import json
    jp = V12 / 'pcb' / 'key_board_v1_2' / 'mech_constraints.json'; jp.parent.mkdir(parents=True, exist_ok=True)
    jp.write_text(json.dumps(mech_constraints(), ensure_ascii=False, indent=1), encoding='utf-8')

    fm.fontManager.addfont('/mnt/c/Windows/Fonts/msyh.ttc')
    plt.rcParams['font.family'] = fm.FontProperties(fname='/mnt/c/Windows/Fonts/msyh.ttc').get_name()
    fig, ax = plt.subplots(figsize=(11, 7.4), dpi=110)
    ax.add_patch(Rectangle((0, 0), W, H, fc='#2E7D32', alpha=.25, ec='k', lw=2))
    for x, y, w, h in KO_E:
        ax.add_patch(Rectangle((x, y), w, h, fc='red', alpha=.15, ec='none'))
    for x, y in MH:
        ax.add_patch(Circle((x, y), FRONT_KO_D / 2, fc='red', alpha=.15, ec='r', ls='--'))
        ax.add_patch(Circle((x, y), BACK_KO_D / 2, fc='none', ec='m', ls=':', lw=1.5))
        ax.add_patch(Circle((x, y), MH_D / 2, fc='white', ec='k'))
        ax.text(x, y - 4.3, f'M3 Φ{MH_D:g}\n({x:g}, {y:g})', ha='center', va='top', fontsize=7)
    for i, ((X, Y), b, o) in enumerate(zip(BTN, btn_body, btn_out), 1):
        ax.add_patch(Rectangle(o[:2], o[2], o[3], fc='none', ec='#E65100', ls='--', lw=1))
        for pd in btn_pads(X, Y): ax.add_patch(Rectangle(pd[:2], pd[2], pd[3], fc='#FFB74D', ec='#E65100', lw=.6))
        ax.add_patch(Rectangle(b[:2], b[2], b[3], fc='#ddd', ec='k', alpha=.85)); ax.add_patch(Circle((X, Y), BTN_STEM_D / 2, fc='#555'))
        ax.text(X, Y + (5.2 if i == 1 else -5.2), f'按键{i} 6×6×7.5 贴片 ({X:g}, {Y:g})', ha='center', va='bottom' if i == 1 else 'top', fontsize=7)
    for (nm, X, Y, w, l, h), r in zip(leds(), led_r):
        ax.add_patch(Rectangle(r[:2], r[2], r[3], fc='#E040FB' if 'RGB' in nm else '#FFD966', ec='k'))
    ax.text(RGB[0], RGB[1] + 1.4, f'三色 1615\n({RGB[0]:g}, {RGB[1]:g})', ha='center', va='bottom', fontsize=7)
    ax.add_patch(Rectangle(pk[:2], pk[2] - pk[0], pk[3] - pk[1], fc='none', ec='#6A1B9A', ls='--', lw=1))
    for _, X, Y, *_ in leds():
        ax.add_patch(Circle((X, Y), TUNNEL_D / 2, fc='none', ec='#C62828', ls=':', lw=.8))
    for ref in SMD_F:
        e = smd_env(ref); ax.add_patch(Rectangle(e[:2], e[2] - e[0], e[3] - e[1], fc='#90CAF9' if ref[0] == 'R' else '#A5D6A7', ec='k', lw=.6))
        ax.text(SMD_F[ref][0], e[3] + 0.15, ref, ha='center', va='bottom', fontsize=6)
    ax.text(pk[2] + 0.3, (pk[1] + pk[3]) / 2, f'R/C 共用让位腔\n(紫虚框, 深 {pk[4]:g})\n离 LED 通道:\n件 {sc["件_LED通道"]:g} / 壁 {sc["腔壁_LED通道"]:g}', ha='left', va='center', fontsize=6)
    ax.text(LED[1][0], YC - 2.0, '单色 0603 ×3\n(' + ' / '.join(f'{X:g}' for X, _ in LED) + f', {YC:g})', ha='center', va='top', fontsize=7)
    ax.add_patch(Rectangle(g['plug'][:2], g['plug'][2] - g['plug'][0], g['plug'][3] - g['plug'][1], fc='none', ec='#1565C0', ls=':', lw=1.2))
    ax.add_patch(Rectangle(g['body'][:2], g['body'][2] - g['body'][0], g['body'][3] - g['body'][1], fc='none', ec='#1565C0', ls='--', lw=1.2))
    ax.text(J1_X, g['plug'][1] + 0.3, f'背面 J1 GH 12P (虚框, 插口朝下) pin1 X{g["pins"][0][1]:g}; 点框 = 插头', ha='center', va='bottom', fontsize=6, color='#1565C0')
    ax.annotate('', (0, -2), (W, -2), arrowprops=dict(arrowstyle='<->')); ax.text(W / 2, -3.4, f'{W:g}', ha='center')
    ax.annotate('', (-2, 0), (-2, H), arrowprops=dict(arrowstyle='<->')); ax.text(-3.4, H / 2, f'{H:g}', va='center', rotation=90)
    ax.set_title(f'按键板板框 {W:g}×{H:g}×{T:g} (正视 = 从机器外面看; 红 = 正面禁布, 紫虚圈 = 背面 Φ{BACK_KO_D:g} 螺母禁布, 橙虚框 = 按键焊盘外包)', fontsize=10)
    note = (f'固定: 支架前面平板压整板正面; 2×M3×8 超薄头埋平板前面沉孔往里穿 平板 + 板 {T:g}, 背面 M3 法兰螺母 Φ7.6×3.7 (孔周正 / 背面 Φ{FRONT_KO_D:g} 禁布)\n'
            f'正面 6 件 (全贴片): 按键 6×6×7.5 (本体高 {BTN_BODY_H:g}, 杆 Φ{BTN_STEM_D:g}, 行程 {BTN_TRAVEL:g}, 焊盘外包 {BTN_PAD_OUT[0]:g}×{BTN_PAD_OUT[1]:g} 脚沿 Y, 11-13 (五) 转 90°);\n'
            f'  三色 1615 {RGB_W:g}×{RGB_L:g}×{RGB_H:g}; 单色 0603 {LED_W:g}×{LED_L:g}×{LED_H:g}。按键焊盘外包离三色 LED {gap_rgb:.2f} (平板背面按键让位与三色隔光孔之间有实心壁)\n'
            f'平板背面: 按键本体 + 脚让位腔, 每颗 LED 一个隔光孔, 其余全贴板, 所以正面别放其他件 (含测试点 / 丝印凸起)\n'
            f'正面另有 0603 R1–R6 / C1 (单面贴, JLC 只贴顶面) @ Y{SMD_Y:g}, X {min(v[0] for v in SMD_F.values()):g}–{max(v[0] for v in SMD_F.values()):g}; 平板背面共用让位腔 {pk[2] - pk[0]:.2f}×{pk[3] - pk[1]:.2f} 深 {pk[4]:g}\n'
            f'背面: 只有 J1 = JST GH 1.25 12P SM12B-GHS-TB 卧贴 (手焊, JLC 不贴), 插口朝板下沿 — 见 pcb/key_board_v1_2/mech_constraints.json\n'
            f'整机位置: 板中心 x=0 (+Y 侧), 正面 y{Y_BOARD_FRONT:g} / 背面 y{Y_BOARD_BACK:g}, 下沿 Z{Z0:g}–上沿 Z{Z0 + H:g}; 整机 x = 20 − X, Z = {Z0:g} + Y')
    ax.text(-3, -5.6, note, fontsize=7.3, va='top')
    ax.set_xlim(-6, W + 4); ax.set_ylim(-18, H + 4); ax.set_aspect('equal'); ax.axis('off')
    plt.tight_layout(); plt.savefig(OUT / 'key_board_outline_v1_2_layout.png')
    print(f'板 {W}x{H}x{T}; 孔 {MH}; 按键 {BTN}; RGB {RGB}; LED {LED}; 按键焊盘离三色 {gap_rgb:.2f}')
    print('正面贴片', SMD_F, '让位腔', [round(v, 3) for v in pk], '间距', sc)


if __name__ == '__main__':
    main()
