"""rim_ring_v1_2b 图纸 (2026-11-17): 沿用 V1.0 出图器, 孔表同 V0.4 rim_ring (第 1 步本件无改动)。先跑同目录 build_stl.py。"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
V10 = HERE.parents[2] / 'v1.0' / 'models'
sys.path.insert(0, str(V10)); sys.path.insert(0, str(HERE))
from drawing_v1_0 import draw  # noqa: E402
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):                # build_stl 是脚本式 (import 即重写 STL, 结果相同)
    from build_stl import (PATTERN_INNER, PATTERN_OUTER, EXTRA_HOLES, HEAD_CB_XY, HEAD_CB_D, HEAD_CB_DEEP,  # noqa: E402
                           PI_HOLES, WIFI_HOLES, PI_THRU_D, PI_INSERT_D, PI_INSERT_DEEP, BASE_OD, RIM_ID, RIM_OD)
xy = lambda pts: "  ".join(f"({x:.2f},{y:.2f})" for x, y in pts)  # noqa: E731
xy_lines = lambda pts, per=2: "\n".join(xy(pts[i:i + per]) for i in range(0, len(pts), per))  # noqa: E731
SP = dict(
    stl=HERE / 'rim_ring_v1_2b.stl', code='rim_ring_v1_2b', short=f'转子承载盘 Φ{BASE_OD:g} (V0.4 改)', qty='1',
    title='转子承载盘 (V0.4 rim_ring 起改; 11-17 第 1 步本件无改动)',
    orient='托盘面 (Z0) 贴床, 唇/凸台朝上', src='v1.2/models/rim_ring_v1_2b/rim_ring_v1_2b.stl',
    origin_note='原点 = 盘心, 托盘面 Z0 (零件系; 装机绕 X 翻转: 世界 Y = −图示 Y)。',
    holes=[
        dict(tag='A', pts=PATTERN_INNER, spec='Φ3.2 通', where='R30 @ 22.5°+45°k'),
        dict(tag='B', pts=PATTERN_OUTER, spec='Φ3.2 通', where='R77.5 @ 22.5°+45°k'),
        dict(tag='C', pts=EXTRA_HOLES, spec='Φ4 通', where='(R72 @ −10°)  (R56 @ −42.5°)'),
        dict(tag='D', pts=HEAD_CB_XY, spec=f'托盘面 Φ{HEAD_CB_D:g}×{HEAD_CB_DEEP:g} 螺丝头沉孔', where='R30 @ 202.5° / 247.5°', lab_off=(-3, -3)),
        dict(tag='P', pts=PI_HOLES, spec=f'Φ{PI_THRU_D:g} 通 + 唇侧 Φ{PI_INSERT_D:g}×{PI_INSERT_DEEP:g} 铜螺母孔', where='V0.4 pi2hub 7 孔:\n' + xy_lines(PI_HOLES)),
        dict(tag='W', pts=WIFI_HOLES, spec=f'Φ{PI_THRU_D:g} 通 + 唇侧 Φ{PI_INSERT_D:g}×{PI_INSERT_DEEP:g} 铜螺母孔', where='V0.4 wifi_shell 沿孔:\n' + xy_lines(WIFI_HOLES)),
    ],
    notes=['11-17 从 V0.4 rim_ring (现行, 与 v0.4/print 同) 原样起改, 与 hub_disc_v1_2b 配对',
           '第 1 步 电机 5 孔只在毂盘: 本件中心 ID50 让毂盘 Φ50 上凸台穿过,',
           '  电机螺丝头沉孔 (外缘 r11.5) / 中心窝都在 Φ50 内, 本件无需改',
           f'同 V0.4: 托盘 Φ{BASE_OD:g}×5, 外唇 ID{RIM_ID:g}/OD{RIM_OD:g}, 内凸台环 OD80/ID70×2.5; P/W 孔为 V0.4 原有'],
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
