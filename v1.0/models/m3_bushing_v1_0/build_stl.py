"""
m3_bushing_v1_0 —— SoC 转接板 Φ4 孔 → M3 转接套 (2026-11-05 用户)

  · 套管: 外 Φ4 (= 板孔, 零间隙) / 内 Φ3.2 (M3 过孔, 2026-11-05 用户 3.3→3.2), 长 = 板厚 1.6 (DR1M90 STEP 实测 1.586)
  · 凸台: Φ8 × 0.5, 卡在板面上不让套掉下去
  ⚠ 套管壁厚只有 (4−3.2)/2 = 0.40 mm, = 0.4 喷嘴一条线宽: FDM 打出来可能只剩一圈或断掉。
零件系: 凸台底面 Z0 (打印: 凸台朝下平放), 套管向 +Z。
"""
import sys
from pathlib import Path

import manifold3d as m3d

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from params_v1_0 import write_stl  # noqa: E402

SLEEVE_OD, BORE_D = 4.0, 3.2
FLANGE_D, FLANGE_T = 8.0, 0.5
SLEEVE_L = 1.6                       # = 板厚
SEG = 96

body = m3d.Manifold.cylinder(FLANGE_T, FLANGE_D / 2, FLANGE_D / 2, SEG) + \
    m3d.Manifold.cylinder(FLANGE_T + SLEEVE_L, SLEEVE_OD / 2, SLEEVE_OD / 2, SEG)
body = body - m3d.Manifold.cylinder(10, BORE_D / 2, BORE_D / 2, SEG).translate((0, 0, -5))

out = Path(__file__).with_name("m3_bushing_v1_0.stl")
v = write_stl(body, out, "POV3D m3_bushing_v1_0")
n = len(body.to_mesh().tri_verts)
assert out.stat().st_size == 84 + 50 * n
print(f"wrote {out.name}: bbox {v.min(0).round(3)} .. {v.max(0).round(3)}, vol {body.volume():.1f} mm3, "
      f"壁厚 {(SLEEVE_OD - BORE_D) / 2:.2f}")
