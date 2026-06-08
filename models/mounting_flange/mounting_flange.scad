// POV 3D mounting flange — parametric

base_od         = 170;
base_id         = 65;
base_t          = 3;

boss_od         = 170;
boss_id         = 165;
boss_h          = 7;

m3_diam         = 3.2;
cb_diam         = 7;
cb_depth        = 2;
n_holes         = 8;
hole_rotation   = 22.5;  // CCW 22.5°

inner_hole_r    = 36.25;     // PCD 72.5
outer_hole_r    = 77.5;      // PCD 155

cut1_a_s        = -5;
cut1_a_e        = 0;
cut2_a_s        = -45;
cut2_a_e        = -40;

// derived
total_h         = base_t + boss_h;    // 10
cutout_r        = boss_od/2 + 2;

module pie_wedge(r, a_s, a_e, seg = 24) {
    polygon(concat(
        [[0, 0]],
        [for (i = [0:seg])
            let (a = a_s + i*(a_e - a_s)/seg)
            [r*cos(a), r*sin(a)]]
    ));
}

module mounting_flange() {
    difference() {
        union() {
            // ----- base ring (OD 170, ID 65, T 3) -----
            difference() {
                cylinder(h = base_t, d = base_od, $fn = 192);
                translate([0, 0, -1])
                    cylinder(h = base_t + 2, d = base_id, $fn = 192);
            }
            // ----- rim boss (Z = base_t .. total_h), with cutouts -----
            translate([0, 0, base_t]) difference() {
                difference() {
                    cylinder(h = boss_h, d = boss_od, $fn = 192);
                    translate([0, 0, -1])
                        cylinder(h = boss_h + 2, d = boss_id, $fn = 192);
                }
                // cutout 1: 0°-10°
                translate([0, 0, -0.1])
                    linear_extrude(height = boss_h + 0.2)
                        pie_wedge(cutout_r, cut1_a_s, cut1_a_e);
                // cutout 2: 40°-50°
                translate([0, 0, -0.1])
                    linear_extrude(height = boss_h + 0.2)
                        pie_wedge(cutout_r, cut2_a_s, cut2_a_e);
            }
        }

        // ----- 8 × M3 inner holes + Φ7 counterbore -----
        for (k = [0 : n_holes - 1]) {
            a = k * 360 / n_holes + hole_rotation;
            translate([inner_hole_r*cos(a), inner_hole_r*sin(a), -1])
                cylinder(h = base_t + 2, d = m3_diam, $fn = 32);
            translate([inner_hole_r*cos(a), inner_hole_r*sin(a), -1])
                cylinder(h = cb_depth + 1, d = cb_diam, $fn = 48);
        }
        // ----- 8 × M3 outer holes + Φ7 counterbore -----
        for (k = [0 : n_holes - 1]) {
            a = k * 360 / n_holes + hole_rotation;
            translate([outer_hole_r*cos(a), outer_hole_r*sin(a), -1])
                cylinder(h = base_t + 2, d = m3_diam, $fn = 32);
            translate([outer_hole_r*cos(a), outer_hole_r*sin(a), -1])
                cylinder(h = cb_depth + 1, d = cb_diam, $fn = 48);
        }
    }
}

mounting_flange();
