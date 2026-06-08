// POV 3D hub disc — parametric source
//
// All mm, axis along +Z, base bottom at Z=0.

base_od        = 165;
base_t         = 3;     // Z = 0 .. 3

lower_boss_d   = 80;
lower_boss_t   = 2.5;   // Z = 3 .. 5.5

upper_boss_d   = 60;
upper_boss_t   = 3.5;   // Z = 5.5 .. 9

rim_boss_id    = 145;
rim_boss_od    = 165;
rim_boss_t     = 2.5;   // Z = 3 .. 5.5
rim_cutout_a_s = 0;     // 外凸圈切口起始角
rim_cutout_a_e = 5;     // 外凸圈切口结束角

m3_diam        = 3.2;
cb_a_diam      = 7.0;   // diamond
cb_b_diam      = 4.2;   // square / PCD-70 / PCD-155
cb_depth       = 4.0;   // pocket depth (4 mm)

// Center counterbore — Φ6.2 × 2.2 mm pocket only (no through-hole),
// opens from the BOTTOM face at (0, 0).
center_cb_diam  = 6.2;
center_cb_depth = 2.2;

// Direction toggle: the central diamond (pattern A) counterbore now opens
// from the TOP face (top of upper boss) downward, recessing the screw head
// into the Φ60 upper boss. All other 20 CBs still open from the bottom.
diamond_cb_from_top = true;

// derived
total_h        = base_t + lower_boss_t + upper_boss_t;  // 9

// Pattern A — diagonals 12 and 15
diag_x = 12;
diag_y = 15;

// Pattern B — square 30×30
square_side = 30;

// Pattern C/D — PCDs
inner_pcd_r = 35;   // Φ70
outer_pcd_r = 77.5; // Φ155

// Angular rotation applied to BOTH PCD ring patterns (degrees, CCW positive).
// The 4 diamond and 4 square holes are NOT rotated.
ring_hole_rotation = 22.5;

module through_hole(x, y) {
    translate([x, y, -1])
        cylinder(h = total_h + 2, d = m3_diam, $fn = 32);
}

module counterbore(x, y, d) {
    // Bottom-opening CB: Z = -0.1 .. cb_depth
    translate([x, y, -0.1])
        cylinder(h = cb_depth + 0.1, d = d, $fn = 32);
}

module counterbore_top(x, y, d) {
    // Top-opening CB: Z = (total_h - cb_depth) .. (total_h + 0.1)
    translate([x, y, total_h - cb_depth])
        cylinder(h = cb_depth + 0.1, d = d, $fn = 32);
}

module hub_disc() {
    difference() {
        union() {
            // base disc (solid)
            cylinder(h = base_t, d = base_od, $fn = 192);
            // lower center boss
            translate([0, 0, base_t])
                cylinder(h = lower_boss_t, d = lower_boss_d, $fn = 192);
            // upper center boss
            translate([0, 0, base_t + lower_boss_t])
                cylinder(h = upper_boss_t, d = upper_boss_d, $fn = 192);
            // outer rim boss (annular) with angular cutout
            translate([0, 0, base_t]) difference() {
                difference() {
                    cylinder(h = rim_boss_t, d = rim_boss_od, $fn = 192);
                    translate([0, 0, -1])
                        cylinder(h = rim_boss_t + 2, d = rim_boss_id, $fn = 192);
                }
                // pie wedge subtracted from rim only
                translate([0, 0, -0.1])
                    linear_extrude(height = rim_boss_t + 0.2)
                        polygon(concat(
                            [[0, 0]],
                            [for (i = [0:24])
                                let (a = rim_cutout_a_s
                                        + i*(rim_cutout_a_e - rim_cutout_a_s)/24)
                                [(rim_boss_od/2 + 2) * cos(a),
                                 (rim_boss_od/2 + 2) * sin(a)]]
                        ));
            }
        }
        // Pattern A — diamond (4 holes), CB Φ7.
        // CB opens from TOP face when diamond_cb_from_top = true.
        for (p = [[ diag_x/2, 0], [-diag_x/2, 0],
                  [0,  diag_y/2], [0, -diag_y/2]]) {
            through_hole(p[0], p[1]);
            if (diamond_cb_from_top)
                counterbore_top(p[0], p[1], cb_a_diam);
            else
                counterbore(p[0], p[1], cb_a_diam);
        }
        // Pattern B — square (4 holes), CB Φ4.2
        for (p = [[ square_side/2,  square_side/2],
                  [-square_side/2,  square_side/2],
                  [ square_side/2, -square_side/2],
                  [-square_side/2, -square_side/2]]) {
            through_hole(p[0], p[1]);
            counterbore(p[0], p[1], cb_b_diam);
        }
        // Pattern C — inner PCD ring Φ70 (8 holes), rotated by ring_hole_rotation
        for (k = [0 : 7]) {
            a = k * 360 / 8 + ring_hole_rotation;
            x = inner_pcd_r * cos(a);
            y = inner_pcd_r * sin(a);
            through_hole(x, y);
            counterbore(x, y, cb_b_diam);
        }
        // Pattern D — outer PCD ring Φ155 (8 holes), rotated by ring_hole_rotation
        for (k = [0 : 7]) {
            a = k * 360 / 8 + ring_hole_rotation;
            x = outer_pcd_r * cos(a);
            y = outer_pcd_r * sin(a);
            through_hole(x, y);
            counterbore(x, y, cb_b_diam);
        }
        // Center counterbore — Φ6.2 × 2.2 mm bottom-opening pocket (no through)
        translate([0, 0, -0.1])
            cylinder(h = center_cb_depth + 0.1, d = center_cb_diam, $fn = 48);
    }
}

hub_disc();
