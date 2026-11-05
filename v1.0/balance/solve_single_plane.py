"""
V1.0 无屏单平面动平衡解算 (2026-11-05, 影响系数法)
====================================================
输入: 基线 CSV (可多次) + 试重 CSV (可多次)。CSV 需含 1 kHz 连续样本:
  电角度列 (--agl, 默认 hfi_agl = S16Agl 原始 0..65535, 回绕) + IMU 通道列 (--ch, 默认 ax ay az gx gy gz)。
做法: 零位取起转前最后静止点的绝对 θe (判极已完成; 首行可能是空闲旧值), 解绕 ÷ 极对数 = 机械角, 上电前必须对标记;
      时间轴用 ms 列 (HSS 实测可能 ~570 Hz 不等间隔); 只取 rpm_est 稳定段; 每通道在机械角上最小二乘拟合 1× 复幅值 V (与时间、转速抖动无关);
      H = (V_trial - V_base) / T;  配重 W = -Σ conj(H)·V_base / Σ|H|²  (多通道最小二乘)。
输出: 需要的 g·mm 与角度, 拆到相邻两个 R82.5 孔的克数; 重复性检查 (含 51.43° 扇区错 / 25.7° 翻极提示)。

角度约定: 试重孔角度 --trial-deg 就是 CAD 世界角 (孔 22.5+45k), 输出角度同一坐标。转向 --dir (+1 = 机械角随 CAD 角增加)。

用法:
  python3 solve_single_plane.py --base b1.csv b2.csv --trial t1.csv --trial-g 2.1 --trial-deg 247.5
  python3 solve_single_plane.py --selftest
"""
import argparse
import cmath
import csv
import math
import re
import sys

import numpy as np

R_HOLE = 82.5
HOLES = [22.5 + 45 * k for k in range(8)]
SECTOR = 360.0 / 7


def load(path, agl, chans):
    """读 hss_bal.py 的 CSV: 跳过 # 报告行; 返回 ms, 电角度, rpm_est, 通道, 报告行。"""
    with open(path, newline="") as f:
        lines = f.read().splitlines()
    foot = [x for x in lines if x.startswith("#")]
    rows = list(csv.DictReader(x for x in lines if not x.startswith("#")))
    if not rows:
        raise SystemExit(f"{path}: 空文件")
    miss = [c for c in ["ms", "rpm_est", agl] + chans if c not in rows[0]]
    if miss:
        raise SystemExit(f"{path}: 缺列 {miss}, 现有 {list(rows[0])}")
    ms = np.array([float(r["ms"]) for r in rows])
    keep = np.r_[True, np.diff(ms) > 0]                # HSS 重复样本去掉
    g = lambda c: np.array([float(r[c]) for r in rows])[keep]
    return ms[keep], g(agl), g("rpm_est"), {c: g(c) for c in chans}, foot


def anchor(rpm_est, ms, start_rpm=20.0, back_ms=30.0):
    """起转前最后的静止点: 判极已完成, 角度才可信 (首行可能是空闲时的旧值, 不能当零位)。"""
    run = np.abs(rpm_est) > start_rpm
    i = next((k for k in range(run.size - 100) if run[k:k + 100].mean() > 0.9), None)
    if i is None:
        raise SystemExit("找不到起转点")
    return int(np.searchsorted(ms, ms[i] - back_ms))


def mech_angle(agl, i0, pp, full=65536.0):
    """从 i0 起解绕电角度; 绝对 θe0 折到 ±180° (扇区中心=0), ÷pp = 机械角 (rad)。"""
    e = np.unwrap(agl[i0:] * (2 * np.pi / full))
    e0 = (e[0] + np.pi) % (2 * np.pi) - np.pi
    return (e - e[0] + e0) / pp, math.degrees(e0)


