"""V1.2 电机线固定: MR30 座 mr30_seat_v1_2 + 电机线束线夹 motor_wire_clamp_v1_2 (2026-11-16)
    cd v1.2/scripts && ../../.venv/bin/python motor_wire_v1_2.py
世界坐标 (同 build_v1_2): 原点在转轴, Z 向上, 底盘顶面 Z0 (底盘 Φ220×6, Z−6..0), +y = 控制板一侧。
输出: v1.2/models/mr30_seat_v1_2/mr30_seat_v1_2.{step,stl}            (打印姿态: 顶面贴床, 槽口朝上)
      v1.2/models/motor_wire_clamp_v1_2/motor_wire_clamp_v1_2.{step,stl} (打印姿态: 顶面贴床, 线槽朝上)
      两个目录各有 *_asm.step (装配坐标, 含接头/线/螺丝/铜螺母示意) + 共用 motor_wire_report.json
底盘切削 (通孔 / 沉孔 / 护套坑) 写在 build_v1_2.py 的 MW_M3 / MW_POCKET (底盘 clean 之前); 本脚本 assert 两边一致,
    B 里还没有时 (先测阶段) 自己在 B.disc 上切, 再做干涉校核。

1) MR30 座 (接头做法照 models/mr30_clamp_12p3x5p3x15p4 第 5–8 步现行规则, 只改固定方式和高度):
   接头 (用户 09-16): 总长 15.4; 本体 (开口侧) 11.8×4.8 长 8.5, 护套 (堵头/出线侧) 12.3×5.3 长 6.9, 同轴, 本体底面比护套高 0.25。
   ⚠ 待用户确认 (假设): 座子固定 MR30-M 公头, 护套 (带线) 朝 −y 接电机线, 开口朝 +y 让控制板那根线的母头插进来。
   位置: 底盘 −x 侧 (x −75..−47, y −9.0..+8.9), 夹在网格 M6 孔 (−62.5, ±12.5) 之间 (孔边 y ±9.3, 座子两端各让 0.3 / 0.4)。
   高度: 定子盘 (flange_disc) 底 FL_Z0 = 8.5 ⇒ 座顶 ≤ 8.0。旧件叠层 10.3 放不下, 取的做法:
     - 去掉旧底板垫片, 座子直接坐底盘顶面 Z0; 底盘顶面挖护套坑 12.3×6.9 深 0.25 (= 本体比护套低出的那 0.25),
       护套坐坑底 Z−0.25, 本体底面正好落在底盘顶面 Z0 被托住 (代替旧垫片的 0.25 凸台), 底盘剩 5.75;
     - 顶板 3 → 2.95: 座顶 = 护套顶 5.05 + 2.95 = 8.0 (= 定子盘底 − 0.5)。
     理由: 只沉 0.25 底盘几乎不受影响, 坑只在护套投影内, 开口外母头照样平放底盘; 沉更深的话 +y 外面的母头也得挖坑 (会跨过 M6 孔)。
   槽 (零间隙零过盈, 台阶对齐): 本体段 11.8 宽 × 顶 Z4.8 / 护套段 12.3 宽 × 顶 Z5.05; 槽底开通 (底盘顶面当槽底); 顶板贴接头顶 (上下零间隙, 螺丝压住)。
   卡牢 (用户 11-16: 要经常拔插):
     插母头 (力推公头往 −y) → 护套尾面顶后墙 (+ 坑尾壁), 挡面 27.2 mm² (12.3×5.3 减出线口);
     拔母头 (力拉公头往 +y) → 护套前端台肩 (护套比本体单边大 0.25) 顶槽台阶: 座子两侧+顶 5.5 mm² + 底盘坑前壁 3.1 mm² = 8.55 mm²
       (按矩形算; 实物端面跑道形, 实际台肩更小, 见旧件记录)。力经座子 → 2×M3 + 坑壁 → 底盘。
   出线 (−y 后墙 2.5 厚, 旧件 3 ⇒ 让 M6 孔): 用户 11-16 实测电机线 3 根 Φ3 并排。针距 3.5 做 3 个 Φ3 U 口时口间肉只剩 0.5 (打不出),
     ⇒ 合并成一条 10×3 长圆口 (3 线心 x −3.5/0/+3.5, 线心 Z2.4 = 针轴, 两端 R1.5, 顶 Z3.9, 直边开到底盘顶面), 线零余量。
     口两侧挡护套尾面各 1.15, 口顶到护套顶 1.15。控制板那端 (+y, 母头) 线按 Φ2.5, 座子不管。
   固定: 2×M3×4 铜螺母 (热压, 件顶面往下 Φ4.2 深 4, 铜螺母顶齐件顶 = 同 mos_clamp_v1_2; 下面 Φ3.4 过孔), 孔 (x −71 / −51, y −0.05);
     M3×12 内六角从底盘底面 Φ7×2 沉孔往上 (头支承 Z−4), 尖 Z8.0 = 件顶 (啮合 4), 拉力把铜螺母压向孔底台阶。
2) 电机线束线夹 (用户 11-16 更正走向): 电机线从出线口 (~(13, −33)) → (30, −45) → 往下到 y≈−62 → 沿 y −62…−65 往 −x
   穿过 31/30/29 号孔一带 → (−40, −60) → 经 22 号孔内侧到 (−64, −40) → 往上进 MR30 −y 端。线夹在 29 (−37.5, −62.5) / 30 (−12.5, −62.5)
   两孔之间, 线在这里沿 x 走。只理线限位, 不卡紧 (用户 11-16):
   桥形压条 x −30..−17 (13, 沿线) × y −74.1..−49.9 (24.2, 横跨线) × 高 6; 底面一条沿 x 的通洞 9.6×3.3 (3×Φ3 并排 9×3, 单边 +0.3, 线可滑动),
     洞心 y −62; 2×M3 在线 ±y 两侧 (−23.5, −53.5) / (−23.5, −70.5), 铜螺母同上 (件顶压入), M3×10 尖 Z6.0 = 件顶。离两 M6 孔边各 1.3。
线径 Φ3、母头外形、公母朝向、M6 孔 (−62.5, ±12.5) 上是否还要装东西 —— 待用户确认。
"""
import io, contextlib, json, math, sys
from pathlib import Path
f_ = io.StringIO()
with contextlib.redirect_stdout(f_):
    import build_v1_2 as B
