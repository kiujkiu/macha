"""
★ fr4_plate_v1_2b —— 转子盘B 玻纤加强板 (2026-11-17 用户定)
  无铜 FR4 光板 Φ165 × 3.0, 11-17 晚改: 毂盘取消, 本板直接压在电机顶面上, 上面是承载盘单件 (并入毂盘); 孔位 8/4 重对称, 绕 Z 转 90° 不变 (整机坐标 = 零件坐标)。
  - 内圈 R34 ×8 + 外圈 R77.5 ×8 (@22.5°+45°k): M3 通孔 Φ3.2 + 底面 Φ7.2×1.5 平底沉孔; 螺丝从下往上穿玻纤板 + 承载盘: 12 颗进承载盘铜螺母, 4 颗再穿屏幕固定件上法兰螺母
  - 电机 4 孔 (正方形对角 16, R8 @45°+90°k): M3 通孔 Φ3.2, 不开沉孔 (电机螺丝从承载盘顶面往下拧, 底面贴电机)
  - 中心: M5 通孔, 实际 Φ5.2 (电机轴头)
  - 厚度 3.0 (11-17 晚由 2.0 改; 毂盘并入承载盘后本板当承力底板)
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
    """板厂 DXF: OUTLINE 外形 / HOLES 通孔 (只这两层参与加工) + CB_BOTTOM 沉孔示意 + CENTER 中心线 + DIM 尺寸 + NOTE 备注。"""
    import ezdxf
    doc = ezdxf.new('R2000', setup=True); doc.units = ezdxf.units.MM
    for n, c in (('OUTLINE', 7), ('HOLES', 1), ('CB_BOTTOM', 3), ('CENTER', 4), ('DIM', 5), ('NOTE', 2)):
        doc.layers.add(n, color=c)
    doc.layers.get('CENTER').dxf.linetype = 'CENTER'
    msp = doc.modelspace()
    R = OD / 2
    msp.add_circle((0, 0), R, dxfattribs={'layer': 'OUTLINE'})
    for x, y in HOLES_IN + HOLES_OUT + HOLES_MOTOR:
        msp.add_circle((x, y), M3_D / 2, dxfattribs={'layer': 'HOLES'})
    msp.add_circle((0, 0), CENTER_D / 2, dxfattribs={'layer': 'HOLES'})
    for x, y in HOLES_IN + HOLES_OUT:
        msp.add_circle((x, y), CB_D / 2, dxfattribs={'layer': 'CB_BOTTOM'})
    # 中心线 + 孔位分布圆
    ca = {'layer': 'CENTER'}
    msp.add_line((-R - 5, 0), (R + 5, 0), dxfattribs=ca); msp.add_line((0, -R - 5), (0, R + 5), dxfattribs=ca)
    for r in (34.0, 77.5, 8.0):
        msp.add_circle((0, 0), r, dxfattribs=ca)
    for x, y in HOLES_IN + HOLES_OUT:
        a = math.atan2(y, x); r = math.hypot(x, y)
        msp.add_line(((r - 6) * math.cos(a), (r - 6) * math.sin(a)), ((r + 6) * math.cos(a), (r + 6) * math.sin(a)), dxfattribs=ca)
    # 尺寸
    da = {'layer': 'DIM'}; ov = dict(dimtxt=3.0, dimasz=2.5, dimdec=1, dimtzin=8)
    def diam(r, ang, txt=None, xo=None):
        a = math.radians(ang)
        d = msp.add_diameter_dim(center=(0, 0), radius=r, angle=ang, dimstyle='EZ_RADIUS', override=ov, text=txt or '<>', dxfattribs=da)
        d.render()
    diam(R, 60, '%%c165')
    diam(77.5, 112.5, '%%c155 (8-%%c3.2)')
    diam(34.0, 202.5, '%%c68 (8-%%c3.2)')
    # 电机孔方阵 & 角度
    msp.add_linear_dim(base=(0, -14), p1=HOLES_MOTOR[2], p2=HOLES_MOTOR[3], text='11.31', dimstyle='EZDXF', override=ov, dxfattribs=da).render()
    msp.add_angular_dim_cra(center=(0, 0), radius=55, start_angle=0, end_angle=22.5, distance=0, dimstyle='EZDXF', override=ov, dxfattribs=da).render()
    msp.add_angular_dim_cra(center=(0, 0), radius=62, start_angle=22.5, end_angle=67.5, distance=0, dimstyle='EZDXF', override=ov, dxfattribs=da).render()
    na = {'layer': 'NOTE'}
    def note(t, x, y, h=3.0):
        msp.add_text(t, height=h, dxfattribs=na).set_placement((x, y))
    hx, hy = HOLES_OUT[0]; note(f'16-%%c{M3_D:g} THRU, %%c{CB_D:g} DEPTH {CB_H:g} FROM BOTTOM', hx + 5, hy + 8, 2.5)
    note(f'4-%%c{M3_D:g} THRU (MOTOR, SQ 11.31, DIAG 16)', -60, -22, 2.5)
    note(f'%%c{CENTER_D:g} THRU', 4, -4, 2.5)
    y0 = -R - 14
    for i, t in enumerate([
        'fr4_plate_v1_2b  POV3D V1.2 ROTOR-B GLASS-FIBER BASE PLATE  QTY 1',
        f'MATERIAL: FR4, NO COPPER, T={T:g} +/-0.1    UNIT: mm    ORIGIN = PLATE CENTER (VIEW FROM TOP)',
        'LAYERS: OUTLINE = board outline, HOLES = drilled thru holes (machine these two only)',
        f'        CB_BOTTOM = 16x %%c{CB_D:g} flat counterbore depth {CB_H:g} on BOTTOM side (controlled depth)',
        'HOLES: inner 8 @ R34, outer 8 @ R77.5, both 22.5+45k deg; motor 4 @ R8, 45+90k deg; center %%c5.2',
    ]):
        note(t, -R, y0 - i * 5.5, 3.0)
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
