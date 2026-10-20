"""
V1.0 新打印件 A3 工程图 (2026-10-20), 一件一张, 写到各零件目录 <code>_drawing.pdf (+ _preview.png)。
几何直接取 STL (drawing_v1_0.draw), 孔位/规格取各 build 脚本的参数 —— 先跑各 build_stl.py 再跑本脚本。
"""
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from drawing_v1_0 import draw  # noqa: E402
import params_v1_0 as P  # noqa: E402
from rim_ring_v1_0.build_stl import (BASE_HOLES, EXTRA_HOLES, HEAD_CB_XY, INSERT_D, INSERT_DEEP,  # noqa: E402
                                     RING_HOLES)
from screen_foot_v1_0.build_stl import AXIS_BAR_D, RING_HOLES as FOOT_RING, WELL_D  # noqa: E402
from top_cap_v1_0.build_stl import SEN_CB_D, SEN_CB_T, SEN_HOLES, SEN_SLOT_L, SEN_SLOT_W, SEN_TH  # noqa: E402
from wifi_plate_v1_0.build_stl import HOLES as PLATE_HOLES, NOTCH_HX, NOTCH_Y0, SHELL_HOLES  # noqa: E402

DATE = "2026-10-20"


def ring(r, n, a0):
    return [(r * math.cos(math.radians(a0 + 360 / n * k)), r * math.sin(math.radians(a0 + 360 / n * k)))
            for k in range(n)]


def xy(pts):
    return "  ".join(f"({x:.2f},{y:.2f})" for x, y in pts)


def xy_lines(pts, per=2):
    return "\n".join(xy(pts[i:i + per]) for i in range(0, len(pts), per))


POST_R = math.hypot(87.5, 62.5)
SPECS = []

# ---------------- hub_disc_v1_0 ----------------
SPECS.append(dict(
    stl=HERE / "hub_disc_v1_0/hub_disc_v1_0.stl", code="hub_disc_v1_0", short="转子下盘 Φ175", qty="1",
    title="转子下盘 (Φ175, 套 rim_ring_v1_0 外唇内; 底面压铜螺母)",
    orient="底面 (Z0) 贴床, 凸台朝上", src="v1.0/models/hub_disc_v1_0/hub_disc_v1_0.stl",
    origin_note="原点 = 盘心, 底面 Z0。",
    holes=[
        dict(tag="A", pts=[(6, 0), (-6, 0), (0, 7.5), (0, -7.5)], spec="Φ3.2 通 + 顶面 Φ7×4 沉头窝",
             where="菱形 对角 12 × 15 (电机法兰)", lab_off=(0, 4.5)),
        dict(tag="B", pts=[(sx * 15, sy * 15) for sx in (1, -1) for sy in (1, -1)],
             spec="Φ3.2 通 + 底面 Φ4.2×4 铜螺母孔", where="30×30 方 (±15, ±15)"),
        dict(tag="C", pts=ring(30, 8, 22.5), spec="Φ3.2 通 + 底面 Φ4.2×4.5 铜螺母孔",
             where="R30 @ 22.5°+45°k"),
        dict(tag="D", pts=ring(P.RING_OUTER_PCD_R, 8, 22.5), spec="Φ3.2 通 + 底面 Φ4.2×4.5 铜螺母孔",
             where=f"R{P.RING_OUTER_PCD_R:g} @ 22.5°+45°k\n(屏幕底座 4 颗 M3 拧这里, 67.5/112.5/247.5/292.5°)"),
        dict(tag="E", pts=[(0, 0)], spec="底面 Φ6.2×2.2 盲窝 (不通)", where="盘心", lab_off=(-3, -3)),
    ],
    notes=["V1.0 改: 底盘 Φ165→175, 外凸台 ID155/OD175, D 组 R77.5→82.5",
           "铜螺母: M3 热熔/压入式, 外径 4.2 孔, 全部从底面压入",
           "高 9: 底盘 3 + 下凸台 Φ70×2.5 + 上凸台 Φ50×3.5; 外凸台环 2.5"],
    views=("front", "top"), dims=[]))