from helpers import write_doc, bbox, solids
from OCP.gp import gp_Trsf, gp_Vec, gp_Ax1, gp_Pnt, gp_Dir
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Cut
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.StlAPI import StlAPI_Writer

cyl, cut, fuse, op, vol, clean, xf = B.cyl, B.cut, B.fuse, B.op, B.vol, B.clean, B.xf
def box(x0, y0, z0, x1, y1, z1): return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()
def common(a, b): return op(BRepAlgoAPI_Common, a, b)
def ivol(a, b): return vol(common(a, b))
def ycyl(x, z, d, y0, y1):                         # 沿 y 的圆柱 (轴 x, z)
    t = gp_Trsf(); t.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), -math.pi / 2)
    s = xf(cyl(0, 0, d, 0, y1 - y0), t)            # 绕 X 转 −90°: +Z → +Y
    tt = gp_Trsf(); tt.SetTranslation(gp_Vec(x, y0, z)); return xf(s, tt)

# ===== 公共 =====
TOP_MAX = B.FL_Z0 - 0.5                            # 8.0 件顶上限 (定子盘底 − 0.5)
M3_HOLE_D = 3.4                                    # 底盘 M3 通孔
CB_D, CB_H = B.M3_CB_D, B.M3_CB_H                  # 底盘底面沉孔 Φ7×2 (同 B 其他 M3)
INS_D, INS_H = B.INS_HOLE_D, 4.0                   # M3×4 铜螺母孔 Φ4.2 深 4: 从件顶面往下压, 铜螺母顶齐件顶 (同 mos_clamp_v1_2);
                                                   #   螺丝拉力把铜螺母往孔底 (Φ4.2→Φ3.4 台阶) 压, 不是往外拔
PASS_D = 3.4                                       # 件内 M3 过孔
BEAR_Z = -B.DISC_T + CB_H                          # −4 头支承
def screw_len(top):                                # 尖 = 件顶 (铜螺母全啮合 4)
    return top - BEAR_Z

