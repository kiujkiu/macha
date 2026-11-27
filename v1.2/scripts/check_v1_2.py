import time,numpy as np
T0=time.time()
from build_v1_2 import *
import io as _io, contextlib as _cl
from scipy.spatial import cKDTree
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
import geocache as GC, pickle as _pk, os as _os
# 11-20: 采样点 / 配对结果按形体键缓存 (geocache), 只重算变了的件; CHECK_CACHE=0 全部重算
_CK = GC.ON and _os.environ.get('CHECK_CACHE','1')!='0'
_PD = GC.DIR/'check'; _PD.mkdir(parents=True, exist_ok=True) if _CK else None
_PAIRF = _PD/'pairs.pkl'
try: _PAIRC = _pk.load(open(_PAIRF,'rb')) if _CK and _PAIRF.exists() else {}
except Exception: _PAIRC = {}
_ST = dict(pts_hit=0, pts_new=0, pair_hit=0, pair_new=0, pair_far=0)
def pts(shape,dens=8.0,defl=0.05):
    if not _CK: return _pts(shape,dens,defl)
    f = _PD/f'pts_{GC._h(GC.key(shape),dens,defl)}.npy'
    if f.exists():
        try: _ST['pts_hit']+=1; return np.load(f)
        except Exception: pass
    a = _pts(shape,dens,defl); _ST['pts_new']+=1
    tmp = f.with_suffix(f'.{_os.getpid()}.tmp.npy'); np.save(tmp, a); _os.replace(tmp, f); return a
def _pts(shape,dens=8.0,defl=0.05):
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
from build_v1_2 import glass_top_lugs as B_lugs
S={**({'cd_clamp':CD.clamp} if CD.HAS_MC else {}),**({'cd_capclamp':CD.cap_clamp} if CD.HAS_CC else {}),'cd_pcb':CD.pcb,'cd_mos':CD.mos,'cd_cap':CD.cap,'cd_sink2':CD.sink2,'board':board,'heatsink':heatsink,'disc':disc,'ring':ring,'flange_disc':fl,'mounting_flange':mf,'motor':motor,'hub':hub,'rim':rim,'seat':seat,'tube':tube,'xt60':xt_env,'shroud_split':shroud_split,'shroud_lo':shroud_lo,'shroud_hi':shroud_hi,'clamp_ring':clamp_ring,'key_bracket':key_bracket,'key_board':key_board,**{f'gt_lug{i}':s_ for i,s_ in enumerate(B_lugs)},'glass_top':glass_top,'glass_disc':glass_disc,'glass_top_hub':glass_top_hub,'glass_top_clamp':glass_top_clamp}
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
# 11-18 整机换成转子盘B (ROTOR_B): 旧件名 → 新件名, 配对表自动改写; 再补转子盘B 自己的配对
RMAP={}
if ROTOR_B:
    with _cl.redirect_stdout(_io.StringIO()):
        import rotor_shroud_b_v1_2 as RSB
    RB=RSB.RB
    for k in ('hub','rim','led_post_a','led_post_b','rotor_shroud_a','rotor_shroud_b','rotor_lid_a','rotor_lid_b'): S.pop(k)
    S.update({'fr4':RB.fr4,'rim_b':RB.rim,**{k:sh for k,(_,sh,_) in zip(RB.SCREEN_KEYS,RB.SCREEN_PARTS)},'shroud_b_a':RSB.shr_a,'shroud_b_b':RSB.shr_b,'lid_b_a':RSB.lid_a,'lid_b_b':RSB.lid_b,'coil':RB.coil})
    if RSB.shr_b is None: S.pop('shroud_b_b')   # 11-27 侧环整圈一件   # 11-21 屏幕支撑件 A ×2 (0/180°) + B ×2 (90/270°)
    RMAP={'hub':'fr4','rim':'rim_b','led_post_a':'scr_sup_0','led_post_b':'scr_sup_180','rotor_shroud_a':'shroud_b_a','rotor_shroud_b':'shroud_b_b' if RSB.shr_b is not None else 'shroud_b_a','rotor_lid_a':'lid_b_a','rotor_lid_b':'lid_b_b'}
_KEY={k:GC.key(v) if GC.ON else k for k,v in S.items()}; _BB={k:bbox(v) for k,v in S.items()}
_P={}; _K={}
def _p(k):
    if k not in _P: _P[k]=pts(S[k])
    return _P[k]
def md(a,b):
    A,Bb=_BB[a],_BB[b]; gap=max(0.0,A[0]-Bb[3],Bb[0]-A[3],A[1]-Bb[4],Bb[1]-A[4],A[2]-Bb[5],Bb[2]-A[5])
    if gap>20: return float('inf')                   # 包围盒相距 > 20 ⇒ 与原来 distance_upper_bound=20 的结果相同 (inf)
    Pa=_p(a); m=np.all((Pa>=np.array(Bb[:3])-20)&(Pa<=np.array(Bb[3:])+20),axis=1)   # 对方包围盒外扩 20 以外的点距离必 > 20, 不用查 (结果不变)
    if not m.any(): return float('inf')
    if b not in _K: _K[b]=cKDTree(_p(b))
    d,_=_K[b].query(Pa[m],k=1,distance_upper_bound=20); return float(d.min())
