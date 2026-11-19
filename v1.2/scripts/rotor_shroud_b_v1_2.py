# -*- coding: utf-8 -*-
"""转子盘B 转子罩 (11-17 夜, 用户: 罩子 4 片 → 2 片; 锁到屏幕固定件上)。
    cd v1.2/scripts && ../../.venv/bin/python rotor_shroud_b_v1_2.py
由 V1.2 rotor_shroud_v1_2 (罩身 A/B 沿 x=0 分 + 顶盖 ±y 两片) 改:
  - 分法: 沿灯板那条线分成 +y / −y 两半, 每半连自己的顶盖做成一件 (罩身两端竖缝 y −14.46…+5.74 本来就把罩壁断开, 顶盖本来就是 ±y 两片)
  - 原 x=0 分缝凸耳 + 切向螺丝取消 (那条缝没了)
  - 罩底 4 个凸台: 原坐承载盘顶 Z32 → 改坐屏幕固定件弧形带顶 Z37 (抬 5), 孔 r79 → r77 (= 固定件上的 M3×4 铜螺母), M3×8 从上往下
    +y 半 = 40°/140° 两颗, −y 半 = 220°/320° 两颗 (各锁两个固定件)
  - 顶盖螺丝 (原 47.5/132.5/227.5/312.5°) 取消, 盖与唇局部填实; 配重孔上方顶盖开 Φ5.8 孔, 配重螺丝从罩顶插
打印: 倒放 (罩顶 Z73.08 落床, 顶盖整面贴床; 原单独顶盖时唇顶低 2 要支撑, 现在没有了)。
"""
import io, contextlib, json, math
f_ = io.StringIO()
with contextlib.redirect_stdout(f_):
    import rotor_b_v1_2 as RB
RS, B, LS = RB.RS, RB.B, RB.LS
from helpers import write_doc
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.gp import gp_Trsf, gp_Vec, gp_Ax1, gp_Pnt, gp_Dir

cyl, cut, fuse, clean, gbox, vol, bbox, xf, rotz, solids = B.cyl, B.cut, B.fuse, B.clean, B.gbox, B.vol, B.bbox, B.xf, B.rotz, B.solids
common, common_v, sector, pol, prism_xz = RB.common, RB.common_v, RS.sector, RS.pol, RS.prism_xz
Z0, Z1, R0, R1 = RS.Z0, RS.Z1, RS.R0, RS.R1
BOSS_Z0 = RB.H_Z1                     # 37.0 凸台底 = 固定件带顶
BOSS_T = 4.0                          # 4 (同原凸台厚; 11-18 盘顶改 30.5 后旧 RS.BOSS_Z1 - RS.Z0 不再是 4, 写死)
BOSS_Z1 = BOSS_Z0 + BOSS_T            # 41.0 螺丝头支承
GUS_Z1 = BOSS_Z1 + (R0 - RS.BOSS_RI)  # 45° 斜撑贴壁顶
HOLE_R = RB.SHR_LOCK_R                # 77
MNT_A = list(RB.SHR_LOCK_ANG)         # 40/140/220/320
MNT_L = 8.0                           # M3×8: 支承 Z41 → 尾 Z33 (固定件铜螺母 Z33–37 吃满 4)
assert abs(BOSS_Z1 - MNT_L - (RB.H_Z1 - RB.H_INS_H)) < 1e-6
SPLIT_Y = RS.ECC                      # 分界: 灯板中面 y = SCR_ECC (11-18 夜 −4.69, 原 −4.36; 两端竖缝内)
# 11-18 夜 用户: 底板上边 R85 圆弧伸出罩壁 r82–85 ⇒ +y 半罩底开缺口 = 底板板框外扩 BB_NOTCH_CLR, 从罩底到板顶 + BB_NOTCH_CLR (伸出的板被玻璃座挡住, 外面看不到)
BB_NOTCH = False                      # 11-19 用户: 底板回 r4j 矩形 (最远 r76.78 < 罩内壁 r82), 不再开缺口; 要恢复 R85 圆弧时改 True
BB_NOTCH_CLR = 0.5
BB_NOTCH_Z1 = B.Z_BB0 + B.BB_T + BB_NOTCH_CLR   # 37.1


