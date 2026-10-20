"""
V1.0 屏幕锁紧方式 —— 理解示意 第 3 版 (2026-10-20, 非定稿, 不可打印)

用户描述 (2026-10-20, 配 V0.3 实物照片):
  · 两块灯板 PCB 背靠背间距 **4.6 = 六角铜螺母对边** (M3 通孔内螺纹, 对边 4.6, 长 4.0)
  · 铜螺母**侧躺**在两板之间的缝里, 轴线竖直 (上下出螺丝), 两个平面分别贴两块板背面焊盘
  · 同一侧板边的螺母都在一条竖直轴线上 (同心) ⇒ 一根 M3 螺杆从上到下穿过, 锁住两块屏;
    螺杆上端穿**顶盖** (上塑料件), 下端进**底座** (下塑料件, 照片里的三角脚座), 底座固定到转子
第 3 版 (用户 2026-10-20 改): **每组 2 颗螺母上下同心叠放, 上颗焊灯板 A、下颗焊灯板 B**
(拆螺丝即可分开两屏); 每侧 **3 组** (上/中/下, 沿用现有孔位高度); 每侧 **2 根螺丝**:
上螺丝从顶盖向下锁进上组, 下螺丝从底座向上穿下组、锁进中组。顶盖/底座形状仍为占位。

坐标: 世界 X = 屏厚方向 (LED 面朝 ±X), Y = 屏宽, Z = 屏高 (灯板下沿 Z=0); 偏心同 V1.0
(面 B LED 面在轴 X=0)。输出 screen_screw_concept.3mf + _preview.png。
"""
import struct
import zipfile
from pathlib import Path
import numpy as np
import manifold3d as m3d
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle, Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

for _f in ("/mnt/c/Windows/Fonts/simhei.ttf",):
    if Path(_f).exists():
        font_manager.fontManager.addfont(_f)
