import numpy as np, zipfile, io
from build_v1_2 import *
from mf3_v1_2 import mesh, write3mf
# 板: 去掉 < 1 mm 的小件 (0402 电阻电容等), 只为看效果
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
B=BRep_Builder();C=TopoDS_Compound();B.MakeCompound(C); kept=0
for s in solids(board):
    b=bbox(s)
    if max(b[3]-b[0],b[4]-b[1])>=1.2 or b[5]-b[2]>=1.0: B.Add(C,s); kept+=1
print('board solids kept',kept)
fl=flange_disc; mf=mounting_flange
P_=[('打印底盘 Φ220×4.5',disc_print,'#8A8F98',0.05),('玻纤板 FR4 Φ220×3',fr4,'#C8D86A',0.05),('线圈环 (托法兰盘, 单独件)',ring,'#E0A030',0.05),('电机 Φ55×21.5 (占位)',motor,'#333333',0.05),
    ('电机控制板',C,'#2E7D32',0.08),('散热片 40×20×6',heatsink,'#C0392B',0.05),
    *([('MOS 压块 mos_clamp_v1_2',CD.clamp,'#E69138',0.05)] if CD.HAS_MC else []),*([('电容卡件 cap_clamp_v1_2',CD.cap_clamp,'#B45F06',0.05)] if CD.HAS_CC else []),('线圈驱动板 (元件级, 按照片估)',CD.pcb,'#38761D',0.05),('线圈驱动 MOS TO-220',CD.mos,'#222222',0.05),
    ('线圈驱动 电解电容 Φ10×20',CD.cap,'#1155CC',0.05),('线圈驱动 散热片 40×20×6 (转 90°)',CD.sink2,'#C0392B',0.05),
    ('按键支架 key_bracket_v1_2',key_bracket,'#F1C232',0.03),('按键板 (简模)',key_board,'#2E7D32',0.03)]
EXT=[('法兰盘 flange_disc_v1_2 (底减3)',fl,'#D9A441',0.05),('安装法兰 mounting_flange_v1_2 (外裙短3)',mf,'#B5895A',0.05),
     ('转子毂盘 hub_disc_v1_2 (降10.2)',hub,'#4F86C6',0.05),(f'承载盘 rim_ring Φ{RIM_D:g} (降10.2)',rim,'#6AA84F',0.05)]
A = V12 / 'assembly_v1_2'
# 11-16 新转子布局: 灯板支撑 5 件 + 转子罩两半 + 无线模块托盘 (各零件脚本 import 只建几何, 不写文件)
import io as _io, contextlib as _cl
with _cl.redirect_stdout(_io.StringIO()):
    import led_support_v1_2 as LS, rotor_shroud_v1_2 as RS, wireless_holder_v1_2 as WH, motor_wire_v1_2 as MW
MW_SEAT, MW_CLAMP = MW.mr30_seat(), MW.wire_clamp()   # 11-16 晚: 底盘 MR30 座 + 电机线束线夹 (装配坐标; 打印件 STL/STEP 由 motor_wire_v1_2.py 写 models/)
P_ += [('MR30 座 mr30_seat_v1_2',MW_SEAT,'#F1C232',0.03),('电机线束线夹 motor_wire_clamp_v1_2',MW_CLAMP,'#E69138',0.03)]
ROT=[('灯板支撑 +x led_post_a_v1_2',LS.post_a,'#F1C232',0.03),('灯板支撑 −x led_post_b_v1_2',LS.post_b,'#E69138',0.03),
     ('灯板夹条 led_bar_v1_2',LS.bar_s,'#8E7CC3',0.03),('灯板顶部件 led_top_v1_2',LS.top,'#6FA8DC',0.03),('顶部配平梳齿 led_comb_v1_2',LS.comb_s,'#3D85C6',0.03),
     ('转子罩 A rotor_shroud_a_v1_2',RS.shr_a,'#6FA8DC',0.05),('转子罩 B rotor_shroud_b_v1_2 (与 A 不同件)',RS.shr_b,'#93C47D',0.05),
     ('转子罩顶盖 +y rotor_lid_v1_2',RS.lid_a,'#CFE2F3',0.05),('转子罩顶盖 −y rotor_lid_b_v1_2',RS.lid_b,'#A4C2F4',0.05),
     ('无线模块托盘 wireless_holder_v1_2',WH.H,'#F1C232',0.03)]
