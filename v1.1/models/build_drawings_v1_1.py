"""
V1.1 新打印件 A3 工程图 (2026-10-21), 画法同 v1.0/models/build_drawings_v1_0.py (共用 drawing_v1_0.draw)。
先跑 glass_seat_v1_1/build_stl.py 再跑本脚本。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "v1.0" / "models"))
from drawing_v1_0 import draw  # noqa: E402
import glass_seat_v1_1.build_stl as GS  # noqa: E402

DATE = "2026-10-21"
SPECS = []

# ---------------- glass_seat_v1_1 ----------------
_ears = [(sx * GS.EAR_C[0], sy * GS.EAR_C[1]) for sx in (1, -1) for sy in (1, -1)]
SPECS.append(dict(
    stl=HERE / "glass_seat_v1_1/glass_seat_v1_1.stl", code="glass_seat_v1_1", short="罩子定位环 + PCB 托架", qty="1",
    title=f"透明罩定位环 (亚克力/PC 管 OD{GS.GLASS_OD:g}×{GS.GLASS_T:g}) + 底板 PCB {GS.PCB_W:g}×{GS.PCB_L:g} 托架",
    orient="底面 (Z0) 贴床, 原样平放", src="v1.1/models/glass_seat_v1_1/glass_seat_v1_1.stl",
    origin_note="原点 = 底板中心, 底面 Z0 = 圆底板顶面 (零件系 = 装配世界系, +Y = 电机线缺口方向)。",
    holes=[
        dict(tag="A", pts=_ears, spec=f"Φ{GS.M6_D:g} 通 + 顶面 Φ{GS.M6_CB_D:g}×{GS.M6_CB_H:g} 沉头",
             where="(±62.5, ±62.5) = 底板 M6 网格孔\nM6×12 内六角 ×4 锁到底板"),
        dict(tag="B", pts=GS.PCB_HOLES, spec=f"导轨顶面 Φ{GS.INSERT_D:g}×{GS.INSERT_H:g} M3 铜螺母孔",
             where=f"(±{GS.PCB_HOLES[0][0]:g}, {GS.PCB_HOLES[0][1]:g} / {GS.PCB_HOLES[1][1]:g})\n"
                   f"PCB 孔距 {2 * GS.PCB_HOLES[0][0]:g}×{GS.PCB_HOLES[1][1] - GS.PCB_HOLES[0][1]:g}, M3×6 ×4",
             lab_off=(0, -4)),
    ],
    notes=[f"底座圈 R{GS.LIP_IR:g}..{GS.GLASS_OD / 2:g} × {GS.SEAT_H:g} 厚: 罩子坐在上面 (罩底 Z{GS.GLASS_Z0:g}); "
           f"+Y 过线槽宽 {GS.SLOT_W:g}",
           f"定位唇 Φ{2 * GS.LIP_IR:g}/Φ{2 * GS.LIP_OR:g} 到 Z{GS.LIP_TOP:g}, 顶部外倒角 {GS.LIP_CH:g}; "
           f"插进罩子内孔 Φ{2 * GS.GLASS_IR:g}",
           f"定位唇单边间隙 {GS.GLASS_IR - GS.LIP_OR:.1f}; {GS.LIP_GAP_A[0]:g}..{GS.LIP_GAP_A[1]:g}° 断开让 PCB",
           f"PCB 导轨 X ±{GS.RAIL_X[0]:g}..{GS.RAIL_X[1]:g}, 顶面 Z{GS.PCB_Z0:g} (= 定子底盘方块顶); "
           f"PCB 放 Y {GS.PCB_Y0:.2f}..{GS.PCB_Y1:.2f}",
           f"元件限高 {GS.PCB_COMP_H:.1f} (r<85, 上方定子法兰); 外角离罩子内壁 1.74, 罩子 ID 公差 ≤ 单边 1",
           "铜螺母: M3 热熔, Φ4.2 孔 ×4 (B 组)"],
    views=("front", "top"), dims=[], date=DATE, proj="V1.1"))


if __name__ == "__main__":
    only = set(sys.argv[1:])
    for sp in SPECS:
        if only and sp["code"] not in only:
            continue
        sp["out"] = sp["stl"].parent / f"{sp['code']}_drawing.pdf"
        out, png, sl = draw(sp)
        print(f"wrote {out}  ({sl})")