plt.rcParams["font.sans-serif"] = ["SimHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

HERE = Path(__file__).parent
BOARDS = HERE.parent / "boards"
STL_TRI = np.dtype([("normal", "<f4", 3), ("verts", "<f4", (3, 3)), ("attr", "<u2")])

# ---- 尺寸 ----
LED_T = 1.84                                   # 灯板厚
NUT_AF, NUT_L = 4.6, 4.0                       # 六角铜螺母: 对边 (= 板间距) / 长 (沿 Z)
GAP = NUT_AF                                   # 背靠背 4.6
ECC = GAP / 2 + LED_T                          # 4.14, 面 B LED 面在轴
ROD_D = 3.0
HOLE_X = 78.47                                 # 板系 |x| ⇒ 世界 |Y|
ROWS = (79.35, -28.15, -135.65)                # 板系 y
EDGE_X, EDGE_BOT, EDGE_TOP = 81.975, -140.66, 84.36
BOARD_H = EDGE_TOP - EDGE_BOT                  # 225.02
LED_AREA = 75.0, -84.375, 84.375
CAP_T, FOOT_H = 8.0, 15.0                      # 顶盖厚 / 底座高 (示意)
HEAD_D, HEAD_H = 5.5, 3.0                      # M3 内六角头
BR_C, BR_GAP, BR_ON_LED_Y = (65.91, 38.86), 3.33, -112.908
X_C = ECC                                      # 缝中心 = 螺杆轴线 X
X_BACK_A, X_BACK_B = ECC + GAP / 2, ECC - GAP / 2
X_LED_A, X_LED_B = X_BACK_A + LED_T, X_BACK_B - LED_T


def read_stl(path):
    raw = path.read_bytes()
    n = struct.unpack_from("<I", raw, 80)[0]
    return np.frombuffer(raw, dtype=STL_TRI, count=n, offset=84)["verts"].astype(np.float64)


def tris(man):
    m = man.to_mesh()
    v = np.asarray(m.vert_properties)[:, :3]
    return v[np.asarray(m.tri_verts)]


def xform(t, R, T=(0.0, 0.0, 0.0)):
    out = t @ np.asarray(R, float).T + np.asarray(T, float)
    return out[:, ::-1, :].copy() if np.linalg.det(R) < 0 else out


def led_to_world(t, face):
    """灯板系 (x,y,z; z0=背面, z-1.84=LED 面) → 世界。face +1 = A (LED 朝 +X)。"""
    R = np.array([[0, 0, -1], [-1, 0, 0], [0, 1, 0]], float)
    w = xform(t, R, (GAP / 2, 0.0, -EDGE_BOT))
    if face < 0:
        w = xform(w, np.diag([-1.0, -1.0, 1.0]))
    return w + np.array([ECC, 0.0, 0.0])


def hex_z(af, h):
    """竖直六角柱, 两平面朝 ±X (贴两块板), 底面 z=0。"""
    return m3d.Manifold.cylinder(h, af / np.sqrt(3), af / np.sqrt(3), 6).rotate((0, 0, 30))


def cyl_z(d, h, n=32):
    return m3d.Manifold.cylinder(h, d / 2, d / 2, n)


def union(ms):
    return m3d.Manifold.batch_boolean(ms, m3d.OpType.Add)


parts = []   # (name, tris, color)

# ---- 灯板 ×2 + LED 区示意 + 桥板 ----
board = read_stl(BOARDS / "led_icn2260_v01_260921_board.stl")
bridge = read_stl(BOARDS / "bridge_gw5a_2026-10-15_board.stl")
br = xform(bridge - np.array([BR_C[0], BR_C[1], 0.0]), np.diag([-1.0, 1.0, -1.0]),
           (0.0, BR_ON_LED_Y, -LED_T - BR_GAP))
led_area = tris(m3d.Manifold.cube((2 * LED_AREA[0], LED_AREA[2] - LED_AREA[1], 0.6), False)
                .translate((-LED_AREA[0], LED_AREA[1], -LED_T - 0.6)))
for face, tag, col in ((+1, "A", "#3355cc"), (-1, "B", "#1b2a66")):
    parts.append((f"灯板 {tag}", led_to_world(board, face), col))
    parts.append((f"LED 区 {tag} (示意 150x168.75)", led_to_world(led_area, face), "#9ec5ff"))
    parts.append((f"桥板 {tag}", led_to_world(br, face), "#1f9a6a"))

# ---- 铜螺母 (侧躺, 轴 Z): 每组 2 颗上下叠, 上颗焊 A / 下颗焊 B ---- + 螺丝 (上 1 / 下 1 每侧)
row_z = [y - EDGE_BOT for y in ROWS]           # 每组中心高 (= 两颗螺母交界面)
GRP_H = 2 * NUT_L
nuts_a, nuts_b, screws = [], [], []
for sy in (1, -1):
    y = sy * HOLE_X
    for z in row_z:
        nuts_a.append(hex_z(NUT_AF, NUT_L).translate((X_C, y, z)))
        nuts_b.append(hex_z(NUT_AF, NUT_L).translate((X_C, y, z - NUT_L)))
    top_tip = row_z[0] - GRP_H / 2                                      # 上螺丝: 顶盖 → 穿到上组底
    screws.append(cyl_z(HEAD_D, HEAD_H).translate((X_C, y, BOARD_H + CAP_T))
                  + cyl_z(ROD_D, BOARD_H + CAP_T - top_tip).translate((X_C, y, top_tip)))
    bot_tip = row_z[1] + GRP_H / 2                                      # 下螺丝: 底座 → 穿到中组顶
    screws.append(cyl_z(HEAD_D, HEAD_H).translate((X_C, y, -FOOT_H))
                  + cyl_z(ROD_D, bot_tip + FOOT_H - HEAD_H).translate((X_C, y, -FOOT_H + HEAD_H)))
TOP_L = BOARD_H + CAP_T - (row_z[0] - GRP_H / 2)
BOT_L = row_z[1] + GRP_H / 2 + FOOT_H - HEAD_H
parts.append(("铜螺母 ×6 焊灯板 A (每组上颗)", tris(union(nuts_a)), "#d4a017"))
parts.append(("铜螺母 ×6 焊灯板 B (每组下颗)", tris(union(nuts_b)), "#f0d070"))
parts.append((f"M3 螺丝 ×4 (上 M3x{TOP_L:.0f} ×2 / 下 M3x{BOT_L:.0f} ×2)", tris(union(screws)), "#202020"))
nuts = nuts_a + nuts_b

# ---- 顶盖 (上塑料件, 示意): 横跨两板上沿, 两端过螺杆 ----
CAP_HX = 8.0                                   # 顶盖沿 X 半宽 (中心在缝)
cap = m3d.Manifold.cube((2 * CAP_HX, 2 * (EDGE_X + 4), CAP_T), False) \
    .translate((X_C - CAP_HX, -(EDGE_X + 4), BOARD_H))
for sy in (1, -1):
    cap -= cyl_z(3.4, 40).translate((X_C, sy * HOLE_X, BOARD_H - 10))
parts.append(("顶盖 (上塑料件, 示意, 接顶部定心)", tris(cap), "#c05cd6"))


# ---- 底座 (下塑料件, 示意): 每侧一只梯形脚座, 螺杆从上插入, 底下螺母窝 ----
def foot(sy):
    yb0, yb1 = 66.0, EDGE_X + 4                # 世界 |Y| 范围
    bot_hx, top_hx = 16.0, 7.0                 # 底 / 顶 沿 X 半宽
    prof = [[X_C - bot_hx, -FOOT_H], [X_C + bot_hx, -FOOT_H], [X_C + top_hx, 0.0], [X_C - top_hx, 0.0]]
    f = m3d.Manifold.extrude(m3d.CrossSection([prof]), yb1 - yb0).rotate((90, 0, 0)).translate((0, yb1, 0))
    f -= cyl_z(3.4, 40).translate((X_C, HOLE_X, -FOOT_H - 5))
    f -= cyl_z(HEAD_D + 0.5, HEAD_H + 0.1).translate((X_C, HOLE_X, -FOOT_H - 0.1))   # 螺丝头沉孔
    return f.mirror((0, 1, 0)) if sy < 0 else f


parts.append(("底座 (下塑料件, 示意, 接转子)", tris(union([foot(1), foot(-1)])), "#ff7f2a"))
parts.append(("旋转轴 X=0", tris(m3d.Manifold.cylinder(BOARD_H + 60, 0.4, 0.4, 12).translate((0, 0, -30))), "#ff0000"))

# ---- 自检: 螺母 vs 两块板 (局部板片近似; 贴面 → 体积应 ~0) ----
slab = lambda xa, xb: m3d.Manifold.cube((xb - xa, 2 * EDGE_X, BOARD_H), False).translate((xa, -EDGE_X, 0))
for nm, s in (("A", slab(X_BACK_A, X_LED_A)), ("B", slab(X_LED_B, X_BACK_B))):
    print(f"  螺母 ∩ 灯板{nm} 体积 {(union(nuts) ^ s).volume():.4f} (贴面应 0)")
print(f"背靠背 {GAP:.2f} = 螺母对边, 偏心 {ECC:.2f}; LED 面 X = {X_LED_B:+.2f} (B) / {X_LED_A:+.2f} (A); "
      f"螺杆轴线 X = {X_C:.2f}, |Y| = {HOLE_X}")
print(f"螺母组 (2×{NUT_L:g}={GRP_H:g}) 中心高 Z = {', '.join(f'{z:.2f}' for z in row_z)} "
      f"(灯板下沿 Z0, 上沿 {BOARD_H:.2f}); 上组顶到上沿 {BOARD_H - row_z[0] - GRP_H/2:.2f}, 下组底到下沿 {row_z[2] - GRP_H/2:.2f}")
print(f"上螺丝 M3 杆长 {TOP_L:.2f} (顶盖 {CAP_T:g} + 上组 {GRP_H:g}); "
      f"下螺丝 杆长 {BOT_L:.2f} (底座 {FOOT_H - HEAD_H:g} + 下组 + 空段 + 中组)")


# ---- 3MF ----
def write_3mf(path, named):
    mats = "".join(f'<base name="{n}" displaycolor="{c.upper()}FF"/>' for n, _, c in named)
    objs, items = [], []
    for i, (name, t, _) in enumerate(named):
        v, idx = np.unique(np.round(t.reshape(-1, 3), 4), axis=0, return_inverse=True)
        tri = idx.reshape(-1, 3)
        tri = tri[(tri[:, 0] != tri[:, 1]) & (tri[:, 1] != tri[:, 2]) & (tri[:, 0] != tri[:, 2])]
        vs = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in v)
        ts = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in tri)
        objs.append(f'<object id="{i + 2}" name="{name}" type="model" pid="1" pindex="{i}">'
                    f'<mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>')
        items.append(f'<item objectid="{i + 2}"/>')
    model = ('<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
             f'<resources><basematerials id="1">{mats}</basematerials>{"".join(objs)}</resources>'
             f'<build>{"".join(items)}</build></model>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml",
                   '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/'
                   'package/2006/content-types"><Default Extension="rels" ContentType="application/'
                   'vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" '
                   'ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr("_rels/.rels",
                   '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.'
                   'org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" '
                   'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr("3D/3dmodel.model", model)


out = HERE / "screen_screw_concept.3mf"
write_3mf(out, parts)
print(f"wrote {out}")

# ---- 预览: 整体 iso | 过螺杆竖剖 (X-Z, Y=-78.47) | 过一颗螺母横剖 (X-Y) ----
fig = plt.figure(figsize=(18, 10))
ax = fig.add_subplot(1, 3, 1, projection="3d")
for name, t, c in parts:
    ax.add_collection3d(Poly3DCollection(t, facecolor=c, edgecolor="none", alpha=0.9))
ax.set_xlim(-120, 120); ax.set_ylim(-120, 120); ax.set_zlim(-30, 250)
ax.set_box_aspect((1, 1, 280 / 240)); ax.view_init(15, -20); ax.set_title("整体 (示意)")


def rect(ax, x0, x1, z0, z1, c, lbl=None, **kw):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=c, ec="k", lw=0.5, label=lbl, **kw))


