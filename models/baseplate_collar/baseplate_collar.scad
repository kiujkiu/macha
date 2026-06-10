// POV 3D baseplate_collar — merged baseplate + ring collar (parametric)
//
// Combines:
//   - baseplate (square 100×100×5, central boss Φ65/Φ55 H23)
//   - ring collar Φ80/Φ65 H13, sleeved over boss
// Both notches aligned at 75°–105° (+Y direction).

base_side       = 100;
base_thick      = 5;

m6_pattern_side = 75;
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

collar_od         = 80;
collar_id         = 65;       // = boss_od
collar_h          = 13;
collar_z0         = base_thick;
collar_notch_h    = 6;

// derived
m3_side    = m3_diag / sqrt(2);
notch_r    = boss_od / 2 + 2;
collar_notch_r = collar_od / 2 + 2;

module baseplate_collar() {
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
}

baseplate_collar();
