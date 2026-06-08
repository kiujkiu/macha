// L-angle bracket for POV 3D — parametric
// All dimensions in mm. Cross-section drawn in (u, v) plane, extruded along Z.

length    = 140;    // 总长 / bracket length
leg_a     = 15;     // 水平腿外形长 / leg A outer length (with M3 holes)
leg_b     = 6;      // 斜腿外形长   / leg B outer length (short stub)
thick_a   = 3;      // 水平腿壁厚   / leg A thickness
thick_b   = 3;      // 斜腿壁厚     / leg B thickness
angle_deg = 90;     // 两腿夹角     / inside angle at outer corner

// M3 通孔 / M3 clearance through-holes on leg A
hole_diam            = 3.2;
hole_y_from_free_end = 5;     // 孔 Y 位置（从 leg A 自由端起算）
// X positions kept at original 4-hole pattern (200 mm, X=6,66,134,194);
// right-side trimmed to 170 mm removes X=194, leaving 3 holes.
hole_x_positions     = [6, 66, 134];

// --- Derived ---
ct = cos(angle_deg);
st = sin(angle_deg);
u_inner = (thick_a + thick_b * ct) / st;
p3_y    = thick_b * st + u_inner * ct;
hole_y  = leg_a - hole_y_from_free_end;
hole_xs = hole_x_positions;

// --- Geometry ---
module bracket() {
    difference() {
        linear_extrude(height = length)
            polygon([
                [0,                              0                            ],  // P0 outer corner
                [leg_a,                          0                            ],  // P1 leg A outer end
                [leg_a,                          thick_a                      ],  // P2 leg A inner-start
                [p3_y,                           thick_a                      ],  // P3 inner corner
                [leg_b*ct + thick_b*st,          leg_b*st - thick_b*ct        ],  // P4 leg B inner end
                [leg_b*ct,                       leg_b*st                     ]   // P5 leg B outer end
            ]);
        for (hx = hole_xs)
            translate([hole_y, -1, hx])
                rotate([-90, 0, 0])
                    cylinder(h = thick_a + 2, d = hole_diam, $fn = 48);
    }
}

bracket();
