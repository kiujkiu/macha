// screen_solder_jig — 焊接时给 screen_150x169 定位的 5 面托盘 (2026-07-21 用户)
// 底 + 4 壁, 开口朝上 (+Z); 屏正面朝下落入内腔, 四壁锁位, 背面朝上焊。
// 参数与 build_stl.py 保持一致 (改尺寸两处同步)。

// ===== Parameters =====
cav_w  = 150.3;    // X — 屏宽 (150→150.3, +0.3 间隙)
cav_h  = 169.05;   // Y — 屏高 (168.75→169.05, +0.3 间隙)
depth  = 15.0;     // Z — 内腔深
wall   = 4.0;      // 壁厚
floor_t = 3.0;     // 底厚

hole_d  = 3.2;             // M3 通孔 (端壁)
hole_xs = [-64, 0, 64];    // X 间距 64
hole_z  = floor_t + 6.6;   // 9.6 — 孔心距内腔底 6.6

sq_side = 40.0;            // 底面 4×40×40 方孔 (2×2 对称)
sq_cx   = 36.0;
sq_cy   = 42.0;
sq_centers = [[-sq_cx,-sq_cy],[-sq_cx,sq_cy],[sq_cx,-sq_cy],[sq_cx,sq_cy]];

$fn = 48;
slop = 0.1;

out_w = cav_w + 2*wall;    // 158
out_h = cav_h + 2*wall;    // 176.75
out_z = depth + floor_t;   // 18

module screen_solder_jig() {
    difference() {
        // outer solid block, centered in XY, bottom at Z=0
        translate([-out_w/2, -out_h/2, 0])
            cube([out_w, out_h, out_z]);

        // pocket cavity, centered, open at +Z
        translate([-cav_w/2, -cav_h/2, floor_t])
            cube([cav_w, cav_h, depth + slop]);

        // 3 M3 through-holes along Y — each pierces BOTH ±Y walls
        for (x = hole_xs)
            translate([x, 0, hole_z])
                rotate([90, 0, 0])
                    cylinder(h = out_h + 4, d = hole_d, center = true);

        // 4 × 40×40 square through-holes in the floor (2×2 对称)
        for (c = sq_centers)
            translate([c[0] - sq_side/2, c[1] - sq_side/2, -slop])
                cube([sq_side, sq_side, floor_t + 2*slop]);
    }
}

screen_solder_jig();
