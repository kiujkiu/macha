// screen_plate_v3 — v3 双面屏支架两件套: 中央屏幕板 (与 build_plate.py 同参, 2026-07-10)
// 局部系 = 盘坐标系 (未转45°), Z0 = 盘顶面; 板厚 6 居中到轴平面: X -3..+3
// 两面各贴一块屏 (前屏 X-3 面, 后屏 X+3 面); 屏幕孔/接口窗两侧屏共用 (对头短螺丝)
// 主体 Y ±88 × Z 21..213.5; 顶部中央凸舌 ±40 × Z 213.5..235 (top_cap_v3 双腿夹持)

FIN_T    = 6;
FIN_X0   = -FIN_T / 2;         // -3 (居中)
FIN_HW   = 88;                 // 半宽 (156→176, 塔柱外移)
PLATE_Z0 = 21;                 // 翼板底边 (堆叠顶 + 余量)
NOTCH_HW = 60; NOTCH_TOP = 50;           // 底部中央让位缺口 (顶 = 盘面+50 = 屏底沿)
FIN_TOP  = 213.5;              // 主体顶 (= 50 + 10.5 + 147 + 6)
TAB_HW   = 40;  TAB_TOP = 235;           // 顶部凸舌 (屏顶 219 之上; 帽板底 238 留 3)
CAP_HOLE_Y = 22; CAP_HOLE_Z = [225.3, 230.8];  // 顶帽夹舌孔 (装配系 271.0 / 276.5)
WIN_HW = 27; WIN_Z0 = 93; WIN_Z1 = 127;  // 接口窗 + 顶 R27 拱 (圆心 (0,127))
M3 = 3.2;
JOINT_Y = 82;  JOINT_Z = [28, 56, 84];   // 底座连接孔 (= gantry_v3 塔柱中心)
SCREEN_HOLES = [[-52.5, 60.5], [52.5, 60.5], [-49.975, 207.5], [49.975, 207.5]];

module plate_profile() {   // (Y,Z)
    difference() {
        union() {
            translate([-FIN_HW, PLATE_Z0]) square([2*FIN_HW, FIN_TOP - PLATE_Z0]);
            translate([-TAB_HW, FIN_TOP - 1]) square([2*TAB_HW, TAB_TOP - FIN_TOP + 1]);  // 顶舌
        }
        union() {  // 接口窗 + 顶拱
            translate([-WIN_HW, WIN_Z0]) square([2*WIN_HW, WIN_Z1 - WIN_Z0]);
            translate([0, WIN_Z1]) circle(r = WIN_HW, $fn = 96);
        }
        translate([-NOTCH_HW, PLATE_Z0-1]) square([2*NOTCH_HW, NOTCH_TOP-PLATE_Z0+1]);  // 底部中央缺口
        for (h = SCREEN_HOLES) translate(h) circle(d = M3, $fn = 32);                   // 两侧屏共用
        for (z = JOINT_Z) for (sy = [-1, 1]) translate([sy*JOINT_Y, z]) circle(d = M3, $fn = 32);
        for (z = CAP_HOLE_Z) for (sy = [-1, 1]) translate([sy*CAP_HOLE_Y, z]) circle(d = M3, $fn = 32);
    }
}

translate([FIN_X0, 0, 0]) rotate([90, 0, 90]) linear_extrude(FIN_T) plate_profile();
