"""
V1.0 验证板 STEP → STL 孪生 (2026-10-16)

把 boards/step/*.step (嘉立创 EDA / Altium 导出, 含元件模型) 转成 STL, 坐标原样
(各板自身 PCB 坐标, 单位 mm), 另把板体 (Board 实体) 单独导出一份 *_board.stl,
并打印包围盒/板厚供堆叠用。STEP 不进 git (见 .gitignore), STL 进。

用法: ../../.venv/bin/python step2stl.py [名字...]   (缺省 = step/ 下全部)
"""
import sys
from pathlib import Path
from OCP.STEPCAFControl import STEPCAFControl_Reader
from OCP.TDocStd import TDocStd_Document
from OCP.TCollection import TCollection_ExtendedString
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TDF import TDF_Label
try:
    from OCP.TDF import TDF_LabelSequence
except ImportError:                      # OCP 8: 序列类型挪到 OCP.collections
    from OCP.collections import Sequence_TDF_Label as TDF_LabelSequence
from OCP.TDataStd import TDataStd_Name
from OCP.TopLoc import TopLoc_Location
from OCP.BRep import BRep_Builder
from OCP.TopoDS import TopoDS_Compound
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib

HERE = Path(__file__).parent
STEP_DIR = HERE / "step"
LIN_TOL, ANG_TOL = 0.05, 0.3


def label_name(lab):
    attr = TDataStd_Name()
    if lab.FindAttribute(TDataStd_Name.GetID_s(), attr):
        return attr.Get().ToExtString()
    return ""


def leaves(st, lab, loc, out):
    """展开装配树 → [(名字, 已定位 shape)]"""
    if st.IsReference_s(lab):
        r = TDF_Label()
        st.GetReferredShape_s(lab, r)
        leaves(st, r, loc * st.GetLocation_s(lab), out)
        return
    if st.IsAssembly_s(lab):
        kids = TDF_LabelSequence()
        st.GetComponents_s(lab, kids)
        for i in range(1, kids.Length() + 1):
            leaves(st, kids.Value(i), loc, out)
        return
    shp = st.GetShape_s(lab)
    out.append((label_name(lab), shp.Moved(loc)))


def bbox(shape):
    b = Bnd_Box()
    BRepBndLib.Add_s(shape, b)
    a, c = b.CornerMin(), b.CornerMax()
    return a.X(), a.Y(), a.Z(), c.X(), c.Y(), c.Z()


LAYER_NAMES = {"TopCopper", "BottomCopper", "TopSilkscreen", "BottomSilkscreen",
               "TopFpcStiffener", "BottomFpcStiffener"}
LITE_MIN = 2.5


def _ok(s):
    try:
        bbox(s)
        return True
    except Exception:
        return False


def _dims(s):
    x0, y0, z0, x1, y1, z1 = bbox(s)
    return x1 - x0, y1 - y0, z1 - z0


def _area(s):
    d = _dims(s)
    return d[0] * d[1]


def write_stl(shapes, path):
    comp = TopoDS_Compound()
    bld = BRep_Builder()
    bld.MakeCompound(comp)
    for s in shapes:
        bld.Add(comp, s)
    BRepMesh_IncrementalMesh(comp, LIN_TOL, False, ANG_TOL, True)
    w = StlAPI_Writer()
    w.ASCIIMode = False
    w.Write(comp, str(path))
    return comp


def convert(step):
    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    rd = STEPCAFControl_Reader()
    rd.SetNameMode(True)
    assert rd.ReadFile(str(step)) == 1, step
    rd.Transfer(doc)
    st = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    roots = TDF_LabelSequence()
    st.GetFreeShapes(roots)
    parts = []
    for i in range(1, roots.Length() + 1):
        leaves(st, roots.Value(i), TopLoc_Location(), parts)
    parts = [(n, s) for (n, s) in parts if not s.IsNull() and _ok(s)]
    board = [s for (n, s) in parts if n.startswith("Board")]
    if not board:   # Altium 导出无 "Board" 名 —— 取平面面积最大的实体当板体
        board = [max(parts, key=lambda p: _area(p[1]))[1]]
    stem = step.stem
    comp = write_stl([s for _, s in parts], HERE / f"{stem}.stl")
    # 精简版 (装配用): 去铜皮/丝印/补强层, 去 XY 两向都 < LITE_MIN 的小件 (0402/0603 等)
    lite = [s for (n, s) in parts
            if not n.split("~")[0] in LAYER_NAMES and
            (s in board or max(_dims(s)[:2]) >= LITE_MIN)]
    write_stl(lite, HERE / f"{stem}_lite.stl")
    x0, y0, z0, x1, y1, z1 = bbox(comp)
    print(f"{stem}: {len(parts)} 实体  整体 X {x0:.2f}..{x1:.2f} Y {y0:.2f}..{y1:.2f} Z {z0:.2f}..{z1:.2f}")
    if board:
        bc = write_stl(board, HERE / f"{stem}_board.stl")
        x0, y0, z0, x1, y1, z1 = bbox(bc)
        print(f"   板体 {x1-x0:.2f} × {y1-y0:.2f} × 厚 {z1-z0:.2f}  "
              f"(X {x0:.2f}..{x1:.2f} Y {y0:.2f}..{y1:.2f} Z {z0:.2f}..{z1:.2f})")
    else:
        print("   ⚠ 没找到 Board 实体; 前 15 个名字:", [n for n, _ in parts[:15]])


if __name__ == "__main__":
    names = sys.argv[1:]
    for p in sorted(STEP_DIR.glob("*.step")):
        if not names or any(n in p.stem for n in names):
            convert(p)
