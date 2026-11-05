"""
V1.0 动平衡四次法 (2026-11-05): 只用 5 Hz 振幅, 不用任何相位基准。
================================================================
背景: 电角度 ÷7 的零位各次不一致 (谐波指纹测得 δ 非 51.43° 整数倍), 相位解算不可靠 → 改振幅法。
模型: A_i = g·|U + T_i|, 基线 A_0 = g·|U|。未知 U (复数, g·mm) 和 g; 同一试重放 ≥3 个孔即可解。
振幅: 对 ms 列做时间轴最小二乘, 在实测平均机械频率上拟合正余弦 (频率由 rpm_est 均值, 再 ±2% 搜峰)。
孔: 俯视逆时针编号 1~8, 角度 = 22.5 + 45·(n-1)。

用法:
  python3 solve_four_run.py --g 4.8 --base f1.csv f2.csv --hole 1 h1.csv --hole 4 h4.csv --hole 6 h6.csv
  python3 solve_four_run.py --selftest
"""
import argparse
import cmath
import math
import sys

import numpy as np

import solve_single_plane as S

R = 82.5
CH = ["ax", "ay", "az"]
LSB_MG = 0.2441


def hole_deg(n):
    return 22.5 + 45.0 * (n - 1)


def amps(path, rpm0=300.0):
    ms, _, rpm, d, foot = S.load(path, "hfi_agl", CH)
    t = ms / 1000.0
    m = np.abs(np.abs(rpm) - rpm0) < 0.1 * rpm0
    i = np.where(m)[0]
    m[: i[0] + int(0.7 * 3000)] = False                # 跳过刚到速的 ~3 s
    t = t[m] - t[m].mean()
    f0 = np.abs(rpm[m]).mean() / 60
    bad = [x for x in foot if "valid=0" in x]
    out = {}
    for c in CH:
        y = d[c][m] - d[c][m].mean()
        best = 0.0
        for f in f0 * np.linspace(0.98, 1.02, 41):
            A = np.column_stack([np.cos(2 * np.pi * f * t), np.sin(2 * np.pi * f * t), t])
            x = np.linalg.lstsq(A, y, rcond=None)[0]
            best = max(best, math.hypot(x[0], x[1]))
        out[c] = best * LSB_MG
    return out, bool(bad)


def fit(a0, trials, g_w):
    """a0 基线振幅; trials [(复数试重 T, 振幅)]。返回 U, 灵敏度 k (振幅/(g·mm)), 相对残差。"""
    rs = np.arange(10, 4000, 5.0)
    an = np.radians(np.arange(0, 360, 1.0))
    Ug = rs[:, None] * np.exp(1j * an[None, :])
    T = np.array([t for t, _ in trials])
    A = np.array([a for _, a in trials])
    base = np.abs(Ug)
    pred = np.abs(Ug[..., None] + T)                   # (r, a, n)
    allp = np.concatenate([base[..., None], pred], axis=2)
    alla = np.r_[a0, A]
    k = (allp * alla).sum(2) / (allp ** 2).sum(2)      # 每个 U 的最优增益
    e = ((k[..., None] * allp - alla) ** 2).sum(2)
    i = np.unravel_index(e.argmin(), e.shape)
    return Ug[i], k[i], math.sqrt(e[i] / (alla ** 2).sum())


def report(base, holes, g):
    print(f"试重 {g} g @ r{R} = {g * R:.0f} g·mm")
    for c in CH:
        a0 = float(np.mean([b[c] for b in base]))
        tr = [(cmath.rect(g * R, math.radians(hole_deg(n))), float(np.mean([x[c] for x in v]))) for n, v in holes.items()]
        U, k, err = fit(a0, tr, g)
        W = -U
        ang = math.degrees(cmath.phase(W)) % 360
        h0, w0, h1, w1 = S.split(abs(W), ang)
        n0, n1 = int((h0 - 22.5) / 45) + 1, int((h1 - 22.5) / 45) + 1
        print(f"  {c}: 基线 {a0:.3f} mg, 试重 " + " ".join(f"{n}号 {t[1]:.3f}" for n, t in zip(holes, tr)) +
              f" | 配重 {abs(W):.0f} g·mm ∠{ang:.0f}° = {abs(W) / R:.2f} g → {n0}号 {w0:.2f} g + {n1}号 {w1:.2f} g  (拟合残差 {err * 100:.0f}%)")


def selftest():
    U = cmath.rect(420.0, math.radians(300))
    k = 0.004
    a0 = k * abs(U)
    tr = [(cmath.rect(396, math.radians(hole_deg(n))), k * abs(U + cmath.rect(396, math.radians(hole_deg(n))))) for n in (1, 4, 6)]
    Uf, kf, e = fit(a0, tr, 4.8)
    print(f"真值 420∠300, 解 {abs(Uf):.0f}∠{math.degrees(cmath.phase(Uf)) % 360:.0f}, 残差 {e:.4f}")
    assert abs(abs(Uf) - 420) < 15 and abs(math.degrees(cmath.phase(Uf)) % 360 - 300) < 3
    rng = np.random.default_rng(0)
    ee = []
    for _ in range(40):
        n = lambda v: v * (1 + rng.normal(0, 0.03))
        Uf, _, _ = fit(n(a0), [(t, n(a)) for t, a in tr], 4.8)
        ee.append((abs(Uf - U)))
    print(f"振幅 3% 噪声下, U 误差中位 {np.median(ee):.0f} g·mm, 最大 {max(ee):.0f}")
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--g", type=float)
    ap.add_argument("--base", nargs="+")
    ap.add_argument("--hole", nargs="+", action="append", help="孔号 csv [csv...]")
    ap.add_argument("--rpm", type=float, default=300.0)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    ld = lambda p: amps(p, a.rpm)
    base = []
    for p in a.base:
        v, bad = ld(p)
        base.append(v)
        print(f"{p.split('/')[-1]}: " + " ".join(f"{c}={v[c]:.3f}" for c in CH) + ("  ⚠ valid=0" if bad else ""))
    holes = {}
    for h in a.hole or []:
        holes[int(h[0])] = []
        for p in h[1:]:
            v, bad = ld(p)
            holes[int(h[0])].append(v)
            print(f"{h[0]}号 {p.split('/')[-1]}: " + " ".join(f"{c}={v[c]:.3f}" for c in CH) + ("  ⚠ valid=0" if bad else ""))
    if len(holes) >= 3:
        report(base, holes, a.g)


if __name__ == "__main__":
    sys.exit(main())
