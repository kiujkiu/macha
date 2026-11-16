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
P_=[('底盘 Φ220×6 (平板)',disc,'#8A8F98',0.05),('线圈环 (托法兰盘, 单独件)',ring,'#E0A030',0.05),('电机 Φ55×21.5 (占位)',motor,'#333333',0.05),
    ('电机控制板',C,'#2E7D32',0.08),('散热片 40×20×6',heatsink,'#C0392B',0.05),
    *([('MOS 压块 mos_clamp_v1_2',CD.clamp,'#E69138',0.05)] if CD.HAS_MC else []),*([('电容卡件 cap_clamp_v1_2',CD.cap_clamp,'#B45F06',0.05)] if CD.HAS_CC else []),('线圈驱动板 (元件级, 按照片估)',CD.pcb,'#38761D',0.05),('线圈驱动 MOS TO-220',CD.mos,'#222222',0.05),
    ('线圈驱动 电解电容 Φ10×20',CD.cap,'#1155CC',0.05),('线圈驱动 散热片 40×20×6 (转 90°)',CD.sink2,'#C0392B',0.05),
    ('按键支架 key_bracket_v1_2',key_bracket,'#F1C232',0.03),('按键板 (简模)',key_board,'#2E7D32',0.03)]
EXT=[('法兰盘 flange_disc_v1_2 (底减3)',fl,'#D9A441',0.05),('安装法兰 mounting_flange_v1_2 (外裙短3)',mf,'#B5895A',0.05),
     ('转子毂盘 hub_disc_v1_2 (降10.2)',hub,'#4F86C6',0.05),('承载盘 rim_ring Φ170 (降10.2)',rim,'#6AA84F',0.05)]
A = V12 / 'assembly_v1_2'
# 11-16 新转子布局: 灯板支撑 5 件 + 转子罩两半 + 无线模块托盘 (各零件脚本 import 只建几何, 不写文件)
import io as _io, contextlib as _cl
with _cl.redirect_stdout(_io.StringIO()):
    import led_support_v1_2 as LS, rotor_shroud_v1_2 as RS, wireless_holder_v1_2 as WH
ROT=[('灯板支撑 +x led_post_a_v1_2',LS.post_a,'#F1C232',0.03),('灯板支撑 −x led_post_b_v1_2',LS.post_b,'#E69138',0.03),
     ('灯板门形支撑 led_gate_v1_2',LS.gate_s,'#B45F06',0.03),('灯板顶部件 led_top_v1_2',LS.top,'#6FA8DC',0.03),('顶部配平梳齿 led_comb_v1_2',LS.comb_s,'#3D85C6',0.03),
     ('转子罩 A rotor_shroud_a_v1_2',RS.shr_a,'#6FA8DC',0.05),('转子罩 B rotor_shroud_b_v1_2 (= A 转 180°)',RS.shr_b,'#93C47D',0.05),
     ('无线模块托盘 wireless_holder_v1_2',WH.H,'#F1C232',0.03)]
GTOP=[('玻璃上 glass_top_v1_2',glass_top,'#7FB3D5',0.05),('圆环玻璃 OD180×ID20×10 (外购)',glass_disc,'#AED6F1',0.1),('中心堵头 glass_top_hub_v1_2',glass_top_hub,'#2E86C1',0.02)]
write3mf(f'{A}_底盘+线圈环+电机+控制板.3mf',P_)
write3mf(f'{A}_含法兰+转子盘.3mf',P_+EXT)
write3mf(f'{A}_含法兰+转子盘+玻璃罩定位环.3mf',P_+EXT+[('玻璃下 (下罩+定位环) glass_shroud_v1_2',seat,'#7FB3D5',0.05),('XT60 压块',xt_clamp,'#F1C232',0.05),('XT60 底垫',xt_shim,'#E69138',0.05)])
write3mf(f'{A}_玻璃罩版整机_合并.3mf',P_+EXT+ROT+[('玻璃下 (下罩+定位环) glass_shroud_v1_2',seat,'#7FB3D5',0.05),('玻璃罩 OD200x5 H245',tube,'#D6EAF8',0.1),*GTOP,('XT60 压块',xt_clamp,'#F1C232',0.05),('XT60 底垫',xt_shim,'#E69138',0.05)])
write3mf(f'{A}_玻璃罩版整机_分体外卡环.3mf',P_+EXT+ROT+[('玻璃下-底座 glass_shroud_lower_v1_2',shroud_lo,'#7FB3D5',0.05),('玻璃下-玻璃座 glass_shroud_upper_v1_2',shroud_hi,'#5DADE2',0.05),('外卡环 glass_clamp_ring_v1_2',clamp_ring,'#2E86C1',0.05),('玻璃罩 OD200x5 H245',tube,'#D6EAF8',0.1),*GTOP,('XT60 压块',xt_clamp,'#F1C232',0.05),('XT60 底垫',xt_shim,'#E69138',0.05)])
for n,sh in (('base_disc_v1_2',disc),('coil_ring_v1_2',ring),('flange_disc_v1_2',flange_disc),('mounting_flange_v1_2',mounting_flange),('glass_shroud_v1_2',seat),('glass_shroud_lower_v1_2',shroud_lo),('glass_shroud_upper_v1_2',shroud_hi),('glass_clamp_ring_v1_2',clamp_ring),('glass_top_v1_2',glass_top),('glass_top_hub_v1_2',glass_top_hub),
             ('led_gate_v1_2',LS.gate_s),('led_comb_v1_2',LS.comb_s),('rotor_shroud_a_v1_2',RS.shr_a),('rotor_shroud_b_v1_2',RS.shr_b),('wireless_holder_v1_2',WH.H)):
    d = V12 / 'models' / n; d.mkdir(parents=True, exist_ok=True)
    BRepMesh_IncrementalMesh(sh,0.02,False,0.2,True); w=StlAPI_Writer(); w.ASCIIMode=False; w.Write(sh,str(d / f'{n}.stl'))
    if n == 'wireless_holder_v1_2':   # 它的 STEP 由 wireless_holder_v1_2.py 写 (含模块占位/螺丝/铜螺母/引脚, led_support/rotor_shroud 干涉校核要读), 不覆盖
        continue
    write_doc([(n, sh, '#8A8F98', None, False)], d / f'{n}.step', n)
print('ok')