# 11-18 整机换成转子盘B (build_v1_2.ROTOR_B): 毂盘+承载盘 → 玻纤板+承载盘单件; 立板 → 屏幕固定件; 罩子 4 件 → 2 片
if ROTOR_B:
    with _cl.redirect_stdout(_io.StringIO()):
        import rotor_shroud_b_v1_2 as RSB
    RB = RSB.RB
    EXT = EXT[:2] + [('玻纤板 fr4_plate_v1_2b Φ165×3 (无铜 FR4, 板厂件)',RB.fr4,'#C9B458',0.05),('承载盘 rim_ring_v1_2b (转子盘B, 并入毂盘)',RB.rim,'#6AA84F',0.05)]
    ROT = [*[(n,sh,c,0.03) for n,sh,c in RB.SCREEN_PARTS],   # 11-21 屏幕支撑件 A ×2 + B ×2 (原 屏幕玻纤板 ×4 + 侧立件 ×2)
           *[r for r in ROT if not r[0].startswith(('灯板支撑','转子罩'))],
           *[(f'{t} {n}',sh,c,0.05) for n,t,sh,c in RSB.PARTS4]]
GTOP=[('玻璃上 glass_top_v1_2',glass_top,'#7FB3D5',0.05),('圆环玻璃 OD180×ID20×10 (外购)',glass_disc,'#AED6F1',0.1),('中心堵头 glass_top_hub_v1_2',glass_top_hub,'#2E86C1',0.02),('玻璃压圈 glass_top_clamp_v1_2',glass_top_clamp,'#1B4F72',0.05),('硅胶垫 上 OD180×ID171×1 (外购, 压后 0.8)',glass_gasket_top,'#E5E7E9',0.05),('硅胶垫 下 OD180×ID171×1 (外购, 压后 0.8)',glass_gasket_bot,'#E5E7E9',0.05)]
write3mf(f'{A}_底盘+线圈环+电机+控制板.3mf',P_)
write3mf(f'{A}_含法兰+转子盘.3mf',P_+EXT)
write3mf(f'{A}_含法兰+转子盘+玻璃罩定位环.3mf',P_+EXT+[('玻璃下 (下罩+定位环) glass_shroud_v1_2',seat,'#7FB3D5',0.05),('XT60 压块',xt_clamp,'#F1C232',0.05),('XT60 底垫',xt_shim,'#E69138',0.05)])
write3mf(f'{A}_玻璃罩版整机_合并.3mf',P_+EXT+ROT+[('玻璃下 (下罩+定位环) glass_shroud_v1_2',seat,'#7FB3D5',0.05),('玻璃罩 OD200x5 H245',tube,'#D6EAF8',0.1),*GTOP,('XT60 压块',xt_clamp,'#F1C232',0.05),('XT60 底垫',xt_shim,'#E69138',0.05)])
write3mf(f'{A}_玻璃罩版整机_分体外卡环.3mf',P_+EXT+ROT+[('玻璃下-底座 glass_shroud_lower_v1_2',shroud_lo,'#7FB3D5',0.05),('玻璃下-玻璃座 glass_shroud_upper_v1_2',shroud_hi,'#5DADE2',0.05),('外卡环 glass_clamp_ring_v1_2',clamp_ring,'#2E86C1',0.05),('玻璃罩 OD200x5 H245',tube,'#D6EAF8',0.1),*GTOP,('XT60 压块',xt_clamp,'#F1C232',0.05),('XT60 底垫',xt_shim,'#E69138',0.05)])
for n,sh in (('base_disc_v1_2_gf',disc_print),('base_fr4_v1_2',fr4),('coil_ring_v1_2',ring),('flange_disc_v1_2',flange_disc),('mounting_flange_v1_2',mounting_flange),('glass_shroud_v1_2',seat),('glass_shroud_lower_v1_2',shroud_lo),('glass_shroud_upper_v1_2',shroud_hi),('glass_clamp_ring_v1_2',clamp_ring),('glass_top_v1_2',glass_top),('glass_top_hub_v1_2',glass_top_hub),('glass_top_clamp_v1_2',glass_top_clamp),
             ('led_bar_v1_2',LS.bar_s),('led_comb_v1_2',LS.comb_s),*([] if ROTOR_B else [('rotor_shroud_a_v1_2',RS.shr_a),('rotor_shroud_b_v1_2',RS.shr_b),('rotor_lid_v1_2',RS.lid_a),('rotor_lid_b_v1_2',RS.lid_b)]),('wireless_holder_v1_2',WH.H)):
    d = V12 / 'models' / n; d.mkdir(parents=True, exist_ok=True)
    BRepMesh_IncrementalMesh(sh,0.02,False,0.2,True); w=StlAPI_Writer(); w.ASCIIMode=False; w.Write(sh,str(d / f'{n}.stl'))
    if n == 'wireless_holder_v1_2':   # 它的 STEP 由 wireless_holder_v1_2.py 写 (含模块占位/螺丝/铜螺母/引脚, led_support/rotor_shroud 干涉校核要读), 不覆盖
        continue
    write_doc([(n, sh, '#8A8F98', None, False)], d / f'{n}.step', n)
