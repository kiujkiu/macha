// top_cap_v2 — v2 rotor cap (POV3D top steady bearing), parametric mirror of
// build_cap_v2.py. L-SHAPE: leg at the +X end, outer face flush with the slab
// +X edge (screen assembly rotated 180 deg -> screen_plate back at asm X=+13.27).
// Modeled in PRINT orientation: slab top face on Z=0 (bed),
// back leg rising up (+Z). Assembly mapping: asm_z = CAPTOP - z, asm_x = x,
// asm_y = -y  (CAPTOP = 292.7, asm Z datum = perfboard top, axis = (0,0)).
// Units: mm. PLA, print flat, support-free.

$fn = 96;

/* ---------- parameters ---------- */
// slab (asm Z 283.7..292.7)
slab_t   = 9.0;
slab_x0  = -65.0;      // asm X -65
slab_x1  =  17.27;     // asm X +17.27 (flush with the leg outer face)
slab_hw  =  72.0;      // Y half-width (+-72 -> 144)

// back leg (asm X +13.27..+17.27, Z 247..292.7)
leg_x0   =  13.27;     // front face lands on screen_plate back (asm X=+13.27)
leg_x1   =  17.27;     // outer face flush with slab +X edge -> L section
leg_hw   =  56.0;      // Y +-56 -> 112 wide
leg_h    =  45.7;      // print z 0..45.7 (asm 247..292.7)

// axis bore + M6x40 flat-head recess (recess from slab BOTTOM = print top)
m6_bore    = 6.2;
head_d     = 13.0;
head_depth = 2.7;

// cap fixing: 2 x M3 clearance through the leg, along X
m3_clear = 3.4;
screw_y  = 49.975;     // asm Y=+-49.975 (screen top-row nut holes, M3x16)
screw_pz = 39.5;       // print z (= 292.7 - asm 253.2)

// counterweight bank, -X overhang: 10 + 9 = 19 x Phi6.5, 品字形
cw_d      = 6.5;
cw_tri    = 14.0;                       // equilateral-triangle pitch
cw_row_dx = cw_tri * sin(60);           // 12.12 row spacing
cw_ax     = -46.0;                      // row A (10 holes)
cw_bx     = cw_ax - cw_row_dx;          // row B -58.12 (9 holes)
eps = 1.0;

/* ---------- part ---------- */
module top_cap_v2() {
    difference() {
        union() {
            // slab, flat face on the bed
            translate([slab_x0, -slab_hw, 0])
                cube([slab_x1 - slab_x0, 2*slab_hw, slab_t]);
            // back leg (inside the slab footprint — no overhang)
            translate([leg_x0, -leg_hw, 0])
                cube([leg_x1 - leg_x0, 2*leg_hw, leg_h]);
        }
        // axis: Phi6.2 through slab
        translate([0, 0, -eps])
            cylinder(h = slab_t + 2*eps, d = m6_bore);
        // Phi13 x 2.7 head recess from the slab bottom face (= print TOP)
        translate([0, 0, slab_t - head_depth])
            cylinder(h = head_depth + eps, d = head_d);
        // 2 x Phi3.4 along X through the leg
        for (sy = [-screw_y, screw_y])
            translate([leg_x0 - eps, sy, screw_pz])
                rotate([0, 90, 0])
                    cylinder(h = (leg_x1 - leg_x0) + 2*eps, d = m3_clear);
        // 19 x Phi6.5 counterweight holes + Phi13 x 2.7 CB from the slab TOP
        // face (asm Z292.7 = print z0, bed side)
        for (k = [0:9])
            cw_hole(cw_ax, (k - 4.5) * cw_tri);
        for (k = [0:8])
            cw_hole(cw_bx, (k - 4.0) * cw_tri);
    }
}

module cw_hole(x, y) {
    translate([x, y, -eps]) {
        cylinder(h = slab_t + 2*eps, d = cw_d);           // through
        cylinder(h = head_depth + eps, d = head_d);       // counterbore
    }
}

top_cap_v2();
