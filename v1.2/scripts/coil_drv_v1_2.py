"""POV3D V1.2 定子线圈驱动小板 (XKT-801) 校核 + 预览 (几何/参数在 coil_drv_geom.py, 已并进 build_v1_2: B.CD).

用户 11-12 夜:「mos锁住就可以」/「之前有一个类似xt60的件…就是锁这个mos的」/「再做一个卡电容的吧，电容卡半圆」/「mos偏心一点，电容是居中的」
- 沿板长轴 (Y): MOS (x58, 板中心 +2.95) → 板 (x55.05) → 电解电容 (轴 = 板中心线), MOS 尖 → 电容远端 71
- MOS 压块 mos_clamp_v1_2 (= models/mos_clamp_16x10x4p5 的 V1.2 版, 2×M3 低耳) 只锁 MOS; PCB 只靠 MOS 引脚挂着, 不罩不压
- MOS 背板贴散热片 (40×20 转 90°, 40 沿 Y, 嵌底盘通槽, 顶齐 Z0); 电容平躺在底盘弧形槽 (深 2.5), 半圆鞍形卡件 cap_clamp_v1_2
- 两件各 2×M3×12 从底盘底面 Φ7×2 沉孔往上, 法兰螺母坐耳顶; 可用高度 Z0..9.5 (定子盘底), 螺母顶 / 螺尖 / 件顶 ≤ 9.0

本脚本 import build_v1_2 (会重建全部几何)。两件 STEP/STL 由 build_v1_2.py 主程序出到 models/mos_clamp_v1_2/;
本脚本出 models/mos_clamp_v1_2/coil_drv_asm_v1_2.step (局部装配), 预览 out/coil_drv_preview.png, 打印校核表。
"""
import sys, math, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
T0 = time.time()
import build_v1_2 as B
from build_v1_2 import cyl, cut, fuse, op, clean, xf, vol, bbox, gbox
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Vec, gp_Trsf, gp_Pln
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common, BRepAlgoAPI_Section
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound

C = B.CD                            # 几何在 coil_drv_geom.py (build_v1_2 调 make, 已并进底盘)
globals().update({k: v for k, v in vars(C).items() if k[0].isupper()})
clamp, cap_clamp, pcb, mos, cap, sink2, screws, nuts, disc_cut_list = C.clamp, C.cap_clamp, C.pcb, C.mos, C.cap, C.sink2, C.screws, C.nuts, C.disc_cut_list
COIL_DRV_HOLES = ALL_HOLES


def dist(a, b):
    d = BRepExtrema_DistShapeShape(a, b); d.Perform(); return d.Value()
def cvol(a, b):
    return vol(op(BRepAlgoAPI_Common, a, b))


def checks():
    rows = []
    # 底盘 (合并后): GRID_REMOVE 已不开, 再切本件
    env = cyl(0, 0, B.DISC_D, -B.DISC_T, 0)
    disc_new = B.disc                    # 已含本件切口 (顶面平, 无支撑筋)
    names = list(PARTS)
    EXPECT = {('clamp', 'mos'), ('clamp', 'sink2'), ('mos', 'pcb'), ('mos', 'sink2')} | {(f'nut{i}', f'screw{i}') for i in range(len(screws))}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            v = cvol(PARTS[a], PARTS[b]); d = dist(PARTS[a], PARTS[b])
            if d < 2.0 or v > 1e-6:
                rows.append((a, b, d, v, tuple(sorted((a, b))) in {tuple(sorted(p)) for p in EXPECT}))
    ext = dict(flange_disc=B.flange_disc, mounting_flange=B.mounting_flange, ring=B.ring, board=B.board,
               seat=B.seat, xt_env=B.xt_env, xt_clamp=B.xt_clamp, heatsink_motor=B.heatsink, disc_new=disc_new)
    for a in names:
        for b, sb in ext.items():
            v = cvol(PARTS[a], sb); d = dist(PARTS[a], sb)
            rows.append((a, b, d, v, (a, b) in EXPECT))
    # 底盘新切口离现有孔/槽 ≥1 (现有空腔 = 盘包络 − 原盘(补实 15/19))
    voids = cut(cut(env, B.disc), *disc_cut_list)     # 底盘其它孔/槽 (去掉本件切口)
    hole_rows = []
    lbl = CUT_LBL
    for n, c in zip(lbl, disc_cut_list):
        hole_rows.append((n, dist(op(BRepAlgoAPI_Common, c, env), voids)))
    # 新切口之间 (散热片槽 ↔ 螺丝沉孔 ↔ 电容槽)
    for i in range(len(disc_cut_list)):
        for j in range(i + 1, len(disc_cut_list)):
            if lbl[i].split('Φ')[0].replace('沉孔', '') == lbl[j].split('Φ')[0].replace('沉孔', ''): continue   # 同一孔的通孔 / 沉孔
            hole_rows.append((f'{lbl[i]}↔{lbl[j]}', dist(op(BRepAlgoAPI_Common, disc_cut_list[i], env), op(BRepAlgoAPI_Common, disc_cut_list[j], env))))
    return rows, hole_rows, disc_new


