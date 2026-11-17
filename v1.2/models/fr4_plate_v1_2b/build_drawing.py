"""fr4_plate_v1_2b 图纸 (2026-11-17): 沿用 V1.0 出图器。先跑同目录 build.py。成品拷到 v1.2/转子盘B/。"""
import sys, shutil
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'v1.0' / 'models')); sys.path.insert(0, str(HERE))
from drawing_v1_0 import draw  # noqa: E402
from build import OD, T, M3_D, CB_D, CB_H, CENTER_D, HOLES_IN, HOLES_OUT, HOLES_MOTOR  # noqa: E402
SP = dict(
    stl=HERE / 'fr4_plate_v1_2b.stl', code='fr4_plate_v1_2b', short=f'玻纤加强板 Φ{OD:g}×{T:g}', qty='1',
    title=f'转子盘B 玻纤加强板 (无铜 FR4 Φ{OD:g}×{T:g}, 垫毂盘底面)',
    orient='板件 (无打印); 图示 = 装配姿态, 底面 Z0 (沉孔面) 朝下贴电机', src='v1.2/models/fr4_plate_v1_2b/fr4_plate_v1_2b.stl',
    origin_note='原点 = 盘心 (= 毂盘 hub_disc_v1_2b 零件系), 底面 Z0。',
    holes=[
        dict(tag='A', pts=HOLES_IN, spec=f'M3 通 Φ{M3_D:g} + 底面 Φ{CB_D:g}×{CB_H:g} 平底沉孔', where='内圈 R30 @ 22.5°+45°k'),
        dict(tag='B', pts=HOLES_OUT, spec=f'M3 通 Φ{M3_D:g} + 底面 Φ{CB_D:g}×{CB_H:g} 平底沉孔', where='外圈 R82.5 @ 22.5°+45°k'),
        dict(tag='C', pts=HOLES_MOTOR, spec=f'M3 通 Φ{M3_D:g} (不沉)', where='电机 4 孔: 正方形对角 16 (R8 @ 45°+90°k)', lab_off=(0, 4.5)),
        dict(tag='D', pts=[(0, 0)], spec=f'M5 通 Φ{CENTER_D:g}', where='盘心 (电机轴头)', lab_off=(-3, -3)),
    ],
    notes=[f'材料: FR4 玻纤板 厚 {T:g} ±0.1, 无铜 (不覆铜或全蚀刻; 带铜在无线线圈旁会发热、吃功率)',
           'A/B 16 孔: 螺丝从下往上, 穿本板 + 毂盘, 锁进承载盘铜螺母;',
           f'  沉孔深 {CB_H:g}: 只藏得下头高 ≤{CB_H:g} 的超薄头 M3',
           'C 4 孔: 电机螺丝从毂盘顶面往下拧, 穿本板进电机 (比无板时加长 2)',
           f'外圈沉孔边到板边 {OD / 2 - 82.5 - CB_D / 2:.1f}; 重量约 87 g (密度 1.85 g/cm3)',
           '下单: DXF 同目录 (OUTLINE 外形 / HOLES 通孔 / CB_BOTTOM 沉孔示意), 沉孔按本图底面控深'],
    views=('front', 'top'), dims=[], proj='V1.2', date='2026-11-17', material='FR4 无铜')
SP['out'] = HERE / 'fr4_plate_v1_2b_drawing.pdf'
out, png, sl = draw(SP)
print('wrote', out, sl)
_B = HERE.parents[1] / '转子盘B'; _B.mkdir(exist_ok=True)
for _f in (SP['stl'], SP['out'], HERE / 'fr4_plate_v1_2b.dxf'):
    shutil.copy2(_f, _B / _f.name)
print('  → 转子盘B/')
