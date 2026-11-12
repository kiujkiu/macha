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
S={'board':board,'heatsink':heatsink,'disc':disc,'ring':ring,'flange_disc':fl,'mounting_flange':mf,'motor':motor,'hub':hub,'rim':rim,'seat':seat,'tube':tube,'xt60':xt_env,'shroud_split':shroud_split,'clamp_ring':clamp_ring}
for i,p in enumerate(posts): S[f'post{i}']=p
for i,n in enumerate(seat_nuts): S[f'seat_nut{i}']=n
P={k:pts(v) for k,v in S.items()}; print('sampled',f'{time.time()-T0:.0f}s',flush=True)
K={k:cKDTree(v) for k,v in P.items()}
def md(a,b): d,_=K[b].query(P[a],k=1,distance_upper_bound=20); return float(d.min())
PAIRS=[('board',x) for x in ('ring','flange_disc','mounting_flange','motor','seat','tube','post0','post1','post2','post3')]+\
 [('ring',x) for x in ('disc','flange_disc','mounting_flange','motor','seat')]+[('motor',x) for x in ('disc','hub','flange_disc','mounting_flange')]+\
 [('hub','mounting_flange'),('hub','flange_disc'),('rim','mounting_flange'),('seat','mounting_flange'),('seat','flange_disc'),('seat','rim'),('seat','hub')]+\
 [(f'seat_nut{i}','mounting_flange') for i in range(4)]+[('heatsink','disc')]+[('clamp_ring','shroud_split'),('clamp_ring','tube'),('shroud_split','tube')]+[('xt60',x) for x in ('board','seat','mounting_flange','flange_disc','disc','ring')]
for a,b in PAIRS:
    d=md(a,b); flag=''
    if d<0.3:
        v=vol(op(BRepAlgoAPI_Common,S[a],S[b])); flag=f'  相交体积 {v:.3f} mm3'
    print(f'{a:14s} ↔ {b:16s} 最小距离 ≈ {d:6.2f}{flag}',flush=True)
print(LOG['disc_holes']['grid'],'网格孔;', 'ring',LOG['ring'],flush=True)
print(f'done {time.time()-T0:.0f}s')
