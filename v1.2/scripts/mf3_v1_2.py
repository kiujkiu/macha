"""3MF 写出 (从 export_3mf_v1_2.py 拆出, 11-13 晚; export_3mf / assembly_noglass 共用)。"""
import numpy as np, zipfile
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
def mesh(shape, defl):
    BRepMesh_IncrementalMesh(shape, defl, False, 0.3, True)
    V=[];T=[];n=0; e=TopExp_Explorer(shape,TopAbs_FACE)
    while e.More():
        f=TopoDS.Face(e.Current()); L=TopLoc_Location(); tr=BRep_Tool.Triangulation_s(f,L)
        if tr is not None:
            t=L.Transformation(); k=tr.NbNodes()
            V.append(np.array([[p.X(),p.Y(),p.Z()] for p in (tr.Node(i).Transformed(t) for i in range(1,k+1))]))
            tt=np.array([[tr.Triangle(i).Value(j) for j in (1,2,3)] for i in range(1,tr.NbTriangles()+1)])-1
            if f.Orientation()==TopAbs_REVERSED: tt=tt[:,[0,2,1]]
            T.append(tt+n); n+=k
        e.Next()
    return np.vstack(V),np.vstack(T)
def write3mf(path, parts):
    mats=''.join(f'<base name="{n}" displaycolor="{c}FF"/>' for n,_,c,_ in parts)
    objs=[];items=[]
    for i,(n,s,c,defl) in enumerate(parts):
        V,T=mesh(s,defl)
        vs='\n'.join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x,y,z in V)
        ts='\n'.join(f'<triangle v1="{a}" v2="{b}" v3="{c_}"/>' for a,b,c_ in T)
        objs.append(f'<object id="{i+2}" name="{n}" type="model" pid="1" pindex="{i}"><mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>')
        items.append(f'<item objectid="{i+2}"/>'); print(n,len(V),len(T),flush=True)
    model=('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
           f'<resources><basematerials id="1">{mats}</basematerials>{"".join(objs)}</resources><build>{"".join(items)}</build></model>')
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels','<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model',model)