print('ok')
# 11-16 晚: 底盘 / 毂盘 / 承载盘的 out/零件 + out/打印STL 在这里也重写一遍 (build_v1_2.py 只在 __main__ 写, import 时不写), 保证与当前 build 一致;
#   名字同 build_v1_2 NEW 表 (承载盘仍叫 rim_ring_v1_2_D170, 用户 11-16 晚定转子回 Φ170); 姿态同 build POSE: 底盘/毂盘原样, 承载盘翻面; 落床 z=0
from OCP.gp import gp_Trsf, gp_Vec, gp_Ax1, gp_Pnt, gp_Dir
RIM_NAME = 'rim_ring_v1_2_D170'
_fx = gp_Trsf(); _fx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi)
_ROT_OUT = ((('rim_ring_v1_2b', RB.rim, True),) if ROTOR_B else (('hub_disc_v1_2', hub, False), (RIM_NAME, rim, True)))
for n, sh, flip in (('base_disc_D220x5_v1_2_gf', disc_print, False), *_ROT_OUT):   # 11-18 玻纤板方案 (旧一体底盘 base_disc_D220x6 冻结不再写)
    write_doc([(n, sh, '#8A8F98', None, False)], OUT / '零件' / f'{n}.step', n)
    t = xf(sh, _fx) if flip else sh
    _tt = gp_Trsf(); _tt.SetTranslation(gp_Vec(0, 0, -bbox(t)[2])); t = xf(t, _tt)
    BRepMesh_IncrementalMesh(t, 0.02, False, 0.2, True); w = StlAPI_Writer(); w.ASCIIMode = False; w.Write(t, str(OUT / '打印STL' / f'{n}.stl'))
# 承载盘装配坐标 STL (出图用, models/<名>/ 同其它件)  —— 转子盘B 的 models/ 由 rotor_b_v1_2.py 写
_d = V12 / 'models' / RIM_NAME; _d.mkdir(parents=True, exist_ok=True)
BRepMesh_IncrementalMesh(rim, 0.02, False, 0.2, True); w = StlAPI_Writer(); w.ASCIIMode = False; w.Write(rim, str(_d / f'{RIM_NAME}.stl'))
write_doc([(RIM_NAME, rim, '#6AA84F', None, False)], _d / f'{RIM_NAME}.step', RIM_NAME)
import shutil
# 11-18 转子盘B 进整机: out/ 里旧转子 (毂盘/承载盘 D170/立板/罩子 4 件) 的打印 STL 挪进 out/打印STL/作废_转子盘A/ (不删, 防误打)
if ROTOR_B:
    _old = OUT / '打印STL' / '作废_转子盘A'; _old.mkdir(exist_ok=True)
    for _n in ('hub_disc_v1_2', RIM_NAME, 'led_post_a_v1_2', 'led_post_b_v1_2', 'rotor_shroud_a_v1_2', 'rotor_shroud_b_v1_2', 'rotor_lid_v1_2', 'rotor_lid_b_v1_2'):
        for _f in (OUT / '打印STL' / f'{_n}.stl', OUT / '零件' / f'{_n}.step'):
            if _f.exists(): shutil.move(str(_f), str(_old / _f.name)); print('作废挪走', _f.name)
