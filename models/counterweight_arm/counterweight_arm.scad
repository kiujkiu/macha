// counterweight_arm — 转子配重臂 (与 build_stl.py 同参, 2026-08-03)
// v3 / v3.1 共用一件。坐标系 = 罩子零件系 XY, Z0 = 罩顶面 (罩零件系 Z50 / 装配 Z92.2)。
// 骑在罩顶跨接缝: 4 颗 M3 里 2 颗进 shroud_half_A、2 颗进 shroud_half_B
// ⇒ 本件顺带把两半在顶部连成一体。
// 打印: **翻面 — 顶面贴床, 带沉孔的底面朝上** ⇒ 沉孔口朝上, 零支撑零桥接。
// ⚠ 底面全贴罩顶 → 板下无空间, M6 五金全部放板上面, 螺杆往下伸出量必须为 0
// ⇒ M6 用大扁头 (Φ12.5×3) 从下面插入沉进底面沉孔, 螺杆朝上叠垫圈/螺母。

r_out    = 85;          // 罩外径 R = 旋转包络上限 (用户: 不超 Φ170)
base_t   = 6;           // 底板厚
x_in     = -44;         // 内端
hw       = 26;          // 半宽 (2026-08-04 用户"做宽一点": 19 → 26)

m3_xs    = [-50, -72];  // 对罩顶 4 个铜花螺母位
m3_y     = 14;
m3_d     = 3.4;

// 2× M6 光孔 (2026-08-27 三改: 上下 → 左右, 上下居中 Y=0, 孔距 13, 左孔离左边缘 8)
m6_edge  = 8;                                   // 左孔中心离左边缘 (Y=0 处 = X -r_out)
m6_pitch = 13;                                  // 孔距 (沿 X)
m6_xs    = [-r_out + m6_edge, -r_out + m6_edge + m6_pitch];   // = [-77, -64]
m6_y     = 0;
m6_d     = 6.5;         // 光孔
m6_cb_d  = 12.5;        // 沉孔 Φ (M6 大扁头)
m6_cb_h  = 3;           // 沉孔深, 开在**底面**

module counterweight_arm() {
  difference() {
    intersection() {                                     // 底板 (外缘随 R85 裁), 全件等厚
      translate([-r_out-1, -hw, 0]) cube([x_in + r_out + 1, 2*hw, base_t]);   // 42 长
      cylinder(h = base_t, r = r_out, $fn = 256);
    }
    for (x = m6_xs) {                                    // 2× M6 光孔 (孔距 13, Y=0)
      translate([x, m6_y, -1]) cylinder(h = base_t + 2, d = m6_d, $fn = 48);
      translate([x, m6_y, -1]) cylinder(h = m6_cb_h + 1, d = m6_cb_d, $fn = 64);  // 底面沉孔
    }
    for (x = m3_xs) for (s = [1,-1])                     // M3 ×4
      translate([x, s*m3_y, -1]) cylinder(h = base_t + 2, d = m3_d, $fn = 32);
  }
}

counterweight_arm();
