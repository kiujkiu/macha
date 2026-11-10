"""
V0.4 带屏 升速扫频 (2026-11-09)。每档调一次 mtr 的 hss_bal.py 采集, 算 1× 振幅, 过门限就停, 不再升速。

限速: hss_bal.py 源码里 RPM_MAX = 300 (指令限幅也写进固件 RunCfg.rpm_max)。本脚本运行时把它替换成
       --max (默认 900, 用户 11-09 批准) 再执行, 不改 hss_bal.py 文件本身。
门限 (每档跑完判, 档内不能中途打断, 所以档距要小):
  · 采集无效 (故障 / 翻极 / 反转 / 末态不空闲) → 停
  · 任一加计 1× > --lim mg (默认 10)                      → 停
  · ax 或 ay 比上一档涨 > --jump 倍 (默认 4; 上一档 < 0.2 mg 时不判, 噪底附近比值没意义) → 停
  · 力矩限幅命中 d_tq_hit > 0 只报警 (含义待电机窗口确认)
输出: 每档一行 (加计 ax/ay/az mg, 陀螺 gx/gy dps 的 1×, 相对上档比值 vs ω² 比值), 汇总写 <tag 前缀>_summary.json。

用法:
  python3 sweep_v04.py 250 300 350 400 450 500 550 600 --prefix v04_sw
  python3 sweep_v04.py 250 600 50 --range --prefix v04_sw     (起 止 步)
"""
import argparse
import json
import math
import os
import subprocess
import sys

import numpy as np

HSS = "/mnt/d/claude_workspace/mtr/APL+LDR_V1.1/tools/hss/hss_bal.py"
OUT = "/mnt/d/claude_workspace/mtr/APL+LDR_V1.1/tools/_cap/hss/bal"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "v1.0", "balance"))
import solve_single_plane as S  # noqa: E402

ACC_MG = 1000.0 / 4096          # LSB → mg
GYR_DPS = 1.0 / 16              # LSB → dps
CH = ["ax", "ay", "az", "gx", "gy"]


def run_capture(tag, rpm, secs, rmax, step=0):
    src = open(HSS, encoding="utf-8").read()
    assert "RPM_MAX = 300" in src and "abs(rpm) <= RPM_MAX" in src, "hss_bal.py 改过了, 先核对限速写法"
    src = src.replace("RPM_MAX = 300", f"RPM_MAX = {rmax}")
    if step:   # 两段起转: 1 s 指令 step, 5 s 再给目标 (11-10: 一口气升到 900 时在 ~715 rpm 偶发 HFI 发散)
        old = "'1.00:%X:%X:2' % (jl.A['RunCmd'], rpm & 0xFFFF)"
        assert old in src, "hss_bal.py 起转事件写法变了"
        src = src.replace(old, f"'1.00:%X:%X:2' % (jl.A['RunCmd'], {int(step)} & 0xFFFF), '5.00:%X:%X:2' % (jl.A['RunCmd'], rpm & 0xFFFF)")
    boot = ("import sys; sys.argv=[{f!r},{t!r},{r!r},{s!r}]; "
            "exec(compile(open('/dev/stdin').read(), {f!r}, 'exec'), {{'__file__': {f!r}, '__name__': '__main__'}})"
            ).format(f=HSS, t=tag, r=str(rpm), s=str(secs))
    p = subprocess.run([sys.executable, "-c", boot], input=src, text=True, capture_output=True,
                       cwd=os.path.dirname(HSS), timeout=secs + 200)
    tail = (p.stdout + p.stderr).strip().splitlines()
    rep = json.load(open(os.path.join(OUT, tag + ".json"))) if os.path.exists(os.path.join(OUT, tag + ".json")) else {}
    return rep, tail[-1] if tail else ""