def phasors(path, a):
    ms, agl, rpm_est, d, foot = load(path, a.agl, a.ch)
    for x in foot:
        if "valid" in x and not re.search(r"valid\D{0,3}1", x):
            print(f"  ⚠ {path}: 采集报告 valid≠1, 这次作废重测: {x[:160]}")
    dt = np.diff(ms)
    i0 = anchor(rpm_est, ms)
    th, e0 = mech_angle(agl, i0, a.pp)
    t_s = (ms[i0:] - ms[i0]) / 1000.0
    m = (np.abs(np.abs(rpm_est[i0:]) - a.rpm) < a.rpm_tol) & (t_s > a.skip)
    if t_s[m].size < 2 or t_s[m][-1] - t_s[m][0] < 5:
        raise SystemExit(f"{path}: 稳速段不足 5 s")
    if abs(e0) > 120:
        print(f"  ⚠ {path}: 起转 θe={e0:.0f}°, 离扇区边界太近, 手动对位可能落到邻扇区")
    t = th[m] * a.dir
    turns = abs(t[-1] - t[0]) / (2 * np.pi)
    # 时间轴用 ms 列 (HSS 不等间隔); 机械角上拟合, 转速抖动不影响
    A = np.column_stack([np.cos(t), np.sin(t), np.ones_like(t), t_s[m] - t_s[m].mean()])
    out = {}
    for c in a.ch:
        x = np.linalg.lstsq(A, d[c][i0:][m], rcond=None)[0]
        res = d[c][i0:][m] - A @ x
        out[c] = complex(x[0], -x[1])                # s(t)=Re(V e^{jθ}) → V = a - j b
        out[c + "_noise"] = float(res.std() * math.sqrt(2 / max(turns * 20, 1)))   # 样本相关, 保守按每圈 20 个独立点
    rate = m.sum() / (t_s[m][-1] - t_s[m][0])
    print(f"  {path}: θe0 {e0:+.0f}°, 稳速 {t_s[m][-1] - t_s[m][0]:.1f} s / {turns:.0f} 圈, {np.abs(rpm_est[i0:][m]).mean():.1f}"
          f"±{rpm_est[i0:][m].std():.1f} rpm, {rate:.0f} Hz, 最大间隔 {dt.max():.0f} ms  " +
          "  ".join(f"{c}={abs(out[c]):.4g}∠{math.degrees(cmath.phase(out[c])):.0f}°" for c in a.ch))
    if dt.max() >= 14:
        print(f"  ⚠ {path}: 间隔 ≥14 ms, 300 rpm 下电角度解绕不安全, 重测")
    return out


def mean_runs(runs, a, tag):
    v = {c: np.mean([r[c] for r in runs]) for c in a.ch}
    if len(runs) > 1:
        print(f"  {tag} 重复性:")
        for c in a.ch:
            vs = [r[c] for r in runs]
            big = abs(v[c]) > 3 * runs[0][c + "_noise"]
            dp = max(abs(math.degrees(cmath.phase(x / vs[0]))) for x in vs)
            da = (max(map(abs, vs)) - min(map(abs, vs))) / max(abs(v[c]), 1e-12) * 100
            note = ""
            if big and dp > 15:
                n = dp / SECTOR
                note = (" ⚠ 接近 51.43° 整数倍: 扇区错" if abs(n - round(n)) < 0.15 and round(n) >= 1 else
                        " ⚠ 接近 25.7°: 疑翻极" if abs(dp - SECTOR / 2) < 6 else " ⚠ 相位不重复")
            print(f"    {c}: 幅值差 {da:.0f}%  相位差 {dp:.0f}°{note if big else '  (信号≈噪声, 不计)'}")
    return v


