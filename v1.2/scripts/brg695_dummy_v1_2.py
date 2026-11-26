"""695ZZ 模拟件 (打印试装, 11-26 用户「轴承还没到, 模拟一个」): 外 Φ13 × 内 Φ5 × 4, 尺寸 = 实物公称 (0 间隙, 与堵头座同规矩), 外/内边倒角 0.2。
    cd v1.2/scripts && ../../.venv/bin/python brg695_dummy_v1_2.py   → v1.2/顶部连接/零件/brg695_dummy_print.stl
"""
import io, contextlib, struct, numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    import build_v1_2 as B
from mf3_v1_2 import mesh
c = 0.2; R, r, h = 6.5, 2.5, 4.0
s = B.revol([(r + c, 0), (R - c, 0), (R, c), (R, h - c), (R - c, h), (r + c, h), (r, h - c), (r, c)])
V, T = mesh(s, 0.01); f = B.V12 / '顶部连接' / '零件' / 'brg695_dummy_print.stl'
with open(f, 'wb') as fh:
    fh.write(b'brg695_dummy'.ljust(80, b' ') + struct.pack('<I', len(T)))
    for t in T:
        q = V[t]; n = np.cross(q[1] - q[0], q[2] - q[0]); n = n / (np.linalg.norm(n) + 1e-12); fh.write(struct.pack('<12fH', *n, *q.ravel(), 0))
print(f, len(T), round(B.vol(s), 1))
