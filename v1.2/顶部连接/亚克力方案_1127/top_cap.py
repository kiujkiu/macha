"""亚克力中心孔 盖子 top_cap_v1_2 (2026-11-27 用户「8mm吧按照2+3+3」)
亚克力 8 厚 (2+3+3), 孔 Ø10.05 (Z 从亚克力底: 台肩 0–2, MR105 2–5, 螺柱顶 5.5, M3 超薄头 5.5–7 随轴转)
盖子 = 顶板 Ø10.0×0.7 (Z7.3–8, 顶面齐平) + 裙边 Ø10.0/Ø8.0 高 2.3 (Z5–7.3) 坐轴承外圈 ⇒ 同时压住轴承
头顶离顶板 0.3, 头外径 Φ7 离裙边内壁 0.5。外圆 4 条压紧筋到 Ø10.15。顶面朝下打印 (层高 0.1)。"""
import math
from pathlib import Path
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse, BRepAlgoAPI_Common
from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Trsf, gp_Ax1
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
D_OUT, D_SK_IN, T_TOP, H_SK, RIB_D, RIB_W, N_RIB = 10.0, 8.0, 0.7, 2.3, 10.15, 0.6, 4
cyl = lambda d, z0, z1: BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, z0), gp_Dir(0, 0, 1)), d / 2, z1 - z0).Shape()
H = T_TOP + H_SK                                       # 打印坐标: 顶面 z=0 贴床
s = BRepAlgoAPI_Cut(cyl(D_OUT, 0, H), cyl(D_SK_IN, T_TOP, H + 1)).Shape()
for k in range(N_RIB):
    b = BRepPrimAPI_MakeBox(gp_Pnt(D_OUT / 2 - 0.3, -RIB_W / 2, 0.3), RIB_D / 2 - D_OUT / 2 + 0.3, RIB_W, H - 0.3).Shape()
    t = gp_Trsf(); t.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 2 * math.pi * k / N_RIB)
    s = BRepAlgoAPI_Fuse(s, BRepAlgoAPI_Common(BRepBuilderAPI_Transform(b, t, True).Shape(), cyl(RIB_D, 0, H)).Shape()).Shape()
out = Path(__file__).resolve().parent
w = STEPControl_Writer(); w.Transfer(s, STEPControl_AsIs); w.Write(str(out / 'top_cap_v1_2.step'))
BRepMesh_IncrementalMesh(s, 0.01, False, 0.1, True); StlAPI_Writer().Write(s, str(out / 'top_cap_v1_2.stl')); print('盖子 ok, 高', H)
