// POV 3D 电机垫片 motor_shim_v4  (2026-09-03)
// 垫在 baseplate_collar_v4 凸台内腔底面 (装配 Z=5) 上, 把 C4110 抬高 thick。
// 与 build_stl.py 的参数必须一致 (本文件是复刻不是 import)。

boss_id        = 55;      // 复刻自 baseplate_collar_v4: 凸台内孔
m3_rot         = 0;       // 电机孔整组转角
m3_diag        = 25;      // 电机孔对角间距
center_cb_diam = 12;      // 底盘顶面中央沉孔直径

thick     = 2;                        // 2026-09-03 用户指定
od        = 54;                       // 2026-09-03 用户指定
clear_rad = (boss_id - od) / 2;       // 派生: 0.5 单边隙
m3_diam   = 3.4;                      // 过孔 (底盘上是 Φ3.2, 这里放 0.2)
center_d  = center_cb_diam;           // 12

m3_off = m3_diag / sqrt(2) / 2;       // 8.8388

module motor_shim_v4() {
    difference() {
        cylinder(h = thick, d = od, $fn = 192);

        // 中央 Φ12 通孔
        translate([0, 0, -1])
            cylinder(h = thick + 2, d = center_d, $fn = 48);

        // 4 × Φ3.4 电机过孔 (对角 25)
        rotate([0, 0, m3_rot])
            for (sx = [-1, 1], sy = [-1, 1])
                translate([sx * m3_off, sy * m3_off, -1])
                    cylinder(h = thick + 2, d = m3_diam, $fn = 48);
    }
}

motor_shim_v4();
