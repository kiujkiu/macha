// POV 3D baseplate_collar — merged baseplate + ring collar (parametric)
//
// Combines:
//   - baseplate (square 100×100×5, central boss Φ65/Φ55 H23)
//   - ring collar Φ80/Φ65 H13, sleeved over boss
// Both notches aligned at 75°–105° (+Y direction).

base_side       = 100;
base_thick      = 5;

m6_diag         = 75 * sqrt(2);       // 106.07 (2026-07-29 v4: 配 200×200 网格板)
m6_pattern_side = m6_diag / sqrt(2);   // = 75 方形边长 → 脚落网格位 (±37.5,±37.5)
m6_diam         = 6.5;

m3_diag         = 25;
m3_diam         = 3.2;
cb_diam         = 7;
cb_depth        = 2;

center_cb_diam  = 12;
center_cb_depth = 1;

boss_od         = 65;
boss_id         = 55;
boss_h          = 23;

notch_a_start   = 75;
notch_a_end     = 105;
notch_h         = 8;

collar_od         = 84;  // 80→84 (2026-07-10) 螺母孔加肉, M6帽Φ12.5留1.75
collar_id         = 65;       // = boss_od
collar_h          = 13;
collar_z0         = base_thick;
collar_notch_h    = 8;  // 6→8 (2026-07-13) 与凸台同高

// flange_disc 连接孔 (2026-07-10): flange 内圈 8 孔 (PCD 72.5) 坐在套环顶面
flange_hole_r   = 36.25;      // = PCD 72.5 / 2, 套环壁 32.5..40 正中
flange_m3_diam  = 3.2;
flange_cb_diam  = 4.2;        // M3×4×4.5 铜花螺母
flange_cb_depth = 4;
collar_top      = collar_z0 + collar_h;   // 18

// derived
m3_side    = m3_diag / sqrt(2);
notch_r    = boss_od / 2 + 2;
collar_notch_r = collar_od / 2 + 2;

module baseplate_collar_v4() {
  difference() {
    union() {
        // === base with holes (no notch cuts the base) ===
        difference() {
            translate([-base_side/2, -base_side/2, 0])
                cube([base_side, base_side, base_thick]);
            for (sx = [-1, 1]) for (sy = [-1, 1])
                translate([sx * m6_pattern_side/2, sy * m6_pattern_side/2, -1])
                    cylinder(h = base_thick + 2, d = m6_diam, $fn = 48);
            for (sx = [-1, 1]) for (sy = [-1, 1]) {
                translate([sx * m3_side/2, sy * m3_side/2, -1])
                    cylinder(h = base_thick + 2, d = m3_diam, $fn = 32);
                translate([sx * m3_side/2, sy * m3_side/2, -1])
                    cylinder(h = cb_depth + 1, d = cb_diam, $fn = 48);
            }
            // 中央 Φ12 沉孔（顶面向下 1mm）
            translate([0, 0, base_thick - center_cb_depth])
                cylinder(h = center_cb_depth + 1, d = center_cb_diam, $fn = 64);
        }

        // === boss with notch ===
        translate([0, 0, base_thick]) difference() {
            difference() {
                cylinder(h = boss_h, d = boss_od, $fn = 96);
                translate([0, 0, -1])
                    cylinder(h = boss_h + 2, d = boss_id, $fn = 96);
            }
            linear_extrude(height = notch_h + 0.1)
                polygon(concat(
                    [[0, 0]],
                    [for (i = [0:24])
                        let (a = notch_a_start + i*(notch_a_end - notch_a_start)/24)
                        [notch_r*cos(a), notch_r*sin(a)]]
                ));
        }

        // === ring collar (sleeved over boss) with aligned notch ===
        translate([0, 0, collar_z0]) difference() {
            difference() {
                cylinder(h = collar_h, d = collar_od, $fn = 128);
                translate([0, 0, -1])
                    cylinder(h = collar_h + 2, d = collar_id, $fn = 128);
            }
            translate([0, 0, -0.05])
                linear_extrude(height = collar_notch_h + 0.1)
                    polygon(concat(
                        [[0, 0]],
                        [for (i = [0:28])
                            let (a = notch_a_start + i*(notch_a_end - notch_a_start)/28)
                            [collar_notch_r*cos(a), collar_notch_r*sin(a)]]
                    ));
        }
    }
    // === 8× flange_disc 连接孔: Φ3.2 通 (Z0..18) + Φ4.2×4 沉孔 顶面+底面 ===
    for (k = [0:7]) {
        a = 22.5 + 45 * k;
        translate([flange_hole_r*cos(a), flange_hole_r*sin(a), -1])
            cylinder(h = collar_top + 2, d = flange_m3_diam, $fn = 32);
        translate([flange_hole_r*cos(a), flange_hole_r*sin(a),
                   collar_top - flange_cb_depth])
            cylinder(h = flange_cb_depth + 1, d = flange_cb_diam, $fn = 32);
        translate([flange_hole_r*cos(a), flange_hole_r*sin(a), -1])
            cylinder(h = flange_cb_depth + 1, d = flange_cb_diam, $fn = 32);
    }
  }
}

baseplate_collar_v4();
