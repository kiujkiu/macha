import time,numpy as np
T0=time.time()
from build_v1_2 import *
from scipy.spatial import cKDTree
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
def pts(shape,dens=8.0,defl=0.05):
    BRepMesh_IncrementalMesh(shape,defl,False,0.2,True)
    out=[]; e=TopExp_Explorer(shape,TopAbs_FACE); rng=np.random.default_rng(0)
    while e.More():
        f=TopoDS.Face(e.Current()); L=TopLoc_Location(); tr=BRep_Tool.Triangulation_s(f,L)
        if tr is not None:
            t=L.Transformation()
            V=np.array([[p.X(),p.Y(),p.Z()] for p in (tr.Node(i).Transformed(t) for i in range(1,tr.NbNodes()+1))])
            T=np.array([[tr.Triangle(i).Value(j) for j in (1,2,3)] for i in range(1,tr.NbTriangles()+1)])-1
            out.append(V); A=V[T]; ar=0.5*np.linalg.norm(np.cross(A[:,1]-A[:,0],A[:,2]-A[:,0]),axis=1)
            n=rng.poisson(ar*dens)
            if n.sum():
                idx=np.repeat(np.arange(len(T)),n); u=rng.random((len(idx),2)); m=u.sum(1)>1; u[m]=1-u[m]
                a=A[idx]; out.append(a[:,0]+u[:,:1]*(a[:,1]-a[:,0])+u[:,1:]*(a[:,2]-a[:,0]))
        e.Next()
    return np.vstack(out)
fl=flange_disc; mf=mounting_flange
S={**({'cd_clamp':CD.clamp} if CD.HAS_MC else {}),**({'cd_capclamp':CD.cap_clamp} if CD.HAS_CC else {}),'cd_pcb':CD.pcb,'cd_mos':CD.mos,'cd_cap':CD.cap,'cd_sink2':CD.sink2,'board':board,'heatsink':heatsink,'disc':disc,'ring':ring,'flange_disc':fl,'mounting_flange':mf,'motor':motor,'hub':hub,'rim':rim,'seat':seat,'tube':tube,'xt60':xt_env,'shroud_split':shroud_split,'shroud_lo':shroud_lo,'shroud_hi':shroud_hi,'clamp_ring':clamp_ring,'key_bracket':key_bracket,'key_board':key_board,'glass_top':glass_top,'glass_disc':glass_disc,'glass_top_hub':glass_top_hub}
for i,p in enumerate(posts): S[f'post{i}']=p
# 11-16 新转子布局: 灯板支撑 5 件 + Φ8 轴/688, 转子罩两半, 无线托盘 + 模块占位, 底板 r4b (交付 STEP) + 两块灯板
# 11-16 晚 偏心 + 耳朵脚: 中间 T 件 led_mid_t 取消; 顶盖两片不同件 (rotor_lid_v1_2 +y / rotor_lid_b_v1_2 −y); 底盘加 MR30 座 + 电机线夹 (motor_wire_v1_2)
import io as _io, contextlib as _cl
with _cl.redirect_stdout(_io.StringIO()):
    import led_support_v1_2 as LS, rotor_shroud_v1_2 as RS, wireless_holder_v1_2 as WH, motor_wire_v1_2 as MW, fpc_v1_2 as F
S.update({'led_post_a':LS.post_a,'led_post_b':LS.post_b,'led_bar':LS.bar_s,'led_top':LS.top,'led_comb':LS.comb_s,'rod':LS.rod,'brg688':LS.brg,
          'led_a':LS.led_a,'led_b':LS.led_b,'bb_r2':LS.bb_step,'rotor_shroud_a':RS.shr_a,'rotor_shroud_b':RS.shr_b,'rotor_lid_a':RS.lid_a,'rotor_lid_b':RS.lid_b,'bridge_a':F.bridge_a,'bridge_b':F.bridge_b,'fpc_a':F.fpc_a,'fpc_b':F.fpc_b,'seat_j5':F.seat_j5,'seat_j6':F.seat_j6,
          'wireless_holder':WH.H,'wireless_module':WH.module,'mr30_seat':MW.mr30_seat(),'motor_wire_clamp':MW.wire_clamp(),'ant_a':LS.ant_a,'ant_b':LS.ant_b})
