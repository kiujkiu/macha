// top_cap_v3_1 — v3 双面屏顶部薄压条 (与 build_stl.py 同参, 2026-07-22 终版)。
// 装配系 Z 260.95..267.95 (底面压屏顶); 平躺打印零支撑。
// 轴 Φ6.2 通 + Φ13×2.7 底面头窝 (M6×20 平头, 先装后压屏); 2×Φ3.2 @ (0,±64) M3×12。

blk_x=9; blk_y=70; z0=260.95; z1=267.95;
difference(){
  translate([-blk_x,-blk_y,z0]) cube([2*blk_x,2*blk_y,z1-z0]);
  translate([0,0,z0-1]) cylinder(h=z1-z0+2, d=6.2, $fn=48);        // 轴通孔
  translate([0,0,z0-1]) cylinder(h=2.7+1, d=13, $fn=48);           // 底面头窝
  for(y=[64,-64]) translate([0,y,z0-1]) cylinder(h=z1-z0+2, d=3.2, $fn=32);  // 屏顶孔
}
