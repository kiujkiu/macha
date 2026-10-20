"""rotor_shroud_v3 预览: 装上/掀开一半/单件三视。生成 shroud_v3_preview.png。"""
import math, struct
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Noto Sans CJK SC", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = Path(__file__).parent
V3 = HERE.parent.parent
MODELS = V3.parent / "models"
STL_TRI = np.dtype([("normal", "<f4", 3), ("verts", "<f4", (3, 3)), ("attr", "<u2")])
DISC_TOP, ROTOR_Z0, SCR = 42.2, 31.7, -45.0


def read_stl(p):
    raw = p.read_bytes()
    n = struct.unpack_from("<I", raw, 80)[0]
    return np.frombuffer(raw, dtype=STL_TRI, count=n, offset=84)["verts"].astype(np.float64)


def rot_z(a, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    x = a[..., 0].copy(); y = a[..., 1].copy()
    a[..., 0] = c * x - s * y
    a[..., 1] = s * x + c * y
    return a


inner, shroud = [], []
ring = read_stl(MODELS / "rim_ring/rim_ring.stl")
ring[..., 1] = -ring[..., 1]; ring[..., 2] = DISC_TOP - ring[..., 2]
inner.append((ring, "#9ccf9c"))
_e = math.radians(135.0)
off = np.array([-10.0 * math.cos(_e), -10.0 * math.sin(_e), 0.0])
inner.append((rot_z(read_stl(MODELS / "pi2hub75e/pi2hub75e.stl")
                    + np.array([0, 0, DISC_TOP + 5.0]), 225.0) + off, "#2a7d2a"))
inner.append((rot_z(read_stl(MODELS / "mlkpai_board/mlkpai_board.stl")
                    + np.array([0, 0, DISC_TOP + 15.1]), 225.0) + off, "#e03020"))
te = read_stl(V3 / "models/bottom_portal_v3/portal_tee_v3.stl") + np.array([0, 0, DISC_TOP])
inner.append((rot_z(te.copy(), SCR), "#aa6622"))
inner.append((rot_z(te.copy(), SCR + 180.0), "#aa6622"))
ws = read_stl(MODELS / "usb_wifi/wifi_shell.stl")
ws = ws[..., [2, 1, 0]] * np.array([1.0, 1.0, -1.0])
ws[..., 0] += 43.0 - 46.4 / 2; ws[..., 1] += -13.0; ws[..., 2] += 18.1 + DISC_TOP
inner.append((rot_z(ws, 135.0), "#22aaaa"))
inner.append((rot_z(read_stl(MODELS / "usb_wifi/usb_wifi_module_flat.stl")
                    + np.array([0, 0, DISC_TOP]), 135.0), "#111111"))
sc = read_stl(MODELS / "screen_150x169_t13/screen_150x169_t13.stl") + np.array([0, 0, DISC_TOP + 50.0])
sc = sc[np.asarray(sc)[:, :, 2].max(axis=1) < DISC_TOP + 110.0]     # 只画屏下段
inner.append((rot_z(sc, SCR), "#3355cc"))
for tag, col in (("A", "#b8c0d0"), ("B", "#98a0b0")):
    sh = read_stl(HERE / f"shroud_half_{tag}_v3.stl") + np.array([0, 0, DISC_TOP])
    shroud.append((rot_z(sh, SCR), col))

VIEWS = [(20, -55, "装上 (两半合拢)", True, True),
         (20, -55, "掀开 A 半 (看内部)", True, False),
         (89, -90, "俯视 (封顶 + 屏缝)", True, True)]
fig = plt.figure(figsize=(16.5, 5.6))
for i, (elev, azim, title, show_in, show_A) in enumerate(VIEWS):
    ax = fig.add_subplot(1, 3, i + 1, projection="3d")
    if show_in:
        for t, c in inner:
            ax.add_collection3d(Poly3DCollection(t, facecolor=c, edgecolor="none", alpha=.95))
    for j, (t, c) in enumerate(shroud):
        if j == 0 and not show_A:
            continue
        ax.add_collection3d(Poly3DCollection(t, facecolor=c, edgecolor="none",
                                             alpha=.62 if show_A and i == 0 else .95))
    ax.set_xlim(-95, 95); ax.set_ylim(-95, 95); ax.set_zlim(28, 118)
    ax.set_box_aspect((1, 1, .55)); ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=9)
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
fig.tight_layout()
png = HERE / "shroud_v3_preview.png"
fig.savefig(png, dpi=125, bbox_inches="tight")
print(f"wrote {png}")
