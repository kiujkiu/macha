"""
MOS 管压块 mos_clamp_16x10x4p5 (2026-09-14)

用户: 参考 saddle_clamp_sq6, 把一颗 MOS 管 (长16 宽10 高4.5, TO-220) 锁到 M6 网格板上
(v4 网格板厚 13, M6 螺纹孔节距 25), 螺丝用 M6 大扁头 (头 Φ12.5 × 2.6)。

sq6 结构 = 倒 U 通槽 + 两侧低脚 (厚3) + 2×M6 @ 25。照搬放不下:
  孔距 25, 大扁头 Φ12.5 => 两颗头之间只剩 25 - 12.5 = 12.5,
  而 MOS 宽 10 + 间隙 0.4 + 两侧壁 2×3 = 16.4 -> 头压在侧壁上 (单边干涉 1.95)。
解法 (最简): 脚抬到与顶面齐平 = 底部带槽的平顶压块, 螺丝头坐顶面, 与槽不再冲突;
孔距仍是 25, 槽与孔之间的肉 = 12.5 - 3.25 - 5.2 = 4.05。

同日追加 (用户在俯视图上标注):
  1) +Y 长边外加挡板, 厚 2。我的理解: 全长 38 × 全高 7.3 (与顶面齐平), 封住槽 +Y 端 -> 盲槽;
     MOS 舌片端顶住挡板定位, 引脚端从 -Y 开口出。
  2) "这个宽度加长 1cm" (宽 14 -> 24), 三选项里用户选「槽跟着加深, 挡板仍 2 厚」:
     槽深 14 -> 24, 挡板 2 仍在最外, 开口面与孔位不动 (孔心距开口面 7) => 件宽 26。
     代价: MOS 只有 16 长, 顶住挡板时引脚端缩进开口 8, 引脚要从槽里穿出; 不顶挡板则 MOS 可在槽里前后调 8。
  3) (2026-09-15) 复核 FE 实算: 平顶块极刚, 0.2 过盈时两脚落不到板上, 夹紧力全靠拧螺丝 (手拧 M6 上千 N) 会压裂封装。
     用户选「过盈改 0, 加导热垫」: PRELOAD 0 => 槽高 4.5、件高 7.5, 两脚贴板; 垫厚待定 (PAD_T, 默认 0)。

坐标: X = 两孔连线 (横跨 MOS 宽度), Y = 槽方向 (MOS 长度, -Y 开口, +Y 挡板), Z 向上, 贴板底面 Z=0。
"""
import math
import struct
from pathlib import Path

import numpy as np
import manifold3d as m3d

# ===== 参数 =====
MOS_L, MOS_W, MOS_H = 16.0, 10.0, 4.5   # 用户给的 MOS 包络
SIDE_CLR    = 0.2     # 槽宽 单侧间隙
PRELOAD     = 0.0     # 过盈 = (MOS + 垫) 叠高 - 槽高; 用户选 0: 两脚贴板, 拧到底也压不坏封装
PAD_T       = 0.0     # MOS 下导热硅胶垫厚 (用户要加, 厚度待定); 垫时 PRELOAD 取垫允许的压缩量 (约垫厚 10-20%)
T_TOP       = 3.0     # 槽顶厚 (同 sq6 料厚)
PITCH       = 25.0    # 网格板 M6 孔节距
HOLE_D      = 6.5     # M6 通孔 (同 sq6)
END         = 6.5     # 孔心到 X 端面 (>= 头半径 6.25, 头整圈落在件上)
HOLE_Y_OPEN = 7.0     # 孔心到开口面 (原带宽 14 的一半, 加宽时保持不动)
CH_D        = 24.0    # 槽深 (开口面 -> 挡板内面); 用户加宽 1cm: 14 -> 24
BAFFLE_T    = 2.0     # +Y 端挡板厚 (用户指定): 全长全高, 封住槽一端

# 五金 / 板 (只用于校核)
HEAD_D, HEAD_T = 12.5, 2.6   # M6 大扁头 实测
PLATE_T  = 13.0              # v4 网格板厚
SQ6_WALL = 3.0               # sq6 侧壁厚 (论证低脚方案为何不行)

SEG = 96

CH_W   = MOS_W + 2 * SIDE_CLR       # 10.4
CH_H   = MOS_H + PAD_T - PRELOAD    # 4.5
H      = CH_H + T_TOP               # 7.5
HX     = PITCH / 2                  # 12.5
HALF_L = HX + END                   # 19
L      = 2 * HALF_L                 # 38
Y_OPEN = -HOLE_Y_OPEN               # -7  开口面 (孔心在 Y=0)
Y_BAF  = Y_OPEN + CH_D              # 17  挡板内面
Y_END  = Y_BAF + BAFFLE_T           # 19  挡板外面
DEPTH  = Y_END - Y_OPEN             # 26  件总宽 (沿 Y)
WEB    = HX - HOLE_D / 2 - CH_W / 2 # 4.05
MOS_Y0 = Y_BAF - MOS_L              # 1   MOS 顶住挡板时引脚端 Y
MOS_RECESS = MOS_Y0 - Y_OPEN        # 8   引脚端缩进开口 (负数 = 伸出)
MOS_CY = Y_BAF - MOS_L / 2          # 9   MOS 中心 Y (偏舌片侧)

