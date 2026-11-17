// 地脚垫高圆筒 leg_riser_d55x60  (2026-09-14)
// 圆筒 外径 55 / 内径 46 / 高 60; 内部米字加强筋厚 5 (0/45/90/135°),
// 筋从底面做到 Z=55, 最上面 5mm 不做加强。
// 与 build_stl.py 的参数必须一致 (本文件是复刻不是 import)。

od        = 55;   // 外径
id        = 46;   // 内径
h         = 60;   // 总高
rib_t     = 5;    // 米字加强筋厚度
top_clear = 5;    // 最上面不做加强的高度

rib_h = h - top_clear;          // 55
rib_l = (id + od) / 2;          // 筋条总长, 两端伸进壁厚中线

module leg_riser_d55x60() {
    difference() {
        cylinder(h = h, d = od, $fn = 256);
        translate([0, 0, -1]) cylinder(h = h + 2, d = id, $fn = 256);
    }
    for (a = [0, 45, 90, 135])
        rotate([0, 0, a])
            translate([-rib_l / 2, -rib_t / 2, 0])
                cube([rib_l, rib_t, rib_h]);
}

leg_riser_d55x60();
