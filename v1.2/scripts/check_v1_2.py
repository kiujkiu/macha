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
S={**({'cd_clamp':CD.clamp} if CD.HAS_MC else {}),**({'cd_capclamp':CD.cap_clamp} if CD.HAS_CC else {}),'cd_pcb':CD.pcb,'cd_mos':CD.mos,'cd_cap':CD.cap,'cd_sink2':CD.sink2,'board':board,'heatsink':heatsink,'disc':disc,'ring':ring,'flange_disc':fl,'mounting_flange':mf,'motor':motor,'hub':hub,'rim':rim,'seat':seat,'tube':tube,'xt60':xt_env,'shroud_split':shroud_split,'clamp_ring':clamp_ring,'key_bracket':key_bracket,'key_board':key_board}
for i,p in enumerate(posts): S[f'post{i}']=p
for i,(x,y) in enumerate(SH_M6): S[f'seat_nut{i}']=cyl(x,y,SH_NUT_D,NUT_Z0,NUT_Z0+3.7)   # 11-12 夜: M3 法兰螺母实高 3.7 (build 里 seat_nuts 仍按 2.4)
P={k:pts(v) for k,v in S.items()}; print('sampled',f'{time.time()-T0:.0f}s',flush=True)
K={k:cKDTree(v) for k,v in P.items()}
def md(a,b): d,_=K[b].query(P[a],k=1,distance_upper_bound=20); return float(d.min())
_CC=('cd_capclamp',) if CD.HAS_CC else ()
_MC=('cd_clamp',) if CD.HAS_MC else ()
PAIRS=[('board',x) for x in ('ring','flange_disc','mounting_flange','motor','seat','tube','post0','post1','post2','post3')]+\
 [('ring',x) for x in ('disc','flange_disc','mounting_flange','motor','seat')]+[('motor',x) for x in ('disc','hub','flange_disc','mounting_flange')]+\
 [('hub','mounting_flange'),('hub','flange_disc'),('rim','mounting_flange'),('seat','mounting_flange'),('seat','flange_disc'),('seat','rim'),('seat','hub')]+\
 [(f'seat_nut{i}',x) for i in range(4) for x in ('mounting_flange','flange_disc')]+[('heatsink','disc')]+[('clamp_ring','shroud_split'),('clamp_ring','tube'),('shroud_split','tube')]+[('xt60',x) for x in ('board','seat','mounting_flange','flange_disc','disc','ring')]+\
 [(c,x) for c in _MC+_CC+('cd_cap','cd_sink2','cd_pcb','cd_mos') for x in ('flange_disc','mounting_flange','ring','board','seat','xt60','shroud_split')]+[('cd_sink2','disc'),('cd_cap','disc'),('cd_pcb','disc')]+[(c,'disc') for c in _MC+_CC]+\
 [(c,x) for c in _MC for x in ('cd_pcb','cd_mos','cd_sink2','cd_cap')]+[(c,x) for c in _CC for x in ('cd_cap','cd_pcb','cd_sink2')+_MC]+[('cd_cap','cd_pcb'),('cd_mos','cd_sink2')]+\
 [('key_bracket',x) for x in ('disc','seat','shroud_split','key_board','ring','flange_disc','mounting_flange','rim')]+[('key_board',x) for x in ('disc','seat','shroud_split','ring','flange_disc','mounting_flange','rim')]   # 11-13 按键板+支架
for a,b in PAIRS:
    d=md(a,b); flag=''
    if d<0.3:
        v=vol(op(BRepAlgoAPI_Common,S[a],S[b])); flag=f'  相交体积 {v:.3f} mm3'
    print(f'{a:14s} ↔ {b:16s} 最小距离 ≈ {d:6.2f}{flag}',flush=True)
print(LOG['disc_holes']['grid'],'网格孔;', 'ring',LOG['ring'],flush=True)
print(f'done {time.time()-T0:.0f}s')
