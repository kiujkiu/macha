import numpy as np, zipfile, io
from build_v1_2 import *
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
# 板: 去掉 < 1 mm 的小件 (0402 电阻电容等), 只为看效果
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
B=BRep_Builder();C=TopoDS_Compound();B.MakeCompound(C); kept=0
for s in solids(board):
    b=bbox(s)
    if max(b[3]-b[0],b[4]-b[1])>=1.2 or b[5]-b[2]>=1.0: B.Add(C,s); kept+=1
print('board solids kept',kept)
fl=flange_disc; mf=mounting_flange
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
P_=[('底盘 Φ220×6 (平板)',disc,'#8A8F98',0.05),('线圈环 (托法兰盘, 单独件)',ring,'#E0A030',0.05),('电机 Φ55×21.5 (占位)',motor,'#333333',0.05),
    ('电机控制板',C,'#2E7D32',0.08),('散热片 40×20×6',heatsink,'#C0392B',0.05),
    *([('MOS 压块 mos_clamp_v1_2',CD.clamp,'#E69138',0.05)] if CD.HAS_MC else []),*([('电容卡件 cap_clamp_v1_2',CD.cap_clamp,'#B45F06',0.05)] if CD.HAS_CC else []),('线圈驱动板 (元件级, 按照片估)',CD.pcb,'#38761D',0.05),('线圈驱动 MOS TO-220',CD.mos,'#222222',0.05),
    ('线圈驱动 电解电容 Φ10×20',CD.cap,'#1155CC',0.05),('线圈驱动 散热片 40×20×6 (转 90°)',CD.sink2,'#C0392B',0.05)]
EXT=[('法兰盘 flange_disc_v1_2 (底减3)',fl,'#D9A441',0.05),('安装法兰 mounting_flange_v1_2 (外裙短3)',mf,'#B5895A',0.05),
     ('转子毂盘 hub_disc_v1_2 (降10.2)',hub,'#4F86C6',0.05),('承载盘 rim_ring Φ178 (降10.2)',rim,'#6AA84F',0.05)]
A = V12 / 'assembly_v1_2'
write3mf(f'{A}_底盘+线圈环+电机+控制板.3mf',P_)
write3mf(f'{A}_含法兰+转子盘.3mf',P_+EXT)
write3mf(f'{A}_含法兰+转子盘+玻璃罩定位环.3mf',P_+EXT+[('玻璃罩下罩+定位环 glass_shroud_v1_2',seat,'#7FB3D5',0.05),('XT60 压块',xt_clamp,'#F1C232',0.05),('XT60 底垫',xt_shim,'#E69138',0.05)])
write3mf(f'{A}_玻璃罩版整机_合并.3mf',P_+EXT+[('玻璃罩下罩+定位环 glass_shroud_v1_2',seat,'#7FB3D5',0.05),('玻璃罩 OD200x5 H245',tube,'#D6EAF8',0.1),('XT60 压块',xt_clamp,'#F1C232',0.05),('XT60 底垫',xt_shim,'#E69138',0.05)])
write3mf(f'{A}_玻璃罩版整机_分体外卡环.3mf',P_+EXT+[('下罩 (分体) glass_shroud_split_v1_2',shroud_split,'#7FB3D5',0.05),('外卡环 glass_clamp_ring_v1_2',clamp_ring,'#2E86C1',0.05),('玻璃罩 OD200x5 H245',tube,'#D6EAF8',0.1),('XT60 压块',xt_clamp,'#F1C232',0.05),('XT60 底垫',xt_shim,'#E69138',0.05)])
for n,sh in (('base_disc_v1_2',disc),('coil_ring_v1_2',ring),('flange_disc_v1_2',flange_disc),('mounting_flange_v1_2',mounting_flange),('glass_shroud_v1_2',seat),('glass_shroud_split_v1_2',shroud_split),('glass_clamp_ring_v1_2',clamp_ring)):
    d = V12 / 'models' / n; d.mkdir(parents=True, exist_ok=True)
    BRepMesh_IncrementalMesh(sh,0.02,False,0.2,True); w=StlAPI_Writer(); w.ASCIIMode=False; w.Write(sh,str(d / f'{n}.stl'))
    write_doc([(n, sh, '#8A8F98', None, False)], d / f'{n}.step', n)
print('ok')
