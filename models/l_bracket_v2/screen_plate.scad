// screen_plate — v2 屏幕支架两件套: 屏幕板 (与 build_plate.py 同参)
// 局部系 = 盘坐标系, Z0 = 盘顶面; 板 X -13.27..-7.27, Y ±78, Z 21..213.5
// 屏底沿=盘面+50; 板底中央 |Y|≤60 (12cm) 开缺口到 盘面+50 (2026-07-03 深夜)

SCREEN_T = 7.27;
FIN_T    = 6;
FIN_X1   = -SCREEN_T;          // -7.27 前面 (贴屏背)
FIN_X0   = FIN_X1 - FIN_T;     // -13.27
FIN_HW   = 78;   // 162→156, 让位筋墙 (2026-07-03)
PLATE_Z0 = 21;   // 翼板底边
NOTCH_HW = 60; NOTCH_TOP = 50;           // 底部中央让位缺口
FIN_TOP  = 213.5;
WIN_HW = 27; WIN_Z0 = 93; WIN_Z1 = 127;
M3 = 3.2;
JOINT_Y = 71;  JOINT_Z = [28, 56, 84];   // 直通孔, 无沉头 (2026-07-03)
SCREEN_HOLES = [[-52.5, 60.5], [52.5, 60.5], [-49.975, 207.5], [49.975, 207.5]];

module plate_profile() {   // (Y,Z)
    difference() {
        translate([-FIN_HW, PLATE_Z0]) square([2*FIN_HW, FIN_TOP - PLATE_Z0]);
        union() {  // 接口窗 + 顶拱
            translate([-WIN_HW, WIN_Z0]) square([2*WIN_HW, WIN_Z1 - WIN_Z0]);
            translate([0, WIN_Z1]) circle(r = WIN_HW, $fn = 96);
        }
        translate([-NOTCH_HW, PLATE_Z0-1]) square([2*NOTCH_HW, NOTCH_TOP-PLATE_Z0+1]);  // 底部中央缺口
        for (h = SCREEN_HOLES) translate(h) circle(d = M3, $fn = 32);
        for (z = JOINT_Z) for (sy = [-1, 1]) translate([sy*JOINT_Y, z]) circle(d = M3, $fn = 32);
    }
}

translate([FIN_X0, 0, 0]) rotate([90, 0, 90]) linear_extrude(FIN_T) plate_profile();
