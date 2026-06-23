// POV 3D 盒子 — open on ONE LONG SIDE (+X), windowed asymmetric front panel
// 外形 22(X) × 24(Y) × 64(Z)
// 开口面 = +X 侧 (64×24)
// 前面(-Y) 1mm(开窗+孔) / 后面(+Y) 2mm(孔) / -X 侧 2mm / 顶·底(±Z) 2mm
// 前面板中央开穿窗口: 沿Z(64长) 35 × 沿X(22宽) 14, 居中
// 前后面板各 2 × M4(Φ4.5) 通孔, X 居中, 中心距 44 (Z=10,54)

ext_l = 22; ext_w = 24; ext_h = 64;   // X, Y, Z
wall_front = 1; wall_back = 2; wall_side = 2; wall_end = 2;
win_z = 35; win_x = 14; win_zc = ext_h/2; win_xc = 4;   // window (右移4,右缘到+X开口边)
hole_d = 4.5; hole_cc = 44;
hole_z = [ext_h/2 - hole_cc/2, ext_h/2 + hole_cc/2];   // 10, 54

cav_x0 = -ext_l/2 + wall_side;   // -9  (+X open)
cav_y0 = -ext_w/2 + wall_front;  // -11
cav_y1 =  ext_w/2 - wall_back;   //  10
cav_z0 = wall_end;               // 2
cav_z1 = ext_h - wall_end;       // 62

module box_22x24x64() {
    difference() {
        translate([-ext_l/2, -ext_w/2, 0]) cube([ext_l, ext_w, ext_h]);
        // cavity, open toward +X
        translate([cav_x0, cav_y0, cav_z0])
            cube([ext_l/2 + 1 - cav_x0, cav_y1 - cav_y0, cav_z1 - cav_z0]);
        // through window in front (-Y) panel; +X edge reaches the panel edge
        translate([win_xc - win_x/2, -ext_w/2 - 1, win_zc - win_z/2])
            cube([ext_l/2 + 1 - (win_xc - win_x/2), wall_front + 1.5, win_z]);
        // 2 × M4 through-holes along Y
        for (z = hole_z)
            translate([0, 0, z]) rotate([90, 0, 0])
                cylinder(h = ext_w + 4, d = hole_d, $fn = 48, center = true);
    }
}

box_22x24x64();
