// wifi_box — USB WiFi 网卡倒扣盒 (与 build_box.py 同参, 2026-07-09 第三版定稿)。
// 盘坐标系, Z0 = 盘顶面 = 打印姿态 (开口朝下, 零支撑, 顶板 15.1 桥接)。
// 模块侧立整块 14.5×40×70 (天线反折在内), 以 14.5×70 面坐盘, 插头朝 +Y (米联派 J6 方向)。
// 4 耳脚借盘环孔 M3×14 (耳3+盘5+rim_ring3.5, 环底垫片+螺母)。
// 装配: 盒倒置 → 模块放入 → 母头从窗外插合 → 翻正扣盘 → 4 螺丝 → 扎带勒母头壳。

BLK_T = 14.5;  BLK_L = 70;  BLK_H = 40;      // 模块整块 厚×长×高
XC = 52;  CLR = 0.3;  WALL = 3;              // 中线 / 间隙 / 壁厚 (用户指定 3)
IX0 = XC-BLK_T/2-CLR;  IX1 = XC+BLK_T/2+CLR; // 内腔 X 44.45..59.55
IY = BLK_L/2+CLR;                            // 内腔 Y ±35.3
IZ1 = BLK_H+0.4;                             // 内腔顶 40.4
OX0 = IX0-WALL;  OX1 = IX1+WALL;  OY = IY+WALL;  OZ1 = IZ1+WALL;
ZC = BLK_H/2;                                // 插头/母头轴线高 20
WIN_W = 10.7;  WIN_H = 19.1;                 // 母头出口窗 (母头壳 10.3×18.7 +0.4)
TIE_W = 6;  TIE_H = 3;                       // 扎带槽 (窗上下各一)
DISC_M3 = [[32.336,13.393],[32.336,-13.393],[71.601,29.658],[71.601,-29.658]];
FL_T = 3;  WFL_X0 = 28.3;  EFL_X1 = 75.8;  EFL_HY = 37;   // 整条翼板 (2 耳合一)
GUS_T = 2.5;  WGUS_YS = [0,20,-20,37.05,-37.05];  EGUS_YS = [0,20,-20,35.75,-35.75];
RIB_YS = [-20,0,20];                         // 西内壁摩擦筋 0.25×2

module bbox(x0,x1,y0,y1,z0,z1){ translate([x0,y0,z0]) cube([x1-x0,y1-y0,z1-z0]); }
module gusset(x_out,x_wall,yc){              // 三角加强筋 45° (免支撑)
  arm = abs(x_wall-x_out);
  translate([0,yc+GUS_T/2,0]) rotate([90,0,0]) linear_extrude(GUS_T)
    polygon(x_out<x_wall ? [[x_out,FL_T],[x_wall,FL_T],[x_wall,FL_T+arm]]
                         : [[x_wall,FL_T+arm],[x_wall,FL_T],[x_out,FL_T]]);
}

difference(){
  union(){
    difference(){
      bbox(OX0,OX1,-OY,OY,0,OZ1);                       // 外壳
      bbox(IX0,IX1,-IY,IY,-1,IZ1);                      // 内腔 (开口朝下)
    }
    for(yc=RIB_YS) bbox(IX0,IX0+0.25,yc-1,yc+1,1,IZ1-1);   // 摩擦筋
    bbox(WFL_X0,OX0,-OY,OY,0,FL_T);                     // 西翼板 (整条全长)
    bbox(OX1,EFL_X1,-EFL_HY,EFL_HY,0,FL_T);             // 东翼板 (整条 ±37)
    for(yc=WGUS_YS) gusset(WFL_X0,OX0,yc);              // 西加强筋 ×5
    for(yc=EGUS_YS) gusset(EFL_X1,OX1,yc);              // 东加强筋 ×5
  }
  bbox(XC-WIN_W/2,XC+WIN_W/2,IY-1,OY+1,ZC-WIN_H/2,ZC+WIN_H/2);   // 母头出口窗
  for(z0=[ZC-WIN_H/2-1-TIE_H, ZC+WIN_H/2+1])                     // 扎带槽 ×2
    bbox(XC-TIE_W/2,XC+TIE_W/2,IY-1,OY+1,z0,z0+TIE_H);
  for(h=DISC_M3) translate([h[0],h[1],-1]) cylinder(h=FL_T+2, d=3.4, $fn=32);  // 翼板孔
}