# ---------------- rim_ring_v1_0 ----------------
SPECS.append(dict(
    stl=HERE / "rim_ring_v1_0/rim_ring_v1_0.stl", code="rim_ring_v1_0", short="转子承载盘 Φ180", qty="1",
    title="转子承载盘 (Φ180, 外唇 175/180; DR1M90 底板 4 孔)",
    orient="托盘面 (Z0) 贴床, 唇/凸台朝上", src="v1.0/models/rim_ring_v1_0/rim_ring_v1_0.stl",
    origin_note="原点 = 盘心, 托盘面 Z0 (零件系; 装机绕 X 翻转: 世界 Y = −图示 Y)。",
    holes=[
        dict(tag="A", pts=RING_HOLES[:8], spec="Φ3.2 通", where="R30 @ 22.5°+45°k"),
        dict(tag="B", pts=RING_HOLES[8:], spec="Φ3.2 通",
             where=f"R{P.RING_OUTER_PCD_R:g} @ 22.5°+45°k (屏幕底座借 4 个)"),
        dict(tag="C", pts=EXTRA_HOLES, spec="Φ4 通", where="(R72 @ −10°)  (R56 @ −42.5°)"),
        dict(tag="D", pts=HEAD_CB_XY, spec="托盘面 Φ7.5×2 螺丝头沉孔", where="R30 @ 202.5° / 247.5°",
             lab_off=(-3, -3)),
        dict(tag="E", pts=BASE_HOLES, spec=f"Φ3.2 通 + 唇侧 Φ{INSERT_D:g}×{INSERT_DEEP:g} 铜螺母孔",
             where="DR1M90 底板 4 孔 (图示零件系):\n" + xy_lines(BASE_HOLES)),
    ],
    notes=["V1.0 改: Φ170→180, 外圈 8 孔 R77.5→82.5, 去 pi2hub/wifi 孔, 加 E 组",
           "E 组: 唇侧压铜螺母, 上面拧 M3×5 尼龙垫柱撑 DR1M90",
           "走线槽 −45..−40°, R40..61, 唇侧深 2 (沿用 V0.4)",
           "托盘厚 5, 外唇高 5.5 (Φ175/180), 内凸台环 Φ70/80×2.5"],
    views=("front", "top"), dims=[]))

# ---------------- screen_foot_v1_0 ----------------
SPECS.append(dict(
    stl=HERE / "screen_foot_v1_0/screen_foot_v1_0_posY_asm.stl", code="screen_foot_v1_0", short="屏幕底座 (portal_tee 式)", qty="2 (+Y 件 1 + −Y 镜像件 1)",
    title="屏幕底座 (portal_tee 结构, 托两块灯板下角, M3 锁进 hub_disc 铜螺母)",
    subtitle="图示 = +Y 件装机姿态 (世界坐标); −Y 件 = 绕 XZ 面镜像, 另有 STL",
    orient="内侧面 (Y71) 贴床 (STL 已是打印姿态), 零支撑",
    src="v1.0/models/screen_foot_v1_0/screen_foot_v1_0_posY.stl / _negY.stl",
    origin_note="原点 = 转轴 (世界), Z = 世界高度 (底面 Z42.2 = 承载面)。",
    holes=[
        dict(tag="A", pts=FOOT_RING, spec=f"Φ3.4 通 (底条) + 上方 Φ{WELL_D:g} 工艺井贯穿",
             where=f"借 rim_ring 外圈环孔 R{P.RING_OUTER_PCD_R:g} @67.5°/112.5°\nM3×14 拧进 hub_disc 底面铜螺母",
             lab_off=(0, -4)),
        dict(tag="B", pts=[(P.COL_X, P.COL_Y)], spec=f"底条 Φ{AXIS_BAR_D:g} + 顶托 Φ3.4 + 中间 Φ{WELL_D:g} 让位",
             where=f"屏幕螺母列轴线 ({P.COL_X:.2f}, {P.COL_Y:g})\n下螺丝从底下往上穿", lab_off=(4, -4)),
    ],
    notes=[f"顶托顶面 = 灯板下沿 Z{P.LED_EDGE_BOT_Z:.2f}, 托住两块灯板下角",
           "外形裁到 R ≤ 87, 给以后的圆罩子让位",
           "底条 5 厚 / 梯形壁 5 厚 / 腿 5 宽 / 顶托 5 厚",
           "⚠ 底条轴线孔现为 Φ3 (用户定), 下螺丝过不去 —— 装法待定"],
    dims=[]))

# ---------------- top_cap_v1_0 ----------------
SPECS.append(dict(
    stl=HERE / "top_cap_v1_0/top_cap_v1_0_asm.stl", code="top_cap_v1_0", short="屏幕顶盖 + 光电座", qty="1",
    title="屏幕顶盖 (压两块灯板上沿, 中心 M6 → Φ8 螺柱进 688; 光电模块座)",
    subtitle="图示 = 装机姿态 (世界坐标); 打印时顶面朝下",
    orient="顶面朝下 (头窝朝上), STL 已是打印姿态", src="v1.0/models/top_cap_v1_0/top_cap_v1_0.stl",
    origin_note="原点 = 转轴 (世界), Z = 世界高度 (底面 = 灯板上沿)。",
    holes=[
        dict(tag="A", pts=[(P.COL_X, P.COL_Y), (P.COL_X, -P.COL_Y)], spec="Φ3.4 通 (屏顶 M3, 往下进上组铜螺母)",
             where=f"({P.COL_X:.2f}, ±{P.COL_Y:g})", lab_off=(6, 0)),
        dict(tag="B", pts=[(0, 0)], spec="Φ6.4 通 + 底面 Φ13×2.7 M6 头窝", where="转轴 (0,0)", lab_off=(-6, 3)),
        dict(tag="C", pts=SEN_HOLES, spec=f"Φ3.2 通 + 底面 Φ{SEN_CB_D:g}×{SEN_CB_T:g} 头窝 (光电模块)",
             where=xy(SEN_HOLES), lab_off=(7, 0)),
    ],
    notes=[f"排针尾让位槽 {SEN_SLOT_L:g}×{SEN_SLOT_W:g} 贯穿, 绕两孔中点转 {SEN_TH:.2f}°",
           "光电模块平贴顶面, 光轴过转轴 (槽中心 r41.87)",
           "⚠ 先从底面装光电螺丝 / M6, 再把顶盖压上屏幕",
           "厚 7"],
    dims=[]))

