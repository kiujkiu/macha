// portal_tee_v3_1 — v3.1 偏心屏实验 (2026-07-31)
// ⚠ 主体几何可读副本; 实际打印件以 STL 为准 (让位/布尔特征无法在 SCAD 复刻)
// portal_tee_v3 — v3 屏幕底部支撑 T 型件 (与 build_tee.py 同参, 2026-07-23 终版)。
// 盘系 Z0=承载面; ×2 (第二件绕 Z 转 180°); 平躺打印 (外侧面 Y=76.601 贴床) 零支撑。
// 底横条装转子两颗 M3; 梯形加强壁齐外侧面; 顶平板托梯形 (托面 Z50=屏底), 内边 13.4=屏厚;
// 屏孔 (0,64) M3×12 + Φ7.5×4 帽让位窝; 2×Φ7 工艺井过壁。

bar_x=33.5; bar_h=5; y0=66.601; y1=76.601;      // 底横条 67×10×5
stem_hw=2.5; stem_z1=50;                        // 竖梃 5×10
gus_t=5; gy0=y1-gus_t;                          // 梯形壁厚 5, 齐外侧
pad_t=5; pad_z0=stem_z1-pad_t;                  // 顶托 Z45..50
pad_y0=59.601; pad_wi=16; pad_wo=16;   // v3.1: 顶托改等宽 ±16           // 托梯形: 内 ±6.7, 外 ±10
foot_holes=[[29.658,71.601],[-29.658,71.601]];
well_d=7; well_z1=20;
scr_y=64;
scr_ecc=6.7;                        // v3.1 偏心量
scr_xs=[-scr_ecc,0,scr_ecc];        // 3 个离散屏孔位

difference(){
  union(){
    translate([-bar_x,y0,0]) cube([2*bar_x,y1-y0,bar_h]);            // 底横条
    translate([-stem_hw,y0,bar_h]) cube([2*stem_hw,y1-y0,pad_z0-bar_h]); // 竖梃
    translate([0,gy0+gus_t,0]) rotate([90,0,0]) linear_extrude(gus_t)    // 梯形壁
      polygon([[-bar_x,bar_h],[bar_x,bar_h],[pad_wo,pad_z0],[-pad_wo,pad_z0]]);
    translate([0,0,pad_z0]) linear_extrude(pad_t)                        // 顶平板托
      polygon([[pad_wo,y1],[-pad_wo,y1],[-pad_wi,pad_y0],[pad_wi,pad_y0]]);
  }
  for(h=foot_holes){
    translate([h[0],h[1],-1]) cylinder(h=bar_h+2, d=3.4, $fn=32);        // 脚孔
    translate([h[0],h[1],bar_h]) cylinder(h=well_z1-bar_h, d=well_d, $fn=32);  // 工艺井
  }
  for (sx = scr_xs) {                                                    // v3.1: 3 个离散屏孔
    translate([sx,scr_y,pad_z0-1]) cylinder(h=pad_t+2, d=3.2, $fn=32);   // 屏孔
    translate([sx,scr_y,pad_z0-4]) cylinder(h=4, d=7.5, $fn=32);         // 帽让位窝
  }
}