# ===== 1 MR30 座 =====
SHEATH_W, SHEATH_H, SHEATH_L = 12.3, 5.3, 6.9      # 护套 (出线侧)
BODY_W, BODY_H, BODY_L = 11.8, 4.8, 8.5            # 本体 (开口侧)
MR_L = SHEATH_L + BODY_L                           # 15.4
BODY_LIFT = (SHEATH_H - BODY_H) / 2                # 0.25
POCKET_D = BODY_LIFT                               # 底盘护套坑深 0.25 ⇒ 本体底面 = 底盘顶 Z0
FLOOR_T = 1.2                                      # 11-18 用户: 座子加底片 1.2 (原底开, 护套坐底盘坑; 玻纤板方案后坑成了 FR4 通孔 S1, 护套悬空)
Z_SH0 = FLOOR_T                                    # 护套底 1.2 (原 −0.25); 本体底 1.45 (本体段底片 1.45 = 原底盘坑台阶)
Z_SH1 = Z_SH0 + SHEATH_H                           # 护套顶 5.05
Z_BD0, Z_BD1 = Z_SH0 + BODY_LIFT, Z_SH0 + BODY_LIFT + BODY_H   # 本体 0 .. 4.8
PIN_Z = Z_SH0 + SHEATH_H / 2                       # 针轴 2.4
MR_PITCH = 3.5
T_TOP = 1.5                                        # 顶板 (11-18: 2.95→1.5, 让给底片 1.2 + 原坑 0.25): 座顶 = 8.0 = 定子盘底 − 0.5 = M3×14 尖
SEAT_H = Z_SH1 + T_TOP                             # 8.0
REAR_T = 2.5                                       # 后墙 (旧件堵头 3)
MR_XC = -61.0
SEAT_HX = 16.0                                     # 座 x 半宽 (32; 11-18 用户: 铜螺母压进去撑变形 ⇒ 28→32 只加宽, 孔位不动: 外壁 1.9→3.9, 内壁 (到护套槽) 仍 1.75)
Y_R = -9.0                                         # 后墙外面
Y_CAPI = Y_R + REAR_T                              # −6.5 护套尾面
Y_STEP = Y_CAPI + SHEATH_L                         #  0.4 护套/本体台阶
Y_OPEN = Y_STEP + BODY_L                           #  8.9 开口面
MW_WIRE_D = 3.0                                    # 电机线 (用户 11-16 实测) 零余量
SLOT_HW = MR_PITCH + MW_WIRE_D / 2                 # 5.0 合并出线口半宽 (10×3)
SLOT_TOP = PIN_Z + MW_WIRE_D / 2                   # 3.9
# 11-18 用户: 两版 —— 玻纤板版 (整机默认, 孔外移 1, 内壁 2.75) / _old 版 (配旧一体底盘 Φ220×6, 原孔 ±10, 内壁 1.75); 都加宽 32 + 底片
MR_INS_DX, MR_INS_DX_OLD = 11.0, 10.0
def mr_ins(dx=MR_INS_DX): return [(MR_XC - dx, (Y_R + Y_OPEN) / 2), (MR_XC + dx, (Y_R + Y_OPEN) / 2)]
MR_INS = mr_ins()
assert MR_INS_DX - INS_D / 2 - SHEATH_W / 2 >= 2.5 and SEAT_HX - MR_INS_DX - INS_D / 2 >= 2.5, '铜螺母孔壁 < 2.5'
MR_POCKET = None                                   # 11-18: 座子加底片, 底盘/玻纤板护套坑取消

assert SEAT_H <= TOP_MAX + 1e-9, (SEAT_H, TOP_MAX)
assert B.DISC_T - POCKET_D >= 2.0
for gx, gy in [(-62.5, 12.5), (-62.5, -12.5)]:
    assert (gx, gy) in B.GRID                       # 网格坐标作定位参考 (11-18 起这几个 M6 孔已删, 只校间隙)
    assert gy - B.M6_D / 2 >= Y_OPEN + 0.3 - 1e-9 if gy > 0 else gy + B.M6_D / 2 <= Y_R - 0.3 + 1e-9, 'MR30 座压到 M6 孔'
U_RIB_OLD = MR_PITCH - MW_WIRE_D                   # 0.5 ⇒ 分开做 3 个 Φ3 U 口打不出, 合并
assert U_RIB_OLD < 0.8

