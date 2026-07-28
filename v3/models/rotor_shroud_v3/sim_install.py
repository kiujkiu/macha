"""rotor_shroud_v3 安装过程模拟 (2026-07-27, 用户: "锁这两个半圆的时候, 这个
螺丝帽要通过全部的这个孔, 你需要模拟一下螺丝的安装过程")。

快照式布尔只证明「装好之后不打架」, 不证明「装得进去」。本脚本模拟三段运动:

  A. 半罩竖直下落      h = 60 → 0 mm, 每步查 vs 全部转子邻居
     (h≥60 时罩底已高过 T 件顶 92.2, 可横向滑入把屏套进屏缝)
  B. 螺丝落井          M3×12 (头 Φ7.5×2.5 + 杆 Φ3) 从井口落到井底台肩,
     含 ±0.75 横向游隙 (头 Φ7.5 在 Φ9 井里) 的 8 个方位极限位置
  C. 螺丝刀通道        井口往上到机器外, Φ7 直杆, 查全部静止件 + 转子上部件

运行: pov3d/.venv/bin/python v3/models/rotor_shroud_v3/sim_install.py
"""
import math
import struct
from pathlib import Path
import numpy as np
import manifold3d as m3d

HERE = Path(__file__).parent
V3 = HERE.parent.parent
MODELS = V3.parent / "models"
STL_TRI = np.dtype([("normal", "<f4", 3), ("verts", "<f4", (3, 3)), ("attr", "<u2")])
DISC_TOP, ROTOR_Z0, V3_SCR_ROT = 42.2, 31.7, -45.0
COL_R, COL_ANG = 77.5, (22.5, 157.5, 202.5, 337.5)      # 零件系
WELL_D, HEAD_D, HEAD_H, SHANK_D, SCREW_L, FLOOR_T = 9.0, 7.5, 2.5, 3.0, 12.0, 3.0


def read_stl(p):
    raw = p.read_bytes()
    n = struct.unpack_from("<I", raw, 80)[0]
    return np.frombuffer(raw, dtype=STL_TRI, count=n, offset=84)["verts"].astype(np.float64)


def to_manifold(tris):
    v = tris.reshape(-1, 3)
    u, inv = np.unique(np.round(v, 4), axis=0, return_inverse=True)
    i = inv.astype(np.uint32).reshape(-1, 3)
    m = m3d.Manifold(m3d.Mesh(vert_properties=u.astype(np.float32), tri_verts=i))
    if m.volume() < 0:
        m = m3d.Manifold(m3d.Mesh(vert_properties=u.astype(np.float32),
                                  tri_verts=i[:, ::-1].copy()))
    return m


def rot_z(a, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    x = a[..., 0].copy(); y = a[..., 1].copy()
    a[..., 0] = c * x - s * y
    a[..., 1] = s * x + c * y
    return a


# ===== 零件系里的罩子两半 (Z0 = 承载面) =====
HALF = {t: to_manifold(read_stl(HERE / f"shroud_half_{t}_v3.stl")) for t in "AB"}

# ===== 零件系里的转子邻居 (与罩子同随 V3_SCR_ROT, 故直接折算) =====
def part_frame():
    o = {}
    te = read_stl(V3 / "models/bottom_portal_v3/portal_tee_v3.stl")
    o["portal_tee_A"] = te.copy()
    o["portal_tee_B"] = rot_z(te.copy(), 180.0)
    ws = read_stl(MODELS / "usb_wifi/wifi_shell.stl")
    ws = ws[..., [2, 1, 0]] * np.array([1.0, 1.0, -1.0])
    ws[..., 0] += 43.0 - 46.4 / 2; ws[..., 1] += -13.0; ws[..., 2] += 18.1
    o["wifi_shell"] = rot_z(ws, 180.0)
    o["usb_wifi_module"] = rot_z(read_stl(MODELS / "usb_wifi/usb_wifi_module_flat.stl"), 180.0)
    _e = math.radians(135.0)
    o["pi2hub75e"] = rot_z(read_stl(MODELS / "pi2hub75e/pi2hub75e.stl")
                           + np.array([0.0, 0.0, 5.0]), 270.0) \
        + np.array([-10.0 * math.cos(_e), -10.0 * math.sin(_e), 0.0])
    o["mlkpai_board"] = rot_z(read_stl(MODELS / "mlkpai_board/mlkpai_board.stl")
                              + np.array([0.0, 0.0, 15.1]), 270.0) \
        + np.array([-10.0 * math.cos(_e), -10.0 * math.sin(_e), 0.0])
    o["dual_screen"] = read_stl(MODELS / "screen_150x169_t13/screen_150x169_t13.stl") \
        + np.array([0.0, 0.0, 50.0])
    # 已装好的紧固件头 (Φ7.5×2.5): wifi 沿 4 + T 脚 4 + 屏底 2
    heads = None
    def _rp(x, y, d):
        r = math.radians(d)
        return (x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r))
    spec = [(_rp(ax, ay, -V3_SCR_ROT), 3.0) for (ax, ay) in
            [(-42.99, 0.14), (18.24, 61.38), (-60.67, 17.82), (0.57, 79.05)]]
    spec += [((s * hx, s * 71.601), 5.0) for s in (1.0, -1.0) for hx in (29.658, -29.658)]
    spec += [((0.0, hy), 41.0) for hy in (64.0, -64.0)]
    for (hx, hy), hz in spec:
        c = m3d.Manifold.cylinder(HEAD_H, HEAD_D / 2, HEAD_D / 2, 48, False) \
            .translate((hx, hy, hz))
        heads = c if heads is None else heads + c
    hm = heads.to_mesh()
    o["fastener_heads"] = (np.asarray(hm.vert_properties)[:, :3])[np.asarray(hm.tri_verts)]
    return {k: to_manifold(v) for k, v in o.items()}


