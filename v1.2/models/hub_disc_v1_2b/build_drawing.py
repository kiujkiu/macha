"""hub_disc_v1_2b 图纸 (2026-11-17): 沿用 V1.0 出图器 (v1.0/models/drawing_v1_0.draw), 孔表照 hub_disc_v1_0 只改 A/E 两组。
先跑同目录 build_stl.py 再跑本脚本。"""
import math, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
V10 = HERE.parents[2] / 'v1.0' / 'models'
sys.path.insert(0, str(V10)); sys.path.insert(0, str(HERE))
from drawing_v1_0 import draw  # noqa: E402
import params_v1_0 as P  # noqa: E402
import importlib.util
_sp = importlib.util.spec_from_file_location('hb', HERE / 'build_stl.py')
ring = lambda r, n, a0: [(r * math.cos(math.radians(a0 + 360 / n * k)), r * math.sin(math.radians(a0 + 360 / n * k))) for k in range(n)]  # noqa: E731
SP = dict(
    stl=HERE / 'hub_disc_v1_2b.stl', code='hub_disc_v1_2b', short='转子下盘 Φ175 (V1.0 改)', qty='1',
    title='转子下盘 (V1.0 hub_disc 起改, 11-17 第 1 步: 电机 5 孔换新电机)',
    orient='底面 (Z0) 贴床, 凸台朝上', src='v1.2/models/hub_disc_v1_2b/hub_disc_v1_2b.stl',
    origin_note='原点 = 盘心, 底面 Z0。',
    holes=[
        dict(tag='A', pts=ring(8, 4, 45), spec='Φ3.2 通 + 顶面 Φ7×4 沉头窝',
             where='新电机转子 4×M3: 正方形对角 16 (R8 @ 45°+90°k)', lab_off=(0, 4.5)),
        dict(tag='B', pts=[(sx * 15, sy * 15) for sx in (1, -1) for sy in (1, -1)],
             spec='Φ3.2 通 + 底面 Φ4.2×4 铜螺母孔', where='30×30 方 (±15, ±15)'),
        dict(tag='C', pts=ring(30, 8, 22.5), spec='Φ3.2 通 + 底面 Φ4.2×4.5 铜螺母孔', where='R30 @ 22.5°+45°k'),
        dict(tag='D', pts=ring(P.RING_OUTER_PCD_R, 8, 22.5), spec='Φ3.2 通 + 底面 Φ4.2×4.5 铜螺母孔',
             where=f'R{P.RING_OUTER_PCD_R:g} @ 22.5°+45°k'),
        dict(tag='E', pts=[(0, 0)], spec='底面 Φ6.2×3.5 盲窝 (不通)', where='盘心 (电机轴头)', lab_off=(-3, -3)),
    ],
    notes=['11-17 从 V1.0 hub_disc_v1_0 起改, 第 1 步只改电机 5 孔:',
           '  A 组 菱形 12×15 → 正方形对角 16 (45°); E 窝深 2.2 → 3.5',
           '其余同 V1.0: 底盘 Φ175×3, 下凸台 Φ70×2.5, 上凸台 Φ50×3.5,',
           '  外凸台环 ID155/OD175×2.5, B/C/D 组孔',
           '铜螺母: M3, 外径 4.2 孔, 全部从底面压入'],
    views=('front', 'top'), dims=[], proj='V1.2', date='2026-11-17')
SP['out'] = HERE / 'hub_disc_v1_2b_drawing.pdf'
out, png, sl = draw(SP)
print('wrote', out, sl)
# 11-17 用户: 成品放 v1.2/转子盘B/ (STL + 图纸)
import shutil
_B = HERE.parents[1] / '转子盘B'; _B.mkdir(exist_ok=True)
for _f in (SP['stl'], SP['out']):
    shutil.copy2(_f, _B / _f.name)
print('  → 转子盘B/')