def mr30_seat(dx=MR_INS_DX):
    s = box(MR_XC - SEAT_HX, Y_R, 0, MR_XC + SEAT_HX, Y_OPEN, SEAT_H)
    s = cut(s, box(MR_XC - BODY_W / 2, Y_STEP, Z_BD0, MR_XC + BODY_W / 2, Y_OPEN + 1, Z_BD1))     # 本体段槽 11.8, 底片 1.45 (11-18)
    s = cut(s, box(MR_XC - SHEATH_W / 2, Y_CAPI, Z_SH0, MR_XC + SHEATH_W / 2, Y_STEP, Z_SH1))    # 护套段槽 12.3, 底片 1.2 (11-18)
    ys = (Y_R - 1, Y_CAPI + 0.01)                                                                 # 后墙出线口: 10×3 长圆 + 直边到底
    w = fuse(box(MR_XC - SLOT_HW, ys[0], Z_SH0, MR_XC + SLOT_HW, ys[1], PIN_Z),                 # 11-18: 直边开到底片顶 (原开到底)
             box(MR_XC - MR_PITCH, ys[0], PIN_Z - 0.01, MR_XC + MR_PITCH, ys[1], SLOT_TOP),
             *[ycyl(MR_XC + k * MR_PITCH, PIN_Z, MW_WIRE_D, *ys) for k in (-1, 1)])
    s = cut(s, w)
    for x, y in mr_ins(dx):
        s = cut(s, cyl(x, y, PASS_D, -1, SEAT_H + 1), cyl(x, y, INS_D, SEAT_H - INS_H, SEAT_H + 1))
    return clean(s)

def mr30_plug(dx=0.0, dy=0.0, dz=0.0):                # 公头示意 (矩形盒)
    return fuse(box(MR_XC - SHEATH_W / 2 + dx, Y_CAPI + dy, Z_SH0 + dz, MR_XC + SHEATH_W / 2 + dx, Y_STEP + dy, Z_SH1 + dz),
                box(MR_XC - BODY_W / 2 + dx, Y_STEP + dy, Z_BD0 + dz, MR_XC + BODY_W / 2 + dx, Y_OPEN + dy, Z_BD1 + dz))

# ===== 2 电机线束线夹 =====
# 用户 11-16 更正: 线在这里沿 x 穿过 (从 31/30 号孔一带往 −x 走到 (−40, −60) 再拐去 MR30), 夹子长边 (y) 横跨在线上方,
#   两颗 M3 一颗在线 +y 侧、一颗在 −y 侧; 3×Φ3 并排, 槽沿 x。
CL_XC, CL_YC = -23.5, -62.0                        # 线束中心 (y 与两 M6 孔 (−37.5/−12.5, −62.5) 同排, 线从两孔之间过)
CL_HX = 6.5                                        # 夹子 x 半宽 (13 = 沿线方向长)
CL_WIRE_D, CL_PITCH = 3.0, 3.0                     # 3 线贴在一起 (用户实测 Φ3)
CL_WIRE_Y = [CL_YC + k * CL_PITCH for k in (-1, 0, 1)]
CL_ZC = CL_WIRE_D / 2                              # 线平放底盘, 线心 Z1.5
CL_CLR = 0.3                                       # 用户 11-16: 线夹只理线限位, 槽单边 +0.3, 线能滑动
CL_CH_HW = CL_PITCH + CL_WIRE_D / 2 + CL_CLR       # 4.8 桥洞半宽 (9.6)
CL_CH_H = CL_WIRE_D + CL_CLR                       # 3.3 桥洞高
CL_H = 6.0                                         # 件顶 = M3×10 尖 (铜螺母顶齐件顶)
CL_INS_DY, CL_INS_DY_OLD = 9.5, 8.5                # 铜螺母孔心离线束中心 (y); 11-18 两版: 玻纤板版 9.5 (到线槽肉 2.6) / _old 版 8.5 (原孔, 1.6)
def cl_ins(dy=CL_INS_DY): return [(CL_XC, CL_YC + dy), (CL_XC, CL_YC - dy)]   # +y 侧 / −y 侧
CL_INS = cl_ins()
EAR_H = INS_D / 2 + 3.0                            # 5.1 孔到 y 端面 (11-18: 端壁 1.5→3.0)
def cl_span(dy=CL_INS_DY): return CL_YC - dy - EAR_H, CL_YC + dy + EAR_H
CL_Y0, CL_Y1 = cl_span()                           # 玻纤板版 −76.6 .. −47.4 (29.2); _old −75.6 .. −48.4 (27.2)
assert CL_H <= TOP_MAX and CL_H - CL_CH_H >= 2.0
assert CL_INS_DY - INS_D / 2 - CL_CH_HW >= 1.2, '铜螺母孔到线槽肉 < 1.2'
for gx, gy in [(-37.5, -62.5), (-12.5, -62.5)]:
    assert (gx, gy) in B.GRID                       # 网格坐标作定位参考 (11-18 起这几个 M6 孔已删, 只校间隙)
    assert abs(gx - CL_XC) - B.M6_D / 2 - CL_HX >= 1.0, '线夹压到 M6 孔'

