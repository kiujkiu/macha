"""V1.2 定子光电发射板压片 B 版 ir_clamp_b_v1_2 — 11-24 用户「sup_b做一个3mm厚度的，给定子是不是可以直接用」
取屏幕支撑件 B (screen_sup_b_v1_2b) 贴承载盘那一面起 3mm 厚 (板槽 / 电阻让位槽 / 4 定位销 / 长圆穿线槽原样带过来),
翻面 (板槽朝上贴定子盘底) 转到 IR_ANG, 用定子盘外圈 2 颗 B 螺丝 (r77.5 @IR_ANG±22.5, 与转子 N 孔同半径同角距) 锁;
螺丝处底面 Φ IR_CL_NUT_CB_D 沉孔深 CB_DEPTH 1.5 (11-24 装 270° 位, 247.5° 螺母下方是电机线夹)。
    cd v1.2/scripts && ../../.venv/bin/python ir_clamp_b_v1_2.py [--check]
"""
import io, contextlib, math, sys, json
with contextlib.redirect_stdout(io.StringIO()):
    import build_v1_2 as B
    import rotor_b_v1_2 as RB
from OCP.gp import gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir, gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
T = 3.0
Z0 = RB.SP_Z0
assert abs(B.LID_R - RB.OPT_R) < 1e-6 and abs(B.IR_R - RB.OPT_R) < 1e-6 and RB.SP_HOLE_A == (22.5, -22.5), (B.LID_R, B.IR_R, RB.OPT_R)   # 定子 B 孔 / LED 与转子 N 孔 / 通光孔同 r77.5, 角距 ±22.5
loc = B.op(B.BRepAlgoAPI_Common, RB.screen_sup_b_loc, B.gbox(-200, -200, Z0 - 1, 200, 200, Z0 + T))   # 局部 (放 0°): 板槽在 Z0 面, LED 在 (77.5, 0)
loc = B.fuse(loc, *[B.cyl(x, y, RB.SP_NUT_CB_D + 0.2, Z0, Z0 + T) for x, y in RB.LOCK_B_LOC])   # 转子罩锁 S 窝 (Φ8 深 3.8) 切 3 后成通孔, 定子用不到 ⇒ 补实
CB_DEPTH = 1.5                                    # 11-24 用户「挖1.5mm沉孔」: 底面螺母沉孔 Φ IR_CL_NUT_CB_D 深 1.5 (留 1.5); 装 270° 时螺母 Z6.8–10.5, 离 247.5° 下方电机线夹顶 Z6.0 0.8
loc = B.cut(loc, *[B.cyl(x, y, B.IR_CL_NUT_CB_D, Z0 + T - CB_DEPTH, Z0 + T + 1) for x, y in RB.SP_HOLES_LOC['out']])   # 螺母沉孔 (翻面后在底面)
def tf(s, t): return BRepBuilderAPI_Transform(s, t, True).Shape()
f = gp_Trsf(); f.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi)       # 绕径向轴翻面: y→−y, z→−z (板对称, 销/槽对称)
m = gp_Trsf(); m.SetTranslation(gp_Vec(0, 0, B.FL_Z0 + Z0))                         # 原 Z0 面 → 定子盘底 FL_Z0
r = gp_Trsf(); r.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), math.radians(B.IR_ANG))
ir_clamp_b = B.clean(tf(tf(tf(loc, f), m), r))
bb = B.bbox(ir_clamp_b)
INFO = dict(t=T, z=(round(bb[2], 2), round(bb[5], 2)), v=round(B.vol(ir_clamp_b), 1), ang=B.IR_ANG, holes=B.IR_CL_HOLES)
if __name__ == '__main__':
    print(json.dumps(INFO, ensure_ascii=False, default=str))
    if '--check' not in sys.argv:
        RB.out('ir_clamp_b_v1_2', ir_clamp_b, color='#C9B458')   # _print: 装配姿态落床 (底面螺母沉孔朝床; 顶面有定位销, 不能朝床)
        print('写出', RB.OUTD)