# ======================== 预览 ========================
def section_lines(sh, pnt, nrm):
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopoDS import TopoDS
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.GCPnts import GCPnts_QuasiUniformDeflection
    import numpy as np
    s = BRepAlgoAPI_Section(sh, gp_Pln(gp_Pnt(*pnt), gp_Dir(*nrm)), False); s.Approximation(True); s.Build()
    out = []; e = TopExp_Explorer(s.Shape(), TopAbs_EDGE)
    while e.More():
        c = BRepAdaptor_Curve(TopoDS.Edge(e.Current())); q = GCPnts_QuasiUniformDeflection(c, 0.03)
        if q.IsDone() and q.NbPoints() > 1:
            out.append(np.array([[q.Value(i).X(), q.Value(i).Y(), q.Value(i).Z()] for i in range(1, q.NbPoints() + 1)]))
        e.Next()
    return out


def preview(disc_new, path):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager as fm
    fm.fontManager.addfont('/mnt/c/Windows/Fonts/msyh.ttc')
    plt.rcParams['font.family'] = fm.FontProperties(fname='/mnt/c/Windows/Fonts/msyh.ttc').get_name()
    COL = dict(clamp='#e69138', cap_clamp='#b45f06', pcb='#38761d', mos='#222222', cap='#1155cc', sink2='#999999', screw='#cc0000', nut='#990000',
               disc='#7f7f7f', flange_disc='#8e7cc3', mounting_flange='#b4a7d6', ring='#c9a227', xt='#d4b106', seat='#76a5af')
    def draw(ax, sh, pnt, nrm, ij, col, lw=1.2, ls='-'):
        for L in section_lines(sh, pnt, nrm):
            ax.plot(L[:, ij[0]], L[:, ij[1]], color=col, lw=lw, ls=ls)
    fig = plt.figure(figsize=(18, 13))
    YC_SEC = (CAP_Y0 + CAP_Y1) / 2
    HOLE_Y = C.MC_HOLES[0][1] if C.MC_HOLES else (MOS_Y_LEAD + MOS_Y_TIP) / 2
    if C.CC_HOLES: YC_SEC = C.CC_HOLES[0][1]
    # 俯视: Z=2 截面 (压块/卡件, PCB, MOS, 电容, 螺丝) + Z=6 压块截面 (虚) + 底盘 Z=−1 截面 (孔/槽)
    ax = fig.add_subplot(1, 2, 1)
    draw(ax, disc_new, (0, 0, -1), (0, 0, 1), (0, 1), COL['disc'], 0.7)
    draw(ax, B.ring, (0, 0, 2), (0, 0, 1), (0, 1), COL['ring'])
    draw(ax, B.xt_env, (0, 0, 2), (0, 0, 1), (0, 1), COL['xt'])
    draw(ax, B.seat, (0, 0, 2), (0, 0, 1), (0, 1), COL['seat'], 0.8)
    for k in ('pcb', 'mos', 'cap'): draw(ax, PARTS[k], (0, 0, 2.4 if k != 'cap' else 3.5), (0, 0, 1), (0, 1), COL[k], 1.6)
    for k in ('clamp', 'cap_clamp'):
        if k in PARTS: draw(ax, PARTS[k], (0, 0, 2), (0, 0, 1), (0, 1), COL[k], 1.8)
    if C.HAS_MC: draw(ax, clamp, (0, 0, 6), (0, 0, 1), (0, 1), COL['clamp'], 1.0, '--')
    for nt in nuts: draw(ax, nt, (0, 0, 3.5), (0, 0, 1), (0, 1), COL['nut'], 1.0)
    import numpy as np
    t = np.linspace(-math.pi / 2, math.pi / 2, 200)
    ax.plot(82.5 * np.cos(t), 82.5 * np.sin(t), color=COL['flange_disc'], ls=':', lw=1.2, label='定子盘外缘 r82.5 (底 Z9.5)')
    ax.plot(SINK_X0 + np.array([0, SINK_LX, SINK_LX, 0, 0]), SINK_Y0 + np.array([0, 0, SINK_LY, SINK_LY, 0]), color=COL['sink2'], lw=2, label='散热片 20×40 (转 90°, Z−6..0)')
    for i, (x, y) in enumerate(COIL_DRV_HOLES): ax.text(x + 1, y + 4.6, f'M3 #{i}', fontsize=9, color=COL['screw'])
    for x, y in GRID_REMOVE: ax.plot(x, y, 'x', color='r', ms=10, mew=2); ax.text(x + 1.5, y - 2.5, '取消 M6', fontsize=8, color='r')
    for x0, y0, x1, y1, zb in BCAP_PITS: ax.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], color='m', lw=1.2, ls='--')
    ax.plot([], [], '--', color='m', label=f'背面电容坑 (底 Z{BCAP_PITS[0][4]:g})' if BCAP_PITS else '无电容坑')
    ax.plot([XB, XB], [MOS_Y_LEAD - 3, MOS_Y_TIP + 8], 'k-.', lw=0.6); ax.text(XB + 0.5, MOS_Y_TIP + 8, 'A-A', fontsize=9)
    ax.plot([XPC] * 2, [CAP_Y0 - 6, SINK_Y1 + 4], color='#2e86c1', ls=':', lw=1.0, label=f'板中心线 x{XPC:g} (散热片 / MOS 压块 / 电容卡件 对称轴)')
    ax.plot([CAP_X, CAP_X], [CAP_Y0 - 3, Y_PCB1], 'k-.', lw=0.6); ax.text(CAP_X + 0.5, CAP_Y0 - 3, 'D-D', fontsize=9)
    ax.plot([XB - 22, XB + 22], [HOLE_Y, HOLE_Y], 'k-.', lw=0.6); ax.text(XB + 22.5, HOLE_Y, 'B-B', fontsize=9)
    ax.plot([XB - 22, XB + 22], [YC_SEC] * 2, 'k-.', lw=0.6); ax.text(XB + 22.5, YC_SEC, 'C-C', fontsize=9)
    ax.set_xlim(28, 100); ax.set_ylim(-58, 40); ax.set_aspect('equal'); ax.grid(alpha=.25); ax.legend(loc='lower right', fontsize=8)
    ax.set_title(f'俯视 (+Y 上): 实线 Z2 截面 / 橙虚线 = MOS 压块 Z6 截面 / 灰 = 底盘 Z−1 截面\n'
                 f'MOS x {XB:g} → 板中心 x {XPC:.2f} → 电容轴 x {CAP_X:.2f}; MOS 尖 y{Y_TIP:g} → 电容远端 y{CAP_Y0:g} = {Y_TIP - CAP_Y0:g}', fontsize=10)
    secs = [('A-A (x=%.1f, 沿 MOS 中心线) / D-D 同理' % XB, (XB, 0, 0), (1, 0, 0), (1, 2), (CAP_Y0 - 4, MOS_Y_TIP + 8)),
            ('B-B (y=%.1f, MOS 压块 2×M3)' % HOLE_Y, (0, HOLE_Y, 0), (0, 1, 0), (0, 2), (30, 90)),
            ('C-C (y=%.1f, 电容中点 / 卡件)' % YC_SEC, (0, YC_SEC, 0), (0, 1, 0), (0, 2), (30, 90))]
    for k, (ttl, p, n, ij, xl) in enumerate(secs):
        ax = fig.add_subplot(3, 2, 2 * k + 2)
        draw(ax, disc_new, p, n, ij, COL['disc'], 0.8)
        for nm in ('flange_disc', 'mounting_flange', 'ring', 'seat'): draw(ax, getattr(B, nm), p, n, ij, COL[nm], 0.9)
        draw(ax, B.xt_env, p, n, ij, COL['xt'], 0.9)
        for nm in ('sink2', 'mos', 'pcb', 'cap', 'clamp', 'cap_clamp'):
            if nm in PARTS: draw(ax, PARTS[nm], p, n, ij, COL[nm], 1.5)
        for s_ in screws: draw(ax, s_, p, n, ij, COL['screw'], 1.0)
        for s_ in nuts: draw(ax, s_, p, n, ij, COL['nut'], 1.0)
        for z, lab in ((STATOR_Z0, f'定子盘底 Z{STATOR_Z0:g}'), *([(bbox(clamp)[5], f'MOS 压块顶 {bbox(clamp)[5]:g}')] if C.HAS_MC else []), *([(bbox(cap_clamp)[5], f'电容卡件顶 {bbox(cap_clamp)[5]:g}')] if C.HAS_CC else []), (CAP_ZA + CAP_D / 2, f'电容顶 {CAP_ZA + CAP_D / 2:g}'),
                       (SCREW_TIP, f'螺尖 {SCREW_TIP:g}'), (MOS_T, f'MOS 顶 {MOS_T:g}'), *([(C.MC_NUT_Z0, f'螺母底 {C.MC_NUT_Z0:g}')] if C.HAS_MC else []),
                       (FRONT_Z, f'正面最高件顶 {FRONT_Z:g}'), (PCB_Z1, f'PCB {PCB_Z0:g}–{PCB_Z1:g} (挂 MOS 脚, 不压)'), (0, 'Z0 底盘顶'), (-B.DISC_T, f'底盘底 −{B.DISC_T:g}')):
            ax.axhline(z, color='#bbbbbb', lw=0.5, ls='--')
            if k == 0 or lab.startswith(('定子', '螺', '电容', '耳', 'MOS 压')): ax.text(xl[1] + 0.5, z, lab, fontsize=7, va='center')
        ax.set_xlim(*xl); ax.set_ylim(-8, 12); ax.set_aspect('equal'); ax.grid(alpha=.2); ax.set_title(ttl, fontsize=10)
    fig.tight_layout(); fig.savefig(path, dpi=110); plt.close(fig)


