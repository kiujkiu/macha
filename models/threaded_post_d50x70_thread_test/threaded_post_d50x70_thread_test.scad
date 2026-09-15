// 螺纹试打件 threaded_post_d50x70_thread_test  (2026-09-14)
// = 母件 threaded_post_d50x70 在顶板底面横切只留上面: Φ50×2.52 实心圆片 (母件顶板) + 整段螺纹柱 (高 15, 中空壁厚 3)。
// 螺纹牙型/打印间隙/倒角/内孔全部来自母件 SCAD, 母件改参数这里自动同步。
// 与 build_stl.py 一致: 切面平移到 Z=0 贴床, 螺纹朝上。

use <../threaded_post_d50x70/threaded_post_d50x70.scad>

base_h    = 70;   // 母件下部圆柱高 (须与母件一致)
base_keep = 2.52; // 下部圆柱保留高度 = 母件顶板厚 plate_t (须与母件同步, 否则切进腔/过渡区)
z_top     = 85;   // 母件总高
z_cut     = base_h - base_keep;

translate([0, 0, -z_cut])
    intersection() {
        threaded_post_d50x70();
        translate([-30, -30, z_cut]) cube([60, 60, z_top - z_cut + 5]);
    }
