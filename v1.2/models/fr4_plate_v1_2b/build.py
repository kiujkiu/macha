"""
★ fr4_plate_v1_2b —— 转子盘B 玻纤加强板 (2026-11-17 用户定)
  无铜 FR4 光板 Φ165 × 3.0, 11-17 晚改: 毂盘取消, 本板直接压在电机顶面上, 上面是承载盘单件 (并入毂盘); 孔位 8/4 重对称, 绕 Z 转 90° 不变 (整机坐标 = 零件坐标)。
  - 内圈 R34 ×8 + 外圈 R77.5 ×8 (@22.5°+45°k): M3 通孔 Φ3.2 + 底面 Φ7.2×1.5 平底沉孔; 螺丝从下往上穿玻纤板 + 承载盘: 12 颗进承载盘铜螺母, 4 颗再穿屏幕固定件上法兰螺母
  - 电机 4 孔 (正方形对角 16, R8 @45°+90°k): M3 通孔 Φ3.2, 不开沉孔 (电机螺丝从承载盘顶面往下拧, 底面贴电机)
  - 中心: M5 通孔, 实际 Φ5.2 (电机轴头)
  - 厚度 2.0 (用户问够不够: 抗弯刚度 ∝ E·t³, 2 mm FR4 约为 3 mm 打印 PLA 底板 2 倍; 3 mm 重 +45 g, 收益不划算)
  输出: STL (底面 Z0, 沉孔朝下 = 装配姿态) + DXF (外形 + 全部通孔, 给板厂) + 图纸 (build_drawing.py)
"""
import math
from pathlib import Path
import manifold3d as m3d
import numpy as np, struct

HERE = Path(__file__).resolve().parent
OD, T = 165.0, 3.0   # 11-17 晚: 厚 2 → 3 (用户: 毂盘并入承载盘, 玻纤板当承力底板); 11-17: 175 → 170 → 165 (用户: = 毂盘 Φ165, 正好垫在毂盘下; 承载盘外唇 ID165/OD170 下沿齐毂盘底, 落在板外)
M3_D, CB_D, CB_H = 3.2, 7.2, 1.5   # 11-17 晚 用户: 沉孔深 1 → 1.5
CENTER_D = 5.2
ring = lambda r, n, a0: [(r * math.cos(math.radians(a0 + 360 / n * k)), r * math.sin(math.radians(a0 + 360 / n * k))) for k in range(n)]  # noqa: E731
HOLES_IN = ring(34.0, 8, 22.5)        # 内圈: 11-17 晚 R30 → R34 (电机 Φ55: 头沉孔 Φ7.2 内缘 r30.4, 离电机 2.9)
HOLES_OUT = ring(77.5, 8, 22.5)       # 外圈 (V0.4 R77.5)
HOLES_MOTOR = ring(8.0, 4, 45.0)      # 电机 (新电机 4×M3 对角 16)
SEG = 64


def cyl(d, x, y, z0, z1, seg=SEG):
    return m3d.Manifold.cylinder(z1 - z0, d / 2, d / 2, seg, False).translate((x, y, z0))


def build():
    p = cyl(OD, 0, 0, 0, T, 256)
    for x, y in HOLES_IN + HOLES_OUT:
        p -= cyl(M3_D, x, y, -1, T + 1) + cyl(CB_D, x, y, -1, CB_H)
    for x, y in HOLES_MOTOR:
        p -= cyl(M3_D, x, y, -1, T + 1)
    p -= cyl(CENTER_D, 0, 0, -1, T + 1)
    return p


def write_stl(part, out, name):
    mesh = part.to_mesh(); v = np.asarray(mesh.vert_properties)[:, :3]; t = np.asarray(mesh.tri_verts)
    with open(out, 'wb') as f:
        f.write(name.encode().ljust(80, b' ')); f.write(struct.pack('<I', len(t)))
        for a, b, c in t:
            n = np.cross(v[b] - v[a], v[c] - v[a]); L = np.linalg.norm(n); n = n / L if L else n
            f.write(struct.pack('<12fH', *n, *v[a], *v[b], *v[c], 0))
    return v


def write_dxf(out):
    import ezdxf
    doc = ezdxf.new('R2000', setup=True); doc.units = ezdxf.units.MM
    doc.layers.add('OUTLINE', color=7); doc.layers.add('HOLES', color=1); doc.layers.add('CB_BOTTOM', color=3); doc.layers.add('NOTE', color=2)
    msp = doc.modelspace()
    msp.add_circle((0, 0), OD / 2, dxfattribs={'layer': 'OUTLINE'})
    for x, y in HOLES_IN + HOLES_OUT + HOLES_MOTOR:
        msp.add_circle((x, y), M3_D / 2, dxfattribs={'layer': 'HOLES'})
    msp.add_circle((0, 0), CENTER_D / 2, dxfattribs={'layer': 'HOLES'})
    for x, y in HOLES_IN + HOLES_OUT:                       # 沉孔只作标示 (板厂按图纸/备注做底面控深)
        msp.add_circle((x, y), CB_D / 2, dxfattribs={'layer': 'CB_BOTTOM'})
    msp.add_text('FR4 no copper, T=2.0; CB_BOTTOM: 16x D7.2 depth 1.0 from bottom side', height=3,
                 dxfattribs={'layer': 'NOTE'}).set_placement((-OD / 2, -OD / 2 - 8))
    doc.saveas(out)


if __name__ == '__main__':
    part = build()
    v = write_stl(part, HERE / 'fr4_plate_v1_2b.stl', 'POV3D fr4_plate_v1_2b D165x3 FR4')
    write_dxf(HERE / 'fr4_plate_v1_2b.dxf')
    vol = part.volume()
    print(f'bbox Z {v[:, 2].min():.2f}..{v[:, 2].max():.2f}  体积 {vol:.1f} mm³  重量 ≈ {vol * 1.85e-3:.1f} g (FR4 1.85 g/cm³)  genus {part.genus()}')
    assert part.genus() == 16 + 4 + 1, part.genus()
    pts = HOLES_IN + HOLES_OUT + HOLES_MOTOR
    gap = min(math.dist(a, b) for i, a in enumerate(pts) for b in pts[i + 1:]) 
    print(f'孔心最小间距 {gap:.2f}; 外圈沉孔边到板边 {OD / 2 - 77.5 - CB_D / 2:.2f}; 电机孔边到中心孔边 {8 - M3_D / 2 - CENTER_D / 2:.2f}')
