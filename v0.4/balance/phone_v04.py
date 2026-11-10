"""
V0.4 顶部振动: phyphox (手机放顶部轴承架) 远程访问 → 1× 振幅 (2026-11-10)。
phyphox「加速度 (含 g)」实验, ⋮ → 允许远程访问; 默认网址 http://10.10.21.228 (用 --url 改)。

用法:
  python3 phone_v04.py run <tag> [--rpm 900] [--step 600] [--secs 35]   手机开始录 → 调 sweep_v04 跑一档 → 停录 → 存 CSV + 算 1×
  python3 phone_v04.py tap <tag> [--secs 40]                               电机不转, 录 N 秒, 用户敲顶部 → 各次敲击衰减主频
  python3 phone_v04.py amp <tag> [--rpm 900]                               对已存 CSV 重算
输出: _cap/hss/bal/<tag>_phone.csv (t, ax, ay, az m/s²)
1× 振幅: 稳速段 (手机时间 15 s .. secs-8 s) 在转频 ±2% 内搜峰做正余弦最小二乘, 单位 m/s² 与 mg 都给。
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "/mnt/d/claude_workspace/mtr/APL+LDR_V1.1/tools/_cap/hss/bal"
G = 9.80665


def get(url, path):
    with urllib.request.urlopen(url + path, timeout=10) as r:
        return json.loads(r.read().decode())


def fetch(url):
    j = get(url, "/get?acc_time=full&accX=full&accY=full&accZ=full")
    b = j["buffer"]
    n = min(len(b[k]["buffer"]) for k in ("acc_time", "accX", "accY", "accZ"))
    return np.array([[b[k]["buffer"][i] for k in ("acc_time", "accX", "accY", "accZ")] for i in range(n)], float)


def save(tag, a):
    p = os.path.join(OUT, tag + "_phone.csv")
    np.savetxt(p, a, delimiter=",", header="t,ax,ay,az", comments="", fmt="%.6f")
    return p


def load(tag):
    return np.loadtxt(os.path.join(OUT, tag + "_phone.csv"), delimiter=",", skiprows=1)


def amp1x(a, rpm, t0, t1):
    t = a[:, 0]
    m = (t >= t0) & (t <= t1)
    tt = t[m] - t[m].mean()
    f0 = rpm / 60.0
    out = {}
    for k, c in enumerate(("ax", "ay", "az")):
        y = a[m, k + 1] - a[m, k + 1].mean()
        best = (0, f0)
        for f in f0 * np.linspace(0.98, 1.02, 41):
            A = np.column_stack([np.cos(2 * np.pi * f * tt), np.sin(2 * np.pi * f * tt), tt])
            x = np.linalg.lstsq(A, y, rcond=None)[0]
            best = max(best, (math.hypot(x[0], x[1]), f))
        out[c] = best[0]
        out["f_" + c] = best[1]
    nf = []
    for k in range(2):
        y = a[m, k + 1] - a[m, k + 1].mean()
        for r in (0.63, 1.37):
            A = np.column_stack([np.cos(2 * np.pi * r * f0 * tt), np.sin(2 * np.pi * r * f0 * tt), tt])
            x = np.linalg.lstsq(A, y, rcond=None)[0]
            nf.append(math.hypot(x[0], x[1]))
    out["nf"] = float(np.sqrt(np.mean(np.square(nf))))
    out["fs"] = float(m.sum() / (t1 - t0))
    return out


def show(tag, o):
    print("%s 顶部 1×  ax %.3f ay %.3f az %.3f m/s²  (= %.0f / %.0f / %.0f mg; 噪底 %.3f; 频率 %.2f Hz; 采样 %.0f Hz)"
          % (tag, o["ax"], o["ay"], o["az"], o["ax"] / G * 1000, o["ay"] / G * 1000, o["az"] / G * 1000, o["nf"], o["f_ax"], o["fs"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "tap", "amp"])
    ap.add_argument("tag")
    ap.add_argument("--url", default="http://10.10.21.228")
    ap.add_argument("--rpm", type=int, default=900)
    ap.add_argument("--step", type=int, default=600)
    ap.add_argument("--secs", type=float, default=35)
    ap.add_argument("--max", type=int, default=900, help="限速 (传给 sweep_v04)")
    ap.add_argument("--lim", type=float, default=30, help="底部 1× 门限 mg")
    a = ap.parse_args()
    if a.cmd == "amp":
        show(a.tag, amp1x(load(a.tag), a.rpm, 15, a.secs - 8)); return
    get(a.url, "/control?cmd=clear"); time.sleep(0.5)
    get(a.url, "/control?cmd=start")
    if a.cmd == "run":
        r = subprocess.run([sys.executable, os.path.join(HERE, "sweep_v04.py"), str(a.rpm), "--step", str(a.step), "--secs", str(a.secs),
                            "--prefix", a.tag, "--lim", str(a.lim), "--max", str(a.max)], capture_output=True, text=True)
        print("\n".join(x for x in r.stdout.splitlines() if "rpm" in x and "扫速" not in x))
        time.sleep(1)
    else:
        print(f"手机在录, {a.secs:.0f} s 内敲顶部 (两个水平方向各 3 下, 间隔 5 s)", flush=True)
        time.sleep(a.secs)
    get(a.url, "/control?cmd=stop")
    d = fetch(a.url)
    print("手机样本", len(d), "时长 %.1f s" % (d[-1, 0] - d[0, 0]) if len(d) else "")
    save(a.tag, d)
    if a.cmd == "run":
        show(a.tag, amp1x(d, a.rpm, 15, a.secs - 8))
    else:
        t = d[:, 0]
        for k, c in enumerate(("ax", "ay")):
            y = d[:, k + 1] - np.median(d[:, k + 1]); env = np.abs(y)
            taps, last = [], -9
            for i in np.where(env > np.percentile(env, 99.8) * 0.5)[0]:
                if t[i] - last > 3: taps.append(i); last = t[i]
            res = []
            for i in taps:
                m = (t > t[i] + 0.15) & (t < t[i] + 2.5); tt = t[m] - t[m][0]; yy = y[m] - y[m].mean()
                if len(tt) < 50: continue
                fr = np.arange(3, 45, 0.05)
                P = np.abs(np.exp(-2j * np.pi * fr[:, None] * tt[None, :]) @ (yy * np.hanning(len(yy))))
                res.append((round(float(t[i]), 1), round(float(fr[P.argmax()]), 2)))
            print(c, "敲击 (时刻 s, 衰减主频 Hz):", res)


if __name__ == "__main__":
    main()
