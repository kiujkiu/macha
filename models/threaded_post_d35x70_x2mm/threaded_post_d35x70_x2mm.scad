// 螺纹柱 简单试打版 threaded_post_d35x70_x2mm  (2026-09-15; 原名 threaded_post_d50x70_x2mm)
// = threaded_post_d50x70 (100 kg 定稿 F1) 的简化变体, 用户要求先打出来试。⚠ 未做受力分析 / 仿真。
// 用户指定: 十字筋 (0/90°); 筒壁 / 筋 / 顶板厚统一 2; 螺纹凸起 (大径) Φ27.5 / 凹陷 (小径) Φ24.5 直接建模不留间隙 (牙高 1.5)。
// 替用户定: 顶端倒角 C1.75 (C1.5 时倒角顶端半径 = 小径半径, 边线重合易退化; 1.75 ⇒ 顶端 Φ24.0);
//          底边倒角 C0.2 (壁 2 时首层环宽 1.9 ≥ 4 线 1.68);
//          45° 过渡 6.4 (> 十字格内切圆半径 5.83 + 0.5, 腔顶无水平面, 免支撑; Φ50 时是 9.5);
//          过渡棱柱与 r = rc + wall/2 圆柱求交 (否则筋端过渡凸出外壁)。
// 2026-09-15 再追加 (用户要求): 下部圆柱直径 Φ50 → Φ35 (内腔 Φ31, 台阶面环宽 3.75)。
// 2026-09-15 再追加 (用户要求): 底部封死 (底板 2), 从外面看是完整圆柱; 内腔 Z 2–68 被十字筋隔成 4 个密闭格腔。
// 螺纹柱中空 (用户追加): 壁厚 3 从牙底量 ⇒ 内孔 Φ18.5 盲孔深 15, 孔底在台阶面。
// 其余同 F1: 下柱高 70, 螺纹柱高 15, P3 60° 对称梯形右旋单线。
// 与 build_stl.py 的参数必须一致 (本文件是复刻不是 import)。
// 螺纹做法: 横截面 r(θ) 用 linear_extrude 扭转拉伸 (单线螺纹横截面沿轴匀速旋转 = 精确螺旋)。

base_d  = 35;     // 下部圆柱直径 (F1 50; 2026-09-15 用户要求改成 35)
base_h  = 70;     // 下部圆柱高
thr_h   = 15;     // 螺纹柱高
thr_maj = 27.5;   // 大径 (牙顶) (F1 26.5)
thr_min = 24.5;   // 小径 (牙底)
pitch   = 3;      // 螺距
thr_clear = 0;    // 打印间隙 (直径) (F1 0.4; 本版直接按 27.5/24.5 建模)
bot_ch    = 0.2;  // 底边外圈 45° 倒角, 防首层象脚 (F1 0.3)
wall       = 2;     // 下柱筒壁厚 (F1 2.94)
plate_t    = 2;     // 下柱腔顶顶板厚 (F1 3.36)
bot_t      = 2;     // 底板厚: 底部封死, 从外面看是完整圆柱 (0 = 底口敞开)
rib_t      = 2;     // 十字加强筋厚 (F1 3.36 米字)
rib_angles = [0, 90];   // 十字筋 (F1 [0, 45, 90, 135]); 筋和过渡共用
stud_wall  = 3;     // 螺纹柱壁厚, 从牙底 (小径) 量到内孔 (用户要求中空 3 mm)
bore_d     = thr_min - 2 * stud_wall;   // 螺纹柱内孔直径 18.5
bore_depth = thr_h; // 盲孔深 15, 孔底在台阶面 Z=70
rib_l   = base_d - wall;   // 筋条总长 = 腔半径 + 外半径, 两端伸进壁厚中线
gusset  = 6.4;    // 筋两侧/筒壁与腔顶 45° 过渡直角边 (F1 6), 须 > 格内切圆半径 (十字/Φ35/壁 2/筋 2: 5.83) + 0.5 ⇒ 腔顶无水平面
zc      = base_h - plate_t;    // 腔顶 68
rc      = base_d / 2 - wall;   // 腔半径 15.5
r_gclip = rc + wall / 2;       // 45° 过渡裁剪圆柱半径 = 筒壁中线 16.5 (x2mm 新增)
e       = 0.5;    // 过渡三角形外扩进筋/壁/顶板, 免共面

flank_angle = 60;   // 牙型角
chamfer     = 1.75; // 顶端 45° 倒角, 0 = 不倒 (F1 1.5)
right_hand  = true;
n_sec       = 360;  // 横截面分段

r_maj = (thr_maj - thr_clear) / 2;   // 实际建模 13.75
r_min = (thr_min - thr_clear) / 2;   // 12.25
depth = r_maj - r_min;                      // 1.5
flank_run = depth * tan(flank_angle / 2);   // 0.866
crest = (pitch - 2 * flank_run) / 2;        // 0.634

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

module threaded_post_d35x70_x2mm() {
    difference() {
        union() {
            difference() {
                rotate_extrude($fn = 256)      // 带底边倒角的回转截面
                    polygon([[0, 0], [base_d / 2 - bot_ch, 0], [base_d / 2, bot_ch],
                             [base_d / 2, base_h], [0, base_h]]);
                // 下柱内腔 (底部封死留底板 bot_t, 顶留顶板 plate_t ⇒ 密闭空腔)
                translate([0, 0, bot_t > 0 ? bot_t : -1])
                    cylinder(h = base_h - plate_t - (bot_t > 0 ? bot_t : -1), d = base_d - 2 * wall, $fn = 256);
            }
            // 十字加强筋: 从底面通到腔顶, 两端伸进壁厚中线, 顶端伸进顶板一半
            for (a = rib_angles)
                rotate([0, 0, a])
                    translate([-rib_l / 2, -rib_t / 2, 0])
                        cube([rib_l, rib_t, base_h - plate_t / 2]);
            // 45° 过渡 (筋两侧 + 筒壁一圈), 整体与 r = r_gclip 圆柱求交:
            // 筋端 (筒壁中线处) 三角形顶宽 rib_t/2 + gusset + e, 半径超出外圆, 不裁会凸出外壁
            intersection() {
                union() {
                    // 筋两侧 (rotate([90,0,90]) 把 2D (y,z) 三角形沿 X 拉伸)
                    for (a = rib_angles, s = [1, -1])
                        rotate([0, 0, a]) scale([1, s, 1])
                            rotate([90, 0, 90]) translate([0, 0, -rib_l / 2])
                                linear_extrude(height = rib_l)
                                    polygon([[rib_t / 2 - e, zc - gusset - e], [rib_t / 2 + gusset + e, zc + e],
                                             [rib_t / 2 - e, zc + e]]);
                    // 筒壁一圈
                    rotate_extrude($fn = 256)
                        polygon([[rc - gusset - e, zc + e], [rc + e, zc - gusset - e], [rc + e, zc + e]]);
                }
                translate([0, 0, -1]) cylinder(h = base_h + 2, r = r_gclip, $fn = 256);
            }
            translate([0, 0, base_h]) thread_stud();
        }
        // 螺纹柱内孔 (bore_d = 0 时实心; 本版 Φ18.5 深 15 盲孔)
        if (bore_d > 0)
            translate([0, 0, base_h + thr_h - bore_depth]) cylinder(h = bore_depth + 1, d = bore_d, $fn = 128);
    }
}

threaded_post_d35x70_x2mm();