def amps(path, rpm0):
    ms, _, rpm, d, _ = S.load(path, "hfi_agl", CH)
    t = ms / 1000.0
    m = np.abs(np.abs(rpm) - rpm0) < 0.05 * rpm0
    i = np.where(m)[0]
    if i.size < 3000:
        return None, 0.0
    m[: i[0] + int(0.7 * 3000)] = False                 # 刚到速 ~3 s 不用
    m[i[-1] - 300:] = False                              # 停机前 0.3 s 不用
    t = t[m] - t[m].mean()
    f0 = np.abs(rpm[m]).mean() / 60
    out = {}
    for c in CH:
        y = d[c][m] - d[c][m].mean()
        best = 0.0
        for f in f0 * np.linspace(0.98, 1.02, 41):
            A = np.column_stack([np.cos(2 * np.pi * f * t), np.sin(2 * np.pi * f * t), t])
            x = np.linalg.lstsq(A, y, rcond=None)[0]
            best = max(best, math.hypot(x[0], x[1]))
        out[c] = best * (ACC_MG if c[0] == "a" else GYR_DPS)
    # 噪底: 同样拟合在非谐波频率 (0.63/1.37/1.63 倍转频), ax/ay 取均方根 → 1× 低于它 2~3 倍就分辨不了了
    nf = []
    for c in ("ax", "ay"):
        y = d[c][m] - d[c][m].mean()
        for r in (0.63, 1.37, 1.63):
            A = np.column_stack([np.cos(2 * np.pi * r * f0 * t), np.sin(2 * np.pi * r * f0 * t), t])
            x = np.linalg.lstsq(A, y, rcond=None)[0]
            nf.append(math.hypot(x[0], x[1]) * ACC_MG)
    out["nf"] = float(np.sqrt(np.mean(np.square(nf))))
    return out, float(np.std(np.abs(rpm[m])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rpms", type=float, nargs="+")
    ap.add_argument("--range", action="store_true", help="rpms = 起 止 步")
    ap.add_argument("--prefix", default="v04_sw")
    ap.add_argument("--secs", type=float, default=30.0)
    ap.add_argument("--max", type=int, default=900)
    ap.add_argument("--lim", type=float, default=10.0)
    ap.add_argument("--jump", type=float, default=4.0)
    ap.add_argument("--step", type=int, default=0, help="两段起转: 先到此转速, 5 s 再到目标")
    a = ap.parse_args()
    rpms = list(np.arange(a.rpms[0], a.rpms[1] + 1e-9, a.rpms[2])) if a.range else a.rpms
    rpms = [int(round(r)) for r in rpms]
    assert all(0 < r <= a.max for r in rpms), f"转速超出 --max {a.max}"

    res, prev = [], None
    print(f"扫速 {rpms} rpm, 每档 {a.secs:.0f} s, 限速 {a.max}, 门限 {a.lim} mg / 跳变 {a.jump}×", flush=True)
    for r in rpms:
        tag = f"{a.prefix}_{r}"
        rep, line = run_capture(tag, r, a.secs, a.max, a.step if a.step and a.step < r else 0)
        row = dict(tag=tag, rpm=r, valid=bool(rep.get("valid")), tq_hit=rep.get("d_tq_hit"))
        A, sd = amps(os.path.join(OUT, tag + ".csv"), r) if os.path.exists(os.path.join(OUT, tag + ".csv")) else (None, 0)
        row.update(amp=A, rpm_sd=round(sd, 2))
        res.append(row)
        if not A:
            print(f"{r:5d} rpm  没有稳速段 / 无数据: {line}", flush=True)
            stop = "无稳速数据"
        else:
            ratio = ""
            if prev:
                w2 = (r / prev["rpm"]) ** 2
                ratio = "  比上档 ax ×%.2f ay ×%.2f (ω² ×%.2f)" % (A["ax"] / prev["amp"]["ax"], A["ay"] / prev["amp"]["ay"], w2)
            print("%5d rpm  ax %6.3f ay %6.3f az %6.3f mg (噪底 %.3f) | gx %.4f gy %.4f dps | sd %.1f rpm | 有效 %s tq_hit %s%s"
                  % (r, A["ax"], A["ay"], A["az"], A["nf"], A["gx"], A["gy"], sd, row["valid"], row["tq_hit"], ratio), flush=True)
            stop = None
            if not row["valid"]:
                stop = "采集无效: " + line
            elif max(A["ax"], A["ay"], A["az"]) > a.lim:
                stop = f"1× 超 {a.lim} mg"
            elif prev and any(prev["amp"][c] >= 0.2 and A[c] / prev["amp"][c] > a.jump for c in ("ax", "ay")):
                stop = f"比上档涨 > {a.jump}×"
            if row["tq_hit"]:
                print(f"      ⚠ 力矩限幅命中 {row['tq_hit']} 次", flush=True)
        if stop:
            print(f"停: {stop}, 不再升速", flush=True)
            row["stop"] = stop
            break
        prev = row
    json.dump(res, open(os.path.join(OUT, a.prefix + "_summary.json"), "w"), ensure_ascii=False, indent=1)
    print("汇总", os.path.join(OUT, a.prefix + "_summary.json"))


if __name__ == "__main__":
    main()