ax = fig.add_subplot(1, 3, 2)
rect(ax, X_BACK_A, X_LED_A, 0, BOARD_H, "#3355cc", "灯板 A")
rect(ax, X_LED_B, X_BACK_B, 0, BOARD_H, "#1b2a66", "灯板 B")
for i, z in enumerate(row_z):
    rect(ax, X_BACK_B, X_BACK_A, z, z + NUT_L, "#d4a017", "铜螺母 焊 A (上颗)" if i == 0 else None)
    rect(ax, X_BACK_B, X_BACK_A, z - NUT_L, z, "#f0d070", "铜螺母 焊 B (下颗)" if i == 0 else None)
tt, bt = row_z[0] - GRP_H / 2, row_z[1] + GRP_H / 2
rect(ax, X_C - ROD_D / 2, X_C + ROD_D / 2, tt, BOARD_H + CAP_T, "#202020", "M3 螺丝 (上↓ / 下↑)", alpha=0.85)
rect(ax, X_C - ROD_D / 2, X_C + ROD_D / 2, -FOOT_H + HEAD_H, bt, "#202020", alpha=0.85)
rect(ax, X_C - HEAD_D / 2, X_C + HEAD_D / 2, BOARD_H + CAP_T, BOARD_H + CAP_T + HEAD_H, "#202020")
rect(ax, X_C - HEAD_D / 2, X_C + HEAD_D / 2, -FOOT_H, -FOOT_H + HEAD_H, "#202020")
rect(ax, X_C - CAP_HX, X_C + CAP_HX, BOARD_H, BOARD_H + CAP_T, "#c05cd6", "顶盖 (上塑料件)")
ax.add_patch(Polygon([[X_C - 16, -FOOT_H], [X_C + 16, -FOOT_H], [X_C + 7, 0], [X_C - 7, 0]],
                     fc="#ff7f2a", ec="k", lw=0.5, alpha=0.6, label="底座 (下塑料件)"))