print('shapes keyed',f'{time.time()-T0:.0f}s',flush=True)
_CC=('cd_capclamp',) if CD.HAS_CC else ()
_MC=('cd_clamp',) if CD.HAS_MC else ()
PAIRS=[(f'gt_lug{i}',x) for i in range(len(B_lugs)) for x in ('tube','glass_top','led_top','led_a','led_b','rod')]+[('board',x) for x in ('ring','flange_disc','mounting_flange','motor','seat','tube','post0','post1','post2','post3')]+\
 [('ring',x) for x in ('disc','flange_disc','mounting_flange','motor','seat')]+[('motor',x) for x in ('disc','hub','flange_disc','mounting_flange')]+\
 [('hub','mounting_flange'),('hub','flange_disc'),('rim','mounting_flange'),('seat','mounting_flange'),('seat','flange_disc'),('seat','rim'),('seat','hub')]+\
 [(f'seat_nut{i}',x) for i in range(4) for x in ('mounting_flange','flange_disc')]+[('heatsink','disc')]+[('clamp_ring','shroud_split'),('shroud_lo','shroud_hi'),('clamp_ring','shroud_hi'),('shroud_hi','tube'),('shroud_hi','rim'),('shroud_hi','hub'),('clamp_ring','tube'),('shroud_split','tube')]+[('xt60',x) for x in ('board','seat','mounting_flange','flange_disc','disc','ring')]+\
 [(c,x) for c in _MC+_CC+('cd_cap','cd_sink2','cd_pcb','cd_mos') for x in ('flange_disc','mounting_flange','ring','board','seat','xt60','shroud_split')]+[('cd_sink2','disc'),('cd_cap','disc'),('cd_pcb','disc')]+[(c,'disc') for c in _MC+_CC]+\
 [(c,x) for c in _MC for x in ('cd_pcb','cd_mos','cd_sink2','cd_cap')]+[(c,x) for c in _CC for x in ('cd_cap','cd_pcb','cd_sink2')+_MC]+[('cd_cap','cd_pcb'),('cd_mos','cd_sink2')]+\
 [('key_bracket',x) for x in ('disc','seat','shroud_split','key_board','ring','flange_disc','mounting_flange','rim')]+[('key_board',x) for x in ('disc','seat','shroud_split','ring','flange_disc','mounting_flange','rim')]+\
 [('glass_top',x) for x in ('tube','glass_disc','glass_top_hub')]+[('glass_top_hub','glass_disc')]+[('glass_top_clamp',x) for x in ('glass_top','glass_disc','glass_top_hub','tube')]+\
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
if ROTOR_B:
    _seen=set(); _np=[]
    for x,y in PAIRS+[('hub','rim')]:      # 旧表里 hub/rim 没有互配对 (贴面), 新的 fr4/rim_b 要查
        x,y=RMAP.get(x,x),RMAP.get(y,y)
        if x==y or frozenset((x,y)) in _seen: continue
        _seen.add(frozenset((x,y))); _np.append((x,y))
    for x,y in [('coil',z) for z in ('fr4','rim_b','ring','flange_disc','mounting_flange','motor')]+[(h,z) for h in RB.SCREEN_KEYS[:4] for z in ('fr4','rim_b','shroud_b_a','shroud_b_b','bb_r2','wireless_holder','wireless_module','led_a','led_b','led_bar','fpc_a','fpc_b','bridge_a','bridge_b','seat_j5','seat_j6','ant_a','ant_b')]+\
               [('fr4',z) for z in ('flange_disc','mounting_flange','ring','motor','wireless_module','bb_r2')]+[('rim_b',z) for z in ('motor','wireless_module','seat_j5','seat_j6','led_bar')]+[('shroud_b_a','shroud_b_b')]+\
               [(h,z) for h in RB.SCREEN_KEYS for z in ('led_top',)]:   # 11-21 侧立件取消 (原 post_b_a/b 配对并进上面支撑件)
        if frozenset((x,y)) in _seen: continue
        _seen.add(frozenset((x,y))); _np.append((x,y))
    PAIRS=[(x,y) for x,y in _np if x in S and y in S]   # 11-27 侧环整圈时没有 shroud_b_b
    print(f'转子盘B: 配对 {len(PAIRS)} 组',flush=True)
_HIT0=set(_PAIRC)
for a,b in PAIRS:
    ck=('c1',_KEY[a],_KEY[b])
    if _CK and ck in _PAIRC: d,v=_PAIRC[ck]; _ST['pair_hit']+=1
    else:
        d=md(a,b); v=vol(op(BRepAlgoAPI_Common,S[a],S[b])) if d<0.3 else None
        _ST['pair_far' if d==float('inf') else 'pair_new']+=1
        if _CK: _PAIRC[ck]=(d,v)
    flag='' if v is None else f'  相交体积 {v:.3f} mm3'
    if _os.environ.get('CHECK_BRIEF') and not (v is not None and v>1e-3) and not (_CK and ck not in _HIT0): continue   # 11-20 quick --check: 只列本次新算的配对 + 所有相交
    if a=='led_top' and b=='rod' and flag: flag+='  (预期: Φ8 轴压入 Φ7.85 孔过盈)'
    if a=='led_a' and b=='led_b' and flag: flag+='  (待查: 灯板 V0.2.0 STEP 上角 F 面 2 件 6×4 伸出 F 面 6.09 > 间隙 4.6, 各穿进对面板 1.47; 非结构件)'
    print(f'{a:14s} ↔ {b:16s} 最小距离 ≈ {d:6.2f}{flag}',flush=True)
print(LOG['disc_holes']['grid'],'网格孔;', 'ring',LOG['ring'],flush=True)
if _CK:
    tmp=_PAIRF.with_suffix(f'.{_os.getpid()}.tmp'); _pk.dump(_PAIRC,open(tmp,'wb')); _os.replace(tmp,_PAIRF)
    print(f"缓存: 采样 命中 {_ST['pts_hit']} / 新算 {_ST['pts_new']}; 配对 命中 {_ST['pair_hit']} / 新算 {_ST['pair_new']} / 包围盒远 {_ST['pair_far']}",flush=True)
print(f'done {time.time()-T0:.0f}s')
