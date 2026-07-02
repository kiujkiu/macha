// POV 3D — 米联派 MLKPAI-FS03 ZYNQ H 形支架 (t=3), 居中坐标系 +Y 上
// 旋转 H: 上下满宽横梁 + 中间竖脊, 缺口开左右; 中间 5 孔居中 (0,0)
bw=85; bh=56; hx=bw/2; hy=bh/2;
slot_w=25; slot_h=44;       // 凹槽 左右宽 × 上下高 (两侧相同)
bar_in=slot_h/2;            // 22 上下横梁内缘 y (横梁各 6mm)
spine_x=hx-slot_w;         // 17.5 中脊半宽 (凹槽朝外开口)
cen=[0,0];                  // 中间 5 孔中心 (居中; 芯片实际在 0,+3.7)
cd=24; sq=24;               // Φ24 + 24 方阵
chx=39.5; chy=25;           // 角孔 |X|,|Y| —— 间距 79×50 (实测)
t=3; m3c=3.4; m3s=3.4;

module mlkpai_h_bracket() {
    difference() {
        union() {
            translate([-hx, bar_in, 0]) cube([bw, hy-bar_in, t]);     // top bar
            translate([-hx,-hy,0])      cube([bw, hy-bar_in, t]);     // bottom bar
            translate([-spine_x,-hy,0]) cube([2*spine_x, bh, t]);     // central spine
        }
        translate([cen[0],cen[1],-1]) cylinder(h=t+2, d=cd, $fn=96);  // Φ24 centred
        for (s=[[-chx,chy],[chx,chy],[-chx,-chy],[chx,-chy]])         // corner M3
            translate([s[0],s[1],-1]) cylinder(h=t+2, d=m3c, $fn=48);
        for (sx=[-1,1]) for (sy=[-1,1])                               // 24-square M3
            translate([cen[0]+sx*sq/2, cen[1]+sy*sq/2, -1]) cylinder(h=t+2, d=m3s, $fn=48);
    }
}
mlkpai_h_bracket();
