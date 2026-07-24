// rim_ring — 外圈托盘环 v3 (与 build_stl.py 同参, 2026-07-22 定稿几何)。
// 零件系: Z0 = 托盘承载面 (装配绕 X 翻转后朝上), Z5 = 唇侧面, 总高 10.5。
// 2026-07-20/21/22: 承载盘并入 (7 pi2hub 孔), 中孔 ID60->50, 内圈 8 孔 R35->30,
// 内凸台环 OD80/ID70x2.5 (唇侧, 落 hub 底板顶兼径向定心), 挖槽 R40..61,
// wifi 定稿单组 4 沿孔 (盒 XC43 + 长边平移-13; -15→-13 消除沉孔侵内凸台环), 4 环孔头沉孔 Φ7.5x2.0 (承载面侧, R30+R77.5 @202.5/247.5)。
// 孔位坐标由 build_stl.py 公式导出 (改参数请以它为准再同步这里)。

base_id  = 50;   base_od = 170;  base_h = 5;      // 托盘环
rim_id   = 165;  rim_od  = 170;  rim_h  = 5.5;    // 外唇 Z5..10.5 (完整整圈)
iboss_od = 80;   iboss_id = 70;  iboss_h = 2.5;   // 内凸台环 (唇侧 Z5..7.5)
notch_r0 = 40;   notch_r1 = 61;                   // 扇形挖槽 R40..61
notch_a0 = -45;  notch_a1 = -40; notch_deep = 2;  // -45..-40 deg, 唇侧深 2 (Z3..5)
m3 = 3.2;  inner_pcd_r = 30;  outer_pcd_r = 77.5; // 16 环孔 PCD Φ60 + Φ155
insert_d = 4.2;  insert_deep = 4.5;               // 铜螺母沉孔 (唇侧往下, 台肩 0.5)
head_cb_d = 7.5; head_cb_deep = 2.0;              // 4 环孔头沉孔 (承载面侧, 内圈+外圈)
head_cb_angles = [202.5, 247.5];                  // wifi 角落 4 颗锁紧螺丝 (内圈 2 在模块底下, 外圈 2 挨盒东侧)
extra_d = 4;                                      // 2 Φ4 通孔
extra_polar = [[-10, 72], [-42.5, 56]];           // (deg, R)
pi_holes = [[71.418,4.95],[38.184,38.184],[4.95,71.418],[52.679,-3.182],
            [-3.182,52.679],[17.324,-38.537],[-38.537,17.324]];      // 7 pi2hub
wifi_holes = [[-42.992,-0.141],[18.243,-61.377],[-60.67,-17.819],[0.566,-79.055]]; // 4 wifi (XC43, -13)

module ann(z0, h, r_in, r_out){
  translate([0,0,z0]) difference(){
    cylinder(h=h, r=r_out, $fn=240);
    translate([0,0,-1]) cylinder(h=h+2, r=r_in, $fn=240);
  }
}
module thru(x, y, d=m3){ translate([x,y,-1]) cylinder(h=12.5, d=d, $fn=32); }
module insert_pocket(x, y){                       // 唇侧 Z5 往下 4.5 (占 Z0.5..5, +1 溢出)
  translate([x,y,base_h-insert_deep]) cylinder(h=insert_deep+1, d=insert_d, $fn=32);
}

difference(){
  union(){
    ann(0, base_h, base_id/2, base_od/2);         // 托盘环
    ann(base_h, rim_h, rim_id/2, rim_od/2);       // 外唇
    ann(base_h, iboss_h, iboss_id/2, iboss_od/2); // 内凸台环
  }
  // 扇形挖槽 (唇侧面往下 2)
  translate([0,0,base_h-notch_deep]) linear_extrude(notch_deep+1)
    intersection(){
      difference(){ circle(r=notch_r1, $fn=240); circle(r=notch_r0, $fn=240); }
      polygon([[0,0], for(a=[notch_a0:0.5:notch_a1]) [100*cos(a),100*sin(a)]]);
    }
  // 16 环孔 (22.5 + k*45)
  for(k=[0:7]){
    a = 22.5 + k*45;
    thru(inner_pcd_r*cos(a), inner_pcd_r*sin(a));
    thru(outer_pcd_r*cos(a), outer_pcd_r*sin(a));
  }
  // 4 环孔头沉孔 (承载面 Z0 侧, 内圈 + 外圈)
  for(a=head_cb_angles) for(r=[inner_pcd_r, outer_pcd_r])
    translate([r*cos(a), r*sin(a), -1])
      cylinder(h=head_cb_deep+1, d=head_cb_d, $fn=48);
  // 7 pi2hub 孔 + 4 wifi 沿孔 (Φ3.2 通 + 铜螺母沉孔)
  for(p=pi_holes){ thru(p[0],p[1]); insert_pocket(p[0],p[1]); }
  for(p=wifi_holes){ thru(p[0],p[1]); insert_pocket(p[0],p[1]); }
  // 2 Φ4 通孔
  for(p=extra_polar) thru(p[1]*cos(p[0]), p[1]*sin(p[0]), extra_d);
}