# 低脚方案的干涉量 (头内缘 vs 侧壁外缘) —— 这就是做平顶的原因
LOWFOOT_CLASH = (CH_W / 2 + SQ6_WALL) - (HX - HEAD_D / 2)   # 1.95
assert LOWFOOT_CLASH > 0

assert CH_H > 0 and T_TOP > 0 and BAFFLE_T > 0
assert WEB >= 3.0, f"槽与孔之间肉太薄: {WEB}"
assert HX + HEAD_D / 2 <= HALF_L, "头超出 X 端面"
assert Y_OPEN + HEAD_D / 2 <= 0 <= Y_END - HEAD_D / 2, "头超出件的前/后端"

# ===== 建模 =====
body    = m3d.Manifold.cube((L, DEPTH, H), False).translate((-HALF_L, Y_OPEN, 0))
# 槽只从 -Y 开口, 止于挡板内面
channel = m3d.Manifold.cube((CH_W, CH_D + 1, CH_H + 1), False).translate((-CH_W / 2, Y_OPEN - 1, -1))
hole    = m3d.Manifold.cylinder(H + 2, HOLE_D / 2, HOLE_D / 2, SEG, False)

part = body - channel
for sx in (-1, 1):
    part = part - hole.translate((sx * HX, 0, -1))

# ===== 校核 =====
assert len(part.decompose()) == 1, "件不是一整块"

def inter_vol(a, b):
    return a.volume() - (a - b).volume()

hole_poly = SEG / 2 * math.sin(2 * math.pi / SEG) * (HOLE_D / 2) ** 2

# 1) MOS 从 -Y 开口推入顶住挡板: 只与槽顶重叠 (= 压紧量), 侧壁/挡板零干涉 —— 居中 / 贴一侧壁 都查
mos = m3d.Manifold.cube((MOS_W, MOS_L, MOS_H), False).translate((-MOS_W / 2, MOS_Y0, PAD_T))   # 坐在垫上
roof_len = min(Y_BAF, MOS_Y0 + MOS_L) - max(Y_OPEN, MOS_Y0)   # MOS 在槽顶下的长度
ov_expect = MOS_W * roof_len * PRELOAD
for dx in (0.0, SIDE_CLR - 1e-4, -(SIDE_CLR - 1e-4)):
    ov = inter_vol(mos.translate((dx, 0, 0)), part)
    assert abs(ov - ov_expect) < 1e-3, f"MOS 偏 {dx}: 重叠 {ov} != 压紧 {ov_expect}"

# 2) 挡板真的挡住: MOS 再往 +Y 推 PUSH -> 吃进挡板 PUSH × 宽 × 全高; 若引脚端在槽内, 槽顶重叠少一条 PUSH
PUSH = 0.1
ov_push = inter_vol(mos.translate((0, PUSH, 0)), part) - ov_expect
lost = PUSH * MOS_W * PRELOAD if MOS_Y0 > Y_OPEN else 0.0
assert abs(ov_push - (PUSH * MOS_W * MOS_H - lost)) < 1e-3, f"挡板没挡住: 多重叠 {ov_push}"

# 3) 盲槽: 槽高中部截面 = 外形 - 槽 (深 CH_D) - 2 孔; 挡板那条 (Y ∈ [Y_BAF, Y_END]) 全实心
a_mid = part.slice(CH_H / 2).area()
a_mid_expect = L * DEPTH - CH_W * CH_D - 2 * hole_poly
assert abs(a_mid - a_mid_expect) < 1e-3, f"槽高中部截面 {a_mid} != {a_mid_expect}"
strip = m3d.Manifold.cube((L, BAFFLE_T, H), False).translate((-HALF_L, Y_BAF, 0))
assert abs(inter_vol(strip, part) - L * BAFFLE_T * H) < 1e-3, "挡板不是全长全高实心"
# 槽确实开到 Y_OPEN、止于 Y_BAF
assert inter_vol(m3d.Manifold.cube((CH_W - 0.2, CH_D - 0.2, CH_H - 0.2), False)
                 .translate((-CH_W / 2 + 0.1, Y_OPEN + 0.1, 0.1)), part) < 1e-9, "槽里有料"