# 作废文件: 中间 T 件 led_mid_t (11-16 晚 取消); 曾试过的 rim_ring_v1_2_D175 (11-16 晚 改回 Φ170)
for f in [OUT / '零件' / 'rim_ring_v1_2_D175.step', OUT / '打印STL' / 'rim_ring_v1_2_D175.stl', V12 / '转子盘' / 'rim_ring_v1_2_D175.step', V12 / '转子盘' / 'rim_ring_v1_2_D175.stl',
          OUT / '打印STL' / 'led_mid_t_v1_2.stl']:
    if f.exists(): f.unlink(); print('删除', f)
for _dd in ('led_mid_t_v1_2', 'rim_ring_v1_2_D175'):
    if (V12 / 'models' / _dd).exists(): shutil.rmtree(V12 / 'models' / _dd); print(f'删除 models/{_dd}/')
# 11-16 晚 用户: 定子盘 2 件 / 转子盘 2 件 各放一个文件夹 (每次导出都覆盖成最新)
_GROUPS = {'定子盘': [('flange_disc_v1_2', V12 / 'models' / 'flange_disc_v1_2'), ('mounting_flange_v1_2', V12 / 'models' / 'mounting_flange_v1_2')],
           '转子盘': [(RIM_NAME, None), ('hub_disc_v1_2', None)]}
if ROTOR_B:   # 转子盘/ 文件夹 (旧转子) 不再覆盖; 转子盘B/ 由 rotor_b / rotor_shroud_b (STL=打印姿态, STEP=装配) 和出图同步
    _GROUPS.pop('转子盘')
    gd = V12 / '转子盘B'; gd.mkdir(exist_ok=True)
    for n in ('rim_ring_v1_2b', 'screen_sup_a_v1_2b', 'screen_sup_b_v1_2b', 'rotor_shroud_b_a_v1_2b', 'rotor_shroud_b_b_v1_2b', 'rotor_shroud_lid_a_v1_2b', 'rotor_shroud_lid_b_v1_2b'):
        d = V12 / 'models' / n
        for f, dst in ((d / f'{n}_print.stl', gd / f'{n}.stl'), (d / f'{n}.step', gd / f'{n}.step'), (d / f'{n}_drawing.pdf', gd / f'{n}_drawing.pdf')):
            if f.exists():
                try: shutil.copy2(f, dst)
                except PermissionError:                     # 11-19 21:30: .NEW 也开着 → 依次 NEW2/NEW3
                    for _s in ('NEW', 'NEW2', 'NEW3'):
                        try: shutil.copy2(f, dst.with_name(f'{dst.stem}.{_s}{dst.suffix}')); print('  被占用, 另存', dst.stem + '.' + _s); break
                        except PermissionError: continue
    if (V12 / 'models' / 'rim_ring_v1_2b' / 'rotor_b_asm.step').exists(): shutil.copy2(V12 / 'models' / 'rim_ring_v1_2b' / 'rotor_b_asm.step', gd / 'rotor_b_asm.step')
for g, items in _GROUPS.items():
    gd = V12 / g; gd.mkdir(exist_ok=True)
    for n, d in items:
        srcs = ([d / f'{n}.step', d / f'{n}.stl', d / f'{n}_drawing.pdf'] if d else           # 定子盘: models/ 下 (export 本脚本写)
                [OUT / '零件' / f'{n}.step', OUT / '打印STL' / f'{n}.stl', V12 / 'models' / n / f'{n}_drawing.pdf'])   # 转子盘: out/零件 + out/打印STL (打印姿态) + 图纸 (有就拷)
        for f in srcs:
            if not f.exists(): continue
            try:
                shutil.copy2(f, gd / f.name)
            except PermissionError:                         # 11-16 晚: 用户在阅读器里开着 → 另存 .NEW, 不中断
                shutil.copy2(f, gd / f'{f.stem}.NEW{f.suffix}'); print('  被占用, 另存', gd / f'{f.stem}.NEW{f.suffix}')
print('定子盘 / 转子盘 文件夹已更新')