def xcyl(y, z, d, x0, x1):                         # 沿 x 的圆柱
    t = gp_Trsf(); t.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 1, 0)), math.pi / 2)
    s = xf(cyl(0, 0, d, 0, x1 - x0), t)            # 绕 Y 转 +90°: +Z → +X
    tt = gp_Trsf(); tt.SetTranslation(gp_Vec(x0, y, z)); return xf(s, tt)

def wire_clamp(dy=CL_INS_DY):                      # 桥形压条: 底面一个 9.6×3.3 通洞 (沿 x), 两端各一颗 M3
    y0, y1 = cl_span(dy)
    s = box(CL_XC - CL_HX, y0, 0, CL_XC + CL_HX, y1, CL_H)
    s = cut(s, box(CL_XC - CL_HX - 1, CL_YC - CL_CH_HW, -1, CL_XC + CL_HX + 1, CL_YC + CL_CH_HW, CL_CH_H))
    for x, y in cl_ins(dy):
        s = cut(s, cyl(x, y, PASS_D, -1, CL_H + 1), cyl(x, y, INS_D, CL_H - INS_H, CL_H + 1))
    return clean(s)

def clamp_wires(dy=0.0, dz=0.0, d=CL_WIRE_D):
    return [xcyl(y + dy, CL_ZC + dz, d, CL_XC - CL_HX - 3, CL_XC + CL_HX + 3) for y in CL_WIRE_Y]

# ===== 3 底盘切削 (build_v1_2.py MW_M3 / MW_POCKET 应与此一致) =====
MW_M3 = MR_INS + CL_INS
def disc_cuts():
    out = []
    for x, y in MW_M3:
        out += [cyl(x, y, M3_HOLE_D, -B.DISC_T - 1, 1), cyl(x, y, CB_D, -B.DISC_T - 1, -B.DISC_T + CB_H)]
    return out

MW_TOP = [SEAT_H] * len(MR_INS) + [CL_H] * len(CL_INS)
SCREW_L = [screw_len(t) for t in MW_TOP]           # MR30 座 M3×12 / 线夹 M3×10
assert SCREW_L == [14.0, 14.0, 12.0, 12.0], SCREW_L   # 11-18 玻纤板底座 (支承 Z-6): 原 12/10 各 +2
def screws():
    sc = [cyl(x, y, 3.0, BEAR_Z, t) for (x, y), t in zip(MW_M3, MW_TOP)] + [cyl(x, y, 5.5, BEAR_Z - 3.0, BEAR_Z) for x, y in MW_M3]
    ins = [cyl(x, y, INS_D, t - INS_H, t) for (x, y), t in zip(MW_M3, MW_TOP)]
    return sc, ins

def build():
    seat, clamp = mr30_seat(), wire_clamp()
    if hasattr(B, 'MW_M3'):                         # 已并进 build_v1_2
        assert all(math.hypot(a - c, b - d) < 1e-9 for (a, b), (c, d) in zip(B.MW_M3, MW_M3)), (B.MW_M3, MW_M3)
        assert B.MW_POCKET is None and MR_POCKET is None
        assert abs(B.MW_HOLE_D - M3_HOLE_D) < 1e-9
        disc, disc0, merged = B.disc, None, True
    else:
        disc0 = B.disc; disc = clean(cut(B.disc, *disc_cuts())); merged = False
    return seat, clamp, disc, merged

