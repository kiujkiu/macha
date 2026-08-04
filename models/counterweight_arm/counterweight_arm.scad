// counterweight_arm — 转子配重臂 (与 build_stl.py 同参, 2026-08-03)
// v3 / v3.1 共用一件。坐标系 = 罩子零件系 XY, Z0 = 罩顶面 (罩零件系 Z50 / 装配 Z92.2)。
// 骑在罩顶跨接缝: 4 颗 M3 里 2 颗进 shroud_half_A、2 颗进 shroud_half_B
// ⇒ 本件顺带把两半在顶部连成一体。
// 打印: 底面贴床, 零支撑 (全件等厚, 无桥接)。⚠ 底面全贴罩顶 → 板下无空间,
// M6 五金全部放板上面, 螺杆往下伸出量必须为 0。

r_out    = 85;          // 罩外径 R = 旋转包络上限 (用户: 不超 Φ170)
base_t   = 6;           // 底板厚
x_in     = -44;         // 内端
hw       = 26;          // 半宽 (2026-08-04 用户"做宽一点": 19 → 26)

m3_xs    = [-50, -72];  // 对罩顶 4 个铜花螺母位
m3_y     = 14;
m3_d     = 3.4;

m6_x = -77.7; m6_y = 6.5;   // 2× M6 光孔, 孔距 = 2*m6_y = 13 (2026-08-04 二改)
m6_d        = 6.5;      // 光孔 — 凸台与六角窝已取消

module counterweight_arm() {
  difference() {
    intersection() {                                     // 底板 (外缘随 R85 裁), 全件等厚
      translate([-r_out-1, -hw, 0]) cube([x_in + r_out + 1, 2*hw, base_t]);   // 42 长
      cylinder(h = base_t, r = r_out, $fn = 256);
    }
    for (s = [1,-1])                                     // 2× M6 光孔 (孔距 13)
      translate([m6_x, s*m6_y, -1]) cylinder(h = base_t + 2, d = m6_d, $fn = 48);
    for (x = m3_xs) for (s = [1,-1])                     // M3 ×4
      translate([x, s*m3_y, -1]) cylinder(h = base_t + 2, d = m3_d, $fn = 32);
  }
}

counterweight_arm();
