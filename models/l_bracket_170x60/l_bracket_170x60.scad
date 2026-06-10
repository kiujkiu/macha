// POV 3D L-bracket — parametric
//
// L-shape with long leg along +X, short leg along +Z, both 50 mm wide
// along Y. Outer dimensions measured to the outside of each leg.

leg_a = 200;   // long-leg outer length — was 170, +30 on open end
leg_b = 70;    // short-leg outer length — was 60, +10 to reach rim outer PCD
width = 90;    // was 80
thick = 4;

gusset_width = 5;
gusset_y_positions = [gusset_width/2, width - gusset_width/2];   // 2 edge gussets

corner_m3_diam   = 3.2;
corner_boss_diam = 7;
corner_boss_h    = 2;
corner_cb_diam   = 4.2;
corner_cb_depth  = 4;
corner_rect_x    = 49;
corner_rect_y    = 58;
hleg_feat_x_shift = 30;                  // all hleg-top features shifted +30 in X
corner_cx        = hleg_feat_x_shift + 52;   // 82
corner_cy        = 45.5;

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
m3_spacing_c = 70;

// Bottom-row holes (+Y side) are shifted (+1, +1) from the mirror position
shift_bot_x  = 1;
shift_bot_y  = 1;

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
            // 4 × Φ7 × 2 bosses on top of hleg at corner positions
            for (sx = [-1, 1]) for (sy = [-1, 1])
                translate([corner_cx + sx * corner_rect_x/2,
                           corner_cy + sy * corner_rect_y/2, thick])
                    cylinder(h = corner_boss_h, d = corner_boss_diam, $fn = 48);
        }
        // 6 × M3 hleg
        for (p = [[m3_x_a, m3_spacing_a],
                  [m3_x_b, m3_spacing_b],
                  [m3_x_c, m3_spacing_c]]) {
            hole_at(p[0],                 width/2 - p[1]/2);
            hole_at(p[0] + shift_bot_x,   width/2 + p[1]/2 + shift_bot_y);
        }
        // 4 × M3 through boss+hleg
        for (sx = [-1, 1]) for (sy = [-1, 1])
            translate([corner_cx + sx * corner_rect_x/2,
                       corner_cy + sy * corner_rect_y/2, -1])
                cylinder(h = thick + corner_boss_h + 2, d = corner_m3_diam, $fn = 32);
        // 4 × Φ4.2 × 4 counterbore from bottom
        for (sx = [-1, 1]) for (sy = [-1, 1])
            translate([corner_cx + sx * corner_rect_x/2,
                       corner_cy + sy * corner_rect_y/2, -1])
                cylinder(h = corner_cb_depth + 1, d = corner_cb_diam, $fn = 48);
        // 4 × M3 vleg (trapezoid matching rim_ring mating holes)
        for (p = vleg_m3_positions) vleg_hole(p[0], p[1]);
        // 2 × M3 through both gussets along Y
        for (gz = gusset_hole_z_positions)
            translate([gusset_hole_x, -1, gz])
                rotate([-90, 0, 0])
                    cylinder(h = width + 2, d = gusset_hole_diam, $fn = 32);
    }
}

l_bracket();
