// XT60 电源接头压块 xt60_clamp_16p6x9p2x23p9 (v4.10, 2026-09-16) — 平顶块, 2×M6 @ 25 横跨接头, 大扁头坐顶面
// 接头 XT60H-M 两段: 插合本体 15.6×8.2 长11.9 (开口侧, 宽为用户指定, 图纸 15.4) / 出线护套 16.6×9.2 长12 (堵头侧, 图纸 16.4); 本体上下各比护套缩 0.5
// 现行: 压块 38×26.9×11 + 件 2 底板垫片 (38×26.9×2 + 凸台 15.4×11.9×0.5 + 止口四边高 2: 侧/前宽 2, 后边宽 3) = 38×26.9×13 长方体
// 插入靠堵头 + 后边框挡, 拔出靠窄槽台阶挡护套; 堵头厚3 带 2 个 U 型出线口 (Φ2.5 圆心高 4.6 间距 7, 平底 = 后边框顶 z 2); 孔心到开口面 12.5
// 版本历史 (按顺序):
// v4.1 用户指定宽度 16.6 / 15.6 紧配不留余量 => 阶梯槽: 本体段 15.6×8.6 (压紧0.1) + 护套段 16.6×9.0 (压紧0.2); 本体底下垫 0.5 垫片 (单独件 xt60_shim)
// v4.2 用户「所有间隙都改为0」: 台阶对齐 (零窜动), 垫片 = 本体底面 15.6×11.9×0.5; M6 过孔未动
// v4.3 用户「应该是8.7和9.2」: 高度过盈也 0, 槽顶 = 接头顶 (护套 9.2 / 本体 8.7)
// v4.4 用户「厚度改为11mm」: 件高 11 定死, 槽顶厚 1.8 (护套段) / 2.3 (本体段)
// v4.5 用户: 垫片会掉 => 件 2 改底板垫片 = 压块外形 38×26.9 × 厚 2 + 本体下凸台 0.5, 2×Φ6.5 同压块孔, M6 定位
// v4.6 用户「出线端就都在中央，直径都改为2.5mm」: U 口 Φ2.5 零余量, 圆心 = 护套高/2 = 4.6
// v4.7 用户: 上下件嵌套卡在一起 => 止口 2×2 (左右 X 端全长 + 开口端两段, 槽口断开; 底板凸起 / 压块底面台阶),
//      堵头处底板舌头 (高到针轴, 顶面 R1.25) 与 U 口扣成 Φ2.5 圆
// v4.8 用户「两个件就留0.1mm装配」: 嵌套面单边 0.1 (舌头宽 2.3 / 凸台宽 15.4)
// v4.9 用户「组合后从外边看要是一个立方体」: 压块台阶 2.1 宽 × 2.0 高 (高度不留缝, 外观平齐)
// v4.10 用户: 四边都加凸台 / 出线处削 / 后边宽 3 => 取消舌头; 止口四边高 2 (侧/前宽 2, 后边宽 3 全宽); 线底 3.35 > 2 不削
// v3 把两段装反了, v4 按用户实物纠正: 没挡板的开口端是小的本体, 挡板端是大的护套
// ⚠ 参数与 build_stl.py 手工同步 (build_stl.py 是准绳, 带全部校核)

body_w   = 15.6; body_h   = 8.2;    // 插合本体 (开口侧), 宽用户指定
sheath_w = 16.6; sheath_h = 9.2;    // 出线护套 (堵头侧), 宽用户指定
body_l   = 11.9; sheath_l = 12.0;
xt_l     = body_l + sheath_l;       // 23.9
body_lift = (sheath_h - body_h)/2;  // 0.5

side_clr_s = 0;     side_clr_b = 0;     // 紧配, 不留余量 (用户 09-16)
preload_s  = 0;     preload_b  = 0;     // 护套段 / 本体段 压紧量 (用户: 槽顶 9.2 / 8.7)
step_margin = 0;    // 槽台阶比接头台阶往开口侧提前 (所有间隙 0)
assy_clr = 0.1;                             // 两件嵌套面单边装配间隙 (必须在 shim_clr 之前定义)
shim_clr = assy_clr; shim_open_inset = 0; shim_back_gap = 0;   // 凸台两侧留装配间隙

htop     = 11;    // 件高 (用户指定)
cap_t    = 3;     // 堵头厚
wire_d   = 2.5;   // 出线口径 = 线径, 零余量
wire_pitch = 7;   // 出线口间距
wire_zc  = sheath_h/2;   // 4.6 针轴线
pitch    = 25;    // 孔距 (= 网格节距, 横跨接头)
hole_d   = 6.5;   // M6 通孔
end_m    = 6.5;   // 孔心到 X 端面
hole_y_open = 12.5;   // 孔心到开口面

