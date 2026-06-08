// POV 3D flanged annular disc — parametric

base_od         = 165;
base_id         = 65;
base_t          = 4.5;  // 底盘厚度 5→4.5

inner_boss_od   = 80;
inner_boss_id   = 65;
outer_boss_od   = 165;
outer_boss_id   = 145;
boss_t          = 2.5;  // 凸台高度 2→2.5

m3_diam         = 3.2;
n_holes         = 8;
hole_rotation = -22.5;  // 16 通孔顺时针旋转 20° (CW 为负角)
m42_diam        = 4.2;  // 沉孔直径
m42_depth       = 4;    // 沉孔深度 (从底部 z=0 向上)

outer_cutout_a_s = 40;
outer_cutout_a_e = 45;

slot_r_in   = 40;
slot_r_out  = 82.5;
slot_z_bot  = 2;
slot_z_top  = 7;
slot_a_s    = 0;
slot_a_e = 5;

// derived
inner_hole_r = (inner_boss_id/2 + inner_boss_od/2) / 2;   // 36.25
outer_hole_r = (outer_boss_id/2 + outer_boss_od/2) / 2;   // 77.5
total_h      = base_t + boss_t;                            // 7
cutout_r     = outer_boss_od/2 + 2;

module annular_wedge(r_in, r_out, a_s, a_e, seg = 24) {
    polygon(concat(
        [for (i = [0:seg])
            let (a = a_s + i*(a_e - a_s)/seg)
            [r_out*cos(a), r_out*sin(a)]],
        [for (i = [0:seg])
            let (a = a_e - i*(a_e - a_s)/seg)
            [r_in*cos(a), r_in*sin(a)]]
    ));
}

module pie_wedge(r, a_s, a_e, seg = 24) {
    polygon(concat(
        [[0, 0]],
        [for (i = [0:seg])
            let (a = a_s + i*(a_e - a_s)/seg)
            [r*cos(a), r*sin(a)]]
    ));
}

module flange_disc() {
    difference() {
        union() {
            // ----- base disc with central bore (no cutout) -----
            difference() {
                cylinder(h = base_t, d = base_od, $fn = 192);
                translate([0, 0, -1])
                    cylinder(h = base_t + 2, d = base_id, $fn = 192);
            }
            // ----- inner boss ring (Z = base_t .. total_h) -----
            translate([0, 0, base_t]) difference() {
                cylinder(h = boss_t, d = inner_boss_od, $fn = 192);
                translate([0, 0, -1])
                    cylinder(h = boss_t + 2, d = inner_boss_id, $fn = 192);
            }
            // ----- outer boss ring with 40°-50° cutout (Z = base_t .. total_h) -----
            translate([0, 0, base_t]) difference() {
                difference() {
                    cylinder(h = boss_t, d = outer_boss_od, $fn = 192);
                    translate([0, 0, -1])
                        cylinder(h = boss_t + 2, d = outer_boss_id, $fn = 192);
                }
                // outer boss cutout 40°-50°
                translate([0, 0, -0.1])
                    linear_extrude(height = boss_t + 0.2)
                        pie_wedge(cutout_r, outer_cutout_a_s, outer_cutout_a_e);
            }
        }
        // ----- slot wedge: cuts base + outer boss in 0°-10°, R=40..82.5, Z=3..7 -----
        translate([0, 0, slot_z_bot])
            linear_extrude(height = slot_z_top - slot_z_bot)
                annular_wedge(slot_r_in, slot_r_out, slot_a_s, slot_a_e);

        // ----- 8 × M3 inner holes (through 7mm), 顺时针 20° -----
        for (k = [0 : n_holes - 1]) {
            a = k * 360 / n_holes + hole_rotation;
            translate([inner_hole_r*cos(a), inner_hole_r*sin(a), -1])
                cylinder(h = total_h + 2, d = m3_diam, $fn = 32);
        }
        // ----- 8 × M3 outer holes (through 7mm), 顺时针 20° -----
        for (k = [0 : n_holes - 1]) {
            a = k * 360 / n_holes + hole_rotation;
            translate([outer_hole_r*cos(a), outer_hole_r*sin(a), -1])
                cylinder(h = total_h + 2, d = m3_diam, $fn = 32);
        }
        // ----- 8 × M4.2 沉孔 内圈孔位 (从底部 z=0 向上 4mm) -----
        for (k = [0 : n_holes - 1]) {
            a = k * 360 / n_holes + hole_rotation;
            translate([inner_hole_r*cos(a), inner_hole_r*sin(a), -0.1])
                cylinder(h = m42_depth + 0.1, d = m42_diam, $fn = 32);
        }
        // ----- 8 × M4.2 沉孔 外圈孔位 (从底部 z=0 向上 4mm) -----
        for (k = [0 : n_holes - 1]) {
            a = k * 360 / n_holes + hole_rotation;
            translate([outer_hole_r*cos(a), outer_hole_r*sin(a), -0.1])
                cylinder(h = m42_depth + 0.1, d = m42_diam, $fn = 32);
        }
    }
}

flange_disc();
