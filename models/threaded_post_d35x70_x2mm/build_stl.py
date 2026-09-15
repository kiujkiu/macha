"""
螺纹柱 简单试打版 threaded_post_d35x70_x2mm (2026-09-15, 用户要求: 先打出来试; 原名 threaded_post_d50x70_x2mm)

= 已提交的 threaded_post_d50x70 "100 kg 定稿 F1" 的简化变体:
  十字筋 / 厚度统一 2 mm / 螺纹 Φ27.5/Φ24.5 直接建模 (不留间隙)。
  ⚠ 本版未做受力分析 / 仿真, 承载能力未知, 只供试打。
  本脚本由 ../threaded_post_d50x70/build_stl.py 复制后改参数; 建模做法与校核逻辑同 F1 (F1 目录不动)。

与 F1 的差异 (用户指定):
  - 加强筋: 米字 (0/45/90/135°) → 十字 RIB_ANGLES = (0, 90)
  - 筒壁 WALL 2.94 / 筋 RIB_T 3.36 / 顶板 PLATE_T 3.36 → 统一 2.0
  - 螺纹: 名义 Φ26.5/Φ24.5 + 间隙 0.4 (建模 Φ26.1/Φ24.1) → THR_MAJ 27.5 / THR_MIN 24.5 / THR_CLEAR 0,
    直接按 Φ27.5/Φ24.5 建模 ⇒ 牙高 1.0 → 1.5, 60° 牙型下牙顶/牙底平台 0.923 → (3 − 2·1.5·tan30°)/2 ≈ 0.634

由参数派生 / 替用户定的取舍 (用户未指定):
  - 45° 过渡 GUSSET 6.0 → 9.5: 十字 + 壁 2 + 筋 2 时格内切圆半径 r_insc ≈ 8.941 (下面 polylabel 实算),
    取 ceil((r_insc + 0.5 + 0.001)·10)/10 = 9.5, 满足硬约束 GUSSET > r_insc + 0.5 (腔顶无水平面、免支撑), 断言保留
  - 顶端倒角 CHAMFER 1.5 → 1.75: 牙高 1.5 时 C1.5 倒角顶端半径 = 小径半径 12.25, 锥面顶边与芯柱棱线重合易出退化;
    改 1.75 ⇒ 倒角顶端 Φ24.0, 比小径低 0.5
  - 底边倒角 BOT_CH 0.3 → 0.2: 壁厚 2 时首层筒壁环宽 WALL − (BOT_CH − 0.1) = 1.9 ≥ 4 线 1.68
    (按首层底面 z=0 算再扣切片象脚补偿 0.1 为 2 − 0.2 − 0.1 = 1.7, 仍 ≥ 1.68)
  - 过渡棱柱裁剪 (新增几何): GUSSET 大了以后, 筋两侧的 45° 三角棱柱沿筋长 RIB_L、两端在筒壁中线处,
    三角形顶宽 RIB_T/2 + GUSSET + E, 在筋端点处半径可达 √(24² + 11²) ≈ 26.4 > R_BASE 25, 会从外壁凸出去
    ⇒ 全部 45° 过渡先与半径 R_CAV + WALL/2 (= 24, 筒壁中线) 的圆柱求交再并入; 腔内部分不变 (有断言核对),
    与筒壁仍重叠 WALL/2 融合。新增断言: 成品网格所有顶点到 Z 轴半径 ≤ R_BASE + 1e-6 (不超出 Φ50), bbox X/Y 在 ±25 内
  - 体积断言容差: 原计划因"大 GUSSET 时 offset 积分 vs revolve 多边形约 2e-4 系统误差"放宽到 1e-3,
    实测后**保持 F1 的 1e-4 不放宽**: 裁剪后实际相对差只有 2.8e-6; 不裁剪时是 5.3e-4 (多出 28.8 mm³ 正是凸出外壁的
    过渡棱柱), 即那 "2e-4 量级误差" 是几何真错, 放宽到 1e-3 会把凸出放过去
  - 2026-09-15 追加 (用户要求): 螺纹柱中空, 壁厚 3 (从牙底量) ⇒ 内孔 Φ18.5 盲孔深 15, 孔底在 Z=70 台阶面
  - 2026-09-15 再追加 (用户要求): 下部圆柱直径 Φ50 → Φ35 (内腔 Φ31, 台阶面环宽只剩 17.5−13.75 = 3.75);
    GUSSET 按规则 9.5 → 6.4 (十字格内切圆半径 8.941 → 5.834)。上面各条里 23/24/26.4/9.5/8.941 等数是 Φ50 时的值
  - 2026-09-15 再追加 (用户要求): 文件夹改名 threaded_post_d35x70_x2mm; 底部封死 (底板 BOT_T 2, 厚度同统一 2 mm),
    从外面看是完整圆柱。内腔 Z 2–68 被十字筋隔成 4 个密闭格腔 (manifold decompose 多出 4 个负体积块, 断言已按此改)。
    打印仍底面贴床: 底板是首层实心, 腔顶靠 45° 过渡闭合, 免支撑
  - 2026-09-15 再追加 (用户要求): 螺纹柱改回实心 (同步正式件的根部复核结论: 3 mm 中空不满足冲击目标), 螺纹间隙仍 0;
    螺纹间隙 0 已由用户试打确认可拧上 (配塑料/打印内螺纹)
  - 其余同 F1: 下柱高 70, P3 60° 对称梯形右旋单线, 分段数

坐标: 轴 = Z, 大圆柱底面 Z=0 (贴床), 螺纹朝上; 右旋 = 俯视逆时针转一圈上升一个螺距; 0° 筋沿 X。
建模: 牙型梯形沿螺旋线扫掠成"牙条" + 小径芯柱 → 与带倒角的回转包络求交 → 并上大圆柱
      → 减内腔 → 并十字筋 → 并 45° 过渡 (已裁到 R_CAV + WALL/2 以内) → (BORE_D > 0 时) 减螺纹柱内孔。
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d
from shapely.geometry import Polygon, box
from shapely.affinity import rotate as s_rotate
from shapely.ops import polylabel, unary_union

# ===== 参数 (2026-09-15 x2mm 简单试打版; 括号里是 F1 原值) =====
BASE_D   = 35.0     # 下部圆柱直径 (F1 50; 2026-09-15 用户要求改成 35)
BASE_H   = 70.0     # 下部圆柱高
THR_H    = 15.0     # 螺纹柱高
THR_MAJ  = 27.5     # 螺纹大径 (牙顶) (F1 26.5; 用户要求凸起 27.5)
THR_MIN  = 24.5     # 螺纹小径 (牙底) (同 F1; 用户要求凹陷 24.5)
PITCH    = 3.0      # 螺距
WALL     = 2.0      # 下柱筒壁厚 (F1 2.94; 用户要求统一 2 mm)
RIB_T    = 2.0      # 十字加强筋厚 (F1 3.36; 用户要求统一 2 mm)
THR_CLEAR = 0.0     # 打印间隙 (直径) (F1 0.4; 用户要求按 27.5/24.5 直接建模, 不留间隙)
BOT_CH    = 0.2     # 底边外圈 45° 倒角, 防首层象脚 (F1 0.3; 壁 2 时首层环宽 1.9 ≥ 4 线 1.68), 0 = 不倒
GUSSET    = 6.4     # 筋/筒壁与腔顶交角 45° 过渡的直角边 (F1 6.0); = ceil((r_insc + 0.5 + 0.001)·10)/10, Φ35 时 r_insc ≈ 5.834 (Φ50 时 8.941 → 9.5)

# ===== 补充参数 (用户未指定) =====
FLANK_ANGLE = 60.0  # 牙型角 (两侧牙面夹角)
RIGHT_HAND  = True
CHAMFER     = 1.75  # 顶端 45° 倒角 (径向=轴向) (F1 1.5; 牙高 1.5 时 C1.5 顶端半径 = 小径半径易退化 ⇒ 1.75, 顶端 Φ24.0), 0 = 不倒
PLATE_T     = 2.0   # 下柱腔顶顶板厚 (F1 3.36; 用户要求统一 2 mm)
BOT_T       = 2.0   # 底板厚: 底部封死, 从外面看是完整圆柱 (用户要求; 0 = 底口敞开)
STUD_WALL   = THR_MIN / 2   # 螺纹柱实心 (2026-09-15 用户改回, 同步正式件根部复核结论; 中空时为 3.0)
BORE_D      = THR_MIN - 2 * STUD_WALL   # = 0, 实心 (中空时 Φ18.5)
BORE_DEPTH  = 0.0                       # 实心 (中空时 15)
RIB_ANGLES  = (0, 90)   # 十字筋 (F1 (0, 45, 90, 135); 用户要求)

SEG_TURN = 180      # 每圈分段 (螺旋扫掠 + 芯柱 + 包络共用, 让顶点角度对齐)
BASE_SEG = 256      # 大圆柱 + 内腔
BORE_SEG = 128      # 螺纹柱内孔

R_BASE = BASE_D / 2
R_MAJ, R_MIN = (THR_MAJ - THR_CLEAR) / 2, (THR_MIN - THR_CLEAR) / 2   # 实际建模 13.75 / 12.25 (间隙 0)
DEPTH  = R_MAJ - R_MIN                                  # 牙高 1.5
FLANK_RUN = DEPTH * math.tan(math.radians(FLANK_ANGLE / 2))   # 单侧牙面轴向投影 0.866
CREST  = (PITCH - 2 * FLANK_RUN) / 2                    # 牙顶平台 0.634
ROOT   = PITCH - 2 * FLANK_RUN - CREST                  # 牙底平台 0.634
Z_TOP  = BASE_H + THR_H                                 # 85
R_CH_TOP = R_MAJ - CHAMFER                              # 倒角顶端半径 12.0
R_CAV  = R_BASE - WALL                                  # 下腔半径 15.5
HAS_BORE = BORE_D > 0 and BORE_DEPTH > 0
R_BORE = BORE_D / 2 if HAS_BORE else 0.0                # 螺纹柱内孔半径 (0 = 实心)
Z_BORE_BOT = Z_TOP - BORE_DEPTH if HAS_BORE else Z_TOP  # 孔底高度
Z_CEIL = BASE_H - PLATE_T                               # 腔顶 68
RIB_L  = R_CAV + R_BASE                                 # 筋条总长: 两端各伸进壁厚中线
RIB_TOP = Z_CEIL + PLATE_T / 2                          # 筋顶伸进顶板一半, 免共面
R_GCLIP = R_CAV + WALL / 2                              # 45° 过渡裁剪圆柱半径 = 筒壁中线 16.5 (x2mm 新增)

assert THR_MIN < THR_MAJ < BASE_D
assert CREST > 0 and ROOT > 0, "牙型角/牙高/螺距组合不成立"
assert 0 <= CHAMFER < THR_H
assert CHAMFER == 0 or abs(R_CH_TOP - R_MIN) > 0.1, "倒角顶端半径与小径重合, 锥面顶边会压在芯柱棱线上 (x2mm 新增)"
assert R_BORE >= 0 and R_CAV > R_MAJ, "壁厚太大"          # 实心螺纹柱 R_BORE = 0 合法
assert 0 < PLATE_T < BASE_H and Z_CEIL - GUSSET > 5, "顶板/过渡太厚"
assert 0 <= BOT_T < Z_CEIL - GUSSET - 5, "底板太厚, 与腔顶过渡相撞"
assert not HAS_BORE or BORE_DEPTH <= THR_H, "内孔不能穿进顶板 (孔底须 ≥ 台阶面)"
assert R_BORE < R_CH_TOP - 1, "内孔吃到顶端倒角"
assert RIB_TOP < BASE_H, "筋顶穿进螺纹柱内孔"
assert 0 <= BOT_CH < WALL
assert math.hypot(RIB_L / 2, RIB_T / 2) < (R_BASE - BOT_CH) * math.cos(math.pi / BASE_SEG), "筋条角点穿出外壁"
assert R_CAV < R_GCLIP <= R_BASE, "过渡裁剪圆柱须在筒壁里 (既与筒壁重叠融合, 又不超出外圆)"

# ===== 螺旋牙条 (梯形截面沿螺旋扫掠) =====
R_IN = R_MIN - 0.2                       # 牙根埋进芯柱 0.2, 保证布尔融合
HC   = CREST / 2                         # 牙顶半宽
HB   = CREST / 2 + FLANK_RUN * (R_MAJ - R_IN) / DEPTH   # 牙根 (延长到 R_IN) 半宽
assert HB < PITCH / 2, "相邻两圈牙条会相交"
# 芯柱是 SEG_TURN 边内接多边形, 牙根必须埋在它的内切圆里
assert R_IN < R_MIN * math.cos(math.pi / SEG_TURN)
assert R_IN > R_BORE + 1, "牙条内缘穿进内孔"

PROFILE = [(R_IN, -HB), (R_MAJ, -HC), (R_MAJ, HC), (R_IN, HB)]   # (r, dz), (r,z) 平面内逆时针

Z_START = BASE_H - 2 * PITCH             # 牙条起点埋在大圆柱里 (θ=0 处牙顶中心 = 64, 67, 70, ...)
TURNS   = math.ceil((Z_TOP + HB + PITCH - Z_START) / PITCH)
assert Z_START + HB < BASE_H - 0.5 and Z_START + TURNS * PITCH - HB > Z_TOP, "牙条端面没被裁掉"

def helix_thread():
    S = TURNS * SEG_TURN
    hand = 1.0 if RIGHT_HAND else -1.0
    j = np.arange(S + 1)
    th = hand * 2 * math.pi * j / SEG_TURN
    zc = Z_START + PITCH * j / SEG_TURN
    verts = np.empty(((S + 1) * 4, 3))
    for k, (r, dz) in enumerate(PROFILE):
        verts[k::4, 0] = r * np.cos(th)
        verts[k::4, 1] = r * np.sin(th)
        verts[k::4, 2] = zc + dz
    tris = []
    for jj in range(S):
        for k in range(4):
            k2 = (k + 1) % 4
            a, b, c, d = jj*4 + k, (jj+1)*4 + k, (jj+1)*4 + k2, jj*4 + k2
            tris += [(a, b, c), (a, c, d)]
    tris += [(0, 1, 2), (0, 2, 3)]                                   # 起点端面
    e = S * 4
    tris += [(e, e + 2, e + 1), (e, e + 3, e + 2)]                   # 终点端面
    tris = np.array(tris, dtype=np.uint32)
    if not RIGHT_HAND:                                               # 镜像后三角形绕向反了
        tris = tris[:, [0, 2, 1]]
    mesh = m3d.Mesh(vert_properties=verts.astype(np.float32), tri_verts=tris)
    m = m3d.Manifold(mesh)
    assert m.status() == m3d.Error.NoError, f"牙条网格非流形: {m.status()}"
    assert m.volume() > 0, "牙条网格绕向反了"
    return m

def envelope(z0, chamfer):
    """回转包络: 外半径放宽到牙顶外, 顶端按 45° 倒角锥面裁 (chamfer=0 为平顶)。"""
    R_OUT = R_MAJ + 0.5
    if chamfer > 0:
        pts = [(0, z0), (R_OUT, z0),
               (R_OUT, Z_TOP - (R_OUT - R_CH_TOP)),        # 45° 锥面延长到 R_OUT
               (R_CH_TOP, Z_TOP), (0, Z_TOP)]
    else:
        pts = [(0, z0), (R_OUT, z0), (R_OUT, Z_TOP), (0, Z_TOP)]
    return m3d.CrossSection([pts]).revolve(SEG_TURN)

def intersect(a, b):
    return m3d.Manifold.batch_boolean([a, b], m3d.OpType.Intersect)

def poly_area(r, seg):
    """Manifold.cylinder 是内接正多边形, 截面积按多边形算。"""
    return seg / 2 * math.sin(2 * math.pi / seg) * r * r

thread = helix_thread()
core   = m3d.Manifold.cylinder(Z_TOP + 1 - (BASE_H - 1), R_MIN, R_MIN, SEG_TURN, False) \
                   .translate((0, 0, BASE_H - 1))
raw_stud = core + thread

stud = intersect(raw_stud, envelope(BASE_H - 0.5, CHAMFER))
if BOT_CH > 0:                          # 回转截面带底边 45° 倒角
    base = m3d.CrossSection([[(0, 0), (R_BASE - BOT_CH, 0), (R_BASE, BOT_CH),
                              (R_BASE, BASE_H), (0, BASE_H)]]).revolve(BASE_SEG)
else:
    base = m3d.Manifold.cylinder(BASE_H, R_BASE, R_BASE, BASE_SEG, False)
solid = base + stud

if BOT_T > 0:                           # 底部封死: 内腔从底板顶面开始, 成密闭空腔
    cavity = m3d.Manifold.cylinder(Z_CEIL - BOT_T, R_CAV, R_CAV, BASE_SEG, False).translate((0, 0, BOT_T))
else:
    cavity = m3d.Manifold.cylinder(Z_CEIL + 1, R_CAV, R_CAV, BASE_SEG, False).translate((0, 0, -1))
bar = m3d.Manifold.cube((RIB_L, RIB_T, RIB_TOP), False).translate((-RIB_L / 2, -RIB_T / 2, 0))
ribs = bar.rotate((0, 0, RIB_ANGLES[0]))
for a in RIB_ANGLES[1:]:
    ribs = ribs + bar.rotate((0, 0, a))
bore = (m3d.Manifold.cylinder(BORE_DEPTH + 1, R_BORE, R_BORE, BORE_SEG, False).translate((0, 0, Z_BORE_BOT))
        if HAS_BORE else None)                          # 顶端开口 (向上多伸 1 免共面); 实心不开孔

# 45° 过渡: 直角顶点在 (筋面/内壁, Z_CEIL), 斜边从 Z_CEIL−GUSSET 升到顶板;
# 三角形各边外扩 E 伸进筋/壁/顶板, 免共面
def _ccw(pts):
    s = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))
    return pts if s > 0 else pts[::-1]
E = 0.5
assert R_CAV - GUSSET - E > 0, "筒壁过渡三角形越过轴线"
_tri_rib = _ccw([(RIB_T / 2 - E, Z_CEIL - GUSSET - E), (RIB_T / 2 + GUSSET + E, Z_CEIL + E),
                 (RIB_T / 2 - E, Z_CEIL + E)])                          # (y, z), 筋 +y 侧
g_side = (m3d.CrossSection([_tri_rib]).extrude(RIB_L)
          .rotate((0, 0, 90)).rotate((0, 90, 0))                      # (u,v,w) → (X=w, Y=u, Z=v)
          .translate((-RIB_L / 2, 0, 0)))
g_rib = g_side + g_side.rotate((0, 0, 180))                           # 两侧
gussets = g_rib.rotate((0, 0, RIB_ANGLES[0]))
for a in RIB_ANGLES[1:]:
    gussets = gussets + g_rib.rotate((0, 0, a))
_tri_wall = _ccw([(R_CAV - GUSSET - E, Z_CEIL + E), (R_CAV + E, Z_CEIL - GUSSET - E), (R_CAV + E, Z_CEIL + E)])
gussets = gussets + m3d.CrossSection([_tri_wall]).revolve(BASE_SEG)    # 筒壁一圈
# x2mm 新增: 筋侧棱柱两端 (筒壁中线处) 顶宽 RIB_T/2+GUSSET+E, 端点半径会超 R_BASE (Φ35 版 √(16.5²+7.9²) ≈ 18.3 > 17.5),
# 会从外壁凸出 ⇒ 裁到半径 R_GCLIP = R_CAV + WALL/2 的圆柱以内 (腔内 r ≤ R_CAV 部分不受影响, 下面有断言)
gussets_raw = gussets
_gclip = m3d.Manifold.cylinder(BASE_H + 2, R_GCLIP, R_GCLIP, BASE_SEG, False).translate((0, 0, -1))
gussets = intersect(gussets_raw, _gclip)

part = (solid - cavity) + ribs + gussets
if HAS_BORE:
    part = part - bore

# ===== 校核 =====
assert part.status() == m3d.Error.NoError, f"成品非流形: {part.status()}"
_comps = part.decompose()                 # 封底后每格是一个密闭空腔: manifold 每格拆出 1 个负体积块
_pos = [c for c in _comps if c.volume() > 0]
_neg = [c for c in _comps if c.volume() < 0]
assert len(_pos) == 1, f"件不是一整块 (正体积块 {len(_pos)})"
assert len(_neg) == (2 * len(RIB_ANGLES) if BOT_T > 0 else 0), \
    f"密闭空腔个数不对: {len(_neg)} (筋从底板通到顶板且两端并入筒壁, 每格各自密闭, 应为 {2 * len(RIB_ANGLES)})"

# 0) x2mm 新增: 外轮廓不超出 Φ50 (double 精度网格), 且过渡裁剪没有动到腔内部分
_v64 = np.asarray(part.to_mesh64().vert_properties)[:, :3]
r_out_max = float(np.hypot(_v64[:, 0], _v64[:, 1]).max())
assert r_out_max <= R_BASE + 1e-6, f"外轮廓超出 Φ{BASE_D:g}: 顶点最大半径 {r_out_max:.6f}"
assert _v64[:, 0].min() >= -R_BASE - 1e-6 and _v64[:, 0].max() <= R_BASE + 1e-6, "bbox X 超出 ±R_BASE"
assert _v64[:, 1].min() >= -R_BASE - 1e-6 and _v64[:, 1].max() <= R_BASE + 1e-6, "bbox Y 超出 ±R_BASE"
_vg = np.asarray(gussets_raw.to_mesh64().vert_properties)[:, :2]
g_raw_rmax = float(np.hypot(_vg[:, 0], _vg[:, 1]).max())                 # 裁剪前过渡棱柱最大半径 (仅供打印)
_cav_full = m3d.Manifold.cylinder(BASE_H + 2, R_CAV, R_CAV, BASE_SEG, False).translate((0, 0, -1))
_gv_raw, _gv_clip = intersect(gussets_raw, _cav_full).volume(), intersect(gussets, _cav_full).volume()
assert abs(_gv_raw - _gv_clip) < 1e-6 * _gv_raw, f"过渡裁剪动到了腔内部分 {_gv_raw} vs {_gv_clip}"

def radii(cs):
    return [np.hypot(p[:, 0], p[:, 1]) for p in cs.to_polygons()]

# 十字筋落在内腔 (多边形, 顶点取自 manifold 自己的圆) 里的面积
_cav_poly = Polygon(m3d.CrossSection.circle(R_CAV, BASE_SEG).to_polygons()[0])
_strip = box(-RIB_L / 2, -RIB_T / 2, RIB_L / 2, RIB_T / 2)
_ribs_poly = unary_union([s_rotate(_strip, a, origin=(0, 0)) for a in RIB_ANGLES])
rib_area = _ribs_poly.intersection(_cav_poly).area
# 腔被筋分成 2·len(RIB_ANGLES) 格 (十字 4 格); 格内切圆半径 = 45° 过渡要盖满腔顶所需的最小直角边
_cells = _cav_poly.difference(_ribs_poly)
assert len(_cells.geoms) == 2 * len(RIB_ANGLES)
r_insc = max(c.exterior.distance(polylabel(c, 1e-4)) for c in _cells.geoms)
assert GUSSET > r_insc + 0.5, f"45° 过渡盖不满腔顶: GUSSET {GUSSET} vs 内切圆半径 {r_insc:.3f}"
GUSSET_RULE = math.ceil((r_insc + 0.5 + 0.001) * 10) / 10                # 取值规则, 仅供打印对照

# 1) 牙型截面积理论值: 固定 z 的横截面 r(θ) 恰好扫过一整个螺距的牙型,
#    面积 = π/P · ∫ R(u)² du (牙顶/牙底平台 + 两侧线性牙面), 再扣内孔多边形
flank_r2 = (R_MAJ**2 + R_MAJ * R_MIN + R_MIN**2) / 3
area_theory = math.pi / PITCH * (CREST * R_MAJ**2 + ROOT * R_MIN**2 + 2 * FLANK_RUN * flank_r2)
z_mid = BASE_H + (THR_H - CHAMFER) / 2
cs_mid = part.slice(z_mid)
a_mid = cs_mid.area()
bore_in_mid = HAS_BORE and z_mid > Z_BORE_BOT               # 孔底可能高于 z_mid, 或实心
a_mid_expect = area_theory - (poly_area(R_BORE, BORE_SEG) if bore_in_mid else 0.0)
assert abs(a_mid - a_mid_expect) / a_mid_expect < 1e-3, f"螺纹段截面积不对: {a_mid} vs {a_mid_expect}"

_r = radii(cs_mid)
rad_out = np.concatenate([r for r in _r if r.max() > R_BORE + 1])
assert abs(rad_out.max() - R_MAJ) < 1e-3, f"大径不对 {rad_out.max()*2}"
assert abs(rad_out.min() - R_MIN) < 0.05, f"小径不对 {rad_out.min()*2}"   # 牙底圆弧上的顶点在芯柱多边形上
if bore_in_mid:
    rad_in = np.concatenate([r for r in _r if r.max() <= R_BORE + 1])
    assert abs(rad_in.max() - R_BORE) < 1e-3, f"内孔不对 {rad_in.max()*2}"
    wall_thread = rad_out.min() - rad_in.max()
else:
    assert len(_r) == 1, "实心螺纹柱截面应只有外轮廓 (不应有孔)"
    wall_thread = rad_out.min()                                # 实心: 牙底到轴心
assert abs(wall_thread - (R_MIN - (R_BORE if bore_in_mid else 0.0))) < 0.05, f"螺纹柱牙底处壁厚不对 {wall_thread}"
if not HAS_BORE:
    assert len(part.slice(Z_TOP - 0.3).to_polygons()) == 1, "实心螺纹柱顶端不应有孔"

# 2) 下柱分层截面: 筋区 (筒壁环 + 十字筋, 4 个扇形空格) / 顶板 (实心) / 内孔底 (Z=70 以下无孔)
cs_rib = part.slice(Z_CEIL / 2)
a_rib  = cs_rib.area()
a_rib_expect = poly_area(R_BASE, BASE_SEG) - poly_area(R_CAV, BASE_SEG) + rib_area
assert abs(a_rib - a_rib_expect) < 0.05, f"筋区截面积不对 {a_rib} vs {a_rib_expect}"
assert len(cs_rib.to_polygons()) == 1 + 2 * len(RIB_ANGLES), \
    f"筋区应是 1 外轮廓 + {2 * len(RIB_ANGLES)} 个扇形空格"
a_plate = part.slice(Z_CEIL + PLATE_T * 0.75).area()
assert abs(a_plate - poly_area(R_BASE, BASE_SEG)) < 1e-2, f"顶板应实心 {a_plate}"
assert len(part.slice(BASE_H - 0.1).to_polygons()) == 1, "内孔穿进了顶板"
# 底边倒角: 首层外轮廓缩到 R_BASE−BOT_CH, 倒角以上恢复全截面
if BOT_CH > 0:
    _z0 = 1e-3
    a_l0 = part.slice(_z0).area()
    a_l0_expect = poly_area(R_BASE - BOT_CH + _z0, BASE_SEG) - (0.0 if BOT_T > 0 else poly_area(R_CAV, BASE_SEG) - rib_area)
    assert abs(a_l0 - a_l0_expect) < 0.05, f"首层截面积不对 {a_l0} vs {a_l0_expect}"
    _a_above = poly_area(R_BASE, BASE_SEG) if BOT_T > BOT_CH + 0.01 else a_rib_expect
    assert abs(part.slice(BOT_CH + 0.01).area() - _a_above) < 0.05, "倒角以上应恢复全截面"
if BOT_T > 0:                           # 底板实心 / 底板以上才是筋区
    assert len(part.slice(BOT_T - 0.1).to_polygons()) == 1, "底板应为实心整圆"
    assert len(part.slice(BOT_T + 0.3).to_polygons()) == 1 + 2 * len(RIB_ANGLES), "底板以上应是外轮廓 + 各格空腔"

# 2c) 45° 过渡段: 距过渡起点 t 处, 腔截面 = 各格向内偏移 t (manifold 自己的截面做基准);
#     t 超过内切圆半径后格子全闭合 ⇒ 腔顶以下已是整圆, 没有水平天花板
#     (补测到接近闭合处; t 必须 < GUSSET, 否则切面高过 Z=BASE_H 会切到螺纹柱)
_disk_cs  = m3d.CrossSection.circle(R_CAV, BASE_SEG)
_ribs_cs  = m3d.CrossSection.square((RIB_L, RIB_T), True).rotate(RIB_ANGLES[0])
for a in RIB_ANGLES[1:]:
    _ribs_cs = _ribs_cs + m3d.CrossSection.square((RIB_L, RIB_T), True).rotate(a)
cells_cs = _disk_cs - _ribs_cs
def cells_area(t):
    return cells_cs.offset(-t, m3d.JoinType.Miter).area() if t > 0 else cells_cs.area()
for t in (1.0, 2.5, 3.5, 5.0, min(r_insc + 0.3, GUSSET - 0.1)):
    a_g = part.slice(Z_CEIL - GUSSET + t).area()
    a_g_expect = poly_area(R_BASE, BASE_SEG) - cells_area(t)
    assert abs(a_g - a_g_expect) < 0.2, f"过渡段 t={t} 截面积不对 {a_g} vs {a_g_expect}"
z_closed = Z_CEIL - GUSSET + r_insc + 0.05
assert len(part.slice(z_closed).to_polygons()) == 1, "腔顶还剩没被 45° 过渡盖住的水平面"

# 3) 体积 = 实心 − (内腔 − 筋) × 过渡以下腔深 − ∫ 过渡段格截面 dt − 内孔 × 螺纹柱高
v_solid = solid.volume()
_ts = (np.arange(500) + 0.5) / 500 * GUSSET
v_gus_cav = float(np.mean([cells_area(t) for t in _ts])) * GUSSET
v_expect = (v_solid - (poly_area(R_CAV, BASE_SEG) - rib_area) * (Z_CEIL - GUSSET - BOT_T) - v_gus_cav
            - (poly_area(R_BORE, BORE_SEG) * BORE_DEPTH if HAS_BORE else 0.0))
v_gusset_added = (poly_area(R_CAV, BASE_SEG) - rib_area) * GUSSET - v_gus_cav
vol = part.volume()
# x2mm: 容差保持 F1 的 1e-4, 不放宽到 1e-3。实测 (2026-09-15): 过渡已裁剪 → 相对差 2.8e-6;
# 过渡不裁剪 → 5.3e-4 (+28.8 mm³, 就是凸出 Φ50 外壁的棱柱体积)。所以之前以为的"offset 积分 vs revolve 多边形
# 约 2e-4 系统误差"其实是几何真错; 1e-3 会把它放过去, 1e-4 能抓到 (外轮廓半径断言也能抓到)
assert abs(vol - v_expect) / v_expect < 1e-4, f"体积不对 {vol} vs {v_expect}"

# 4) 螺纹段体积 (实心、不倒角) = 截面积 × 螺纹高, 验证扫掠几何
stud_plain = intersect(raw_stud, envelope(BASE_H, 0.0))
v_plain_theory = area_theory * THR_H

# 5) 旋向 + 相位: θ=0 牙顶中心在 z=Z_START+kP ⇒ 同一 z 上, 右旋时 +X 处是牙顶;
#    再往上 P/4, 牙顶转到 +Y (右旋) / −Y (左旋)
def radius_along(cs, ang_deg):
    ray = m3d.CrossSection.square((R_MAJ + 2, 0.02)).translate((0, -0.01)).rotate(ang_deg)
    hit = cs - (cs - ray)
    x0, y0, x1, y1 = hit.bounds()
    return max(math.hypot(x0, y0), math.hypot(x1, y1), math.hypot(x1, y0), math.hypot(x0, y1))
z_crest = Z_START + PITCH * math.ceil((BASE_H + 2 - Z_START) / PITCH)     # 73
assert abs(radius_along(part.slice(z_crest), 0) - R_MAJ) < 0.02
assert abs(radius_along(part.slice(z_crest + PITCH / 2), 0) - R_MIN) < 0.05
ccw_ang = 90 if RIGHT_HAND else -90
assert abs(radius_along(part.slice(z_crest + PITCH / 4), ccw_ang) - R_MAJ) < 0.02, "旋向不对"
assert radius_along(part.slice(z_crest + PITCH / 4), -ccw_ang) < R_MAJ - 0.5, "旋向不对"

# 6) 顶端倒角: 顶面最大半径 = R_CH_TOP
if CHAMFER > 0:
    rad_top = np.concatenate(radii(part.slice(Z_TOP - 1e-3)))
    assert abs(rad_top.max() - R_CH_TOP) < 0.01, f"倒角顶端半径不对 {rad_top.max()}"

# ===== 导出 STL =====
def float32_clean_mesh(m):
    """x2mm 新增: manifold 输出里有大量"两顶点只差 ~1e-10"的零面积碎三角 (牙侧/倒角交线处; F1 已提交的 STL 同样有 ~2300 个),
    写成 float32 STL 后两顶点重合 ⇒ 退化面, 读回时非流形、切片软件会报自动修复。
    这里按 float32 坐标合并顶点、丢掉含重合顶点的三角形, 并断言剩下的仍是单体流形、体积不变。
    返回 (float32 顶点, 三角形, 丢掉的退化三角形数); 试打件脚本经 exec 复用本函数。"""
    g = m.to_mesh()
    v32 = np.asarray(g.vert_properties)[:, :3].astype(np.float32)
    uniq, inv = np.unique(v32, axis=0, return_inverse=True)
    t = inv.reshape(-1)[np.asarray(g.tri_verts)]
    ok = (t[:, 0] != t[:, 1]) & (t[:, 1] != t[:, 2]) & (t[:, 0] != t[:, 2])
    t = t[ok].astype(np.uint32)
    mm = m3d.Manifold(m3d.Mesh(vert_properties=uniq, tri_verts=t))
    assert mm.status() == m3d.Error.NoError, f"float32 清理后非流形: {mm.status()}"
    assert sum(1 for c in mm.decompose() if c.volume() > 0) == 1, "float32 清理后不是一整块"
    assert abs(mm.volume() - m.volume()) < 1e-6 * m.volume(), f"float32 清理后体积变了 {mm.volume()} vs {m.volume()}"
    return uniq, t, int((~ok).sum())

verts, tris, n_degen = float32_clean_mesh(part)

out = Path(__file__).with_name("threaded_post_d35x70_x2mm.stl")
_hdr = (f"threaded_post_x2mm D{BASE_D:g}x{BASE_H:g} thr{THR_MAJ:g}/{THR_MIN:g}xP{PITCH:g}x{THR_H:g} "
        f"c{THR_CLEAR:g} w{WALL:g} r{RIB_T:g} p{PLATE_T:g} g{GUSSET:g} b{BORE_D:g}").encode("ascii")
assert len(_hdr) <= 80, f"STL 头 {len(_hdr)} 字节 > 80, 会被截断"
with out.open("wb") as f:
    f.write(_hdr.ljust(80, b" ")[:80])   # STL 头必须 <=80 字节并截断
    f.write(struct.pack("<I", len(tris)))
    v0 = verts[tris[:, 0]]; v1 = verts[tris[:, 1]]; v2 = verts[tris[:, 2]]
    n = np.cross(v1 - v0, v2 - v0)
    L = np.linalg.norm(n, axis=1, keepdims=True)
    n = np.where(L > 0, n / np.where(L > 0, L, 1), 0)
    rec = np.zeros(len(tris), dtype=[("n", "<f4", 3), ("v0", "<f4", 3), ("v1", "<f4", 3),
                                     ("v2", "<f4", 3), ("attr", "<u2")])
    rec["n"], rec["v0"], rec["v1"], rec["v2"] = n, v0, v1, v2
    f.write(rec.tobytes())

expected = 84 + len(tris) * 50
assert out.stat().st_size == expected, \
    f"STL 大小不对: {out.stat().st_size} != {expected} (STL 头溢出?)"
# STL 里是 float32: 25 附近 float32 最小间隔 ≈ 1.9e-6, 容差放到 1e-5 (double 网格已按 1e-6 断言过)
_vf = verts.astype(float)
r_stl_max = float(np.hypot(_vf[:, 0], _vf[:, 1]).max())
assert r_stl_max <= R_BASE + 1e-5, f"STL 外轮廓超出 Φ{BASE_D:g}: {r_stl_max:.6f}"

# 7) 免支撑: 朝下的面按悬垂角 (0=竖直墙, 90=水平天花板) 统计; 下柱 (贴床面以上、台阶面以下) 必须 ≤45°
_t  = verts[tris].astype(float)
_cr = np.cross(_t[:, 1] - _t[:, 0], _t[:, 2] - _t[:, 0]); _ar = np.linalg.norm(_cr, axis=1) / 2
_nz = _cr[:, 2] / np.maximum(2 * _ar, 1e-12); _zc = _t[:, :, 2].mean(axis=1)
_ov = np.degrees(np.arcsin(np.clip(-_nz, 0, 1)))
_down = (_nz < -1e-3) & (_ar > 1e-4)
_body = _down & (_zc > 1e-3) & (_zc < BASE_H - 1e-3)
_thr  = _down & (_zc >= BASE_H - 1e-3)
ov_body_max = _ov[_body].max()
assert ov_body_max < 45.5, f"下柱仍有 >45° 悬垂面: {ov_body_max:.2f}° @ Z {_zc[_body][_ov[_body].argmax()]:.2f}"

print(f"wrote {out}  ({len(tris)} triangles, {len(verts)} vertices; float32 清理丢掉退化碎三角 {n_degen})")
print(f"  STL 头 ({len(_hdr)} 字节): {_hdr.decode('ascii')}")
print(f"  bbox X: {verts[:,0].min():8.3f} .. {verts[:,0].max():8.3f}")
print(f"  bbox Y: {verts[:,1].min():8.3f} .. {verts[:,1].max():8.3f}")
print(f"  bbox Z: {verts[:,2].min():8.3f} .. {verts[:,2].max():8.3f}")
print(f"  外轮廓顶点最大半径: double {r_out_max:.6f} / STL float32 {r_stl_max:.6f} (≤ {R_BASE:g}); "
      f"过渡棱柱裁剪前最大半径 {g_raw_rmax:.3f} → 裁到 {R_GCLIP:g}")
print(f"  牙型: {FLANK_ANGLE:g}° 梯形, 牙高 {DEPTH:.3f}, 牙面轴向 {FLANK_RUN:.4f}, "
      f"牙顶平台 {CREST:.4f}, 牙底平台 {ROOT:.4f}, {'右' if RIGHT_HAND else '左'}旋, 圈数(扫掠) {TURNS}")
print(f"  打印间隙 {THR_CLEAR:g}: 建模大径 Φ{2*R_MAJ:.2f} / 小径 Φ{2*R_MIN:.2f} (名义 Φ{THR_MAJ:g}/Φ{THR_MIN:g}), "
      f"顶端倒到 Φ{2*R_CH_TOP:.2f};  底边倒角 C{BOT_CH:g}"
      + (f", 首层截面 {a_l0:.2f} (理论 {a_l0_expect:.2f})" if BOT_CH > 0 else ""))
print(f"  壁厚 {WALL:g}: 下柱 Φ{BASE_D:g}/Φ{2*R_CAV:g} 底板 {BOT_T:g} 密闭腔 Z {BOT_T:g}–{Z_CEIL:g} 顶板 {PLATE_T:g}; "
      + (f"螺纹柱内孔 Φ{2*R_BORE:g} 深 {BORE_DEPTH:g} (孔底 Z={Z_BORE_BOT:g})" if HAS_BORE else "螺纹柱实心 (无内孔)")
      + f", 牙底处实测壁厚/半径 {wall_thread:.3f}")
print(f"  十字筋 ×{len(RIB_ANGLES)} {RIB_ANGLES} 厚 {RIB_T:g}, Z 0→{Z_CEIL:g} 并入顶板; 腔内筋面积 {rib_area:.2f} mm^2")
print(f"  45° 过渡 ×{GUSSET:g} (规则 ceil((r_insc+0.501)·10)/10 = {GUSSET_RULE:g}): 格内切圆半径 {r_insc:.3f} "
      f"⇒ 腔在 Z={Z_CEIL - GUSSET + r_insc:.2f} 全闭合 (无水平腔顶), 加料 {v_gusset_added:.1f} mm^3")
print(f"  悬垂: 下柱最大 {ov_body_max:.2f}° (≤45 免支撑); 螺纹段朝下面积 {_ar[_thr].sum():.1f} mm^2, "
      f"最大 {_ov[_thr].max():.1f}° (60° 牙侧)")
print(f"  截面积 螺纹段 Z={z_mid:g}: {a_mid:.3f} (理论 {a_mid_expect:.3f}, 差 {abs(a_mid-a_mid_expect)/a_mid_expect*100:.4f}%)")
print(f"         筋区 Z={Z_CEIL/2:g}: {a_rib:.3f} (理论 {a_rib_expect:.3f}) / 顶板: {a_plate:.3f}")
print(f"  螺纹段(实心不倒角): {stud_plain.volume():.2f} mm^3 (理论 {v_plain_theory:.2f}, "
      f"差 {abs(stud_plain.volume()-v_plain_theory)/v_plain_theory*100:.3f}%)")
print(f"  volume: {vol:10.3f} mm^3  (预期 {v_expect:.3f}, 相对差 {abs(vol-v_expect)/v_expect:.2e})")
print(f"  PETG 实心约 {vol*1.27e-3:.1f} g (1.27 g/cm^3; 若 PLA 约 {vol*1.24e-3:.1f} g)")
_T_eff = PLATE_T + GUSSET - r_insc
print(f"  顶板等效实心厚 T_eff = PLATE_T + GUSSET - r_insc = {_T_eff:.3f}; 线数 WALL {WALL/0.42:.2f} / RIB {RIB_T/0.42:.2f} / "
      f"PLATE {PLATE_T/0.42:.2f}; 首层筒壁环宽 (C{BOT_CH:g}, 层中面 0.1) {WALL-(BOT_CH-0.1):.2f}")
