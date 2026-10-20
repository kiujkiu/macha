// POV 3D 转子侧垫片 hub_shim_v4  (2026-09-03)
// 垫在电机 bell top 与 hub_disc 底面之间 (motor_shim_v4 的转子侧对应件)。
// 与 build_stl.py 的参数必须一致 (本文件是复刻不是 import)。

// ---- 复刻自 models/hub_disc/build_stl.py ----
hub_base_od     = 165;
hub_m3_diam     = 3.2;
diag_x          = 12;     // pattern A 菱形对角 X
diag_y          = 15;     // pattern A 菱形对角 Y
center_cb_diam  = 6.2;    // hub 底面中心盲窝 (深 2.2)

// ---- 垫片自身 ----
thick    = 2;                  // 2026-09-03 用户指定
od       = 100;                // 2026-09-03 用户指定 (「直径做 10cm」)
m3_diam  = 3.4;                // 过孔 (hub 上是 Φ3.2, 这里放 0.2)
center_d = center_cb_diam;     // 6.2

pattern_a = [[ diag_x/2, 0], [-diag_x/2, 0],
             [ 0, diag_y/2], [ 0, -diag_y/2]];

module hub_shim_v4() {
    difference() {
        cylinder(h = thick, d = od, $fn = 192);

        // 中央 Φ6.2 通孔 (对 hub 底面中心窝)
        translate([0, 0, -1])
            cylinder(h = thick + 2, d = center_d, $fn = 48);

        // 4 × Φ3.4 菱形过孔 (对角 12×15, 对电机 bell 的 4 孔菱形)
        for (p = pattern_a)
            translate([p[0], p[1], -1])
                cylinder(h = thick + 2, d = m3_diam, $fn = 48);
    }
}

hub_shim_v4();
