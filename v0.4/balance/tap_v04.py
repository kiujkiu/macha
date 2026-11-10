"""
V0.4 敲击测试 (2026-11-09): 电机不转, HSS 采电机板 IMU, 用户敲机器, 看自由衰减的谱峰 = 整机/支撑模态频率。
不写任何电机命令 (只确认空闲后读)。输出 _cap/hss/bal/<tag>.csv (ms,ax,ay,az,gx,gy,gz) 和谱峰。

用法: python3 tap_v04.py <tag> [秒=20]
"""
import os
import struct
import subprocess
import sys

import numpy as np

HSSDIR = "/mnt/d/claude_workspace/mtr/APL+LDR_V1.1/tools/hss"
sys.path.insert(0, os.path.join(HSSDIR, "..", "acc"))
import jl  # noqa: E402

OUT = os.path.join(HSSDIR, "..", "_cap", "hss", "bal")
tag = sys.argv[1]
secs = float(sys.argv[2]) if len(sys.argv) > 2 else 20.0
fb = os.path.abspath(os.path.join(OUT, tag + ".bin"))


def wp(p):
    return subprocess.run(["wslpath", "-w", p], capture_output=True, text=True).stdout.strip()


s = jl.snap()
if s["state"] != 0 or abs(s["rpm_est"]) > 1:
    sys.exit("电机不在空闲, 不采")
A_RUN, A_IMU = jl.A["RunDbg"], jl.A["ImuDat"] + 12
BLK = [(A_RUN, 4), (A_IMU, 16)]
SS = 4 + 4 + 16
print(f"采 {secs:.0f} s, 开始敲 (第 2 s 后)", flush=True)
r = subprocess.run(["cmd.exe", "/c", "py", "-3", wp(os.path.join(HSSDIR, "hss_step_win.py")), wp(fb), str(secs), "1000", ""]
                   + ["%X:%d" % b for b in BLK], cwd="/mnt/c", capture_output=True, timeout=secs + 60)
d = open(fb, "rb").read()
n = len(d) // SS
ms = np.array([struct.unpack_from("<I", d, i * SS + 4)[0] for i in range(n)], float)
raw = np.array([struct.unpack_from("<7h", d, i * SS + 8)[1:7] for i in range(n)], float)
keep = np.r_[True, np.diff(ms) > 0]
ms, raw = ms[keep], raw[keep]
with open(os.path.join(OUT, tag + ".csv"), "w") as f:
    f.write("ms,ax,ay,az,gx,gy,gz\n")
    for m_, x in zip(ms, raw):
        f.write("%d,%d,%d,%d,%d,%d,%d\n" % ((m_,) + tuple(x)))
t = (ms - ms[0]) / 1000
fr = np.arange(1.0, 40.0, 0.05)
print(f"样本 {len(ms)} ({len(ms)/t[-1]:.0f} Hz)")
for k, c in enumerate(["ax", "ay", "az"]):
    y = raw[:, k] - raw[:, k].mean()
    P = np.abs(np.exp(-2j * np.pi * fr[:, None] * t[None, :]) @ y)
    top = []
    for j in np.argsort(P)[::-1]:
        if all(abs(fr[j] - f0) > 0.8 for f0, _ in top):
            top.append((fr[j], P[j]))
        if len(top) == 4:
            break
    pk = P.max()
    print(c, "  峰 Hz: " + ", ".join(f"{f0:.2f} ({p / pk:.2f})" for f0, p in top), "  峰峰 %.1f mg" % (np.ptp(y) * 1000 / 4096))