OBST = part_frame()

# ============ A. 半罩竖直下落 ============
print("=" * 78)
print("A. 半罩竖直下落 (h = 罩底距最终位的高度, mm)")
STEPS = [60, 50, 40, 30, 24, 20, 16, 13, 11, 9.5, 8, 7, 6, 5.5, 5, 4.5, 4, 3.5,
         3, 2.5, 2, 1.5, 1, 0.5, 0.25, 0]
bad_A = []
for tag in "AB":
    worst = {}
    for h in STEPS:
        moved = HALF[tag].translate((0.0, 0.0, float(h)))
        for k, o in OBST.items():
            v = (moved ^ o).volume()
            if v > 1e-6:
                worst.setdefault(k, []).append((h, v))
    if worst:
        for k, lst in worst.items():
            hs = [f"{h:g}" for h, _ in lst]
            vmax = max(v for _, v in lst)
            print(f"  ✗ 半{tag} 撞 {k:16s} 在 h = {', '.join(hs)}  最大 {vmax:.2f} mm³")
            bad_A.append((tag, k))
    else:
        print(f"  ✓ 半{tag}: {len(STEPS)} 个高度 × {len(OBST)} 个邻居 全程无碰撞")
print("  (h≥60 时罩底 102.2 已高过 T 件顶 92.2 → 可在该高度横向滑入, 屏从屏缝进)")

# ============ B. 螺丝落井 ============
print("\n" + "=" * 78)
print("B. M3×12 落井 (头 Φ7.5×2.5 + 杆 Φ3, 井 Φ9, 井深 47, 含 ±0.75 横向游隙)")
PLAY = (WELL_D - HEAD_D) / 2.0          # 0.75
TOL = 0.05                              # 真干涉下限 (mm³), 见下方说明
screw0 = (m3d.Manifold.cylinder(HEAD_H, HEAD_D / 2, HEAD_D / 2, 64, False)
          .translate((0.0, 0.0, 0.0))
          + m3d.Manifold.cylinder(SCREW_L, SHANK_D / 2, SHANK_D / 2, 48, False)
          .translate((0.0, 0.0, -SCREW_L)))       # 头底在 z=0, 杆朝下
# 分两段: 杆尖到台肩顶面 (z=15) 之前是自由落体, 可满偏心 ±0.75;
# 之后杆尖进引导锥/过孔, 被强制对中 (过孔 Φ3.4 对杆 Φ3 → 残余偏心 ≤0.2)。
# (把「满偏心」和「已落座」叠在一起测是测了互斥状态, 必然假报警。)
# 判据阈值 TOL: 井 Φ9 与头 Φ7.5 都是多边形逼近 (64 边), 内切半径比理想圆小
# ~0.005 → 满偏心 0.75 恰好相切时会产生微米级假交集 (实测最大 0.000 mm³)。
# 取 0.05 mm³ 作为「真干涉」下限, 并把实测最大值打出来自证。
PHASE = [("自由落体 z52→15, 偏心 ±0.75", [float(z) for z in np.arange(15.0, 52.0, 0.5)], PLAY),
         ("导入落座 z15→3,  偏心 ≤0.20", [float(z) for z in np.arange(FLOOR_T, 15.01, 0.25)], 0.2)]
bad_B = []
for tag in "AB":
    angs = [a for a in COL_ANG
            if (math.sin(math.radians(a)) > 0) == (tag == "A")]
    for a in angs:
        cx, cy = COL_R * math.cos(math.radians(a)), COL_R * math.sin(math.radians(a))
        line = f"  半{tag} 立柱{a:6.1f}°:"
        vmax_seen = [0.0]
        for label, zs, play in PHASE:
            hits = []
            for k in range(8):
                ox = play * math.cos(math.radians(k * 45.0))
                oy = play * math.sin(math.radians(k * 45.0))
                for z in zs:
                    v = (screw0.translate((cx + ox, cy + oy, z)) ^ HALF[tag]).volume()
                    vmax_seen[0] = max(vmax_seen[0], v)
                    if v > TOL:
                        hits.append((k * 45.0, z, v))
            if hits:
                line += f"  ✗ {label} {len(hits)} 处卡涉 (最大 {max(h[2] for h in hits):.3f} mm³)"
                bad_B.append((tag, a, label))
            else:
                line += f"  ✓ {label} ({8*len(zs)} 个位姿)"
        print(line + f"   [实测最大交集 {vmax_seen[0]:.4f} mm³]")