for i,(x,y) in enumerate(SH_M6): S[f'seat_nut{i}']=cyl(x,y,SH_NUT_D,NUT_Z0,NUT_Z0+3.7)   # 11-12 夜: M3 法兰螺母实高 3.7 (build 里 seat_nuts 仍按 2.4)
P={k:pts(v) for k,v in S.items()}; print('sampled',f'{time.time()-T0:.0f}s',flush=True)
K={k:cKDTree(v) for k,v in P.items()}
def md(a,b): d,_=K[b].query(P[a],k=1,distance_upper_bound=20); return float(d.min())
_CC=('cd_capclamp',) if CD.HAS_CC else ()
_MC=('cd_clamp',) if CD.HAS_MC else ()
PAIRS=[('board',x) for x in ('ring','flange_disc','mounting_flange','motor','seat','tube','post0','post1','post2','post3')]+\
 [('ring',x) for x in ('disc','flange_disc','mounting_flange','motor','seat')]+[('motor',x) for x in ('disc','hub','flange_disc','mounting_flange')]+\
 [('hub','mounting_flange'),('hub','flange_disc'),('rim','mounting_flange'),('seat','mounting_flange'),('seat','flange_disc'),('seat','rim'),('seat','hub')]+\
 [(f'seat_nut{i}',x) for i in range(4) for x in ('mounting_flange','flange_disc')]+[('heatsink','disc')]+[('clamp_ring','shroud_split'),('shroud_lo','shroud_hi'),('clamp_ring','shroud_hi'),('shroud_hi','tube'),('shroud_hi','rim'),('shroud_hi','hub'),('clamp_ring','tube'),('shroud_split','tube')]+[('xt60',x) for x in ('board','seat','mounting_flange','flange_disc','disc','ring')]+\
 [(c,x) for c in _MC+_CC+('cd_cap','cd_sink2','cd_pcb','cd_mos') for x in ('flange_disc','mounting_flange','ring','board','seat','xt60','shroud_split')]+[('cd_sink2','disc'),('cd_cap','disc'),('cd_pcb','disc')]+[(c,'disc') for c in _MC+_CC]+\
 [(c,x) for c in _MC for x in ('cd_pcb','cd_mos','cd_sink2','cd_cap')]+[(c,x) for c in _CC for x in ('cd_cap','cd_pcb','cd_sink2')+_MC]+[('cd_cap','cd_pcb'),('cd_mos','cd_sink2')]+\
 [('key_bracket',x) for x in ('disc','seat','shroud_split','key_board','ring','flange_disc','mounting_flange','rim')]+[('key_board',x) for x in ('disc','seat','shroud_split','ring','flange_disc','mounting_flange','rim')]+\
 [('glass_top',x) for x in ('tube','glass_disc','glass_top_hub')]+[('glass_top_hub','glass_disc')]+\
 [(a,x) for a in ('led_post_a','led_post_b') for x in ('rim','hub','led_a','led_b','bb_r2','rotor_shroud_a','rotor_shroud_b','rotor_lid_a','rotor_lid_b','wireless_holder','wireless_module','shroud_lo','shroud_hi','tube','bridge_a','bridge_b')]+[('led_bar',x) for x in ('led_a','led_b','led_post_a','led_post_b','bridge_a','bridge_b','rim')]+\
 [('led_top',x) for x in ('led_a','led_b','led_comb','rod','glass_top_hub','glass_top')]+[('led_comb',x) for x in ('led_a','led_b','rod','glass_top_hub','glass_top')]+\
 [('rod',x) for x in ('glass_top_hub','glass_top','brg688')]+[('brg688','glass_top_hub')]+\
 [(a,x) for a in ('rotor_shroud_a','rotor_shroud_b') for x in ('rim','hub','shroud_lo','shroud_hi','tube','led_a','led_b','bb_r2','wireless_holder','wireless_module')]+[('rotor_shroud_a','rotor_shroud_b')]+\
 [('wireless_holder',x) for x in ('rim','hub','wireless_module','led_a','led_b','bb_r2','shroud_lo','shroud_hi')]+[('wireless_module',x) for x in ('rim','led_a','led_b','bb_r2')]+\
 [('led_a',x) for x in ('led_b','rim','hub','bb_r2')]+[('led_b',x) for x in ('rim','hub','bb_r2')]+[('bb_r2',x) for x in ('rim','hub','shroud_hi')]+\
 [(a,x) for a in ('rotor_lid_a','rotor_lid_b') for x in ('rotor_shroud_a','rotor_shroud_b','led_a','led_b','bridge_a','bridge_b','ant_a','ant_b','led_bar','wireless_module','shroud_hi','tube')]+[('rotor_lid_a','rotor_lid_b')]+\
 [(a,x) for a in ('fpc_a','fpc_b','seat_j5','seat_j6') for x in ('led_a','led_b','bb_r2','hub','rim','led_bar','rotor_lid_a','rotor_lid_b','bridge_a','bridge_b','led_post_a','led_post_b')]+[('fpc_a','fpc_b')]+\
 [(a,x) for a in ('rotor_shroud_a','rotor_shroud_b') for x in ('ant_a','ant_b','led_post_a','led_post_b')]+\
 [(a,x) for a in ('mr30_seat','motor_wire_clamp') for x in ('disc','ring','flange_disc','mounting_flange','motor','board','seat','shroud_split','xt60','cd_pcb','cd_cap','cd_mos','cd_sink2','key_bracket','heatsink')+_MC+_CC]+[('mr30_seat','motor_wire_clamp')]   # 11-13 按键板+支架 / 玻璃上; 11-16 新件 (led_top × rod = Φ8 轴压进 Φ7.85 孔, 过盈预期)
for a,b in PAIRS:
    d=md(a,b); flag=''
    if d<0.3:
        v=vol(op(BRepAlgoAPI_Common,S[a],S[b])); flag=f'  相交体积 {v:.3f} mm3'
    if a=='led_top' and b=='rod' and flag: flag+='  (预期: Φ8 轴压入 Φ7.85 孔过盈)'
    if a=='led_a' and b=='led_b' and flag: flag+='  (待查: 灯板 V0.2.0 STEP 上角 F 面 2 件 6×4 伸出 F 面 6.09 > 间隙 4.6, 各穿进对面板 1.47; 非结构件)'
    print(f'{a:14s} ↔ {b:16s} 最小距离 ≈ {d:6.2f}{flag}',flush=True)
print(LOG['disc_holes']['grid'],'网格孔;', 'ring',LOG['ring'],flush=True)
print(f'done {time.time()-T0:.0f}s')