def bb_notch():
    from shapely.geometry import Polygon as _P
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    poly = _P(RB.V.BB_POLY).buffer(BB_NOTCH_CLR, join_style=2)
    pg = BRepBuilderAPI_MakePolygon()
    for x, y in list(poly.exterior.coords)[:-1]: pg.Add(gp_Pnt(x, y, Z0 - 1))
    pg.Close()
    return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(pg.Wire()).Face(), gp_Vec(0, 0, BB_NOTCH_Z1 - (Z0 - 1))).Shape()


def ring_body_b():
    s = B.ann(R0, R1, Z0, Z1)
    for a0, a1 in RS.LIP_ARCS: s = fuse(s, sector(RS.LIP_R0, R0 + 0.5, RS.LIP_Z0, RS.LID_Z0, a0, a1))
    for a in MNT_A:                   # 凸台坐固定件带顶 Z37–41 + 45° 斜撑接罩壁
        b = fuse(gbox(RS.BOSS_RI, -RS.BOSS_W / 2, BOSS_Z0, R0 + 0.5, RS.BOSS_W / 2, BOSS_Z1),
                 prism_xz([(RS.BOSS_RI, BOSS_Z1 - 0.01), (R0 + 0.5, BOSS_Z1 - 0.01), (R0 + 0.5, GUS_Z1 + 0.5)], -RS.BOSS_W / 2, RS.BOSS_W / 2))
        s = fuse(s, xf(b, rotz(a)))
    s = clean(s)
    for a in MNT_A:
        x, y = pol(HOLE_R, a)
        s = cut(s, cyl(x, y, 3.4, BOSS_Z0 - 1, BOSS_Z1 + 0.01), cyl(x, y, RS.ACC_D, BOSS_Z1, Z1 + 1))
    for a in RS.W_A:                  # 配重孔 (原顶盖螺丝位也改成配重孔)
        x, y = pol(RS.W_R, a)
        s = cut(s, cyl(x, y, 3.4, RS.LIP_Z0 - 1, Z1 + 1), cyl(x, y, RS.W_CB_D, RS.W_BEAR, Z1 + 1))
    for sx in (1, -1):                # 两端竖缝 (天线板)
        x0, x1 = (RS.SLOT_X0, R1 + 1) if sx > 0 else (-R1 - 1, -RS.SLOT_X0)
        s = cut(s, gbox(x0, RS.SLOT_Y0, Z0 - 1, x1, RS.SLOT_Y1, Z1 + 1))
    return clean(s)


def lid_plain(k):
    """原顶盖去掉螺丝凸块/沉孔: 取原盖 Z≥LID_Z0 的板, 再把螺丝位的 Φ3.4/Φ5.7 孔补实"""
    lid = RS.lid_a if k == 'a' else RS.lid_b
    plate = common(lid, gbox(-100, -100, RS.LID_Z0, 100, 100, Z1 + 1))
    scr = RS.LID_SCR_A if k == 'a' else [a + 180 for a in RS.LID_SCR_A]
    fill = [common(cyl(*pol(RS.W_R, a), 7.0, RS.LID_Z0, Z1), cyl(0, 0, 2 * RS.LID_R, RS.LID_Z0 - 1, Z1 + 1)) for a in scr]
    return clean(fuse(plate, *fill))


