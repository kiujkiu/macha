// wifi_shell — 新 WiFi 壳子 v1 (与 build_shell.py 同参, 2026-07-22 几何)。
// 侧开口五面盒: 内腔 15.1×70.6×40.4, 壁 3, 开口面 = +X 侧 70.6×40.4 (无壁)。
// 零件系: X0 = 封闭壁外面, 开口在 X=18.1; Z0 = 外底面; Y 对称。
// 安装 = 倒扣 (开口/双端沿朝下贴盘), 罩住放平模块 40×70×14.5; 打印同姿态零支撑。
// ±Y 端沿 (X15.1..18.1 与开口面共面) 外伸 10, 各 2×Φ3.2 + 2 三角筋 2.5 厚 45°。
// +Y 端壁出口窗 10.7×19.1 对准放平母头 (轴线离开口面 7.25), 切穿 +Y 沿板。
// 装配位: 盒 footprint 中线 XC=43 + 沿长边平移 −15, 随 135° 组转 (assembly_v2/v2_1)。

cav = [15.1, 70.6, 40.4];  wall = 3;
ix0 = wall;  ix1 = wall + cav[0];            // 内腔 X 3..18.1 (开口 = X18.1)
iy  = cav[1]/2;  iz0 = wall;  iz1 = wall + cav[2];
ox1 = ix1;  oy = iy + wall;  oz1 = iz1 + wall;   // 外廓 18.1 × ±38.3 × 46.4
win_w = 10.7;  win_h = 19.1;                 // 出口窗 (母头壳 10.3×18.7 +0.4)
win_xc = ox1 - 14.5/2;                       // 10.85 = 放平模块口轴线
win_zc = (iz0 + iz1)/2;                      // 23.2 = 腔 Z 中线
flg_l = 10;  flg_t = 3;  flg_x0 = ox1 - flg_t;   // 沿: X 15.1..18.1, 外伸 10
flg_y1 = oy + flg_l;                         // 48.3
m3 = 3.2;  hole_yc = oy + 5;                 // 孔距壁 5
hole_zs = [(oz1)/2 - 12.5, (oz1)/2 + 12.5];  // 10.7 / 35.7 (宽向 c-c 25 对称)
gus_t = 2.5;  gus_arm = 10;                  // 三角筋 45°, X 5.1..15.1
gus_zs = [0, oz1 - gus_t];                   // 贴沿的两条宽向端边

module bbox(x0,x1,y0,y1,z0,z1){ translate([x0,y0,z0]) cube([x1-x0,y1-y0,z1-z0]); }
module gusset(y_wall, y_out, z0){            // X-Y 面直角三角, 沿 Z 挤 gus_t
  translate([0,0,z0]) linear_extrude(gus_t)
    polygon(y_out > y_wall ? [[flg_x0,y_wall],[flg_x0,y_out],[flg_x0-gus_arm,y_wall]]
                           : [[flg_x0-gus_arm,y_wall],[flg_x0,y_out],[flg_x0,y_wall]]);
}

difference(){
  union(){
    difference(){
      bbox(0,ox1,-oy,oy,0,oz1);                       // 外块
      bbox(ix0,ix1+1,-iy,iy,iz0,iz1);                 // 内腔 (开口朝 +X)
    }
    bbox(flg_x0,ox1,oy,flg_y1,0,oz1);                 // +Y 沿
    bbox(flg_x0,ox1,-flg_y1,-oy,0,oz1);               // -Y 沿
    for(z0=gus_zs){ gusset(oy,flg_y1,z0); gusset(-oy,-flg_y1,z0); }   // 筋 ×4
  }
  // 出口窗 (穿 +Y 端壁 + 切穿 +Y 沿板 —— 必须在沿之后挖)
  bbox(win_xc-win_w/2,win_xc+win_w/2,iy-1,flg_y1+1,win_zc-win_h/2,win_zc+win_h/2);
  for(zc=hole_zs) for(yc=[hole_yc,-hole_yc])          // 4×Φ3.2 (孔轴沿 X)
    translate([flg_x0-1,yc,zc]) rotate([0,90,0]) cylinder(h=flg_t+2, d=m3, $fn=32);
}

// ===== 盘缘裁切 (2026-07-27, 用户: "有个脚出来了, 要砍掉") =====
// -Y 端沿外角原伸到盘系 r=90.22, 悬出 Φ170 承载盘缘 5.2 —— 与转子轴同心的
// R83.5 圆柱求交切齐 (r_max 90.22 -> 83.50)。零件系->盘系:
//   disc_X = z + 19.8 ; disc_Y = y - 13   (135° 组转只绕轴, 不改半径)
// 用法: 把上面的最终实体包在 intersection() { ... trim_cyl(); } 里。
trim_r = 83.5; trim_cx_z = 19.8; trim_cy_y = 13;
module trim_cyl() {
  translate([-200, trim_cy_y, -trim_cx_z]) rotate([0,90,0])
    cylinder(h = 400, r = trim_r, $fn = 512);
}