# 4) 大扁头坐顶面: 头与件零干涉; 头投影除了孔以外整圈落在顶面上
top = part.slice(H - 1e-3)
head = m3d.Manifold.cylinder(HEAD_T, HEAD_D / 2, HEAD_D / 2, SEG, False)
for sx in (-1, 1):
    assert inter_vol(head.translate((sx * HX, 0, H)), part) < 1e-9, "头与件干涉"
    disk = m3d.CrossSection.circle(HEAD_D / 2, SEG).translate((sx * HX, 0))
    unsup = (disk - top).area()
    assert abs(unsup - hole_poly) < 0.01 * hole_poly, f"头有悬空: {unsup} vs 孔 {hole_poly}"

# 5) 板上网格孔落在件底面投影里的 (两孔连线与网格同排)
covered = [(float(gx), float(gy)) for gx in HX + np.arange(-3, 3) * PITCH for gy in np.arange(-3, 4) * PITCH
           if -HALF_L < gx < HALF_L and Y_OPEN < gy < Y_END]

# 6) 理论体积
vol_theory = L * DEPTH * H - CH_W * CH_D * CH_H - 2 * hole_poly * H

# ===== 导出 STL =====
mesh  = part.to_mesh()
verts = np.asarray(mesh.vert_properties)[:, :3]
tris  = np.asarray(mesh.tri_verts)

out = Path(__file__).with_name("mos_clamp_16x10x4p5.stl")
with out.open("wb") as f:
    _hdr = f"mos_clamp 16x10x4.5 L{L:g} W{DEPTH:g} H{H:g} ch{CH_D:g} baffle{BAFFLE_T:g}".encode("ascii")
    f.write(_hdr.ljust(80, b" ")[:80])   # STL 头必须 <=80 字节并截断
    f.write(struct.pack("<I", len(tris)))
    for t in tris:
        v0, v1, v2 = verts[t[0]], verts[t[1]], verts[t[2]]
        n = np.cross(v1 - v0, v2 - v0)
        nl = float(np.linalg.norm(n))
        if nl > 0:
            n = n / nl
        f.write(struct.pack("<3f", *n))
        f.write(struct.pack("<3f", *v0))
        f.write(struct.pack("<3f", *v1))
        f.write(struct.pack("<3f", *v2))
        f.write(struct.pack("<H", 0))

expected = 84 + len(tris) * 50
assert out.stat().st_size == expected, \
    f"STL 大小不对: {out.stat().st_size} != {expected} (STL 头溢出?)"

vol = part.volume()
print(f"wrote {out}  ({len(tris)} triangles, {len(verts)} vertices)")
print(f"  bbox X: {verts[:,0].min():8.3f} .. {verts[:,0].max():8.3f}")
print(f"  bbox Y: {verts[:,1].min():8.3f} .. {verts[:,1].max():8.3f}")
print(f"  bbox Z: {verts[:,2].min():8.3f} .. {verts[:,2].max():8.3f}")
print(f"  volume: {vol:.2f} mm^3  (理论 {vol_theory:.2f}, 差 {abs(vol-vol_theory):.4f})   PLA 实心约 {vol*1.24e-3:.1f} g")
print(f"  外形 {L:g}×{DEPTH:g}×{H:g} (槽深 {CH_D:g} + 挡板 {BAFFLE_T:g}) / 盲槽 {CH_W:g}×{CH_H:g} "
      f"(MOS {MOS_W:g}×{MOS_H:g} + 垫 {PAD_T:g}, 单侧间隙 {SIDE_CLR:g}, 过盈 {PRELOAD:g})")
print(f"  2×Φ{HOLE_D:g} @ {PITCH:g} (孔心距开口面 {HOLE_Y_OPEN:g} / 距挡板外面 {Y_END:g}) / 槽-孔肉 {WEB:.2f} / 低脚方案头-壁干涉 {LOWFOOT_CLASH:.2f}")
print(f"  MOS 顶挡板: 引脚端 Y={MOS_Y0:g} (缩进开口 {MOS_RECESS:g}), 中心 Y={MOS_CY:g} / 重叠 = 压紧 {ov_expect:.2f} mm^3 (居中/贴壁一致) / "
      f"再推 {PUSH:g} 多吃 {ov_push:.2f}")
print(f"  挡板条全实心 {L:g}×{BAFFLE_T:g}×{H:g} / 槽内无料 / 大扁头坐顶面零干涉零悬空")
print(f"  底面投影内的网格孔 (件坐标): {covered}")
for Ls in (10, 12, 16, 20):
    eng = Ls - H
    prot = eng - PLATE_T
    tag = "穿出板底!" if prot > 0 else ("旋入偏少" if eng < 4.5 else "OK")
    print(f"  M6×{Ls}: 旋入 {eng:.1f}, 距板底 {-prot:.1f}  {tag}")