def check(seat, clamp, disc, merged):
    R = dict(merged_in_build=merged)
    R['seat'] = dict(bbox=[round(v, 3) for v in bbox(seat)], vol=round(vol(seat), 2), valid=BRepCheck_Analyzer(seat).IsValid(), n=len(solids(seat)))
    R['clamp'] = dict(bbox=[round(v, 3) for v in bbox(clamp)], vol=round(vol(clamp), 2), valid=BRepCheck_Analyzer(clamp).IsValid(), n=len(solids(clamp)))
    assert R['seat']['valid'] and R['clamp']['valid'] and R['seat']['n'] == 1 and R['clamp']['n'] == 1
    assert bbox(seat)[5] <= TOP_MAX + 1e-6 and bbox(clamp)[5] <= TOP_MAX + 1e-6
    # 底盘: 新切削原来是实心 (不与已有孔/槽/坑重叠), 外扩 1 也是实心 (壁 ≥ 1)
    base = B.disc if not merged else None
    if base is not None:
        cuts = disc_cuts()
        for i, c in enumerate(cuts):
            ci = common(c, cyl(0, 0, B.DISC_D, -B.DISC_T, 0))
            assert abs(ivol(base, ci) - vol(ci)) < 1e-3, f'底盘新切削 {i} 碰到已有特征'
        for x, y in MW_M3:
            g = cyl(x, y, CB_D + 2, -B.DISC_T, -B.DISC_T + CB_H + 1)
            assert abs(ivol(base, g) - vol(g)) < 1e-3, f'沉孔 ({x},{y}) 外 1 mm 不实心'
        R['disc_dv'] = round(vol(base) - vol(disc), 2)
    R['disc_valid'] = BRepCheck_Analyzer(disc).IsValid()
    R['disc_min_t'] = round(B.DISC_T - POCKET_D, 2)
    # M6 沉孔 Φ13 到新 M3 沉孔 Φ7 的肉
    R['cb_web_min'] = round(min(math.hypot(x - a, y - b) - B.CB_D / 2 - CB_D / 2 for x, y in MW_M3 for a, b in B.EXTRA + B.FIXED), 2)
    assert R['cb_web_min'] >= 1.0
    # 静止件
    ST = dict(disc=disc, flange_disc=B.flange_disc, mounting_flange=B.mounting_flange, ring=B.ring, motor=B.motor, board=B.board,
              heatsink=B.heatsink, mos_clamp=B.CD.clamp, cap_clamp=B.CD.cap_clamp, mos=B.CD.mos, cd_pcb=B.CD.pcb, cd_sink2=B.CD.sink2,
              cd_cap=B.CD.cap, key_bracket=B.key_bracket, key_board=B.key_board, xt_clamp=B.xt_clamp, xt_shim=B.xt_shim,
              glass_seat=B.seat, shroud_lo=B.shroud_lo, clamp_ring=B.clamp_ring)
    for i, p in enumerate(B.posts): ST[f'post{i}'] = p
    for i, p in enumerate(B.seat_nuts): ST[f'seat_nut{i}'] = p
    sc, ins = screws()
    R['inter'] = {}; R['gap'] = {}
    for pn, P in (('seat', seat), ('clamp', clamp)):
        for k, S in ST.items():
            v = ivol(P, S); R['inter'][f'{pn}/{k}'] = round(v, 4)
            assert v < 1e-4, f'{pn} 与 {k} 干涉 {v}'
            dd = BRepExtrema_DistShapeShape(P, S); dd.Perform(); R['gap'][f'{pn}/{k}'] = round(dd.Value(), 3)
    assert ivol(seat, clamp) < 1e-6
    dd = BRepExtrema_DistShapeShape(seat, clamp); dd.Perform(); R['gap']['seat/clamp'] = round(dd.Value(), 3)
    # 上方定子盘/安装法兰/线圈环在两件投影内的最低面
    for pn, P in (('seat', seat), ('clamp', clamp)):
        b = bbox(P); col = box(b[0], b[1], 0, b[3], b[4], 40)
        zmin = min([bbox(common(col, S))[2] for S in (B.flange_disc, B.mounting_flange, B.ring) if ivol(col, S) > 1e-6] or [99])
        R[f'{pn}_above_zmin'] = round(zmin, 3); R[f'{pn}_top_gap'] = round(zmin - b[5], 3)
        assert zmin - b[5] >= 0.5 - 1e-3, (pn, '上方最低面', round(zmin, 3), '件顶', round(b[5], 3), '件 bbox', [round(v, 2) for v in b])
    # 接头: 就位零干涉 (座 + 底盘); 挪 0.05 各方向都吃进 (零间隙)
    plug = mr30_plug()
    R['plug_inter'] = dict(seat=round(ivol(plug, seat), 5), disc=round(ivol(plug, disc), 5))
    assert R['plug_inter']['seat'] < 1e-5 and R['plug_inter']['disc'] < 1e-5
    R['plug_shift'] = {}
    for nm, (dx, dy, dz) in dict(px=(0.05, 0, 0), py=(0, 0.05, 0), my=(0, -0.05, 0), pz=(0, 0, 0.05), mz=(0, 0, -0.05)).items():
        p = mr30_plug(dx, dy, dz); R['plug_shift'][nm] = round(ivol(p, seat) + ivol(p, disc), 4)
        assert R['plug_shift'][nm] > 1e-3, f'接头往 {nm} 挪 0.05 不受限'
    # 线: 线夹 3 线就位零干涉 (压紧量 0), 抬 0.05 / 横挪 0.05 吃进; 螺丝 / 铜螺母
    w = clamp_wires()
    R['wire_inter'] = round(sum(ivol(x, clamp) + ivol(x, disc) for x in w), 5); assert R['wire_inter'] < 1e-5
    R['wire_free'] = dict(pz=round(sum(ivol(x, clamp) for x in clamp_wires(dz=0.29)), 4), py=round(sum(ivol(x, clamp) for x in clamp_wires(dy=0.29)), 4),
                          pz_hit=round(sum(ivol(x, clamp) for x in clamp_wires(dz=0.35)), 4), py_hit=round(sum(ivol(x, clamp) for x in clamp_wires(dy=0.35)), 4))
    assert R['wire_free']['pz'] < 1e-5 and R['wire_free']['py'] < 1e-5 and R['wire_free']['pz_hit'] > 1e-4 and R['wire_free']['py_hit'] > 1e-4
    mw = [ycyl(MR_XC + k * MR_PITCH, PIN_Z, MW_WIRE_D, Y_R - 5, Y_CAPI) for k in (-1, 0, 1)]   # MR30 后墙出线 3×Φ3
    R['mr_wire_inter'] = round(sum(ivol(x, seat) + ivol(x, disc) for x in mw), 5); assert R['mr_wire_inter'] < 1e-5
    R['screw_inter'] = round(sum(ivol(s, seat) + ivol(s, clamp) + ivol(s, disc) for s in sc[:len(MW_M3)]), 5)
    R['insert_inter'] = round(sum(ivol(s, seat) + ivol(s, clamp) for s in ins), 5)
    assert R['screw_inter'] < 1e-5 and R['insert_inter'] < 1e-5
    R['heads_in_cb'] = round(sum(ivol(s, disc) for s in sc[len(MW_M3):]), 5); assert R['heads_in_cb'] < 1e-5
    # 壁厚
    R['mr_ins_web'] = dict(slot=round(10.0 - INS_D / 2 - SHEATH_W / 2, 2), out=round(SEAT_HX - 10.0 - INS_D / 2, 2))
    R['mr_slot_lips'] = dict(side=round(SHEATH_W / 2 - SLOT_HW, 2), top=round(Z_SH1 - SLOT_TOP, 2))
    R['mr_m6_gap'] = dict(py=round(12.5 - B.M6_D / 2 - Y_OPEN, 2), my=round(Y_R - (-12.5 + B.M6_D / 2), 2))
    sh = box(MR_XC - SHEATH_W / 2, Y_CAPI - 0.5, Z_SH0, MR_XC + SHEATH_W / 2, Y_CAPI, Z_SH1)             # 护套尾面后 0.5 薄片
    R['tail_stop_mm2'] = round((ivol(sh, seat) + ivol(sh, disc)) / 0.5, 2)                               # 插入方向 (−y) 挡面
    fr = cut(box(MR_XC - SHEATH_W / 2, Y_STEP, Z_SH0, MR_XC + SHEATH_W / 2, Y_STEP + 0.5, Z_SH1), box(MR_XC - BODY_W / 2, Y_STEP - 1, Z_BD0, MR_XC + BODY_W / 2, Y_STEP + 1, Z_BD1))
    R['shoulder_stop_mm2'] = dict(seat=round(ivol(fr, seat) / 0.5, 3), disc=round(ivol(fr, disc) / 0.5, 3))  # 拔出方向 (+y) 台肩
    R['cl_ins_web'] = round(CL_INS_DY - INS_D / 2 - CL_CH_HW, 2)
    R['cl_m6_gap'] = round(min(abs(gx - CL_XC) for gx in (-37.5, -12.5)) - B.M6_D / 2 - CL_HX, 2)
    return R