if __name__ == '__main__':
    print(f'build_v1_2 导入 {time.time() - T0:.0f}s', flush=True)
    print('B.FL_Z0', B.FL_Z0, 'mounting_flange bbox', [round(v, 2) for v in bbox(B.mounting_flange)], 'xt_env', [round(v, 2) for v in bbox(B.xt_env)])
    for n, s in PARTS.items(): assert BRepCheck_Analyzer(s).IsValid(), n
    rows, hole_rows, disc_new = checks()
    print('\n== 干涉 (共用体积 mm³ / 最小距离 mm; 预期接触 = 名义零间隙压紧/啮合) ==')
    bad = 0
    for a, b, d, v, exp in rows:
        flag = '' if v < 1e-3 else ('  (预期)' if exp else '  ← 干涉!')
        bad += (v >= 1e-3 and not exp)
        if d < 3 or v > 1e-3: print(f'{a:6s} ↔ {b:16s} d={d:6.2f}  V={v:8.3f}{flag}')
    print('\n== 底盘新切口 ↔ 现有孔/槽 (要求 ≥1) ==')
    for n, d in hole_rows:
        lim = 0.5 if n.count('背面电容坑') == 2 else 1.0
        print(f'{n:22s} {d:6.2f}{"" if d >= lim - 1e-6 else f"  ← <{lim}!"}'); bad += d < lim - 1e-6
    print(f'\n高度链: 散热片 Z{-SINK_H:g}..0 / MOS 0..{MOS_T} (引脚中心 {MOS_LEAD_Z}) / PCB {PCB_Z0}..{PCB_Z1} (背面件 {BACK_Z0}, 正面件 ..{FRONT_Z}; 不罩不压)'
          f' / 电容 {-CAP_GROOVE}..{CAP_ZC + CAP_D / 2} (轴 Z{CAP_ZC}, 槽深 {CAP_GROOVE}) / 定子盘底 {STATOR_Z0}, Z_LIMIT {Z_LIMIT}')
    for k in ('MC', 'CC'):
        r = getattr(C, f'{k}_RES')
        print(k, '有' if r else f'无 ({C.MERGE_ERR or "文件不存在"})', '孔', getattr(C, f'{k}_HOLES'), '螺母底', getattr(C, f'{k}_NUT_Z0'), 'M3×', getattr(C, f'{k}_SCREW_L'),
              '校核', {a: (round(b, 3) if isinstance(b, float) else b) for a, b in (r.get('checks') or {}).items()} if isinstance(r, dict) else '')
    print('板中心 XPC', XPC, 'MOS XB', XB, '; 散热片 x', SINK_X0, SINK_X1, 'y', SINK_Y0, SINK_Y1, '(MOS 背板 x', XB - MOS_W / 2, XB + MOS_W / 2, ')',
          '; MOS y', MOS_Y_LEAD, '..', MOS_Y_TIP, '; 电容 x', CAP_CX - CAP_D / 2, CAP_CX + CAP_D / 2, 'y', CAP_Y0, CAP_Y1, '引线', CAP_LEAD, '; 链长', MOS_Y_TIP - CAP_Y0)
    print('背面电容坑 (x0,y0,x1,y1,底Z):', BCAP_PITS)
    for k in [k for k in ('clamp', 'cap_clamp') if k in PARTS]: print(k, 'bbox', [round(v, 2) for v in bbox(PARTS[k])], '体积', round(vol(PARTS[k]), 1))
    MD = B.V12 / 'models' / 'mos_clamp_v1_2'; MD.mkdir(parents=True, exist_ok=True)   # 两件 STEP/STL 由 build_v1_2.py 出
    asm = ([('mos_clamp', clamp, '#e69138')] if C.HAS_MC else []) + ([('cap_clamp', cap_clamp, '#b45f06')] if C.HAS_CC else []) + [('coil_drv_pcb', pcb, '#38761d'), ('coil_drv_mos', mos, '#222222'), ('coil_drv_cap', cap, '#1155cc'),
           ('coil_drv_sink', sink2, '#999999')] + [(f'M3_screw_{i}', s, '#cc0000') for i, s in enumerate(screws)] + [(f'M3_insert_{i}', s, '#990000') for i, s in enumerate(nuts)]
    B.write_doc([(n, s, c, None, False) for n, s, c in asm], MD / 'coil_drv_asm_v1_2.step', 'coil_drv_asm_v1_2')
    preview(disc_new, B.OUT / 'coil_drv_preview.png')
    print(f'\n校核 {"通过" if not bad else f"有 {bad} 项不过"}; 用时 {time.time() - T0:.0f}s')
