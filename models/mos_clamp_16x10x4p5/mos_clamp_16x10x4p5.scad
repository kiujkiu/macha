// MOS 管压块 mos_clamp_16x10x4p5 — 参考 saddle_clamp_sq6 (槽 + 2×M6 @ 25)
// 压 TO-220 MOS (长16 宽10 高4.5) 到 M6 网格板 (节距 25); MOS 长度沿 Y 推进底部盲槽
// 平顶: 孔距 25 - 大扁头 Φ12.5 = 12.5 放不下 10 宽 MOS + 两侧壁, 故脚与顶齐平, 头坐顶面
// +Y 端挡板厚 2 (全长全高); 槽深 24 (用户加宽 1cm, 原 14), 开口面与孔位不动
// 过盈 0 (用户 2026-09-15 选定: 两脚贴板, 拧到底也压不坏封装); 垫导热垫时改 pad_t / preload

mos_l = 16; mos_w = 10; mos_h = 4.5;   // MOS 包络
side_clr = 0.2;   // 槽宽单侧间隙
preload  = 0;     // 过盈 = (MOS + 垫) 叠高 - 槽高; 垫导热垫时取垫允许的压缩量
pad_t    = 0;     // MOS 下导热硅胶垫厚 (待定)
t_top    = 3;     // 槽顶厚
pitch    = 25;    // 网格孔距
hole_d   = 6.5;   // M6 通孔
end_m    = 6.5;   // 孔心到 X 端面 (>= 头半径 6.25)
hole_y_open = 7;  // 孔心到开口面
ch_d     = 24;    // 槽深 (开口面 -> 挡板内面)
baffle_t = 2;     // +Y 端挡板厚

ch_w   = mos_w + 2*side_clr;   // 10.4
ch_h   = mos_h + pad_t - preload;   // 4.5
h      = ch_h + t_top;         // 7.5
hx     = pitch/2;              // 12.5
half_l = hx + end_m;           // 19
y_open = -hole_y_open;         // -7 开口面 (孔心在 y=0)

module mos_clamp_16x10x4p5() {
    difference() {
        translate([-half_l, y_open, 0]) cube([2*half_l, ch_d + baffle_t, h]);
        // 底部盲槽: 只从 -Y 端开口, 止于挡板内面 y = y_open + ch_d
        translate([-ch_w/2, y_open - 1, -1]) cube([ch_w, ch_d + 1, ch_h + 1]);
        // 2 × M6 通孔
        for (sx = [-1, 1])
            translate([sx*hx, 0, -1]) cylinder(h = h + 2, d = hole_d, $fn = 96);
    }
}

mos_clamp_16x10x4p5();
