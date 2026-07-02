// 米联派 MLKPAI-FS03 ZYNQ-7020 核心板 数字孪生 (买来板,非打印)
// 仅含: 板外形 + 4×M3 角孔 + 两条 2×25 排针 (J11 上 / J12 下)。居中坐标系,+Y 上。
bw = 85; bh = 56; thick = 1.6;      // 板厚假定 1.6 (位号图无标注)
chx = 39.5; chy = 25; m3 = 3.2;     // 角孔 间距 79×50 (3mm 内缩) —— 已确认
pitch = 2.54; ncol = 25; row_dy = 2.54;
hdr_yc = 24.15;                     // 排针中心线 |Y|
pin_sq = 0.64; pin_up = 5.6; base_h = 2.6;   // 针脚露出 5.6, 座厚 2.6
pin_len = 11;                                 // 针全长 11 (两面都露出)
pin_bot = -(base_h + pin_up);                 // -8.2
base_l = ncol * pitch;             // 63.5
base_w = row_dy + 3;               // 5.54

module mlkpai_board() {
    difference() {
        translate([-bw/2, -bh/2, 0]) cube([bw, bh, thick]);
        for (s = [[-chx,chy],[chx,chy],[-chx,-chy],[chx,-chy]])
            translate([s[0], s[1], -1]) cylinder(h = thick+2, d = m3, $fn = 48);
    }
    header(hdr_yc);      // J11 顶
    header(-hdr_yc);     // J12 底
}

module header(yc) {
    // 塑料基座 (板底面, 排针朝下)
    translate([-base_l/2, yc-base_w/2, -base_h]) cube([base_l, base_w, base_h]);
    // 2×25 方针 (向下穿出)
    for (i = [0:ncol-1]) {
        x = (i - (ncol-1)/2) * pitch;
        for (y = [yc-row_dy/2, yc+row_dy/2])
            translate([x-pin_sq/2, y-pin_sq/2, pin_bot])
                cube([pin_sq, pin_sq, pin_len]);       // 全长 11, 顶面露出 1.2
    }
}

mlkpai_board();
