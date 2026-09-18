// MR30 电源/电机接头压块 mr30_clamp_12p3x5p3x15p4 (v2 阶梯槽 + 底板垫片嵌套) — 平顶块, 2×M6 @ 25 横跨接头, 大扁头坐顶面
// 接头 (用户 09-16): 总长 15.4 (含护套); 前 8.5 = 插合本体 11.8×4.8 (单边小 0.25, 同轴, 底面离板 0.25); 后 6.9 = 护套 12.3×5.3
// 阶梯槽 间隙 0 / 过盈 0 / 台阶对齐: 本体段 11.8×5.05 长 8.5 + 护套段 12.3×5.3 长 6.9
// 出线: 3×U 口 Φ2.5 (= 线径零余量), 圆心 = 护套厚/2 = 2.65, 直边; 下半由件 2 后边框缺口平底 (1.4) 补成内切 Φ2.5 的孔
// 件 2 垫片 (mr30_shim_38x18p4x2p25.stl): 底板 38×18.4×2 + 凸台 11.6×8.5×0.25 + 2×Φ6.5 同轴
//   + 止口四边 高 2: 左右 / 开口端 宽 2 (开口端槽口处断开), 后边 宽 3 全宽; 出线处缺口 宽 2.5 削到 1.4
// 压块底面同位置切台阶 (左右/开口端 2.1 宽, 后边 3.1 宽, 高 2): 竖直面留 0.1 装配间隙, 高度贴合 => 组合外形 38×18.4×10.3 平齐长方体
// ⚠ 后台阶前沿 (距开口面 15.3) 到 M6 孔后缘 (15.15) 只剩 0.15 —— 孔心到开口面 11.9 待用户定
// 装配: 底板放板上 -> 接头放上, 线落进缺口 -> 压块扣下 -> M6×20 穿两件

sheath_w = 12.3; sheath_h = 5.3;
body_step = 0.25;
body_w = sheath_w - 2*body_step;    // 11.8
body_h = sheath_h - 2*body_step;    // 4.8
mr_l   = 15.4;
body_l = 8.5;
body_lift = (sheath_h - body_h)/2;  // 0.25
side_clr = 0; preload = 0; step_margin = 0;   // 接头配合: 间隙 / 过盈 0
t_top  = 3;
cap_t  = 3;
wire_d = 2.5;                       // U 口径 = 线径 (零余量)
wire_pitch = 3.5; n_wire = 3;
wire_zc = sheath_h/2;               // 2.65
ledge_h = wire_zc - wire_d/2;       // 1.4 出线圆最低点 = 后边框缺口底
pitch  = 25; hole_d = 6.5; end_m = 6.5;
hole_y_open = 11.9;                 // 待定

base_t     = 2;      // 垫片底板厚
rim_w      = 2;      // 止口宽 (左右 / 开口端)
rear_rim_w = cap_t;  // 止口宽 (后边) = 堵头厚 3
rim_h      = 2;      // 止口高
assy_clr   = 0.1;    // 嵌套竖直面装配间隙 (高度不留)
boss_w     = body_w + 2*side_clr - 2*assy_clr;   // 11.6

ch_w_b = body_w + 2*side_clr;             // 11.8
ch_h_b = body_lift + body_h - preload;    // 5.05
ch_w_s = sheath_w + 2*side_clr;           // 12.3
ch_h_s = sheath_h - preload;              // 5.3
htop   = ch_h_s + t_top;                  // 8.3
hx     = pitch/2;
half_l = hx + end_m;                      // 19
y_open = -mr_l/2;                         // -7.7
y_step = y_open + body_l - step_margin;   // 0.8
y_capi = mr_l/2;                          // 7.7
y_end  = y_capi + cap_t;                  // 10.7
depth  = mr_l + cap_t;                    // 18.4

module u_slot(xc) {
    translate([xc, y_capi - 1, wire_zc]) rotate([-90, 0, 0])
        cylinder(h = cap_t + 2, d = wire_d, $fn = 96);
    translate([xc - wire_d/2, y_capi - 1, -1]) cube([wire_d, cap_t + 2, wire_zc + 1]);
}

// 止口区域: 宽度加 gw, 顶面 rim_h + gh, 底面 z0 —— 左右全长 + 开口端两段 (|X| >= 本体段槽半宽) + 后边全宽
module rim_region(gw, gh, z0) {
    h = rim_h + gh - z0;
    translate([-half_l, y_end - (rear_rim_w + gw), z0]) cube([2*half_l, rear_rim_w + gw, h]);
    for (sx = [-1, 1]) {
        translate([sx > 0 ? half_l - (rim_w + gw) : -half_l, y_open, z0]) cube([rim_w + gw, depth, h]);
        translate([sx > 0 ? ch_w_b/2 : -half_l, y_open, z0]) cube([half_l - ch_w_b/2, rim_w + gw, h]);
    }
}

module mr30_clamp_12p3x5p3x15p4() {
    difference() {
        translate([-half_l, y_open, 0]) cube([2*half_l, depth, htop]);
        translate([-ch_w_b/2, y_open - 1, -1]) cube([ch_w_b, (y_step - y_open) + 1, ch_h_b + 1]);
        translate([-ch_w_s/2, y_step, -1]) cube([ch_w_s, y_capi - y_step, ch_h_s + 1]);
        for (sx = [-1, 1])
            translate([sx*hx, y_open + hole_y_open, -1]) cylinder(h = htop + 2, d = hole_d, $fn = 96);
        for (i = [0 : n_wire - 1]) u_slot((i - (n_wire - 1)/2) * wire_pitch);
        rim_region(assy_clr, 0, -1);      // 底面台阶: 竖直面让 0.1, 高度贴合
    }
}

// 件 2 (装配坐标, 底板 z -base_t..0; 导出 STL 整体上移 base_t)
module mr30_shim_38x18p4x2p25() {
    difference() {
        union() {
            translate([-half_l, y_open, -base_t]) cube([2*half_l, depth, base_t]);
            translate([-boss_w/2, y_open, 0]) cube([boss_w, body_l, body_lift]);
            difference() {
                rim_region(0, 0, 0);
                if (ledge_h < rim_h)      // 只有线底低于边框顶才削 (XT60 线底 3.35 不削)
                    for (i = [0 : n_wire - 1])
                        translate([(i - (n_wire - 1)/2) * wire_pitch - wire_d/2, y_capi - 1, ledge_h]) cube([wire_d, cap_t + 2, rim_h + 1]);
            }
        }
        for (sx = [-1, 1])
            translate([sx*hx, y_open + hole_y_open, -base_t - 1]) cylinder(h = base_t + 2, d = hole_d, $fn = 96);
    }
}

mr30_clamp_12p3x5p3x15p4();
// %mr30_shim_38x18p4x2p25();
