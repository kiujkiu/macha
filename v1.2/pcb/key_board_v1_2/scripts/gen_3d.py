"""按键板自定义封装的简易 3D 模型 (STEP, 封装坐标, mm, Z=0 板面)
    ../../../../.venv/bin/python scripts/gen_3d.py   (在 key_board_v1_2/ 下)
SW  ZX-QC66-7.5TP: 本体 6×6×3.45, 杆 Φ3.5 顶 Z7.5 (手册 H=7.5), 4 脚 0.7 宽 × 0.25 厚, 从本体边 ±3 伸到 ±4.6 (焊盘中心 ±4.0, ±2.25)
LED XL-1615RGBC: 1.6×1.5×0.6;  LED 0603: 1.6×0.8×0.6
"""
import os
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCP.gp import gp_Pnt, gp_Ax2, gp_Dir
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.Interface import Interface_Static

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib', '3d')
os.makedirs(OUT, exist_ok=True)


def box(x0, y0, z0, x1, y1, z1):
    return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()


def cyl(x, y, d, z0, z1):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, z0), gp_Dir(0, 0, 1)), d / 2, z1 - z0).Shape()


def fuse(*s):
    r = s[0]
    for t in s[1:]:
        r = BRepAlgoAPI_Fuse(r, t).Shape()
    return r


def save(shape, name):
    Interface_Static.SetCVal_s('write.step.unit', 'MM')
    w = STEPControl_Writer(); w.Transfer(shape, STEPControl_AsIs); w.Write(os.path.join(OUT, name + '.step'))
    print('wrote', name)


BODY, BODY_H, STEM_D, H = 6.0, 3.45, 3.5, 7.5
legs = [box(sx * 3.0 if sx > 0 else -4.6, sy * 2.25 - 0.35, 0, 4.6 if sx > 0 else -3.0, sy * 2.25 + 0.35, 0.25) for sx in (1, -1) for sy in (1, -1)]
save(fuse(box(-BODY / 2, -BODY / 2, 0.1, BODY / 2, BODY / 2, BODY_H), cyl(0, 0, STEM_D, BODY_H - 0.01, H), *legs), 'SW_ZX-QC66-7.5TP')
save(box(-0.8, -0.75, 0, 0.8, 0.75, 0.6), 'LED_XL-1615RGBC')
save(box(-0.8, -0.4, 0, 0.8, 0.4, 0.6), 'LED_0603_A-SP192YR6AC')