def half(k):
    sy = 1 if k == 'a' else -1
    ring = ring_body_b()
    y0, y1 = (SPLIT_Y, 100) if sy > 0 else (-100, SPLIT_Y)
    s = common(ring, gbox(-100, y0, Z0 - 1, 100, y1, Z1 + 1))
    s = fuse(s, lid_plain(k))
    if sy > 0 and BB_NOTCH: s = cut(s, bb_notch())  # 底板 R85 缺口
    for a in RS.W_A:                  # 配重孔上方顶盖开孔 (配重螺丝从罩顶插)
        x, y = pol(RS.W_R, a)
        if (y > SPLIT_Y) == (sy > 0): s = cut(s, cyl(x, y, RS.W_CB_D, RS.W_BEAR, Z1 + 1))
    for a in MNT_A:                   # 凸台起子孔穿顶盖
        x, y = pol(HOLE_R, a)
        if (y > SPLIT_Y) == (sy > 0): s = cut(s, cyl(x, y, RS.ACC_D, BOSS_Z1, Z1 + 1))
    return clean(s)


shr_a, shr_b = half('a'), half('b')

def report():
    _fpc = RB.load_fpc()
    rep = dict(vol=dict(a=round(vol(shr_a), 1), b=round(vol(shr_b), 1)), mass_g=dict(a=round(vol(shr_a) * 1.24e-3, 1), b=round(vol(shr_b) * 1.24e-3, 1)),
               valid=dict(a=BRepCheck_Analyzer(shr_a).IsValid(), b=BRepCheck_Analyzer(shr_b).IsValid()), solids=dict(a=len(solids(shr_a)), b=len(solids(shr_b))),
               boss=dict(z=(BOSS_Z0, BOSS_Z1), hole_r=HOLE_R, ang=MNT_A, screw=f'M3×{MNT_L:g}'))
    others = dict(承载盘B=RB.rim, 固定件A=RB.hold_a, 固定件B=RB.hold_b, 底板=RB.VB['baseboard'], 底板器件=RB.VB['bb_parts'], CZ06=RB.VB['cz06'],
                  灯板=RB.VB['led'], 夹条=LS.bar_s, 顶部件=LS.top, 无线托盘=RB.WH.H, FPC_A=_fpc['fpc_a_v1_2'], FPC_B=_fpc['fpc_b_v1_2'],
                  桥板A=_fpc['bridge_a_v1_2'], 桥板B=_fpc['bridge_b_v1_2'], FPC座=_fpc['bb_fpc_seats_v1_2'])
    inter = {}
    for n1, s1 in (('罩A(+y)', shr_a), ('罩B(-y)', shr_b)):
        for n2, s2 in others.items():
            v = common_v(s1, s2)
            if v > 1e-3: inter[f'{n1} × {n2}'] = round(v, 3)
    v = common_v(shr_a, shr_b)
    if v > 1e-3: inter['罩A × 罩B'] = round(v, 3)
    rep['interference_mm3'] = inter
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    return rep


if __name__ == '__main__':
    rep = report()
    for name, sh, col in (('rotor_shroud_b_a_v1_2b', shr_a, '#6FA8DC'), ('rotor_shroud_b_b_v1_2b', shr_b, '#93C47D')):
        d = B.V12 / 'models' / name; d.mkdir(parents=True, exist_ok=True)
        write_doc([(name, sh, col, None, False)], d / f'{name}.step', name)
        BRepMesh_IncrementalMesh(sh, 0.02, False, 0.2, True); w = StlAPI_Writer(); w.ASCIIMode = False; w.Write(sh, str(d / f'{name}.stl'))
        fx = gp_Trsf(); fx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi); t = xf(sh, fx)   # 倒放: 罩顶落床
        tz = gp_Trsf(); tz.SetTranslation(gp_Vec(0, 0, -bbox(t)[2])); t = xf(t, tz)
        BRepMesh_IncrementalMesh(t, 0.02, False, 0.2, True); w = StlAPI_Writer(); w.ASCIIMode = False; w.Write(t, str(d / f'{name}_print.stl'))
    (B.V12 / 'models' / 'rotor_shroud_b_a_v1_2b' / 'shroud_b_report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding='utf-8')
    print('ok')
