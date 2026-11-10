"""
V0.4 带屏动平衡 新件 A3 图纸 (2026-11-09): rotor_shroud_v4 两半 + balance_block_v4。
借 V1.0 通用出图 (v1.0/models/drawing_v1_0.py: STL → 消隐三视图 + 孔表 + 轴测)。
先跑 rotor_shroud_v4/build_shroud.py 和 balance_block_v4/build_stl.py。
用法: python build_drawings_v4_bal.py [code ...]
"""
import math, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / "v1.0/models"))
from drawing_v1_0 import draw  # noqa: E402
import balance_params_v4 as BP  # noqa: E402
sys.path.insert(0, str(HERE / "balance_block_v4"))
import build_stl as BB  # noqa: E402

DATE = "2026-11-09"
def xy(pts): return "  ".join(f"({x:.2f},{y:.2f})" for x, y in pts)
def xy_lines(pts, per=2): return "\n".join(xy(pts[i:i + per]) for i in range(0, len(pts), per))
def pol(r, a): return BP.pol(r, a)

COLS = {"A": (22.5, 157.5), "B": (202.5, 337.5)}
CWM = {"A": [(-50, 14), (-72, 14)], "B": [(-50, -14), (-72, -14)]}
SPECS = []
for h, sgn in (("A", 1), ("B", -1)):
    mpts = [(x, y) for x, y in BP.MOUNT_PTS if sgn * y > 0]
    mang = [a for (x, y), a in zip(BP.MOUNT_PTS, BP.MOUNT_ANGS) if sgn * y > 0]
    SPECS.append(dict(
        stl=HERE / f"rotor_shroud_v4/shroud_half_{h}_v4.stl", code=f"shroud_half_{h}_v4", qty="1", date=DATE, proj="V0.4",
        short=f"转子罩 {h} 半 ({'+Y' if sgn > 0 else '-Y'})",
        title=f"转子电路罩 {h} 半 v4 (= v3_1 + 罩顶配重块安装孔圈), PLA",
        orient="绕 X 翻 180° 顶板贴床, 零支撑 (STL 为装配零件系姿态, 切片时翻面)",
        src=f"v0.4/models/rotor_shroud_v4/shroud_half_{h}_v4.stl",
        origin_note="原点 = 转轴, Z0 = 承载面 (装配 42.2), 零件系 (装配角 = 零件角 −45°)。",
        holes=[
            dict(tag="A", pts=mpts, spec="Φ3.4 通, Φ9 凸台 Z42..50, Φ4.2×4 铜螺母 — 块 M3×10",
                 where=f"r{BP.LOCK_R:g} @ " + "/".join(f"{a:g}°" for a in mang)),
            dict(tag="B", pts=[pol(77.5, a) for a in COLS[h]], spec="Φ9 沉井 + 井底 3 厚台肩 Φ3.4 — M3×12 锁 hub",
                 where="r77.5 @ " + "/".join(f"{a:g}°" for a in COLS[h])),
            dict(tag="C", pts=CWM[h], spec="Φ3.4 通, Φ9 凸台 Z43..50, Φ4.2×4 铜螺母 — 臂 M3×16",
                 where=xy(CWM[h])),
        ],
        notes=["v4 改: 罩顶加配重块安装孔 (A 组), 其余同 rotor_shroud_v3_1",
               "铜花螺母 M3×4×4.5 全部从罩内压入凸台端面, 扣罩前装好",
               f"块可放中心 (零件系): {', '.join(str(c) for c in BP.BLK_CENTERS)}°",
               "两半各 ~87 g PLA, 筒 Φ170/164 高 50, 顶板 2"],
        dims=[]))

