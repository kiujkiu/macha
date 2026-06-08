// POV 3D baseplate — parametric

base_side       = 100;    // 底板边长
base_thick      = 5;      // 底板厚

m6_pattern_side = 75;     // M6 孔阵列正方形边长
m6_diam         = 6.5;

m3_diag         = 25;     // M3 孔阵列正方形对角
m3_diam         = 3.2;
cb_diam         = 7;      // M3 沉孔直径
cb_depth        = 2;      // M3 沉孔深（自底面向上）

boss_od         = 65;
boss_id         = 55;
boss_h          = 23;

notch_a_start   = 80;
notch_a_end     = 100;
notch_h         = 8;

// derived
m3_side  = m3_diag / sqrt(2);
notch_r  = boss_od / 2 + 2;

module baseplate() {
    union() {
        // === base with holes (notch does NOT cut the base) ===
        difference() {
            translate([-base_side/2, -base_side/2, 0])
                cube([base_side, base_side, base_thick]);
            // M6 corner holes
            for (sx = [-1, 1]) for (sy = [-1, 1])
                translate([sx * m6_pattern_side/2, sy * m6_pattern_side/2, -1])
                    cylinder(h = base_thick + 2, d = m6_diam, $fn = 48);
            // M3 center holes + Φ7 counterbore (from bottom)
            for (sx = [-1, 1]) for (sy = [-1, 1]) {
                translate([sx * m3_side/2, sy * m3_side/2, -1])
                    cylinder(h = base_thick + 2, d = m3_diam, $fn = 32);
                translate([sx * m3_side/2, sy * m3_side/2, -1])
                    cylinder(h = cb_depth + 1, d = cb_diam, $fn = 48);
            }
        }
        // === boss with notch only on the boss ===
        translate([0, 0, base_thick]) difference() {
            // annular boss
            difference() {
                cylinder(h = boss_h, d = boss_od, $fn = 96);
                translate([0, 0, -1])
                    cylinder(h = boss_h + 2, d = boss_id, $fn = 96);
            }
            // notch (pie slice), starts exactly at boss bottom
            linear_extrude(height = notch_h + 0.1)
                polygon(concat(
                    [[0, 0]],
                    [for (i = [0:24])
                        let (a = notch_a_start + i*(notch_a_end - notch_a_start)/24)
                        [notch_r*cos(a), notch_r*sin(a)]]
                ));
        }
    }
}

baseplate();
