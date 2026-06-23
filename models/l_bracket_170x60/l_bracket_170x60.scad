// POV 3D L-bracket — parametric
//
// L-shape with long leg along +X, short leg along +Z, both 50 mm wide
// along Y. Outer dimensions measured to the outside of each leg.

leg_a = 200;   // long-leg outer length — was 170, +30 on open end
leg_b = 70;    // short-leg outer length — was 60, +10 to reach rim outer PCD
width = 90;    // was 80
thick = 4;

gusset_width = 5;
gusset_y_positions = [gusset_width/2, width/2, width - gusset_width/2];  // 2 edge + 1 middle

// (4 corner boss/M3/CB features removed per user request 2026-06-11)
hleg_feat_x_shift = 30;                  // all hleg-top features shifted +30 in X

// 2 × M3 gusset through-holes (along Y, hit both gussets)
gusset_hole_diam       = 3.2;
gusset_hole_x          = 19;          // 15 mm right of gusset's vertical (left) edge
gusset_hole_z_positions = [20, 50];   // lower / upper, 30 mm spacing

// 4 × M3 vleg holes — match 4 rim_ring holes (trapezoid, not a rectangle)
vleg_m3_diam        = 3.2;
rim_r_in            = 35;      // PCD Φ70
rim_r_out           = 77.5;    // PCD Φ155
rim_ang_a           = 157.5;   // first mating angle
rim_ang_b           = 202.5;   // second mating angle (symmetric about rim −X)
hleg_dist_from_center = 14.3;  // rim center → hleg inner 200×90 face
function vleg_pos(R, a) = [R * sin(a) + width/2, -R * cos(a) - hleg_dist_from_center];
vleg_m3_positions = [
    vleg_pos(rim_r_in,  rim_ang_a),
    vleg_pos(rim_r_in,  rim_ang_b),
    vleg_pos(rim_r_out, rim_ang_a),
    vleg_pos(rim_r_out, rim_ang_b),
];

m3_diam      = 3.2;
m3_x_a       = hleg_feat_x_shift + 95;   // 125
m3_spacing_a = 20;
m3_x_b       = m3_x_a + 66;              // 191
m3_spacing_b = 20;
m3_x_c       = hleg_feat_x_shift + 8;    // 38
m3_spacing_c = 67;   // was 70; +1 bottom-shift → actual hole c-to-c 68

// 2 rectangular cutouts through hleg (30 Y × 13 X, left edge X=10, c-to-c 45)
slot_len    = 30;
slot_w      = 13;
slot_x_left = 10;
slot_cc     = 45;
slot_y_centers = [width/2 - slot_cc/2, width/2 + slot_cc/2];   // 22.5, 67.5

// Bottom-row holes (+Y side) are shifted (+1, +1) from the mirror position;
// pair C's bottom hole gets an extra +1 Y (2026-06-12)
shift_bot_x  = 1;
shift_bot_y  = 1;
extra_bot_y_c = 1;

module hole_at(x, y) {
    translate([x, y, -1])
        cylinder(h = thick + 2, d = m3_diam, $fn = 32);
}

module gusset(y_center) {
    translate([0, y_center + gusset_width/2, 0])
        rotate([90, 0, 0])
            linear_extrude(height = gusset_width)
                polygon([[thick, thick], [leg_a, thick], [thick, leg_b]]);
}

module vleg_hole(y, z) {
    translate([-1, y, z])
        rotate([0, 90, 0])
            cylinder(h = thick + 2, d = vleg_m3_diam, $fn = 32);
}

module l_bracket() {
    difference() {
        union() {
            cube([leg_a, width, thick]);
            cube([thick, width, leg_b]);
            for (yc = gusset_y_positions) gusset(yc);
        }
        // 6 × M3 hleg
        for (p = [[m3_x_a, m3_spacing_a, 0],
                  [m3_x_b, m3_spacing_b, 0],
                  [m3_x_c, m3_spacing_c, extra_bot_y_c]]) {
            hole_at(p[0],                 width/2 - p[1]/2);
            hole_at(p[0] + shift_bot_x,   width/2 + p[1]/2 + shift_bot_y + p[2]);
        }
        // 4 × M3 vleg (trapezoid matching rim_ring mating holes)
        for (p = vleg_m3_positions) vleg_hole(p[0], p[1]);
        // 2 rectangular cutouts through hleg plate
        for (sy = slot_y_centers)
            translate([slot_x_left, sy - slot_len/2, -1])
                cube([slot_w, slot_len, thick + 2]);
        // 2 × M3 through both gussets along Y
        for (gz = gusset_hole_z_positions)
            translate([gusset_hole_x, -1, gz])
                rotate([-90, 0, 0])
                    cylinder(h = width + 2, d = gusset_hole_diam, $fn = 32);
    }
}

l_bracket();
