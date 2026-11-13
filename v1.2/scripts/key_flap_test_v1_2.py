# -*- coding: utf-8 -*-
"""下罩按键区试打块 key_flap_test_v1_2 (POV3D V1.2, 2026-11-13)
    cd v1.2/scripts && ../../.venv/bin/python key_flap_test_v1_2.py      (先跑 export_3mf_v1_2.py 出 glass_shroud_v1_2.step)
输出 v1.2/models/key_flap_test_v1_2/key_flap_test_v1_2_A_tie.stl / _B_support.stl + 各自 _preview.png
  B_support = 主件现用 (11-13 (四) 用户选): 无断开桥, 横缝开到两凸点边各留 0.4 (Z12.4–19.6), 切片在上舌片下加支撑后钳子拔出 = 下罩 STEP 原样截块。
  A_tie = 对照: 横缝 1.0 + 上舌片底边两侧 0.6 断开桥 (打完刀划开); 同新间距 11 (两键 Z10.5 / Z21.5)。
  A 由 B 重建: 把 B 的缝在墙段里补回实体, 再按 tie 模式切 让位腔 + 外皮孔 / 缝 / 挖薄 (这一块里没有别的特征, 结果与按 tie 建整件下罩再截块相同)。

用户 11-13: 先试打舌片。= 最终下罩实体 (models/glass_shroud_v1_2/glass_shroud_v1_2.step, 装配坐标) ∩ 盒子:
  x 覆盖 H 形舌片 (竖槽 x5.25–12.75) + 4 个导光柱孔 (x−11..3, Φ3.0) 外扩 5; y 85..112 (墙全厚 r90.8–110 + 让位腔); Z0–32。
  保留原 Z0 底面 ⇒ 跟真件一样正立打印 (含让位腔 45° 屋顶)。不进装配 / check。
"""
import math
from pathlib import Path

from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepCheck import BRepCheck_Analyzer

from helpers import read_step, bbox
import key_bracket_v1_2 as KBR

V12 = Path(__file__).resolve().parents[1]
OUT = V12 / 'models' / 'key_flap_test_v1_2'
SRC = V12 / 'models' / 'glass_shroud_v1_2' / 'glass_shroud_v1_2.step'
MARGIN = 5.0


def coupon(cp, r, tag, x0, x1):
    f = r['flap']
    assert BRepCheck_Analyzer(cp).IsValid()
    v = KBR.vol(cp); b = bbox(cp)
    KBR.write_stl(cp, OUT / f'key_flap_test_v1_2_{tag}.stl')
    # 打印时间粗估: 0.4 嘴 0.2 层, 小件多薄壁 / 窄缝有效挤出 ≈4 mm³/s + 每层换层 ≈2 s (100% 实心上限; 支撑另计)
    t_min = v / 4.0 / 60 + (b[5] - b[2]) / 0.2 * 2 / 60
    plt = KBR._font()
    fig, axs = plt.subplots(1, 3, figsize=(18, 7), dpi=100)
    U, V = (x0 - 1, x1 + 1), (84, 112)
    for ax, z in zip(axs[:2], (13.0, 19.0)):
        ax.imshow(KBR.raster([(cp, KBR.C_SH)], ('z', z), U, V, res=0.1), origin='lower', extent=(*U, *V), interpolation='nearest')
        ax.invert_xaxis(); ax.set_title(f'俯视截面 Z{z:g} (外面在上)', fontsize=10); ax.set_xlabel('x (翻转 = 外面看)'); ax.set_ylabel('y'); ax.grid(alpha=.25)
    U3, V3 = (84, 112), (-1, 33)
    axs[2].imshow(KBR.raster([(cp, KBR.C_SH)], ('x', f['recess_x'][0] + f['slot'] / 2), U3, V3, res=0.1), origin='lower', extent=(*U3, *V3), interpolation='nearest')
    axs[2].set_title(f"侧视截面 x={f['recess_x'][0] + f['slot'] / 2:g} (过竖缝; 外面在右)", fontsize=10); axs[2].set_xlabel('y'); axs[2].set_ylabel('Z (打印朝上)'); axs[2].grid(alpha=.25)
    how = (f"横缝 Z{f['bar_z'][0]:g}–{f['bar_z'][1]:g} + 断开桥 Z{f['tie_z'][0]:g}–{f['tie_z'][1]:g} ×2 (打完刀划开)" if f['mode'] == 'tie'
           else f"横缝 Z{f['bar_z'][0]:.1f}–{f['bar_z'][1]:.1f} (高 {f['bar_z'][1] - f['bar_z'][0]:.1f}), 无断开桥 —— 上舌片下加支撑, 钳子拔出")
    fig.suptitle(f"下罩按键区试打块 {tag}  x{x0:.1f}–{x1:.1f}, Z0–32 (原底面贴床正立打印)  体积 {v / 1000:.2f} cm³, 估时 ≈{t_min:.0f} min\n"
                 f"缝宽 {f['slot']:g}; {how}; 导光柱孔 Φ{r['holes'][0][2]:g} ×4; 弹性力 上 {f['F_top']:g} N / 下 {f['F_bot']:g} N", fontsize=11)
    fig.tight_layout(); fig.savefig(OUT / f'key_flap_test_v1_2_{tag}_preview.png'); plt.close(fig)
    print(f'{tag}: bbox {[round(q, 2) for q in b]}  体积 {v / 1000:.2f} cm3  估时 ≈{t_min:.0f} min  横缝 {f["bar_z"]}  断开桥 {f["tie_z"]}  力 {f["F_top"]}/{f["F_bot"]} N')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rA = KBR.make_key_bracket(dict(FLAP_MODE='tie'))
    rB = KBR.make_key_bracket(dict(FLAP_MODE='support'))
    assert KBR.DEFAULTS['FLAP_MODE'] == 'support', '主件 STEP 应为 support 模式'
    f = rA['flap']
    xs = [f['recess_x'][0], f['recess_x'][1]] + [x + s * d / 2 for x, _, d in rA['holes'] for s in (1, -1)]
    x0, x1 = min(xs) - MARGIN, max(xs) + MARGIN
    o = BRepAlgoAPI_Common(read_step(SRC), KBR.box(x0, 85.0, 0.0, x1, 112.0, 32.0)); o.Build(); assert o.IsDone()
    cB = KBR.clean(o.Shape())                                           # 主件 (support 模式) 原样截块
    P = rA['params']
    seg = KBR.cut(KBR.cyl(0, 0, 2 * P['SH_OUT'], 0, 32.0), KBR.cyl(0, 0, 2 * P['SPIG_IN'], -1, 33))
    fill = KBR.op(BRepAlgoAPI_Common, seg, KBR.fuse(*rB['flap']['slots']))
    cA = KBR.clean(KBR.cut(KBR.fuse(cB, fill), rA['pocket'], *rA['skin_holes']))
    coupon(cA, rA, 'A_tie', x0, x1)
    coupon(cB, rB, 'B_support', x0, x1)


if __name__ == '__main__':
    main()
