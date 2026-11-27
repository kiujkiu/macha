"""V1.2 下罩 A 孔补块 sh_insert_v1_2 ×4 — 11-24 用户: 已打印的旧下罩 (三角块顶 Z5, 无圆台) 里塞一块, 让它变成新版 (A 孔处加厚 + 法兰螺母沉孔)。
「做一个能卡在这个三角区的, 厚度是3.6mm, 法兰螺母这个位置是一个8mm直径的通孔 … 要0配, 不要留缝隙」
补块 = 三角区 (x,y > P_N 角区, r < 墙内面) × Z TRI_T → TRI_T+3.6, 减去旧下罩实体 (两片斜筋 / 墙) 0 间隙, 中间 Φ8 通孔 (法兰螺母坐三角块顶)。
    cd v1.2/scripts && ../../.venv/bin/python sh_insert_v1_2.py
"""
import os, io, contextlib, math, json
os.environ['SH_BOSS'] = '0'                       # 旧下罩 (无圆台)
with contextlib.redirect_stdout(io.StringIO()):
    import build_v1_2 as B
    import rotor_b_v1_2 as RB
assert not B.SH_BOSS_ON
T = 3.6
Z0, Z1 = B.TRI_T, B.TRI_T + T                     # 5.0 → 8.6 (法兰螺母 Z5–8.7, 顶高出补块 0.1)
HOLE_D = 8.0
old = B.shroud_lo
PCS = []
for x, y in B.SH_M6:
    sx, sy = (1 if x > 0 else -1), (1 if y > 0 else -1)
    reg = B.common(B.gbox(min(sx * B.P_N, sx * 120), min(sy * B.P_N, sy * 120), Z0, max(sx * B.P_N, sx * 120), max(sy * B.P_N, sy * 120), Z1),
                   B.cyl(0, 0, 2 * B.SPIG_IN + 2, Z0 - 1, Z1 + 1)) if hasattr(B, 'common') else None
    if reg is None:
        reg = B.op(B.BRepAlgoAPI_Common, B.gbox(min(sx * B.P_N, sx * 120), min(sy * B.P_N, sy * 120), Z0, max(sx * B.P_N, sx * 120), max(sy * B.P_N, sy * 120), Z1),
                   B.cyl(0, 0, 2 * B.SPIG_IN + 2, Z0 - 1, Z1 + 1))
    p = B.clean(B.cut(reg, old, B.cyl(x, y, HOLE_D, Z0 - 1, Z1 + 1)))
    PCS.append(p)
V = [round(B.vol(p), 2) for p in PCS]
INFO = dict(t=T, z=(Z0, Z1), hole=HOLE_D, vol=V, bbox=[round(v, 2) for v in B.bbox(PCS[0])])
print(json.dumps(INFO, ensure_ascii=False))
assert max(V) - min(V) < 0.05 * max(V), V         # 4 角应一样
if __name__ == '__main__':
    RB.out('sh_insert_v1_2', PCS[0], color='#E69138')   # 放 45° 角的那块 (4 角同件); _print 底面 (Z5 面) 落床
    print('写出', RB.OUTD)
