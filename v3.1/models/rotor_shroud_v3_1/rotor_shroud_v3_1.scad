// rotor_shroud_v3_1 — v3.1 偏心屏实验 (2026-07-31)
// ⚠ 主体几何可读副本; 实际打印件以 STL 为准 (让位/布尔特征无法在 SCAD 复刻)
// rotor_shroud_v3 — v3 转子电路罩 (与 build_shroud.py 同参, 2026-07-27)。
// 零件系 = 屏局部系, Z0 = 承载面 42.2; 装配 = rotate([0,0,ROTOR_ROT-45]) + Z42.2。
// 两半对开: half="A" (+Y 半) / "B" (-Y 半)。打印: 绕 X 翻 180° 顶板贴床, 零支撑。
// ⚠ 让位 (portal_tee 脚角 / wifi 壳 / wifi 线缆出口槽 / wifi 沿 M3 头) 由 Python
//   端「障碍件 STL 膨胀 0.4 + 向下扫掠」布尔生成, 无法在 SCAD 里复刻 —— 本文件
//   只是主体几何的可读副本, 实际打印件以 shroud_half_[AB]_v3.stl 为准。

half = "A";              // "A" = +Y 半, "B" = -Y 半

od = 170; id = 164; h = 50;          // 筒 Φ170/Φ164 壁 3, 高 50
plate_t = 2; plate_z0 = h - plate_t; // 顶板 Z48..50 (2026-07-27 减重 3->2)
scr_ecc = 6.7;                       // v3.1 偏心量
scr_x0 = -7.0; scr_x1 = 13.7;        // v3.1 非对称屏缝 (同时覆盖居中与偏心)
scr_hw = 7.0;                        // 屏缝半宽 (屏半厚 6.7 + 0.3)
tee_hw = 16.3;   // v3.1: T 顶托加宽到 ±16 tee_y0 = 59.601;      // 加宽段 (让 T 件梯形顶托 20 宽)
slot_y1 = 78;                        // 屏缝末端, 之外顶板做实 (端部封口)
col_r = 77.5; col_d = 14;            // 沉井立柱
col_ang = [22.5, 157.5, 202.5, 337.5];
well_d = 9; floor_t = 3; bore_d = 3.4; lead_d = 5; lead_h = 0.8;
bol_r_in = 76; bol_hw = 4;           // 接缝 bolster (内壁局部加厚)
lip_t = 3; lip_z0 = 41; lip_y = 58;  // 屏缝下翻边
cw_r = 75; cw_ang = [135, 225];      // 配重座 (2026-08-03): 每半 1 个
cw_boss_d = 14; cw_boss_z0 = 38;     // 顶板下挂 Φ14 凸台 Z38..50 (外缘并到内壁 R82)
cw_hole_d = 6.5;                     // M6 过孔上下通
cw_nut_af = 10.3; cw_nut_h = 5.5;    // 自由端六角螺母窝 (M6 螺母对边 10 + 0.3)
seam_gap = 0.15;                     // 对开面单边间隙

module body() {
  difference() {
    union() {
      difference() {                                   // 筒壁
        cylinder(h = h, d = od, $fn = 360);
        translate([0,0,-1]) cylinder(h = h+2, d = id, $fn = 360);
      }
      cylinder(h = plate_z0 + plate_t, d = id, $fn = 360);   // 后面再切掉腰部
      for (a = col_ang)                                 // 沉井立柱 ×4 (兼竖筋)
        translate([col_r*cos(a), col_r*sin(a), 0]) cylinder(h = h, d = col_d, $fn = 64);
      intersection() {                                  // 接缝 bolster ×2
        difference() {
          cylinder(h = h, d = id + 1, $fn = 360);
          translate([0,0,-1]) cylinder(h = h+2, d = 2*bol_r_in, $fn = 360);
        }
        translate([-od/2, -bol_hw, 0]) cube([od, 2*bol_hw, h]);
      }
      for (a = cw_ang)                                  // 配重座凸台 ×2
        translate([cw_r*cos(a), cw_r*sin(a), cw_boss_z0])
          cylinder(h = h - cw_boss_z0, d = cw_boss_d, $fn = 64);
      for (s = [1,-1])                                  // 屏缝下翻边 ×2
        translate([s > 0 ? scr_hw : -(scr_hw+lip_t), -lip_y, lip_z0])
          cube([lip_t, 2*lip_y, plate_z0 - lip_z0]);
    }
    // 顶板只保留 Z plate_z0..h (把上面那个实心柱的腰部挖掉)
    translate([0,0,-1]) cylinder(h = plate_z0 + 1, d = id - 0.001, $fn = 360);
    // 屏缝 (顶板 + 翻边一起切穿)
    translate([-scr_hw, -slot_y1, lip_z0-1]) cube([2*scr_hw, 2*slot_y1, h - lip_z0 + 2]);
    translate([-tee_hw,  tee_y0, lip_z0-1]) cube([2*tee_hw, slot_y1 - tee_y0, h - lip_z0 + 2]);
    translate([-tee_hw, -slot_y1, lip_z0-1]) cube([2*tee_hw, slot_y1 - tee_y0, h - lip_z0 + 2]);
    // 配重座: M6 过孔 + 六角螺母窝 (窝朝凸台自由端开口, 打印姿态里朝上)
    for (a = cw_ang) translate([cw_r*cos(a), cw_r*sin(a), 0]) {
      translate([0,0,cw_boss_z0-1]) cylinder(h = h - cw_boss_z0 + 3, d = cw_hole_d, $fn = 48);
      translate([0,0,cw_boss_z0-1]) rotate([0,0,30])
        cylinder(h = cw_nut_h + 1, d = cw_nut_af/cos(30), $fn = 6);
    }
    // 沉井 + 过孔 + 引导锥
    for (a = col_ang) translate([col_r*cos(a), col_r*sin(a), 0]) {
      translate([0,0,floor_t]) cylinder(h = h - floor_t + 1, d = well_d, $fn = 64);
      translate([0,0,-1]) cylinder(h = floor_t + 2, d = bore_d, $fn = 48);
      translate([0,0,floor_t-lead_h]) cylinder(h = lead_h, d1 = bore_d, d2 = lead_d, $fn = 48);
    }
  }
}

// 分半 (对开面 = 平面 Y=0, 单边间隙 seam_gap)
intersection() {
  body();
  if (half == "A") translate([-od, seam_gap, -1]) cube([2*od, od, h+2]);
  else             translate([-od, -od-seam_gap, -1]) cube([2*od, od, h+2]);
}
