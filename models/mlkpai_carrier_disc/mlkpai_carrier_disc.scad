// mlkpai_carrier_disc — 转子承载盘 Φ170×6 (旧 rim_top_disc 保留)
// 16 挂环孔装 rim_ring; 6 Φ10 凸台(带铜螺母孔)固定 pi2hub; 3 Φ3 托顶连接器
disc_od=170; thick=6;
inner_r=35; outer_r=77.5;
m3=3.2; cb_d=7; cb_deep=2.5;              // 挂环孔 + 顶沉
boss_d=10; boss_h=2;                      // 6 安装凸台
thru_d=3.2; insert_d=4.2; insert_deep=4;  // 通孔 + 铜螺母沉孔(从盘底 Z0..4)
tuo_d=3; tuo_h=2;                         // 3 支托 (Φ3, 让开排针)
boss_top=thick+boss_h;                    // 8

boss_xy=[[-39.5,25],[39.5,25],[-39.5,-25],[39.5,-25],[-39.5,-55],[39.5,-55]];
tuo_xy=[[-48.5,37],[-4,37],[45,40]];

module mlkpai_carrier_disc() {
    difference() {
        union() {
            cylinder(h=thick, d=disc_od, $fn=192);
            for (b=boss_xy) translate([b[0],b[1],thick]) cylinder(h=boss_h, d=boss_d, $fn=64);
            for (t=tuo_xy)  translate([t[0],t[1],thick]) cylinder(h=tuo_h, d=tuo_d, $fn=48);
        }
        // 16 挂环孔 + 顶沉
        for (r=[inner_r,outer_r]) for (k=[0:7]) {
            a=22.5+k*45; x=r*cos(a); y=r*sin(a);
            translate([x,y,-1]) cylinder(h=thick+2, d=m3, $fn=32);
            translate([x,y,thick-cb_deep]) cylinder(h=cb_deep+1, d=cb_d, $fn=48);
        }
        // 6 凸台孔: Φ3.2 通 + Φ4.2 从盘底沉 4 (Z0..4)
        for (b=boss_xy) {
            translate([b[0],b[1],-1]) cylinder(h=boss_top+2, d=thru_d, $fn=32);
            translate([b[0],b[1],-1]) cylinder(h=insert_deep+1, d=insert_d, $fn=48);
        }
    }
}
mlkpai_carrier_disc();
