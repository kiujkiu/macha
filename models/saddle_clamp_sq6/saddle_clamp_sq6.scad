// POV 3D 马鞍压条/抱箍 — 方形过桥, 内腔 6×6, 料厚 3, 2×M6 @ 25
// 夹持 6mm 方棒 (轴沿 Y, 贴板); 顶部方形压条压住, 两脚 M6 固定

inner = 6;          // 内腔方边
half = inner/2;     // 3
zin = inner;        // 内腔高 6 (正方形)
t = 3;              // 料厚
ohalf = half + t;   // 外半宽 6
htop = zin + t;     // 外顶 9
w = 14;             // 压条/脚 宽 (沿Y)
m6 = 6.5; cc = 25; hx = cc/2; foot = hx + 6;   // 18.5

module saddle_clamp_sq6() {
    difference() {
        union() {
            // 方形过桥 (倒U), 开口朝下
            difference() {
                translate([-ohalf, -w/2, 0]) cube([2*ohalf, w, htop]);
                translate([-half, -w/2-1, -1]) cube([inner, w+2, zin+1]);
            }
            // 两脚 (贴板 3mm)
            translate([ohalf, -w/2, 0])  cube([foot - ohalf, w, t]);
            translate([-foot, -w/2, 0])  cube([foot - ohalf, w, t]);
        }
        // 2 × M6 通孔
        for (sx = [-1, 1])
            translate([sx*hx, 0, -1]) cylinder(h = t + 2, d = m6, $fn = 48);
    }
}

saddle_clamp_sq6();