SPECS.append(dict(
    stl=HERE / "balance_block_v4/balance_block_v4_asm.stl", code="balance_block_v4", qty="1~2", date=DATE, proj="V0.4",
    short="移动配重块",
    title="带屏动平衡移动配重块 (贴罩顶, 锁相邻两个安装孔), PLA",
    orient="顶面贴床 (打印 STL 已翻好), 零支撑", src="v0.4/models/balance_block_v4/balance_block_v4.stl",
    origin_note="原点 = 转轴, 块中心在 +X, 底面 Z0 = 罩顶面 (装配 92.2)。图为装配姿态。",
    holes=[
        dict(tag="A", pts=BB.LOCK, spec="Φ3.2 通 + 顶面 Φ7.5×2 头沉 — M3×10 锁罩顶铜螺母", where=xy_lines(BB.LOCK)),
        dict(tag="B", pts=BB.M6, spec="Φ6.5 通 + 底面 Φ13×2.8 头窝 — M6 大扁头, 螺杆朝上叠螺母", where="r78, ±5° / ±15°"),
        dict(tag="C", pts=BB.TRIM, spec="Φ3.2 通 + 底面 Φ7×1.5 头窝 — M3 微调, 螺纹朝上锁螺母", where="r58, 每 8° (-16..+16)"),
    ],
    notes=["扇形 r54..85 ±21° 厚 4.8, 外缘 = 罩 OD170", "估重 6.4 g, 块自身 ~435 g·mm",
           "M6 螺母外角 r83.8 < 85; 窝壁最薄 0.5 (同 V1.0 块)", "必须防松: 尼龙锁紧螺母或螺纹胶"],
    dims=[]))

# ---- counterweight_fan_v4 (2026-11-09 用户改主意: 罩子用旧 v3_1, 只改配重块) ----
sys.path.insert(0, str(HERE / "counterweight_fan_v4"))
import importlib.util as _u
_sp = _u.spec_from_file_location("_fan", HERE / "counterweight_fan_v4/build_stl.py"); CF = _u.module_from_spec(_sp); _sp.loader.exec_module(CF)
SPECS.append(dict(
    stl=HERE / "counterweight_fan_v4/counterweight_fan_v4_asm.stl", code="counterweight_fan_v4", qty="1", date=DATE, proj="V0.4",
    short="扇形配重块 (取代配重臂)",
    title="带屏动平衡扇形配重块 (锁旧罩 rotor_shroud_v3_1 顶 4 个 M3, 取代 counterweight_arm), PLA",
    orient="顶面贴床 (打印 STL 已翻好), 零支撑", src="v0.4/models/counterweight_fan_v4/counterweight_fan_v4.stl",
    origin_note="原点 = 转轴, 罩零件系 (装配角 = 零件角 −45°), 底面 Z0 = 罩顶面 (装配 92.2)。图为装配姿态。",
    holes=[
        dict(tag="A", pts=CF.LOCK, spec="Φ3.4 通 — M3×16 ×4 进罩顶铜花螺母 (同原配重臂)", where=xy_lines(CF.LOCK)),
        dict(tag="B", pts=CF.M6, spec="Φ6.5 通 + 底面 Φ13×2.8 头窝 — M6 大扁头, 杆朝上叠螺母",
             where="r78 @ 106..159 / 180 / 201..254 (每 10.6°) + (−64,0)"),
        dict(tag="C", pts=CF.TRIM, spec="Φ3.2 通 + 底面 Φ7×1.5 头窝 — M3 微调, 螺纹朝上锁螺母",
             where="r64 @ 104..168 / 192..256 每 8°"),
    ],
    notes=["扇形 r58..85 零件角 100..260° ∪ 原臂矩形, 厚 6, 外缘 = 罩 OD170",
           "估重 34 g PLA, 自带 ~1730 g·mm @ 零件 180° (= 偏心屏修正方向)",
           "底面全贴罩顶: 五金全部叠在板上, 杆不许下伸; 窝壁最薄 0.5 (同原臂)",
           "必须防松: 尼龙锁紧螺母或螺纹胶"],
    dims=[]))

if __name__ == "__main__":
    only = set(sys.argv[1:])
    for sp in SPECS:
        if only and sp["code"] not in only: continue
        sp["out"] = sp["stl"].parent / f"{sp['code']}_drawing.pdf"
        out, png, sl = draw(sp)
        print(f"wrote {out}  ({sl})")