ax.axvline(0, color="r", ls="--", lw=1, label="旋转轴")
ax.set_xlim(-25, 30); ax.set_ylim(-25, BOARD_H + 20); ax.set_aspect("equal")
ax.set_xlabel("X mm (屏厚方向)"); ax.set_ylabel("Z mm"); ax.set_title(f"过螺杆竖剖 (Y = -{HOLE_X})")
ax.legend(loc="center right", fontsize=8)

ax = fig.add_subplot(1, 3, 3)
rect(ax, X_BACK_A, X_LED_A, 60, 90, "#3355cc", "灯板 A")
rect(ax, X_LED_B, X_BACK_B, 60, 90, "#1b2a66", "灯板 B")
rect(ax, X_LED_A, X_LED_A + 0.6, 60, 75, "#9ec5ff", "LED 区 (到 |Y|75)")
rect(ax, X_LED_B - 0.6, X_LED_B, 60, 75, "#9ec5ff")
r = NUT_AF / np.sqrt(3)
hexpts = [[X_C + r * np.cos(np.radians(a + 30)), HOLE_X + r * np.sin(np.radians(a + 30))] for a in range(0, 360, 60)]
ax.add_patch(Polygon(hexpts, fc="#d4a017", ec="k", lw=0.6, label="六角铜螺母 对边 4.6 (上颗焊 A / 下颗焊 B)"))
ax.add_patch(plt.Circle((X_C, HOLE_X), ROD_D / 2, fc="#202020", label="M3 螺丝"))
ax.annotate("", (X_BACK_B, 84.5), (X_BACK_A, 84.5), arrowprops=dict(arrowstyle="<->"))
ax.text(X_C, 85, f"{GAP}", ha="center")
ax.axvline(0, color="r", ls="--", lw=1)
ax.set_xlim(-6, 14); ax.set_ylim(68, 88); ax.set_aspect("equal")
ax.set_xlabel("X mm"); ax.set_ylabel("|Y| mm (屏宽方向, 板边 81.98)")
ax.set_title("过一颗螺母横剖 (俯视)")
ax.legend(loc="lower right", fontsize=8)
fig.tight_layout()
png = HERE / "screen_screw_concept_preview.png"
fig.savefig(png, dpi=110)
print(f"wrote {png}")
