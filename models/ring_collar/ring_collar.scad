// POV 3D annular ring collar — parametric

od             = 80;     // 外径 / outer diameter
id             = 65;     // 内径 / inner diameter
height         = 13;     // 总高 / total height

notch_a_start  = 0;      // 槽口起始角 / notch start angle (deg, CCW from +X)
notch_a_end    = 30;     // 槽口结束角 / notch end angle
notch_h        = 6;      // 槽口高度（自底面向上） / notch height from bottom
notch_r        = od / 2 + 2;

module ring_collar() {
    difference() {
        // annular ring
        difference() {
            cylinder(h = height, d = od, $fn = 128);
            translate([0, 0, -1])
                cylinder(h = height + 2, d = id, $fn = 128);
        }
        // notch wedge (subtract from ring only)
        translate([0, 0, -0.05])
            linear_extrude(height = notch_h + 0.1)
                polygon(concat(
                    [[0, 0]],
                    [for (i = [0:28])
                        let (a = notch_a_start + i*(notch_a_end - notch_a_start)/28)
                        [notch_r*cos(a), notch_r*sin(a)]]
                ));
    }
}

ring_collar();
