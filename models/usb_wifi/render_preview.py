"""wifi_box_preview.png — 倒扣盒+模块 与周边件 (龙门/盘/板) 的局部装配目检图。"""
import struct
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
STL_TRI = np.dtype([("normal", "<f4", 3), ("verts", "<f4", (3, 3)), ("attr", "<u2")])

def tris(path, dz=0.0, rot90=False, off=(0, 0)):
    raw = path.read_bytes()
    n = struct.unpack_from("<I", raw, 80)[0]
    t = np.frombuffer(raw, dtype=STL_TRI, count=n, offset=84)["verts"].astype(np.float64).copy()
    if rot90:
        x = t[..., 0].copy(); t[..., 0] = -t[..., 1]; t[..., 1] = x
    t[..., 0] += off[0]; t[..., 1] += off[1]; t[..., 2] += dz
    return t

PARTS = [
    ("disc",   tris(ROOT/"models/mlkpai_carrier_disc/mlkpai_carrier_disc.stl", dz=-5), "#9ccf9c", .35),
    ("gantryA", tris(ROOT/"models/l_bracket_v2/gantry_base_A.stl"), "#aa6622", .5),
    ("gantryB", tris(ROOT/"models/l_bracket_v2/gantry_base_B.stl"), "#aa6622", .5),
    ("pi2hub", tris(ROOT/"models/pi2hub75e/pi2hub75e.stl", dz=5, rot90=True, off=(-10, 0)), "#2a7d2a", .5),
    ("mlkpai", tris(ROOT/"models/mlkpai_board/mlkpai_board.stl", dz=16.1, rot90=True, off=(-10, 0)), "#e03020", .5),
    ("module", tris(HERE/"usb_wifi_module.stl"), "#111111", 1.0),
    ("box",    tris(HERE/"wifi_box.stl"), "#22aaaa", .5),
]

fig = plt.figure(figsize=(16, 9))
views = [(89, -90, "top (盘系)"), (28, -35, "iso"), (2, -90, "側视 -Y→ (天线过脚顶)"), (2, 0, "侧视 +X→")]
for i, (elev, azim, title) in enumerate(views):
    ax = fig.add_subplot(2, 2, i+1, projection="3d")
    for name, t, c, a in PARTS:
        ax.add_collection3d(Poly3DCollection(t, facecolor=c, edgecolor="none", alpha=a))
    ax.set_xlim(0, 110); ax.set_ylim(-105, 105); ax.set_zlim(-8, 95)
    ax.set_box_aspect((110, 210, 103))
    ax.view_init(elev=elev, azim=azim); ax.set_title(title)
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
fig.tight_layout()
png = HERE / "wifi_box_preview.png"
fig.savefig(png, dpi=100)
print("wrote", png)
