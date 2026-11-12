"""mesh -> B-rep: 平面合并 + 圆柱识别, 拓扑共享边 (水密), 失败逐级回退."""
import math, numpy as np
from collections import defaultdict, deque
from OCP.gp import gp_Pnt, gp_Dir, gp_Ax3, gp_Ax2, gp_Pln, gp_Circ, gp_Vec, gp_Cylinder
from OCP.Geom import Geom_Plane, Geom_CylindricalSurface, Geom_Circle, Geom_Line
from OCP.BRep import BRep_Builder, BRep_Tool
from OCP.BRepBuilderAPI import (BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeSolid, BRepBuilderAPI_Sewing, BRepBuilderAPI_MakePolygon)
from OCP.TopoDS import TopoDS_Shell, TopoDS_Wire, TopoDS_Compound, TopoDS_Solid, TopoDS, TopoDS_Face
from OCP.ShapeFix import ShapeFix_Edge, ShapeFix_Face, ShapeFix_Solid, ShapeFix_Shape
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepLib import BRepLib
from OCP.GeomAPI import GeomAPI_Interpolate, GeomAPI_PointsToBSpline
from OCP.collections import HArray1_gp_Pnt as TColgp_HArray1OfPnt
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain

PT=1e-4       # 平面判定 mm
def P(p): return gp_Pnt(float(p[0]),float(p[1]),float(p[2]))
def D(p): return gp_Dir(float(p[0]),float(p[1]),float(p[2]))

def weld(V,T,tol=2e-4):
    k=np.round(V/tol).astype(np.int64)
    u,inv=np.unique(k,axis=0,return_inverse=True); inv=inv.ravel()
    Vn=np.zeros((len(u),3)); c=np.zeros(len(u))
    np.add.at(Vn,inv,V); np.add.at(c,inv,1); Vn/=c[:,None]
    T2=inv[T]
    ok=(T2[:,0]!=T2[:,1])&(T2[:,1]!=T2[:,2])&(T2[:,0]!=T2[:,2])
    return Vn,T2[ok]

