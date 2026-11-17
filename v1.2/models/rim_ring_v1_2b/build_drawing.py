"""rim_ring_v1_2b 图纸 (2026-11-17): 沿用 V1.0 出图器, 孔表同 rim_ring_v1_0 (第 1 步本件无改动)。先跑同目录 build_stl.py。"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
V10 = HERE.parents[2] / 'v1.0' / 'models'
sys.path.insert(0, str(V10)); sys.path.insert(0, str(HERE))
from drawing_v1_0 import draw  # noqa: E402
import params_v1_0 as P  # noqa: E402
from build_stl import BASE_HOLES, EXTRA_HOLES, HEAD_CB_XY, INSERT_D, INSERT_DEEP, RING_HOLES  # noqa: E402
xy = lambda pts: "  ".join(f"({x:.2f},{y:.2f})" for x, y in pts)  # noqa: E731
xy_lines = lambda pts, per=2: "\n".join(xy(pts[i:i + per]) for i in range(0, len(pts), per))  # noqa: E731
SP = dict(
    stl=HERE / 'rim_ring_v1_2b.stl', code='rim_ring_v1_2b', short='转子承载盘 Φ180 (V1.0 改)', qty='1',
    title='转子承载盘 (V1.0 rim_ring 起改; 11-17 第 1 步本件无改动)',
    orient='托盘面 (Z0) 贴床, 唇/凸台朝上', src='v1.2/models/rim_ring_v1_2b/rim_ring_v1_2b.stl',
    origin_note='原点 = 盘心, 托盘面 Z0 (零件系; 装机绕 X 翻转: 世界 Y = −图示 Y)。',
    holes=[
        dict(tag='A', pts=RING_HOLES[:8], spec='Φ3.2 通', where='R30 @ 22.5°+45°k'),
        dict(tag='B', pts=RING_HOLES[8:], spec='Φ3.2 通', where=f'R{P.RING_OUTER_PCD_R:g} @ 22.5°+45°k'),
        dict(tag='C', pts=EXTRA_HOLES, spec='Φ4 通', where='(R72 @ −10°)  (R56 @ −42.5°)'),
        dict(tag='D', pts=HEAD_CB_XY, spec='托盘面 Φ7.5×2 螺丝头沉孔', where='R30 @ 202.5° / 247.5°', lab_off=(-3, -3)),
        dict(tag='E', pts=BASE_HOLES, spec=f'Φ3.2 通 + 唇侧 Φ{INSERT_D:g}×{INSERT_DEEP:g} 铜螺母孔',
             where='DR1M90 底板 4 孔 (图示零件系):\n' + xy_lines(BASE_HOLES)),
    ],
    notes=['11-17 从 V1.0 rim_ring_v1_0 原样起改 (与 hub_disc_v1_2b 配对)',
           '第 1 步 电机 5 孔只在毂盘: 本件中心 ID50 让毂盘 Φ50 上凸台穿过,',
           '  电机螺丝头沉孔 (外缘 r11.5) / 中心窝都在 Φ50 内, 本件无需改',
           '其余同 V1.0: 托盘 Φ180×5, 外唇 ID175/OD180, 内凸台环 OD80/ID70×2.5'],
    views=('front', 'top'), dims=[], proj='V1.2', date='2026-11-17')
SP['out'] = HERE / 'rim_ring_v1_2b_drawing.pdf'
out, png, sl = draw(SP)
print('wrote', out, sl)
# 11-17 用户: 成品放 v1.2/转子盘B/ (STL + 图纸)
import shutil
_B = HERE.parents[1] / '转子盘B'; _B.mkdir(exist_ok=True)
for _f in (SP['stl'], SP['out']):
    shutil.copy2(_f, _B / _f.name)
print('  → 转子盘B/')