# 引导锥捕捉能力
LEAD_D = 5.0
print(f"  引导锥 Φ{SHANK_D:g}→Φ{LEAD_D:g}: 捕捉半径 {(LEAD_D-SHANK_D)/2:.2f} "
      f"> 最大偏心 {PLAY:.2f} → 杆尖必落进孔 ✓ (头仍压 Φ{LEAD_D:g}..Φ{HEAD_D:g} 环面)")

# ============ C. 螺丝刀通道 ============
print("\n" + "=" * 78)
print("C. 螺丝刀通道 (井口 asm 92.2 往上, Φ7 直杆) vs 上方所有件")
up = {}
sc = read_stl(MODELS / "screen_150x169_t13/screen_150x169_t13.stl") + np.array([0, 0, DISC_TOP + 50.0])
up["dual_screen"] = rot_z(sc, V3_SCR_ROT)
cap = read_stl(V3 / "models/top_cap_v3_1/top_cap_v3_1.stl")
cap[..., 1] = -cap[..., 1]; cap[..., 2] = 267.95 - cap[..., 2]; cap = cap[:, ::-1, :].copy()
up["top_cap_v3_1"] = rot_z(cap, V3_SCR_ROT)
fa = rot_z(read_stl(V3 / "models/top_bearing_v3/frame_A_v3.stl"), 135.0); fa[..., 2] += 290.0
up["frame_A_v3"] = fa
fb = read_stl(V3 / "models/top_bearing_v3/frame_B_v3.stl")
fb[..., 1] = -fb[..., 1]; fb[..., 2] = 290.0 + 16.0 - fb[..., 2]; fb = fb[:, ::-1, :].copy()
up["frame_B_v3"] = rot_z(fb, -45.0)
sm = read_stl(MODELS / "photo_sensor/sensor_module.stl")
sm = sm[..., [1, 0, 2]] * np.array([1.0, -1.0, 1.0]); sm = sm + np.array([-3.0, -45.0, 267.95])
_th = np.arcsin(17.0 / 45.0); _R = np.array([[np.cos(_th), -np.sin(_th)], [np.sin(_th), np.cos(_th)]])
sm[..., :2] = (sm[..., :2] - np.array([0.0, -45.0])) @ _R.T + np.array([0.0, -45.0])
up["sensor_module"] = rot_z(sm, V3_SCR_ROT)
UPM = {k: to_manifold(v) for k, v in up.items()}
posts = None
for px in (-75.0, 75.0):
    for py in (-75.0, 75.0):
        c = m3d.Manifold.cylinder(290.0, 4.0, 4.0, 32, False).translate((px, py, 0.0))
        posts = c if posts is None else posts + c
UPM["posts×4"] = posts
UPM["standoff+M6"] = (m3d.Manifold.cylinder(40.0, 4.0, 4.0, 48, False).translate((0, 0, 267.95))
                      + m3d.Manifold.cylinder(17.3, 3.0, 3.0, 32, False).translate((0, 0, 263.65)))

DRIVER_D = 7.0
bad_C = []
for a in COL_ANG:
    ax, ay = COL_R * math.cos(math.radians(a + V3_SCR_ROT)), COL_R * math.sin(math.radians(a + V3_SCR_ROT))
    corr = m3d.Manifold.cylinder(330.0, DRIVER_D / 2, DRIVER_D / 2, 48, False).translate((ax, ay, 92.2))
    hit = [(k, (corr ^ o).volume()) for k, o in UPM.items() if (corr ^ o).volume() > 1e-6]
    a_asm = (a + V3_SCR_ROT) % 360
    if hit:
        print(f"  ✗ 立柱 装配{a_asm:6.1f}° ({ax:6.2f},{ay:6.2f}): 通道被挡 —— "
              + ", ".join(f"{k} {v:.1f}mm³" for k, v in hit))
        bad_C.append(a_asm)
    else:
        print(f"  ✓ 立柱 装配{a_asm:6.1f}° ({ax:6.2f},{ay:6.2f}): Φ{DRIVER_D:g} 通道直通机顶, 无阻挡")

print("\n" + "=" * 78)
ok = not (bad_A or bad_B or bad_C)
print("结论:", "三段运动全部通过 ✓ 装得进去" if ok else
      f"★ A{len(bad_A)} / B{len(bad_B)} / C{len(bad_C)} 处受阻")