ch_w_b = body_w + 2*side_clr_b;             // 15.6
ch_h_b = body_lift + body_h - preload_b;    //  8.7
ch_w_s = sheath_w + 2*side_clr_s;           // 16.6
ch_h_s = sheath_h - preload_s;              //  9.2
t_top  = htop - ch_h_s;                     // 1.8 槽顶厚 (护套段)
hx     = pitch/2;
half_l = hx + end_m;                        // 19
y_open  = -xt_l/2;                          // -11.95
y_xstep = y_open + body_l;                  //  -0.05 接头台阶
y_step  = y_xstep - step_margin;            //  -0.05 槽台阶 (= 接头台阶)
y_capi  = xt_l/2;                           //  11.95
depth   = xt_l + cap_t;                     //  26.9

base_t  = 2;                                // 底板垫片厚 (用户)
rim_w   = 2; rim_h = 2;                     // 止口 (用户「厚度2mm，高度2mm」)
shim_t  = body_lift;                        // 0.5 凸台高
shim_w  = ch_w_b - 2*shim_clr;              // 15.4
back_rim_w = cap_t;                         // 3 后边止口宽
ledge = wire_zc - wire_d/2;                 // 3.35 线底
shim_y0 = y_open + shim_open_inset;         // -11.95
shim_y1 = y_xstep - shim_back_gap;          //  -0.05

module u_slot(xc) {
    translate([xc, y_capi - 1, wire_zc]) rotate([-90, 0, 0])
        cylinder(h = cap_t + 2, d = wire_d, $fn = 96);
    translate([xc - wire_d/2, y_capi - 1, -1]) cube([wire_d, cap_t + 2, wire_zc + 1]);
}

// 止口区域: e>0 时向外/向下延伸 (给压块切台阶用)
module rim_region(e = 0, gw = 0, gh = 0) {
    w = rim_w + gw; h = rim_h + gh;
    for (sx = [-1, 1]) {
        translate([sx > 0 ? half_l - w : -half_l - e, y_open - e, -e]) cube([w + e, depth + 2*e, h + e]);
        translate([sx > 0 ? ch_w_b/2 : -half_l - e, y_open - e, -e]) cube([half_l - ch_w_b/2 + e, w + e, h + e]);
    }
    wb = back_rim_w + gw;
    translate([-half_l - e, y_capi + cap_t - wb, -e]) cube([2*half_l + 2*e, wb + e, h + e]);   // 后边 (出线边)
}

module xt60_clamp_16p6x9p2x23p9() {
    difference() {
        translate([-half_l, y_open, 0]) cube([2*half_l, depth, htop]);
        // 阶梯槽: 本体段 (开口 -> 槽台阶, 窄低) + 护套段 (槽台阶 -> 堵头内面, 宽高)
        translate([-ch_w_b/2, y_open - 1, -1]) cube([ch_w_b, y_step - y_open + 1, ch_h_b + 1]);
        translate([-ch_w_s/2, y_step,     -1]) cube([ch_w_s, y_capi - y_step,     ch_h_s + 1]);
        for (sx = [-1, 1])
            translate([sx*hx, y_open + hole_y_open, -1]) cylinder(h = htop + 2, d = hole_d, $fn = 96);
        for (sx = [-1, 1]) u_slot(sx * wire_pitch/2);
        rim_region(1, assy_clr, 0);   // 底面止口台阶: 宽 + 装配间隙, 高贴合
    }
}

// 件 2 底板垫片: 装配坐标 底板 z∈[-base_t,0] + 凸台 z∈[0,shim_t]
module xt60_shim_38x26p9x2p5() {
    difference() {
        union() {
            translate([-half_l, y_open, -base_t]) cube([2*half_l, depth, base_t]);
            translate([-shim_w/2, shim_y0, 0]) cube([shim_w, shim_y1 - shim_y0, shim_t]);
            difference() {   // 止口边框 (线底低于边框顶时在出线处削)
                rim_region(0);
                if (ledge < rim_h) for (sx = [-1, 1]) translate([sx*wire_pitch/2 - wire_d/2, y_capi - 1, ledge]) cube([wire_d, back_rim_w + 2, rim_h]);
            }
        }
        for (sx = [-1, 1])
            translate([sx*hx, y_open + hole_y_open, -base_t - 1]) cylinder(h = base_t + shim_t + 2, d = hole_d, $fn = 96);
    }
}

xt60_clamp_16p6x9p2x23p9();
%xt60_shim_38x26p9x2p5();   // 装配位置预览 (单独导出时去掉 % 并注释掉上一行)
