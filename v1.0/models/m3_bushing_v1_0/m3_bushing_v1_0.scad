// m3_bushing_v1_0: SoC 转接板 Φ4 孔 -> M3 转接套 (与 build_stl.py 同参数)
sleeve_od = 4.0; bore_d = 3.2; flange_d = 8.0; flange_t = 0.5; sleeve_l = 1.6;
$fn = 96;
difference() {
    union() {
        cylinder(h = flange_t, d = flange_d);
        cylinder(h = flange_t + sleeve_l, d = sleeve_od);
    }
    translate([0, 0, -1]) cylinder(h = flange_t + sleeve_l + 2, d = bore_d);
}
