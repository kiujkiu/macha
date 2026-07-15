// gantry_v3 — v3 双面屏支架: 门形底座 (与 build_gantry.py 同参, 2026-07-10)
// 局部系 = 盘坐标系, Z0 = 盘顶面。
// **同一件打印 2 次**, 装配对角放: 件1 脚在 +Y (塔在 -X 侧),
// 件2 = 件1 绕 Z 转 180° (脚 -Y, 塔 +X 侧)。180° 旋转对称 → 动平衡好;
// 盘 R77.5 环孔为 45° 阵列, 转 180° 后脚孔仍落在既有孔上。
// 连接 = 贯通螺丝: M3×18/20 穿 板(6)+塔(10)=16, 塔背垫片+螺母 (无嵌件无沉头)。
// 打印: 侧躺, 外侧面 (Y=93 平面) 朝下贴床, 零支撑。

PLATE_HT = 3;                     // 板半厚 (screen_plate_v3 板 X -3..+3)
FIN_X0 = -PLATE_HT;               // -3 塔柱前面 (= 板面)
M3 = 3.2;
FOOT_T = 4;  FOOT_HX = 36;  FOOT_Y0 = 63.5;  FOOT_Y1 = 93;   // 外缘随筋墙外移
DISC_R = 85;  RIM_R = 77.5;
TWR_Y0 = 76;  TWR_Y1 = 88;  TWR_TOP = 90;   // 塔宽 12, 中心 82 (屏边 75 留 1)
TWR_D = 10;  TWR_XB = FIN_X0 - TWR_D;        // -13 直背 (平面, 坐螺母)
WALL_T = 5;                                  // 外侧筋墙 (外面与脚外缘共面 = 打印底面)
WALL_PTS = [[-36, 4], [36, 4], [-3, 90], [-13, 90]];   // 满三角 (CCW)
JOINT_Y = 82;  JOINT_Z = [28, 56, 84];       // = 塔柱中心

module gantry_v3() {
    difference() {
        union() {
            translate([-FOOT_HX, FOOT_Y0, 0])            // 脚 (矩形, 外缘平直)
                cube([2*FOOT_HX, FOOT_Y1 - FOOT_Y0, FOOT_T]);
            // 塔柱 (直背方柱, 前面 X=-3 贴板面)
            translate([0, TWR_Y1, 0]) rotate([90, 0, 0])
                linear_extrude(TWR_Y1 - TWR_Y0)
                    polygon([[TWR_XB, FOOT_T], [FIN_X0, FOOT_T],
                             [FIN_X0, TWR_TOP], [TWR_XB, TWR_TOP]]);
            // 外侧筋墙 (满三角, 塔顶直边拉到脚两端)
            translate([0, FOOT_Y1, 0]) rotate([90, 0, 0])
                linear_extrude(WALL_T) polygon(WALL_PTS);
        }
        for (a = [67.5, 112.5])   // 2 脚孔 (借盘 R77.5 环孔)
            translate([RIM_R*cos(a), RIM_R*sin(a), -1])
                cylinder(h = FOOT_T + 2, d = M3, $fn = 32);
        for (z = JOINT_Z)         // 3 贯通连接孔
            translate([TWR_XB - 1, JOINT_Y, z]) rotate([0, 90, 0])
                cylinder(h = TWR_D + 2, d = M3, $fn = 32);
    }
}

gantry_v3();                       // 件1 (脚 +Y)
// 件2 = 同一件绕 Z 转 180° (装配示意, 打印时注释掉):
// rotate([0, 0, 180]) gantry_v3();
