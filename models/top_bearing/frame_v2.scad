// frame_v2.scad — POV3D top_bearing v2 static frames (frame_A_v2 / frame_B_v2)
// Parametric mirror of build_frame_v2.py. PLA.
//
// v2 vs v1: posts moved IN — perfboard is a centre-anchored 25 mm grid, the
// four Φ8×350 M6-threaded posts sit in the outermost corner holes (±125,±125)
// → post_r = 125·√2 = 176.777 (v1: 194.5). Ribs R24..R164 (end ~12.78 from
// pad centre). Everything else identical to v1.
//
// Assembly heights: post tops Z=350; A hub 350..358 (688 #1 pressed 353..358);
// B hub 358..366 (688 #2 pressed 361..366).
// BOM: 688 ×2, M6×16 ×2 (A pads), M6×30 ×2 (B column pads), M3×20+nut ×4.

part = "both";              // "A" | "B" | "both"

seg        = 96;
m3_tight   = 3.2;           // hub clamp holes (thread-forming)
m6_clear   = 6.5;           // pad through holes (no counterbore)

arm_w      = 18;            // arm width = pad Φ18
arm_t      = 8;             // arm thickness
rib_w      = 4;
rib_t      = 6;
hub_d      = 44;
bolt_r     = 14;            // M3 bolt circle (45° + 90k°)
brg_d      = 15.8;          // 688 press pocket Φ
brg_depth  = 5;             // 688 width (8×16×5)
brg_sh_d   = 13;            // shoulder bore, through
pad_d      = 18;
post_r     = 125 * sqrt(2); // 176.777
rib_r0     = 24;
rib_r1     = 164;

// upper=false → frame_A_v2 (z 0..14: arms 0..8, ribs 8..14, pads h8)
// upper=true  → frame_B_v2 (z 0..16: pads h16, arms 8..16, ribs 2..8)
module frame_piece(upper = false) {
    z_arm = upper ? 8 : 0;
    z_top = z_arm + arm_t;                 // local hub top: A 8, B 16
    rib_z = upper ? z_arm - rib_t : z_arm + arm_t;
    pad_h = upper ? 16 : 8;
    difference() {
        union() {
            translate([0, 0, z_arm])
                cylinder(h = arm_t, d = hub_d, $fn = seg);
            for (ang = [0, 90]) rotate([0, 0, ang]) {
                translate([18, -arm_w/2, z_arm])
                    cube([post_r - 18, arm_w, arm_t]);        // arm bar
                translate([rib_r0, -rib_w/2, rib_z])
                    cube([rib_r1 - rib_r0, rib_w, rib_t]);    // rib
                translate([post_r, 0, 0])
                    cylinder(h = pad_h, d = pad_d, $fn = seg); // post pad
            }
        }
        // M6 Φ6.5 plain through holes at the pads
        for (ang = [0, 90]) rotate([0, 0, ang])
            translate([post_r, 0, -1])
                cylinder(h = 20, d = m6_clear, $fn = 32);
        // 688 pocket Φ15.8×5 from the local top + Φ13 shoulder bore through
        translate([0, 0, z_top - brg_depth])
            cylinder(h = brg_depth + 1, d = brg_d, $fn = 96);
        translate([0, 0, -1])
            cylinder(h = 30, d = brg_sh_d, $fn = 96);
        // 4 × Φ3.2 @ R14 (45° + 90k°) clamping the two hubs
        for (k = [0 : 3]) rotate([0, 0, 45 + 90*k])
            translate([bolt_r, 0, -1])
                cylinder(h = 30, d = m3_tight, $fn = 24);
    }
}

// frame_A_v2: print as built
if (part == "A" || part == "both")
    frame_piece(upper = false);

// frame_B_v2: PRINT orientation = flipped (ribs/pads up), as in the STL
if (part == "B" || part == "both")
    translate(part == "both" ? [60, -60, 0] : [0, 0, 0])
        translate([0, 0, 16]) rotate([180, 0, 0])
            frame_piece(upper = true);
