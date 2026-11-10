"""把长时间采集按 30 s 窗算 1× (看漂移)。用法: python3 soak_win.py <tag 不含 _900> [rpm=900]"""
import sys, math, json, numpy as np
import sweep_v04 as W
tag = sys.argv[1]; r0 = float(sys.argv[2]) if len(sys.argv) > 2 else 900
ms, _, rpm, d, _ = W.S.load(f"{W.OUT}/{tag}_{int(r0)}.csv", "hfi_agl", ["ax", "ay", "az"])
t = ms / 1000; ar = np.abs(rpm); i = np.where(np.abs(ar - r0) < 0.05 * r0)[0]; t0 = t[i[0]] + 3; t1 = t[i[-1]] - 0.5
for a in np.arange(t0, t1 - 29, 30):
    m = (t >= a) & (t < a + 30); tt = t[m] - t[m].mean(); f0 = ar[m].mean() / 60; out = []
    for c in ("ax", "ay", "az"):
        y = d[c][m] - d[c][m].mean(); best = 0
        for f in f0 * np.linspace(.98, 1.02, 21):
            A = np.column_stack([np.cos(2*np.pi*f*tt), np.sin(2*np.pi*f*tt), tt]); x = np.linalg.lstsq(A, y, rcond=None)[0]; best = max(best, math.hypot(x[0], x[1]))
        out.append(best * W.ACC_MG)
    print("%5.0f s  ax %.2f ay %.2f az %.2f" % (a - t0, *out))
j = json.load(open(f"{W.OUT}/{tag}_{int(r0)}.json")); print("valid", j["valid"], "fault_samples", j["fault_samples"])
