# 转子盘B (11-17 晚 第一版)

| 文件 | 件 | 说明 |
|---|---|---|
| fr4_plate_v1_2b.dxf / _drawing.pdf / .stl | 玻纤底板 | 无铜 FR4 Φ165×3, 板厂件; DXF 下单, 沉孔 Φ7.2×1.5 按图纸控深 |
| rim_ring_v1_2b.stl / .step | 承载盘 (并入毂盘) | STL = 打印姿态 (托盘顶面朝下), STEP = 装配坐标 |
| screen_holder_v1_2b_a / _b .stl / .step | 屏幕固定件 +x / −x | 两件互为镜像 (灯板偏心 y−4.36) |
| rotor_shroud_b_a / _b _v1_2b .stl / .step / _drawing.pdf | 转子罩 +y / −y 半 | 2 片 (含顶盖), 沿灯板线分; STL = 打印姿态 (罩顶朝下); 各 2 颗 M3×8 锁屏幕固定件 |
| rotor_b_asm.step | 装配 | 玻纤板 + 承载盘 + 两个固定件 + 线圈占位 |

生成脚本: `v1.2/scripts/rotor_b_v1_2.py` (承载盘/固定件/校核), `v1.2/models/fr4_plate_v1_2b/build.py` (玻纤板)。
罩子: `v1.2/scripts/rotor_shroud_b_v1_2.py` (11-17 夜, 干涉 0)。`作废_11-17/` = 先前从 V0.4 拷的毂盘/承载盘 (已被单件承载盘取代)。
