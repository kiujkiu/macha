import pickle,sys,re,struct,json,hashlib,time,os,csv
from pathlib import Path
import numpy as np
from OCP.STEPCAFControl import STEPCAFControl_Reader,STEPCAFControl_Writer
from OCP.STEPControl import STEPControl_AsIs
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString,TCollection_AsciiString
from OCP.XCAFDoc import XCAFDoc_DocumentTool,XCAFDoc_ColorSurf,XCAFDoc_ColorGen
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_Label
from OCP.collections import Sequence_TDF_Label as Seq
from OCP.TopLoc import TopLoc_Location
from OCP.gp import gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound,TopoDS
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_FACE
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.Quantity import Quantity_Color,Quantity_TOC_sRGB
from OCP.Interface import Interface_Static
from OCP.IFSelect import IFSelect_RetDone

SRC=Path('/mnt/d/claude_workspace/macha/pov3d/v1.0/boards')
Interface_Static.SetCVal_s('write.step.schema','AP214IS')
Interface_Static.SetCVal_s('write.step.unit','MM')
def read_step(p):
    doc=TDocStd_Document(TCollection_ExtendedString('XmlOcaf'))
    r=STEPCAFControl_Reader(); r.SetColorMode(True); r.SetNameMode(True)
    assert r.ReadFile(str(p))==IFSelect_RetDone
    r.Transfer(doc)
    st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    q=Seq(); st.GetFreeShapes(q)
    B=BRep_Builder(); C=TopoDS_Compound(); B.MakeCompound(C)
    for i in range(q.Length()): B.Add(C,st.GetShape_s(q.Value(i+1)))
    return C

def bbox(sh):
    b=Bnd_Box(); BRepBndLib.Add_s(sh,b,False); p,q=b.CornerMin(),b.CornerMax(); return (p.X(),p.Y(),p.Z(),q.X(),q.Y(),q.Z())

def solids(sh):
    ex=TopExp_Explorer(sh,TopAbs_SOLID); o=[]
    while ex.More(): o.append(ex.Current()); ex.Next()
    return o

def rgb(h): return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))

def write_doc(items,path,root):
    """items: [(name,shape,color,loc|None)]"""
    doc=TDocStd_Document(TCollection_ExtendedString('XmlOcaf'))
    st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main()); ct=XCAFDoc_DocumentTool.ColorTool_s(doc.Main())
    top=st.NewShape() if len(items)>1 else None
    if top is not None: TDataStd_Name.Set_s(top,TCollection_ExtendedString(root))
    cache={}
    for name,sh,col,loc,asm in items:
        k=id(sh)
        if k not in cache:
            lab=st.AddShape(sh,asm,False)
            TDataStd_Name.Set_s(lab,TCollection_ExtendedString(name))
            c=Quantity_Color(*rgb(col),Quantity_TOC_sRGB)
            ct.SetColor(lab,c,XCAFDoc_ColorGen); ct.SetColor(lab,c,XCAFDoc_ColorSurf)
            cache[k]=lab
        if top is not None:
            comp=st.AddComponent(top,cache[k],TopLoc_Location(loc) if loc else TopLoc_Location())
            TDataStd_Name.Set_s(comp,TCollection_ExtendedString(name))
    if top is not None: st.UpdateAssemblies()
    w=STEPCAFControl_Writer(); w.SetColorMode(True); w.SetNameMode(True)
    assert w.Transfer(doc,STEPControl_AsIs)
    assert w.Write(str(path))==IFSelect_RetDone