def split(u_gmm, ang):
    """矢量 (g·mm @ ang) → 相邻两孔克数。"""
    a = ang % 360
    i = int(((a - 22.5) % 360) // 45)
    h0, h1 = HOLES[i], HOLES[(i + 1) % 8]
    M = np.array([[math.cos(math.radians(h0)), math.cos(math.radians(h1))],
                  [math.sin(math.radians(h0)), math.sin(math.radians(h1))]]) * R_HOLE
    w = np.linalg.solve(M, [u_gmm * math.cos(math.radians(a)), u_gmm * math.sin(math.radians(a))])
    return h0, w[0], h1, w[1]


def solve(vb, vt, T, chans):
    """T = 试重复数 (g·mm∠角)。返回 W (复数 g·mm, 机械角系) 及每通道 H。"""
    H = {c: (vt[c] - vb[c]) / T for c in chans}
    num = sum(H[c].conjugate() * vb[c] for c in chans)
    den = sum(abs(H[c]) ** 2 for c in chans)
    return -num / den, H


def report(vb, vt, a):
    T = cmath.rect(a.trial_g * R_HOLE, math.radians(a.trial_deg))
    # 通道按试重变化量 / 噪声 筛选; 量纲不同 (g, dps) 要先归一化到噪声
    use = [c for c in a.ch if abs(vt[c] - vb[c]) > 5 * a.noise[c]]
    print(f"\n可用通道 (试重变化 > 5×噪声): {use or '无'}")
    if not use:
        raise SystemExit("试重信号不够: 加大试重或提高转速, 或换更软的支撑。")
    vbn = {c: vb[c] / a.noise[c] for c in use}
    vtn = {c: vt[c] / a.noise[c] for c in use}
    W, H = solve(vbn, vtn, T, use)
    for c in use:
        chg = abs(vt[c] - vb[c]) / max(abs(vb[c]), 1e-12) * 100
        Wc = -vbn[c] / H[c]
        print(f"  {c}: 试重改变 {chg:.0f}% (建议 ≥30%);  单通道解 {abs(Wc):.0f} g·mm ∠{math.degrees(cmath.phase(Wc)) % 360:.0f}°")
    u, ang = abs(W), math.degrees(cmath.phase(W)) % 360
    print(f"\n配重 (试重取下后): {u:.0f} g·mm ∠{ang:.0f}°  = r{R_HOLE} 处 {u / R_HOLE:.2f} g")
    h0, w0, h1, w1 = split(u, ang)
    print(f"  拆孔: {h0:g}° {w0:.2f} g + {h1:g}° {w1:.2f} g   (留着试重时要再减去试重, 这里按取下算)")
    print(f"  当前转子不平衡估计: {u:.0f} g·mm ∠{(ang + 180) % 360:.0f}°;  目标 ≤32 g·mm (G6.3@900 rpm, 472 g)")
    return u, ang


def selftest():
    rng = np.random.default_rng(1)
    fs, pp, rpm = 1000.0, 7, 300.0
    U = cmath.rect(180.0, math.radians(97))            # 真不平衡
    Hs = {"ax": cmath.rect(2e-5, 1.1), "gy": cmath.rect(3e-3, -0.6)}
    z0 = 0.31
    import tempfile, os
    d = tempfile.mkdtemp()

    def make(name, extra, sector=0):
        n = 34000
        w = np.minimum(np.arange(n) / 3000.0, 1) * rpm / 60 * 2 * np.pi * (1 + 0.02 * np.sin(np.arange(n) / 700))
        w[:1000] = 0                                    # 1 s 静止
        th = np.cumsum(w) / fs + sector * 2 * np.pi / pp + z0 / pp
        p = os.path.join(d, name)
        rpmv = np.abs(w) * 60 / 2 / np.pi
        with open(p, "w", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(["ms", "state", "rpm_est", "src", "hfi_agl", "ax", "gy"])
            i = 0
            while i < n:
                v = {c: (Hs[c] * (U + extra) * cmath.exp(1j * th[i])).real for c in Hs}
                old = 12345 if i < 500 else (th[i] * pp) / (2 * np.pi) * 65536 % 65536   # 前 0.5 s 空闲旧值
                wr.writerow([i, 3, rpmv[i], 1, old, v["ax"] + rng.normal(0, 5e-3), v["gy"] + rng.normal(0, 0.3)])
                i += int(rng.choice([1, 2, 3], p=[.3, .5, .2]))     # 不等间隔 ~570 Hz
            f.write("# report valid=1\n")
        return p
    T = cmath.rect(2.1 * R_HOLE, math.radians(247.5))
    a = argparse.Namespace(agl="hfi_agl", ch=["ax", "gy"], pp=pp, fs=fs, rpm=rpm, rpm_tol=30, skip=4.0, dir=1,
                           trial_g=2.1, trial_deg=247.5)
    vb = mean_runs([phasors(make("b1.csv", 0), a), phasors(make("b2.csv", 0), a)], a, "基线")
    r = phasors(make("t1.csv", T), a)
    a.noise = {c: r[c + "_noise"] for c in a.ch}
    vt = {c: r[c] for c in a.ch}
    u, ang = report(vb, vt, a)
    err_u, err_a = abs(u - 180) / 180, abs((ang - 277 + 180) % 360 - 180)
    print(f"\nselftest: 真值 180 g·mm ∠277° (不平衡 ∠97° 的反向); 误差 {err_u * 100:.1f}% / {err_a:.1f}°")
    assert err_u < 0.1 and err_a < 5
    print("\n故意把一次基线摆到邻扇区 (应报相位差 ≈51.4°):")
    mean_runs([phasors(make("b3.csv", 0), a), phasors(make("b4.csv", 0, sector=1), a)], a, "基线")
    w = split(180, 277)
    assert w[0] == 247.5 and w[2] == 292.5 and w[1] > 0 and w[3] > 0
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", nargs="+")
    ap.add_argument("--trial", nargs="+")
    ap.add_argument("--trial-g", type=float)
    ap.add_argument("--trial-deg", type=float)
    ap.add_argument("--agl", default="hfi_agl")
    ap.add_argument("--ch", nargs="+", default=["ax", "ay", "az", "gx", "gy", "gz"])
    ap.add_argument("--pp", type=int, default=7)
    ap.add_argument("--fs", type=float, default=1000.0)
    ap.add_argument("--rpm", type=float, default=300.0)
    ap.add_argument("--rpm-tol", type=float, default=30.0)
    ap.add_argument("--skip", type=float, default=4.0, help="起转后跳过秒数")
    ap.add_argument("--dir", type=int, default=1, choices=(1, -1))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.base and a.trial and a.trial_g and a.trial_deg is not None):
        ap.error("需要 --base --trial --trial-g --trial-deg")
    print("基线:")
    rb = [phasors(p, a) for p in a.base]
    vb = mean_runs(rb, a, "基线")
    print("试重:")
    rt = [phasors(p, a) for p in a.trial]
    vt = mean_runs(rt, a, "试重")
    a.noise = {c: max(r[c + "_noise"] for r in rb + rt) for c in a.ch}
    report(vb, vt, a)


if __name__ == "__main__":
    sys.exit(main())
