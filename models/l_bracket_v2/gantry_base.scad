// gantry_base — v2 屏幕支架: 门形底座 A/B (与 build_base.py 同参)
// 局部系 = 盘坐标系, Z0 = 盘顶面。A(+Y)/B(−Y) 互为镜像左右手件。
// 连接 = 贯通螺丝: 沉头 M3×20 穿 板(6)+塔(10), 塔背面垫片+螺母 (无嵌件)。

SCREEN_T = 7.27;  FIN_T = 6;
FIN_X0 = -SCREEN_T - FIN_T;    // -13.27 塔前面
M3 = 3.2;
FOOT_T = 4;  FOOT_HX = 36;  FOOT_Y0 = 63.5;  FOOT_Y1 = 83.5;  // 外缘平直 (弧裁已改平)
DISC_R = 85;  RIM_R = 77.5;
TWR_Y0 = 63.5;  TWR_Y1 = 78.5;  TWR_TOP = 90;
TWR_D = 10;  TWR_XB = FIN_X0 - TWR_D;          // -23.27 直背 (坐螺母)
// (加强墩已删 2026-07-03: 压住后脚孔 (-29.66,±71.6), 脚螺丝从上打不进)
WALL_T = 5;                                     // 外侧筋墙 (外面与脚外缘共面 = 打印底面)
WALL_PTS = [[-36,4],[36,4],[-13.27,90],[-23.27,90]];   // 满三角 (内侧小筋已删)
JOINT_Y = 71;  JOINT_Z = [28, 56, 84];

module piece(s) {   // s = +1 (A) / -1 (B)
    difference() {
        union() {
            translate([-FOOT_HX, s > 0 ? FOOT_Y0 : -FOOT_Y1, 0])   // 脚 (矩形, 外缘平直)
                cube([2*FOOT_HX, FOOT_Y1 - FOOT_Y0, FOOT_T]);
            // 塔柱 (直背方柱)
            translate([0, s > 0 ? TWR_Y1 : -TWR_Y0, 0]) rotate([90, 0, 0])
                linear_extrude(TWR_Y1 - TWR_Y0)
                    polygon([[TWR_XB, FOOT_T], [FIN_X0, FOOT_T], [FIN_X0, TWR_TOP],
                             [TWR_XB, TWR_TOP]]);
            // 外侧筋墙 (满三角, 塔顶直边拉到脚两端)
            translate([0, s > 0 ? FOOT_Y1 : -TWR_Y1, 0]) rotate([90, 0, 0])
                linear_extrude(WALL_T) polygon(WALL_PTS);
        }
        for (a = [67.5, 112.5])   // 2 脚孔 (借盘环孔)
            translate([RIM_R*cos(a), s*RIM_R*sin(a), -1])
                cylinder(h = FOOT_T + 2, d = M3, $fn = 32);
        for (z = JOINT_Z)         // 3 贯通连接孔
            translate([TWR_XB - 1, s*JOINT_Y, z]) rotate([0, 90, 0])
                cylinder(h = TWR_D + 2, d = M3, $fn = 32);
    }
}

piece(1);    // A (+Y)
piece(-1);   // B (−Y)
