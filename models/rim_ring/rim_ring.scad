// POV 3D rim_ring - parametric OpenSCAD source.
//
// Geometry (all mm, axis along +Z, base bottom at Z=0; CCW positive angles,
// 0 deg = +X axis):
//
//   Feature 1 - Base annulus:
//       ID 60, OD 170, height 5  (Z = 0 .. 5)
//       Notch cutout: remove the band r > 40 (Phi > 80),
//                     angles -45 deg .. -40 deg,
//                     Z = 2.5 .. 5
//
//   Feature 2 - 16 Phi3.2 M3 through-holes:
//       PCD Phi70  x 8 holes  (R = 35)
//       PCD Phi155 x 8 holes  (R = 77.5)
//       angles = 22.5 + k * 45  for k = 0..7
//
//   Feature 3 - Outer rim boss:
//       ID 165, OD 170 (2.5 mm wall), height 5.5  (Z = 5 .. 10.5)
//       Two angular cutouts (boss only):
//           -5 deg .. 0 deg
//           -45 deg .. -40 deg

// ===== Parameters =====
BASE_ID = 60.0;
BASE_OD = 170.0;
BASE_H  = 5.0;

NOTCH_R_MIN = 40.0;
NOTCH_A_S   = -45.0;
NOTCH_A_E   = -40.0;
NOTCH_Z_S   = 2.5;
NOTCH_Z_E   = BASE_H;

RIM_ID = 165.0;
RIM_OD = 170.0;
RIM_H  = 5.5;

RIM_CUT1_A_S = -5.0;
RIM_CUT1_A_E =  0.0;
RIM_CUT2_A_S = -45.0;
RIM_CUT2_A_E = -40.0;

TOTAL_H = BASE_H + RIM_H;   // 10.5

M3_DIAM     = 3.2;
INNER_PCD_R = 35.0;          // Phi 70
OUTER_PCD_R = 77.5;          // Phi 155

$fn = 192;

// ===== Helpers =====
module annulus(z0, h, r_in, r_out) {
    translate([0, 0, z0])
        difference() {
            cylinder(h = h, r = r_out);
            translate([0, 0, -1])
                cylinder(h = h + 2, r = r_in);
        }
}

// Pie wedge from origin sweeping a_start..a_end (deg), radius r,
// extruded h, starting at Z=z0.
module wedge(a_start, a_end, r, h, z0, n_seg = 24) {
    translate([0, 0, z0])
        linear_extrude(height = h)
            polygon(points = concat(
                [[0, 0]],
                [ for (i = [0 : n_seg])
                    [ r * cos(a_start + i * (a_end - a_start) / n_seg),
                      r * sin(a_start + i * (a_end - a_start) / n_seg) ] ]
            ));
}

// Through-hole at (x, y)
module through_hole(x, y) {
    translate([x, y, -1])
        cylinder(h = TOTAL_H + 2, r = M3_DIAM / 2);
}

// ===== Assembly =====
difference() {
    union() {
        // Base annulus with notch
        difference() {
            annulus(0, BASE_H, BASE_ID / 2, BASE_OD / 2);
            // Notch: wedge intersected with outer-band annulus
            intersection() {
                wedge(NOTCH_A_S, NOTCH_A_E, BASE_OD / 2 + 2,
                      NOTCH_Z_E - NOTCH_Z_S + 0.4, NOTCH_Z_S - 0.2);
                annulus(NOTCH_Z_S - 0.2, NOTCH_Z_E - NOTCH_Z_S + 0.4,
                        NOTCH_R_MIN, BASE_OD / 2 + 1);
            }
        }

        // Outer rim boss with two angular cutouts
        difference() {
            annulus(BASE_H, RIM_H, RIM_ID / 2, RIM_OD / 2);
            wedge(RIM_CUT1_A_S, RIM_CUT1_A_E, RIM_OD / 2 + 2,
                  RIM_H + 0.4, BASE_H - 0.2);
            wedge(RIM_CUT2_A_S, RIM_CUT2_A_E, RIM_OD / 2 + 2,
                  RIM_H + 0.4, BASE_H - 0.2);
        }
    }

    // 16 Phi3.2 through-holes (8 on PCD70, 8 on PCD155),
    // angles = 22.5 + k*45 for k=0..7
    for (k = [0 : 7]) {
        a = 22.5 + k * 45;
        // Inner PCD Phi70
        through_hole(INNER_PCD_R * cos(a), INNER_PCD_R * sin(a));
        // Outer PCD Phi155
        through_hole(OUTER_PCD_R * cos(a), OUTER_PCD_R * sin(a));
    }
}