# ---------------- wifi_plate_v1_0 ----------------
SPECS.append(dict(
    stl=HERE / "wifi_plate_v1_0/wifi_plate_v1_0.stl", code="wifi_plate_v1_0", short="WiFi 托板 (H 形)", qty="1",
    title="WiFi 托板 (H 形, 尼龙螺柱架在 DR1M90 上; 托 wifi_shell)",
    orient="平放", src="v1.0/models/wifi_plate_v1_0/wifi_plate_v1_0.stl",
    origin_note="原点 = 转轴 (世界 XY), 板底 Z0。",
    holes=[
        dict(tag="A", pts=PLATE_HOLES, spec="Φ3.4 通 — M3×25 尼龙螺柱 (公母) 位",
             where="DR1M90 顶面贴片铜柱正上方:\n" + xy_lines(PLATE_HOLES)),
        dict(tag="B", pts=SHELL_HOLES, spec="Φ3.4 通 — wifi_shell 沿孔, M3×10 从板底往上",
             where=xy_lines(SHELL_HOLES)),
    ],
    notes=[f"H 口 {2 * NOTCH_HX:g} 宽, 从 |Y|={NOTCH_Y0:g} 开到板端; +Y 口穿扁平 USB 延长线",
           "板 70×128×3",
           "装法: 托板+罩+模块先用 4 颗 M3 锁成一组, 再整组拧上尼龙柱"],
    dims=[]))

# ---------------- frame_A / frame_B ----------------
for code, qty, desc, m6, vane, orient in (
        ("frame_A_v1_0", "1", "顶轴承架 A (下层, 688 #1)", [(POST_R, 0), (0, POST_R)], None,
         "STL 即打印姿态 (毂底贴床)"),
        ("frame_B_v1_0", "1", "顶轴承架 B (上层, 688 #2, 臂筋挂挡光滑片)", [(POST_R, 0), (0, -POST_R)],
         [(38.7, 12.0), (48.7, 12.0)], "STL 即打印姿态 (装机翻转 180°, 柱垫朝上打印)")):
    holes = [dict(tag="A", pts=m6, spec="Φ6.5 通 — M6 锁柱顶", where=f"柱位 R{POST_R:.2f} (网格 87.5,62.5 族)",
                  lab_off=(0, 12)),
             dict(tag="B", pts=ring(14, 4, 45), spec="Φ3.2 通 — M3×20+螺母 ×4 夹 A/B 两毂",
                  where="R14 @ 45°+90°k", lab_off=(3.5, 3.5)),
             dict(tag="C", pts=[(0, 0)], spec="688 轴承座 Φ15.8×5 + Φ13 通",
                  where="毂心", lab_off=(-9, 0))]
    if vane:
        holes.append(dict(tag="D", view="left", pts=vane, spec="Φ3.2 横孔 (沿 X 穿筋) — 挡光滑片",
                          where="筋上 r38.7 / r48.7, M3×20+螺母 ×2\n锁 vane_slider_v4 (左视图)", lab_off=(0, 6)))
    SPECS.append(dict(
        stl=HERE / f"top_bearing_v1_0/{code}.stl", code=code, qty=qty, short=desc.split(" (")[0], title=desc + ", PLA",
        orient=orient, src=f"v1.0/models/top_bearing_v1_0/{code}.stl",
        origin_note="原点 = 毂心 (转轴), 图示 = 打印姿态。",
        holes=holes,
        notes=[f"V1.0 改: 柱位 R95.20 → R{POST_R:.2f} (立柱沿网格外挪一格), 臂/筋随之加长",
               "柱: Φ8 × 360, 网格 M6 螺纹孔 (87.5,62.5) 族, 柱角 35.54°+90°k",
               "BOM: 688 ×2, M6×16 ×2 (A 垫) + M6×30 ×2 (B 柱垫), M3×20+螺母 ×4"],
        dims=[]))


if __name__ == "__main__":
    only = set(sys.argv[1:])
    for sp in SPECS:
        if only and sp["code"] not in only:
            continue
        sp["out"] = sp["stl"].parent / f"{sp['code']}_drawing.pdf"
        out, png, sl = draw(sp)
        print(f"wrote {out}  ({sl})")
