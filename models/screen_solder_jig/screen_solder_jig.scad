// screen_solder_jig — 焊接时给 screen_150x169 定位的 5 面托盘 (2026-07-21 用户)
// 底 + 4 壁, 开口朝上 (+Z); 屏正面朝下落入内腔, 四壁锁位, 背面朝上焊。
// 参数与 build_stl.py 保持一致 (改尺寸两处同步)。

// ===== Parameters =====
cav_w  = 150.0;    // X — 屏宽 (screen_150x169: W=150)
cav_h  = 168.75;   // Y — 屏高 (用户给定 168.75)
depth  = 15.0;     // Z — 内腔深
wall   = 4.0;      // 壁厚
floor_t = 3.0;     // 底厚

hole_d  = 3.2;             // M3 通孔
hole_xs = [-64, 0, 64];    // X 间距 64
hole_z  = floor_t + 6.6;   // 9.6 — 孔心距内腔底 6.6

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
    }
}

screen_solder_jig();