def print_pose(s):                                   # 绕 X 翻 180°, 顶面贴床, 居中
    t = gp_Trsf(); t.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi); s = xf(s, t)
    b = bbox(s); tt = gp_Trsf(); tt.SetTranslation(gp_Vec(-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2])); return xf(s, tt)

def export(seat, clamp):
    sc, ins = screws()
    for name, P, col, extra in (('mr30_seat_v1_2', seat, '#F1C232', [('MR30-M 公头 (示意)', mr30_plug(), '#FFD700')] +
                                 [(f'电机线 Φ3 #{k}', ycyl(MR_XC + k * MR_PITCH, PIN_Z, MW_WIRE_D, Y_R - 10, Y_CAPI), '#222222') for k in (-1, 0, 1)]),
                                ('motor_wire_clamp_v1_2', clamp, '#E69138', [(f'电机线 Φ3 #{i}', w, '#222222') for i, w in enumerate(clamp_wires())])):
        d = B.V12 / 'models' / 'mr30_seat_v1_2'; d.mkdir(parents=True, exist_ok=True)   # 11-18 用户: 线夹文件也放 MR30 文件夹
        pp = print_pose(P)
        write_doc([(name, pp, col, None, False)], d / f'{name}.step', name)
        BRepMesh_IncrementalMesh(pp, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(pp, str(d / f'{name}.stl'))
        idx = [i for i, (x, y) in enumerate(MW_M3) if (x, y) in (MR_INS if name.startswith('mr30') else CL_INS)]
        items = [(name, P, col, None, False)] + [(n, s, c, None, False) for n, s, c in extra]
        items += [(f'M3×{SCREW_L[i]:g} 内六角', fuse(sc[i], sc[len(MW_M3) + i]), '#888888', None, False) for i in idx]
        items += [('M3×4 铜螺母', ins[i], '#B8860B', None, False) for i in idx]
        write_doc(items, d / f'{name}_asm.step', name + '_asm')
    # _old 版 (配旧一体底盘 Φ220×6, 原孔位; 旧底盘沉孔 Φ7×2 支承 Z-4 ⇒ MR30 座 M3×12 / 线夹 M3×10): 只出打印件 STEP/STL
    d = B.V12 / 'models' / 'mr30_seat_v1_2'
    for name, P, col in (('mr30_seat_v1_2_old', mr30_seat(MR_INS_DX_OLD), '#F1C232'), ('motor_wire_clamp_v1_2_old', wire_clamp(CL_INS_DY_OLD), '#E69138')):
        pp = print_pose(P)
        write_doc([(name, pp, col, None, False)], d / f'{name}.step', name)
        BRepMesh_IncrementalMesh(pp, 0.02, False, 0.2, True)
        w = StlAPI_Writer(); w.ASCIIMode = False; assert w.Write(pp, str(d / f'{name}.stl'))

if __name__ == '__main__':
    seat, clamp, disc, merged = build()
    R = check(seat, clamp, disc, merged)
    if '--no-export' not in sys.argv:
        export(seat, clamp)
        json.dump(R, open(B.V12 / 'models' / 'mr30_seat_v1_2' / 'motor_wire_report.json', 'w'), indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in R.items() if k not in ('inter',)}, indent=1, ensure_ascii=False))
    print('全部校核通过; 干涉最大', max(R['inter'].values()))
