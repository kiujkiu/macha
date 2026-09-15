// 螺纹柱 threaded_post_d50x70  (2026-09-14)
// 下部圆柱 Φ50 × 70; 上部外螺纹柱高 15, 大径 Φ26.5 / 小径 Φ24.5 / 螺距 3。
// 2026-09-14 改: 上下两柱壁厚 5 (下柱 Φ50/Φ40 底部敞口 + 顶板 5; 螺纹柱内孔 Φ14.5 深 15 盲孔);
//               下腔加米字加强筋厚 5 (0/45/90/135°), 从底面通到腔顶。
// 2026-09-14 打印优化: 螺纹大径/小径各缩 0.4 打印间隙 (建模 Φ26.1/Φ24.1); 底边外圈倒角 C0.6;
//                     筋两侧/筒壁与腔顶 45° 过渡, 腔顶无水平面, 免支撑。
// 2026-09-15 单件承重 100 kg 受力分析定稿 (PETG, 必须 100% 实心): 壁 2.94 / 筋 3.36 / 顶板 3.36 (与壁解耦) /
//            45° 过渡 6 / 螺纹柱实心 / 底边 C0.3。使用时须拧到被支撑物压实台阶面。
// 用户未指定、按常规补: 60° 对称梯形牙, 右旋单线, 顶端 45° 倒角 C1.5。
// 与 build_stl.py 的参数必须一致 (本文件是复刻不是 import)。
// 螺纹做法: 横截面 r(θ) 用 linear_extrude 扭转拉伸 (单线螺纹横截面沿轴匀速旋转 = 精确螺旋)。

base_d  = 50;     // 下部圆柱直径
base_h  = 70;     // 下部圆柱高
thr_h   = 15;     // 螺纹柱高
thr_maj = 26.5;   // 大径 (牙顶)
thr_min = 24.5;   // 小径 (牙底)
pitch   = 3;      // 螺距
thr_clear = 0.4;  // 打印间隙 (直径): 配现成内螺纹, 大径/小径各缩 0.4; 仍偏紧就加大
bot_ch    = 0.3;  // 底边外圈 45° 倒角, 防首层象脚 (100 kg 定稿 0.6→0.3, 给薄壁首层留宽度)
wall       = 2.94;  // 下柱筒壁厚 (100 kg 受力分析定稿, 原 5)
plate_t    = 3.36;  // 下柱腔顶顶板厚 (与 wall 解耦, 原 5)
rib_t      = 3.36;  // 米字加强筋厚 (原 5)
bore_d     = 0;     // 螺纹柱内孔直径, 0 = 实心 (原 Φ14.5; 根部是全件最弱处, 定稿改实心)
bore_depth = 0;     // 内孔深, 从顶端向下量, ≤ thr_h
rib_l   = base_d - wall;   // 筋条总长 = 腔半径 + 外半径, 两端伸进壁厚中线
gusset  = 6;      // 筋两侧/筒壁与腔顶 45° 过渡直角边, 须 > 格内切圆半径 (定稿 4.89) + 0.5 ⇒ 腔顶无水平面, 免支撑
zc      = base_h - plate_t;    // 腔顶
rc      = base_d / 2 - wall;   // 腔半径
e       = 0.5;    // 过渡三角形外扩进筋/壁/顶板, 免共面

flank_angle = 60;   // 牙型角
chamfer     = 1.5;  // 顶端 45° 倒角, 0 = 不倒
right_hand  = true;
n_sec       = 360;  // 横截面分段

r_maj = (thr_maj - thr_clear) / 2;   // 实际建模 (已扣打印间隙)
r_min = (thr_min - thr_clear) / 2;
depth = r_maj - r_min;
flank_run = depth * tan(flank_angle / 2);   // 0.577
crest = (pitch - 2 * flank_run) / 2;        // 0.923

// 牙型: 距最近牙顶中心的轴向距离 d → 半径
function prof_r(d) =
    d <= crest / 2             ? r_maj :
    d <= crest / 2 + flank_run ? r_maj - (d - crest / 2) / flank_run * depth :
                                 r_min;
function wrap_d(u) = abs(u - pitch * round(u / pitch));

// z=0 截面: 角度 θ 处离牙顶中心的轴向偏移 = pitch·θ/360 (右旋)
thread_section = [for (i = [0 : n_sec - 1])
    let (th = 360 * i / n_sec, r = prof_r(wrap_d(pitch * th / 360)))
    [r * cos(th), r * sin(th)]];

module thread_stud() {
    intersection() {
        // OpenSCAD 正 twist = 俯视顺时针; 右旋螺纹截面随高度逆时针转 ⇒ 负 twist
        linear_extrude(height = thr_h, twist = (right_hand ? -1 : 1) * 360 * thr_h / pitch,
                       slices = round(thr_h / pitch * 120))
            polygon(thread_section);
        if (chamfer > 0)
            rotate_extrude($fn = 180)
                polygon([[0, -1], [r_maj + 0.5, -1],
                         [r_maj + 0.5, thr_h - (chamfer + 0.5)],
                         [r_maj - chamfer, thr_h], [0, thr_h]]);
        else
            cylinder(h = thr_h, r = r_maj + 0.5, $fn = 180);
    }
}

module threaded_post_d50x70() {
    difference() {
        union() {
            difference() {
                rotate_extrude($fn = 256)      // 带底边倒角的回转截面
                    polygon([[0, 0], [base_d / 2 - bot_ch, 0], [base_d / 2, bot_ch],
                             [base_d / 2, base_h], [0, base_h]]);
                // 下柱内腔 (底部敞口, 顶留顶板 plate_t)
                translate([0, 0, -1]) cylinder(h = base_h - plate_t + 1, d = base_d - 2 * wall, $fn = 256);
            }
            // 米字加强筋: 从底面通到腔顶, 两端伸进壁厚中线, 顶端伸进顶板一半
            for (a = [0, 45, 90, 135])
                rotate([0, 0, a])
                    translate([-rib_l / 2, -rib_t / 2, 0])
                        cube([rib_l, rib_t, base_h - plate_t / 2]);
            // 45° 过渡: 米字筋两侧 (rotate([90,0,90]) 把 2D (y,z) 三角形沿 X 拉伸)
            for (a = [0, 45, 90, 135], s = [1, -1])
                rotate([0, 0, a]) scale([1, s, 1])
                    rotate([90, 0, 90]) translate([0, 0, -rib_l / 2])
                        linear_extrude(height = rib_l)
                            polygon([[rib_t / 2 - e, zc - gusset - e], [rib_t / 2 + gusset + e, zc + e],
                                     [rib_t / 2 - e, zc + e]]);
            // 45° 过渡: 筒壁一圈
            rotate_extrude($fn = 256)
                polygon([[rc - gusset - e, zc + e], [rc + e, zc - gusset - e], [rc + e, zc + e]]);
            translate([0, 0, base_h]) thread_stud();
        }
        // 螺纹柱内孔 (bore_d = 0 时实心, 定稿即实心)
        if (bore_d > 0)
            translate([0, 0, base_h + thr_h - bore_depth]) cylinder(h = bore_depth + 1, d = bore_d, $fn = 128);
    }
}

threaded_post_d50x70();
