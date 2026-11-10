"""底部 IMU + 顶部手机 一起升速扫 (2026-11-10)。每档跑完判门限, 超了就停不再升。
用法: python3 phone_sweep.py 950 1200 50 [--top 3.0] [--bot 30] [--prefix v04_hs]"""
import argparse, subprocess, sys, os, re
import numpy as np
import phone_v04 as P
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("r0", type=int); ap.add_argument("r1", type=int); ap.add_argument("dr", type=int)
ap.add_argument("--top", type=float, default=3.0, help="顶部 1× 门限 m/s²")
ap.add_argument("--bot", type=float, default=30.0)
ap.add_argument("--jump", type=float, default=2.5, help="顶部比上档涨超此倍就停")
ap.add_argument("--prefix", default="v04_hs")
a = ap.parse_args()
prev = None
for r in range(a.r0, a.r1 + 1, a.dr):
    tag = f"{a.prefix}_{r}"
    p = subprocess.run([sys.executable, os.path.join(HERE, "phone_v04.py"), "run", tag, "--rpm", str(r), "--max", str(a.r1), "--lim", str(a.bot)],
                       capture_output=True, text=True)
    out = p.stdout + p.stderr
    bot = [x for x in out.splitlines() if " rpm " in x]
    top = [x for x in out.splitlines() if "顶部 1×" in x]
    print(f"{r} rpm | 底 {bot[-1].strip() if bot else '?'}\n        | {top[-1].strip() if top else out[-300:]}", flush=True)
    if not top or "有效 True" not in (bot[-1] if bot else ""):
        print("停: 采集无效或手机失败"); break
    m = re.search(r"ax ([\d.]+) ay ([\d.]+)", top[-1]); t = max(float(m.group(1)), float(m.group(2)))
    mb = re.search(r"ax +([\d.]+) ay +([\d.]+) az +([\d.]+)", bot[-1]); b = max(map(float, mb.groups()))
    if t > a.top: print(f"停: 顶部 {t:.2f} > {a.top} m/s²"); break
    if b > a.bot: print(f"停: 底部 {b:.1f} > {a.bot} mg"); break
    if prev and t / prev > a.jump: print(f"停: 顶部比上档涨 {t/prev:.1f}×"); break
    prev = t
