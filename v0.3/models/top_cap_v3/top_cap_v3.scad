// top_cap_v3 — v3 rotor cap (POV3D top steady bearing, double-screen rotor),
// parametric mirror of build_cap.py. SYMMETRIC flat slab + two-leg CLEVIS:
// both slab faces carry screens, so the legs grip the central top TAB of
// screen_plate_v3 (6 thick, between the leg inner faces at X ±3).
// Modeled in PRINT orientation: slab top face on Z=0 (bed), legs rising up
// (+Z). Assembly mapping: asm_z = CAPTOP - z, asm_x = x, asm_y = -y
// (CAPTOP = 292.7, asm Z datum = perfboard top, axis = (0,0)); the part is
// Y-symmetric so the flip is a no-op. Units: mm. PLA, print flat, support-free.
// ASSEMBLY ORDER: preinstall the M6x40 flat head in the cap BEFORE bolting
// the clevis onto the tab (tab top asm 280.7 sits only 3 under the head).

$fn = 96;

/* ---------- parameters ---------- */
captop = 292.7;        // asm Z of the slab top face (print z0)

// slab (asm Z 283.7..292.7 -> print z 0..9), 130 x 144 x 9
slab_t  = 9.0;
slab_hx = 65.0;        // X +-65 -> 130
slab_hw = 72.0;        // Y +-72 -> 144

// clevis legs 4 thick x2 (asm X +-(3..7), Y +-36, Z 267..292.7)
leg_t  = 4.0;
leg_xi = 3.0;          // inner face = tab face (tab 6 thick)
leg_hw = 36.0;         // Y +-36 -> 72 wide
leg_zbot_asm = 267.0;  // screen top 264.7 + 2.3
leg_h  = captop - leg_zbot_asm;    // 25.7 (print z 0..25.7)

// axis bore + M6x40 flat-head recess (from the slab BOTTOM face = print TOP;
// +1 overshoot intentionally notches the leg roots, as in build_cap.py)
m6_bore    = 6.2;
head_d     = 13.0;
head_depth = 2.7;

// tab fixing: 4 x M3 clearance along X through BOTH legs
m3_clear    = 3.4;
screw_y     = 22.0;                // asm Y = +-22
screw_z_asm = [271.0, 276.5];      // -> print z 21.7 / 16.2

// counterweight banks BOTH +-X ends: 10 + 9 = 19 x Phi6.5 each, 品字形
cw_d      = 6.5;
cw_tri    = 14.0;                  // equilateral-triangle pitch
cw_row_dx = cw_tri * sin(60);      // 12.12 row spacing
cw_ax     = 46.0;                  // row A |X| (10 holes, Y=(k-4.5)*14)
cw_bx     = cw_ax + cw_row_dx;     // row B |X| 58.12 (9 holes, Y=(k-4)*14)
eps = 1.0;

/* ---------- part ---------- */
module top_cap_v3() {
    difference() {
        union() {
            // slab, flat face on the bed
            translate([-slab_hx, -slab_hw, 0])
                cube([2*slab_hx, 2*slab_hw, slab_t]);
            // clevis legs (inside the slab footprint — no overhang)
            for (sx = [-1, 1])
                translate([sx > 0 ? leg_xi : -(leg_xi + leg_t), -leg_hw, 0])
                    cube([leg_t, 2*leg_hw, leg_h]);
        }
        // axis: Phi6.2 through everything at (0,0)
        translate([0, 0, -eps])
            cylinder(h = slab_t + leg_h + 2*eps, d = m6_bore);
        // Phi13 x 2.7 head recess from the slab bottom face (= print TOP);
        // +1 up-overshoot notches the leg roots (asm 282.7..286.4) — intended
        translate([0, 0, slab_t - head_depth])
            cylinder(h = head_depth + 1.0, d = head_d);
        // 4 x Phi3.4 along X through both legs (M3x18: leg4+tab6+leg4=14)
        for (az = screw_z_asm, sy = [-screw_y, screw_y])
            translate([-(leg_xi + leg_t) - eps, sy, captop - az])
                rotate([0, 90, 0])
                    cylinder(h = 2*(leg_xi + leg_t) + 2*eps, d = m3_clear);
        // 2 x 19 Phi6.5 counterweight holes (vertical, through the slab),
        // each with a Phi13 x 2.7 CB from the slab TOP face (= print z0, bed)
        for (sx = [-1, 1]) {
            for (k = [0:9]) cw_hole(sx * cw_ax, (k - 4.5) * cw_tri);
            for (k = [0:8]) cw_hole(sx * cw_bx, (k - 4.0) * cw_tri);
        }
    }
}

module cw_hole(x, y) {
    translate([x, y, -eps]) {
        cylinder(h = slab_t + 2*eps, d = cw_d);        // through
        cylinder(h = head_depth + eps, d = head_d);    // counterbore (bed side)
    }
}

top_cap_v3();
