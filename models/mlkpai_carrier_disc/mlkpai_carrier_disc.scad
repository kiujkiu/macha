// mlkpai_carrier_disc — 转子承载盘 Φ170×6 (旧 rim_top_disc 保留)
// 16 挂环孔装 rim_ring; 7 pi2hub 孔 (Φ3.2通+盘底Φ4.2×4铜螺母沉); 凸台/支托均已取消 (2026-07-06/07-03)
disc_od=170; thick=5;   // 厚 6→5 (2026-07-06); 铜螺母沉孔台肩仅剩 1
inner_r=35; outer_r=77.5;
m3=3.2; cb_d=7; cb_deep=2.5;              // 挂环孔 + 顶沉
thru_d=3.2; insert_d=4.2; insert_deep=4;  // 通孔 + 铜螺母沉孔(从盘底 Z0..4)

pcb_rot=90;   // pcb 安装方向在盘上转 90° (反向改 -90)
pcb_off=[-10,0];   // 再沿盘 -X 挪 10 (2026-07-03 晚)
function _rp(p) = [p[0]*cos(pcb_rot)-p[1]*sin(pcb_rot)+pcb_off[0], p[0]*sin(pcb_rot)+p[1]*cos(pcb_rot)+pcb_off[1]];
boss_xy=[for (p=[[-47,44],[0,44],[47,44],[-39.5,25],[39.5,25],[-39.5,-25],[39.5,-25]]) _rp(p)];
// (凸台取消后与环孔无冲突, 16 环孔顶沉全部保留)

module mlkpai_carrier_disc() {
    difference() {
        union() {
            cylinder(h=thick, d=disc_od, $fn=192);
        }
        // 16 挂环孔 + 顶沉
        for (r=[inner_r,outer_r]) for (k=[0:7]) {
            a=22.5+k*45; x=r*cos(a); y=r*sin(a);
            translate([x,y,-1]) cylinder(h=thick+2, d=m3, $fn=32);
            translate([x,y,thick-cb_deep]) cylinder(h=cb_deep+1, d=cb_d, $fn=48);
        }
        // 7 pi2hub 孔: Φ3.2 通 + Φ4.2 从盘底沉 4 (Z0..4)
        for (b=boss_xy) {
            translate([b[0],b[1],-1]) cylinder(h=thick+2, d=thru_d, $fn=32);
            translate([b[0],b[1],-1]) cylinder(h=insert_deep+1, d=insert_d, $fn=48);
        }
    }
}
mlkpai_carrier_disc();
