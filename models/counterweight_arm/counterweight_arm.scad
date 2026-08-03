// counterweight_arm — 转子配重臂 (与 build_stl.py 同参, 2026-08-03)
// v3 / v3.1 共用一件。坐标系 = 罩子零件系 XY, Z0 = 罩顶面 (罩零件系 Z50 / 装配 Z92.2)。
// 骑在罩顶跨接缝: 4 颗 M3 里 2 颗进 shroud_half_A、2 颗进 shroud_half_B
// ⇒ 本件顺带把两半在顶部连成一体。
// 打印: 底面贴床, 零支撑; 六角窝顶面是 10.3 桥接 (螺栓承压台肩, 该层填充调高)。

r_out    = 85;          // 罩外径 R = 旋转包络上限 (用户: 不超 Φ170)
base_t   = 6;           // 底板厚
x_in     = -44;         // 内端
hw       = 19;          // 半宽

m3_xs    = [-50, -72];  // 对罩顶 4 个铜花螺母位
m3_y     = 14;
m3_d     = 3.4;

m6_r        = 75.5;     // M6 力臂
m6_boss_d   = 16;
m6_boss_t   = 10;
m6_d        = 6.5;
m6_hex_af   = 10.3;     // M6 六角头对边 10 + 0.3
m6_hex_h    = 4.5;      // 头高 4 + 0.5

module counterweight_arm() {
  difference() {
    union() {
      intersection() {                                   // 底板 (外缘随 R85 裁)
        translate([-r_out-1, -hw, 0]) cube([x_in + r_out + 1, 2*hw, base_t]);   // = 42
        cylinder(h = base_t, r = r_out, $fn = 256);
      }
      intersection() {                                   // M6 座凸台
        translate([-m6_r, 0, 0]) cylinder(h = m6_boss_t, d = m6_boss_d, $fn = 96);
        cylinder(h = m6_boss_t, r = r_out, $fn = 256);
      }
    }
    // M6: 底面六角窝 (卡六角头防转) + 通孔
    translate([-m6_r, 0, -1]) rotate([0,0,30])
      cylinder(h = m6_hex_h + 1, d = m6_hex_af/cos(30), $fn = 6);
    translate([-m6_r, 0, -1]) cylinder(h = m6_boss_t + 2, d = m6_d, $fn = 48);
    // M3 ×4
    for (x = m3_xs) for (s = [1,-1])
      translate([x, s*m3_y, -1]) cylinder(h = base_t + 2, d = m3_d, $fn = 32);
  }
}

counterweight_arm();
