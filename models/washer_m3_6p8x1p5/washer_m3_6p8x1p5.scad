// POV 3D 平垫圈 washer_m3_6p8x1p5  (2026-09-07)
// 圆环片: 外径 6.8 / 内径 3.3 (M3 过孔) / 厚 1.5。
// 与 build_stl.py 的参数必须一致 (本文件是复刻不是 import)。

od    = 6.8;    // 外径
id    = 3.3;    // 内径 (M3 螺杆过孔)
thick = 1.5;    // 厚度

module washer_m3_6p8x1p5() {
    difference() {
        cylinder(h = thick, d = od, $fn = 128);
        translate([0, 0, -1])
            cylinder(h = thick + 2, d = id, $fn = 96);
    }
}

washer_m3_6p8x1p5();