def components(T):
    he={}
    bad=0
    for i,t in enumerate(T):
        for j in range(3):
            k=(t[j],t[(j+1)%3])
            if k in he: bad+=1
            he[k]=i
    open_=sum((b,a) not in he for a,b in he)
    par=list(range(len(T)))
    def f(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for (a,b),i in he.items():
        j=he.get((b,a))
        if j is not None: par[f(i)]=f(j)
    g=defaultdict(list)
    for i in range(len(T)): g[f(i)].append(i)
    return list(g.values()),bad,open_

def signed_vol(V,T):
    a,b,c=V[T[:,0]],V[T[:,1]],V[T[:,2]]
    return np.einsum('ij,ij->i',a,np.cross(b,c)).sum()/6

class Fail(Exception): pass

def fill_open(V,T):
    he={}
    for t in T:
        for j in range(3): he[(int(t[j]),int(t[(j+1)%3]))]=1
    nx=defaultdict(list)
    for a,b in he:
        if (b,a) not in he: nx[b].append(a)     # 反向走, 补面绕向正确
    add=[]
    while nx:
        st=next(iter(nx)); lp=[st]; cur=st
        while True:
            b=nx[cur].pop()
            if not nx[cur]: del nx[cur]
            if b==st: break
            lp.append(b); cur=b
            if cur not in nx: raise Fail('fill')
        # 去共线后扇形
        add+=[(lp[0],lp[i],lp[i+1]) for i in range(1,len(lp)-1)]
    return np.vstack([T,np.array(add,dtype=T.dtype)]) if add else T,len(add)

def split_nonmanifold_1(V,T,alt=0):
    """非流形边按实体内部配对, 再按角点并查集拆顶点 -> 严格流形."""
    hs=defaultdict(list)
    for i,t in enumerate(T):
        for j in range(3): hs[(int(t[j]),int(t[(j+1)%3]))].append((i,j))
    pairs=[]; nmi=[0]
    for (a,b),L in hs.items():
        if a>b and (b,a) in hs: continue
        R=hs.get((b,a),[])
        if len(L)==1 and len(R)==1: pairs.append((L[0],R[0])); continue
        if not R: continue
        nmi[0]+=1
        e=V[b]-V[a]; e/=np.linalg.norm(e)
        u=np.cross(e,[1,0,0])
        if np.linalg.norm(u)<.1: u=np.cross(e,[0,1,0])
        u/=np.linalg.norm(u); w=np.cross(e,u)
        def ang(h):
            i,j=h; c=V[T[i][(j+2)%3]]-V[a]
            return math.atan2(c@w,c@u)%(2*math.pi)
        # 绕边转: a->b 的三角形其外法向决定实体在其转角的 -方向; 相邻 (a->b, b->a) 夹实体
        items=sorted([(ang(h),0,h) for h in L]+[(ang(h),1,h) for h in R])
        n=len(items)
        k0=next(k for k in range(n) if items[k][1]==0); used=set()
        # 取使 a->b 与其前一 b->a 成对
        for k in range(n):
            x=items[(k0+k)%n]
            if x[1]==0:
                y=items[(k0+k-1)%n]
                if y[1]==1 and x[2] not in used and y[2] not in used:
                    pairs.append((x[2],y[2])); used|={x[2],y[2]}
        l2=[h for h in L if h not in used]; r2=[h for h in R if h not in used]
        pairs+=list(zip(l2,r2))
        if alt>>(nmi[0]-1)&1 and len(L)==2 and len(R)==2:
            pairs=[q for q in pairs if q[0] not in L]+[(L[0],R[1]),(L[1],R[0])] if (L[0],R[0]) in pairs else [q for q in pairs if q[0] not in L]+[(L[0],R[0]),(L[1],R[1])]
    cid=lambda i,j:3*i+j
    par=list(range(3*len(T)))
    def f(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for (i,j),(k,l) in pairs:
        # 三角 i 的边 j: 角 j=a 角 j+1=b ; 三角 k 的边 l: 角 l=b 角 l+1=a
        par[f(cid(i,j))]=f(cid(k,(l+1)%3)); par[f(cid(i,(j+1)%3))]=f(cid(k,l))
    new={}; Vn=[]; T2=T.copy()
    for i in range(len(T)):
        for j in range(3):
            r=f(cid(i,j))
            if r not in new: new[r]=len(Vn); Vn.append(V[T[i][j]])
            T2[i][j]=new[r]
    return np.array(Vn),T2,nmi[0]

def split_nonmanifold(V,T):
    V2,T2,k=split_nonmanifold_1(V,T)
    for alt in range(1,1<<min(k,12)):
        if components(T2)[1]==0: break
        V2,T2,_=split_nonmanifold_1(V,T,alt)
    if components(T2)[1]: raise Fail('nonmanifold')
    return V2,T2

def segment(V,T):
    n=len(T)
    a,b,c=V[T[:,0]],V[T[:,1]],V[T[:,2]]
    cr=np.cross(b-a,c-a); area=np.linalg.norm(cr,axis=1)/2
    nrm=cr/np.maximum(2*area,1e-30)[:,None]
    he={}
    for i,t in enumerate(T):
        for j in range(3): he[(int(t[j]),int(t[(j+1)%3]))]=i
    lab=-np.ones(n,int); planes=[]
    for s in np.argsort(-area):
        if lab[s]>=0: continue
        r=len(planes); nn=nrm[s]; d=nn@a[s]; planes.append((nn,d)); lab[s]=r
        q=deque([s])
        while q:
            i=q.popleft(); t=T[i]
            for j in range(3):
                o=he.get((int(t[(j+1)%3]),int(t[j])))
                if o is None or lab[o]>=0: continue
                pv=V[T[o]]
                if np.abs(pv@nn-d).max()<PT and (nrm[o]@nn>0 or area[o]<1e-6):
                    lab[o]=r; q.append(o)
    return lab,planes,he,nrm,area

def find_cyl(V,T,lab,planes,he):
    """返回 regions->cyl 分组: list of dict(regs, c, ax, r)."""
    R=len(planes)
    adj=defaultdict(list)     # r -> [(r2,a,b)]
    for (a,b),i in he.items():
        j=he.get((b,a))
        if j is None: continue
        if lab[i]!=lab[j]: adj[lab[i]].append((lab[j],a,b))
    cyl_of=-np.ones(R,int); out=[]
    rs=sorted(range(R),key=lambda r:(lab==r).sum())
    for r0 in rs:
        if cyl_of[r0]>=0: continue
        n0=planes[r0][0]
        tried=set()
        for r1,a,b in adj[r0]:
            if cyl_of[r1]>=0 or r1 in tried: continue
            tried.add(r1)
            n1=planes[r1][0]
            ang=math.acos(max(-1,min(1,n0@n1)))
            if not(math.radians(1.0)<ang<math.radians(32)): continue
            e=V[b]-V[a]; L=np.linalg.norm(e)
            if L<1e-3: continue
            ax=e/L
            if abs(ax@n0)>2e-3 or abs(ax@n1)>2e-3: continue
            ax=np.cross(n0,n1); ax/=np.linalg.norm(ax)
            S={r0}; axial=set(); q=deque([r0]); sag=0
            while q:
                r=q.popleft(); nr=planes[r][0]
                for r2,a2,b2 in adj[r]:
                    if cyl_of[r2]>=0: continue
                    e2=V[b2]-V[a2]; l2=np.linalg.norm(e2)
                    if l2<1e-6: continue
                    if abs(abs(e2@ax)/l2-1)>1e-4: continue
                    n2=planes[r2][0]
                    if abs(n2@ax)>3e-3: continue
                    an=math.acos(max(-1,min(1,nr@n2)))
                    if not(math.radians(.5)<an<math.radians(32)): continue
                    axial.add(a2);axial.add(b2); sag=max(sag,an)
                    if r2 not in S: S.add(r2); q.append(r2)
            if len(S)<3 or len(axial)<6: continue
            # 拟合圆
            u=np.cross(ax,[1,0,0]);
            if np.linalg.norm(u)<.1: u=np.cross(ax,[0,1,0])
            u/=np.linalg.norm(u); v=np.cross(ax,u)
            pts=V[list(axial)]; x=pts@u; y=pts@v
            A=np.c_[2*x,2*y,np.ones(len(x))]
            sol=np.linalg.lstsq(A,x*x+y*y,rcond=None)[0]
            cx,cy=sol[0],sol[1]; rad=math.sqrt(max(sol[2]+cx*cx+cy*cy,0))
            res=np.abs(np.hypot(x-cx,y-cy)-rad).max()
            if rad<0.2 or rad>2000 or res>max(3e-3,rad*2e-4): continue
            # 同半径同轴: 各段法向须径向
            c0=cx*u+cy*v
            ok=True; sg=[]
            for r in S:
                ids=np.unique(T[lab==r]); w=V[ids]-c0; w=w-np.outer(w@ax,ax)
                rr=np.linalg.norm(w,axis=1)
                if rr.max()>rad+5e-3 or rr.min()<rad*math.cos(sag/2+1e-3)-5e-3: ok=False;break
                m=w.mean(0); m/=np.linalg.norm(m)
                d=m@planes[r][0]
                if abs(d)<.85: ok=False;break
                sg.append(d>0)
            if not ok or len(set(sg))>1: continue
            for r in S: cyl_of[r]=len(out)
            out.append(dict(regs=S,c=c0,ax=ax,r=rad,conv=sg[0]))
            break
    return out,cyl_of

def split_cyl(cy,planes,V,T,lab):
    """把圆柱按角度切成 <=~120° 片, 返回片列表 (regs, mid-angle)."""
    ax=cy['ax']; u=np.cross(ax,[1,0,0])
    if np.linalg.norm(u)<.1: u=np.cross(ax,[0,1,0])
    u/=np.linalg.norm(u); v=np.cross(ax,u)
    sgn=1 if cy['conv'] else -1
    items=[]
    for r in cy['regs']:
        n=planes[r][0]*sgn
        items.append((math.atan2(n@v,n@u),r))
    items.sort()
    ang=[i[0] for i in items]
    gaps=[((ang[(i+1)%len(ang)]-ang[i])%(2*math.pi),i) for i in range(len(ang))]
    g,i=max(gaps)
    order=items[i+1:]+items[:i+1]
    span=2*math.pi-g if len(ang)>1 else 0
    # 连续段: 有大缺口(>40°)就断开, 再按 110° 切
    steps=[(q[0]-p[0])%(2*math.pi) for p,q in zip(order,order[1:])]
    med=float(np.median(steps)) if steps else 1.0
    groups=[];cur=[order[0]]
    for p,q in zip(order,order[1:]):
        dq=(q[0]-p[0])%(2*math.pi)
        spn=(q[0]-cur[0][0])%(2*math.pi)
        if dq>min(math.radians(40),1.6*med) or spn>math.radians(110):
            groups.append(cur);cur=[q]
        else: cur.append(q)
    groups.append(cur)
    res=[]
    for gp in groups:
        a0=gp[0][0]; sp=(gp[-1][0]-a0)%(2*math.pi)
        mid=a0+sp/2
        res.append(dict(regs=[x[1] for x in gp],mid=mid,u=u,v=v,cy=cy))
    return res

def fit_circle3(pts):
    c=pts.mean(0); _,s,vt=np.linalg.svd(pts-c)
    n=vt[2]
    if s[2]>2e-3*math.sqrt(len(pts)): return None
    x=(pts-c)@vt[0]; y=(pts-c)@vt[1]
    A=np.c_[2*x,2*y,np.ones(len(x))]
    sol=np.linalg.lstsq(A,x*x+y*y,rcond=None)[0]
    r=math.sqrt(max(sol[2]+sol[0]**2+sol[1]**2,0))
    res=np.abs(np.hypot(x-sol[0],y-sol[1])-r).max()
    return c+sol[0]*vt[0]+sol[1]*vt[1],n,r,res,vt[0],vt[1]

class Builder:
    def __init__(s,V,T,use_cyl=True,black=(),tris=()):
        s.V,s.T=V,T
        s.lab,s.planes,s.he,s.nrm,s.area=segment(V,T)
        R=len(s.planes)
        s.grp=np.arange(R)         # region->face group
        s.faces={r:dict(kind='pl',n=s.planes[r][0],d=s.planes[r][1]) for r in range(R)}
        s.ncyl=0
        if use_cyl:
            cyls,_=find_cyl(V,T,s.lab,s.planes,s.he)
            s.ncyl=len(cyls)
            nid=R
            for ci,c in enumerate(cyls):
                if ci in black: continue
                for p in split_cyl(c,s.planes,V,T,s.lab):
                    for r in p['regs']:
                        s.faces.pop(r,None); s.grp[r]=nid
                    s.faces[nid]=dict(kind='cy',ci=ci,**p); nid+=1
        s.tg=s.grp[s.lab].copy()
        nid=max(s.faces)+1
        for r in tris:
            if r not in s.faces: continue
            f=s.faces.pop(r)
            for i in np.where(s.tg==r)[0]:
                s.tg[i]=nid; s.faces[nid]=dict(f); s.faces[nid]['src']=r; nid+=1
        s.vert={}; s.edges={}
    def neigh_cyl(s,g):
        o=set()
        for (a,b),i in s.he.items():
            if s.tg[i]==g:
                h=s.tg[s.he[(b,a)]]
                if s.faces[h]['kind']=='cy': o.add(s.faces[h]['ci'])
        return o
    def vtx(s,i,tol=1e-3):
        if i not in s.vert:
            s.vert[i]=BRepBuilderAPI_MakeVertex(P(s.V[i])).Vertex()
            BRep_Builder().UpdateVertex(s.vert[i],tol)
        return s.vert[i]
    def loops(s):
        bnd=defaultdict(dict)         # g -> {a: [b]}
        s.vg=defaultdict(set)
        for (a,b),i in s.he.items():
            j=s.he.get((b,a))
            if j is None: raise Fail('open')
            s.vg[a].add(s.tg[i]); s.vg[b].add(s.tg[i])
            if s.tg[i]!=s.tg[j]:
                bnd[s.tg[i]].setdefault(a,[]).append(b)
        L={}
        for g,nx in bnd.items():
            ls=[]
            while nx:
                st=next(iter(nx)); cur=st; lp=[st]
                while True:
                    bs=nx[cur]; b=bs.pop()
                    if not bs: del nx[cur]
                    if b==st: break
                    lp.append(b); cur=b
                    if cur not in nx: raise Fail('loop')
                ls.append(lp)
            L[g]=ls
        return L
    def corners(s,lp,g):
        n=len(lp); c=[]
        other=[]
        for i in range(n):
            a,b=lp[i],lp[(i+1)%n]
            other.append(s.tg[s.he[(b,a)]])
        for i in range(n):
            p=s.V[lp[i]]; e0=p-s.V[lp[i-1]]; e1=s.V[lp[(i+1)%n]]-p
            cs=(e0@e1)/(np.linalg.norm(e0)*np.linalg.norm(e1)+1e-30)
            if other[i]!=other[i-1] or len(s.vg[lp[i]])>=3 or cs<math.cos(math.radians(35)):
                c.append(i)
        return c
    def mk_edge(s,ids):
        V=s.V; pts=V[ids]; v0=s.vtx(ids[0]); v1=s.vtx(ids[-1])
        closed=ids[0]==ids[-1]
        d=pts[-1]-pts[0]; L=np.linalg.norm(d)
        if len(ids)==2 or (not closed and L>1e-6 and np.linalg.norm(np.cross(pts-pts[0],d/L),axis=1).max()<PT*2):
            if L<1e-7: raise Fail('deg')
            return BRepBuilderAPI_MakeEdge(v0,v1).Edge()
        if len(ids)>=4 and not closed:
            f=fit_circle3(pts)
            if f and f[3]<max(2e-3,f[2]*2e-4) and f[2]>.1:
                c,n,r,res,e1,e2=f
                # 方向
                w=np.cross(pts[0]-c,pts[1]-c)
                if w@n<0: n=-n
                x=(pts[0]-c)/np.linalg.norm(pts[0]-c)
                circ=Geom_Circle(gp_Ax2(P(c),D(n),D(x)),float(r))
                y=np.cross(n,x)
                pe=pts[-1]-c; t1=math.atan2(pe@y,pe@x)%(2*math.pi)
                gap=abs(np.linalg.norm(pts-c,axis=1)-r).max()
                BRep_Builder().UpdateVertex(v0,max(1e-3,gap*2)); BRep_Builder().UpdateVertex(v1,max(1e-3,gap*2))
                m=BRepBuilderAPI_MakeEdge(circ,v0,v1,0.0,float(t1))
                if m.IsDone(): return m.Edge()
        # 样条
        arr=TColgp_HArray1OfPnt(1,len(ids))
        for k,p in enumerate(pts): arr.SetValue(k+1,P(p))
        it=GeomAPI_Interpolate(arr,False,1e-6); it.Perform()
        if not it.IsDone(): raise Fail('interp')
        m=BRepBuilderAPI_MakeEdge(it.Curve(),v0,v1)
        if not m.IsDone(): raise Fail('splineedge')
        return m.Edge()
    def edge(s,ids):
        k=tuple(ids); kr=k[::-1]
        if k in s.edges: return s.edges[k],True
        if kr in s.edges: return s.edges[kr],False
        s.edges[k]=s.mk_edge(ids)
        return s.edges[k],True
    def wire(s,lp,g,rev):
        c=s.corners(lp,g); n=len(lp)
        if not c: c=[0,n//3,2*n//3] if n>=3 else [0]
        chains=[]
        for i,ci in enumerate(c):
            cj=c[(i+1)%len(c)]
            k=(cj-ci)%n or n
            chains.append([lp[(ci+t)%n] for t in range(k+1)])
        W=TopoDS_Wire(); B=BRep_Builder(); B.MakeWire(W)
        seq=[]
        for ch in chains:
            e,fw=s.edge(ch)
            seq.append(e if fw else e.Reversed())
        if rev: seq=[e.Reversed() for e in seq[::-1]]
        for e in seq: B.Add(W,e)
        W.Closed(True)
        return W
    def build(s):
        L=s.loops(); B=BRep_Builder(); s.flist=[]
        sh=TopoDS_Shell(); B.MakeShell(sh)
        fx=ShapeFix_Edge(); nf=0
        for g,ls in L.items():
            f=s.faces[g]
            if f['kind']=='pl':
                # 用环点重算平面
                n=f['n']; p=n*f['d']
                surf=Geom_Plane(gp_Pln(P(p),D(n))); rev=False
            else:
                cy=f['cy']; ax=cy['ax']; a=f['mid']
                xdir=-(math.cos(a)*f['u']+math.sin(a)*f['v'])   # 片中心落在 u=pi
                surf=Geom_CylindricalSurface(gp_Ax3(P(cy['c']),D(ax),D(xdir)),float(cy['r']))
                rev=not cy['conv']
            F=TopoDS_Face(); B.MakeFace(F,surf,1e-3)
            for lp in ls: B.Add(F,s.wire(lp,g,rev))
            if f['kind']=='cy':
                ex=TopExp_Explorer(F,TopAbs_EDGE)
                while ex.More():
                    fx.FixAddPCurve(TopoDS.Edge(ex.Current()),F,False); ex.Next()
            if rev: F=TopoDS.Face(F.Reversed())
            B.Add(sh,F); nf+=1; s.flist.append((F,g))
        sh.Closed(True)
        BRepLib.SameParameter_s(sh,1e-3,True)
        so=TopoDS_Solid(); B.MakeSolid(so); B.Add(so,sh)
        return so,nf

def vol(sh):
    g=GProp_GProps(); BRepGProp.VolumeProperties_s(sh,g); return g.Mass()

def fallback_sew(V,T):
    sew=BRepBuilderAPI_Sewing(1e-3)
    for t in T:
        w=BRepBuilderAPI_MakePolygon(P(V[t[0]]),P(V[t[1]]),P(V[t[2]]),True).Wire()
        sew.Add(BRepBuilderAPI_MakeFace(w,True).Face())
    sew.Perform(); sh=sew.SewedShape()
    ex=TopExp_Explorer(sh,TopAbs_SHELL)
    if not ex.More(): raise Fail('sew')
    so=BRepBuilderAPI_MakeSolid(TopoDS.Shell(ex.Current())).Solid()
    fxs=ShapeFix_Solid(so); fxs.Perform(); so=fxs.Solid()
    u=ShapeUpgrade_UnifySameDomain(so,True,True,False); u.Build()
    return u.Shape()

def bad_cyls(b,so):
    """找出无效面对应的圆柱编号 (面序与 b.flist 一致)."""
    out=set();nb=0;pl=set()
    an=BRepCheck_Analyzer(so)
    for F,g in b.flist:
        ok=an.IsValid(F)
        if not ok:
            nb+=1
            if b.faces[g]['kind']=='cy': out.add(b.faces[g]['ci'])
            else: pl.add(g)
    return out,pl

def face_tol(F):
    ex=TopExp_Explorer(F,TopAbs_EDGE); m=0
    while ex.More():
        m=max(m,BRep_Tool.Tolerance_s(TopoDS.Edge(ex.Current()))); ex.Next()
    return m

def accept(v,tv,cyl):
    lo,hi=(.997,1.06) if cyl else (.999,1.001)
    r=abs(v)/tv
    return lo-.05*cyl<=r<=hi     # 孔变真圆后体积可略减

def convert_component(V,T):
    tv=abs(signed_vol(V,T)); black=set(); tris=set(); err=None
    for it in range(30):
        try:
            b=Builder(V,T,True,black,tris); so,nf=b.build()
        except Fail as e:
            err=repr(e)[:80]; break
        valid=BRepCheck_Analyzer(so).IsValid(); v=vol(so)
        nc=b.ncyl-len(black)
        loose={b.faces[g]['ci'] for F,g in b.flist if b.faces[g]['kind']=='cy' and face_tol(F)>0.1}
        if loose:
            black|=loose; err=f'loose {loose}'; continue
        if valid and accept(v,tv,nc>0):
            return so,dict(mode='cyl' if nc>0 else 'plane',faces=nf,cyl=nc,vol=v,mvol=tv,black=len(black),trisplit=len(tris))
        err=f'valid={valid} v={v:.3f}/{tv:.3f}'
        nb,pl=bad_cyls(b,so); nb-=black; pl-=tris
        if pl: tris|=pl
        elif nb: black|=nb
        elif nc>0: black|=set(range(b.ncyl))
        else: break
    print('       fail->sew',err,flush=True)
    so=fallback_sew(V,T); v=vol(so)
    if not accept(v,tv,False) or not BRepCheck_Analyzer(so).IsValid(): raise Fail(f'sew bad {v}/{tv}')
    return so,dict(mode='sew',faces=-1,cyl=0,vol=v,mvol=tv,black=0,trisplit=0)

def b_ok(V,T): return True

def convert_part(V,T):
    V,T=weld(V,T)
    T,nfill=fill_open(V,T)
    V,T=split_nonmanifold(V,T)
    comps,bad,open_=components(T)
    B=BRep_Builder(); C=TopoDS_Compound(); B.MakeCompound(C)
    st=[]
    for ids in comps:
        t=T[ids]; u,inv=np.unique(t,return_inverse=True)
        so,info=convert_component(V[u],inv.reshape(-1,3)); B.Add(C,so); st.append(info)
    return C,st,bad,open_+nfill
