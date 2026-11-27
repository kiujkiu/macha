"""V1.2 结构件分 4 组 (11-20 用户「给结构件分组: 底盘安装 / 转子盘 / 灯组件 / 玻璃及上盖」, 目的: 生成更快 + 组装更快)。

本文件 GROUPS 是"哪个件归哪组"的唯一一张表 (quick_v1_2 同步成品文件夹也读它)。
    ① 底盘组      全部静止件: 打印底盘 + 玻纤底板 + 电机 + 控制板 + 线圈驱动 + 按键 + XT60/MR30 + 线圈环 + 定子盘 + 安装法兰
    ② 转子盘组    灯以下的旋转件: 转子玻纤板 + 承载盘B + 屏幕固定件 + 无线夹块/模块 + 底板 + 转子罩
    ③ 灯组件      灯板 ×2 + 夹条 + 梳齿 + 顶部件 + Φ8 轴/688 + 桥板 + FPC + 天线
    ④ 玻璃及上盖  分体下罩 (底座 + 玻璃座 + 外卡环) + 玻璃罩 + 玻璃上 + 圆环玻璃 + 堵头
                  (11-27 亚克力顶: 玻璃上外卡环红绿合一 + 管内弧形件 + 亚克力 Ø200×8 + MR105 + 中心盖子)
组间接口 (螺丝归后装的那组): ①→② 承载盘→电机 4×M3; ②→③ 屏幕固定件 / 夹条螺丝; ③→④ Φ8 轴进堵头 688; ④→① 下罩 4×M3 从盘底。

    cd v1.2/scripts && ../../.venv/bin/python group_asm_v1_2.py [1 2 3 4 | all] [--no-fig] [--no-copy] [--force]
件和螺丝都没变的组 3MF / 组合图直接沿用 (按 geocache 形体键算签名)。
每组输出 v1.2/分组/<n>_<组名>/:  <组名>.3mf (件 + 本组螺丝, 装配坐标) / <组名>_组合图.png,pdf / 清单.md / 零件/ (打印件 STEP + 打印 STL + 图纸)
只建所点组要用的模块 (玻璃组只要 build_v1_2); 几何走 geocache, 没改的件秒出。
"""
import sys, io, contextlib, math, shutil, time
from pathlib import Path

T0 = time.time()
def lap(m): print(f'[{time.time() - T0:5.1f}s] {m}', flush=True)

with contextlib.redirect_stdout(io.StringIO()):
    import build_v1_2 as B
V12 = B.V12


class _Mods:                                     # 零件模块按需 import (import 即建几何; 走 geocache)
    _names = dict(LS='led_support_v1_2', F='fpc_v1_2', WH='wireless_holder_v1_2', RSB='rotor_shroud_b_v1_2', MW='motor_wire_v1_2',
                  V='v2_boards_v1_2', FS='fasteners_v1_2')
    def __getattr__(self, k):
        if k == 'RB': return self.RSB.RB
        with contextlib.redirect_stdout(io.StringIO()):
            m = __import__(self._names[k])
        setattr(self, k, m); return m
M = _Mods()


def _leds():
    mb, mt = M.V.led_mip(B)
    return M.LS.comp([*M.LS.pair(mb), *M.LS.pair(mt)])


# (名称, 取形体, 颜色, 件代号 (models/<代号>/ 有打印件文件) 或 None, 数量, 类别 P 打印 / E 外购·电子·参考)
GROUPS = {
    1: ('底盘组', '全部静止件 (定子以下, 不含玻璃)', [
        (f'打印底盘 Φ220×{B.PRINT_T:g}', lambda: B.disc_print, '#8A8F98', 'base_disc_v1_2_gf', 1, 'P'),
        ('玻纤底板 FR4 Φ220×3 (板厂件)', lambda: B.fr4, '#C8D86A', 'base_fr4_v1_2', 1, 'E'),
        ('电机 Φ55×21.5', lambda: B.motor, '#333333', None, 1, 'E'),
        ('电机控制板', lambda: B.board, '#2E7D32', None, 1, 'E'),
        ('散热片 40×20×6', lambda: B.heatsink, '#C0392B', None, 1, 'E'),
        ('线圈环 coil_ring', lambda: B.ring, '#E0A030', 'coil_ring_v1_2', 1, 'P'),
        ('MOS 压块', lambda: B.CD.clamp, '#E69138', 'mos_clamp_v1_2', 1, 'P'),
        ('电容卡件', lambda: B.CD.cap_clamp, '#B45F06', 'cap_clamp_v1_2', 1, 'P'),
        ('线圈驱动板', lambda: B.CD.pcb, '#38761D', None, 1, 'E'),
        ('线圈驱动 MOS TO-220', lambda: B.CD.mos, '#222222', None, 1, 'E'),
        ('线圈驱动 电解电容 Φ10×20', lambda: B.CD.cap, '#1155CC', None, 1, 'E'),
        ('线圈驱动 散热片', lambda: B.CD.sink2, '#C0392B', None, 1, 'E'),
        ('XT60 压块', lambda: B.xt_clamp, '#F1C232', 'xt60_clamp_v1_2', 1, 'P'),
        ('XT60 底垫', lambda: B.xt_shim, '#E69138', None, 1, 'P'),
        ('按键支架', lambda: B.key_bracket, '#F1C232', 'key_bracket_v1_2', 1, 'P'),
        ('按键板 (简模)', lambda: B.key_board, '#2E7D32', None, 1, 'E'),
        ('按键帽', None, None, 'key_cap_v1_2', 1, 'P'),
        ('导光柱 (外购)', None, None, 'light_pipe_v1_2', 1, 'E'),
        ('MR30 座上件', lambda: M.MW.mr30_split()[0], '#F1C232', 'mr30_seat_v1_2', 1, 'P'),
        ('MR30 座下片', lambda: M.MW.mr30_split()[1], '#BF9000', 'mr30_floor_v1_2', 1, 'P'),
        ('电机线束线夹', lambda: M.MW.wire_clamp(), '#E69138', 'motor_wire_clamp_v1_2', 1, 'P'),
        ('定子盘 flange_disc', lambda: B.flange_disc, '#D9A441', 'flange_disc_v1_2', 1, 'P'),
        ('安装法兰 mounting_flange', lambda: B.mounting_flange, '#B5895A', 'mounting_flange_v1_2', 1, 'P'),
        ('定子光电发射板压片 ir_clamp', lambda: B.ir_clamp, '#E69138', 'ir_clamp_v1_2', 1, 'P'),   # 11-27 原 定子盘/ 文件夹并入
    ]),
    2: ('转子盘组', '灯以下的旋转件', [
        ('转子玻纤板 Φ165×3 (板厂件)', lambda: M.RB.fr4, '#C9B458', 'fr4_plate_v1_2b', 1, 'E'),
        ('承载盘B', lambda: M.RB.rim, '#6AA84F', 'rim_ring_v1_2b', 1, 'P'),
        ('无线线圈 (转子侧)', lambda: M.RB.coil, '#B87333', None, 1, 'E'),
        ('屏幕支架件 A ×2 (同一件, PETG, 0/180°)', lambda: M.LS.comp([M.RB.SCR_SUP[0], M.RB.SCR_SUP[2]]), '#F1C232', 'screen_sup_a_v1_2b', 2, 'P'),   # 11-21 取代屏幕玻纤板 ×4 + 侧立件 ×2
        ('上下件 B ×2 (同一件, PETG, 90/270°)', lambda: M.LS.comp([M.RB.SCR_SUP[1], M.RB.SCR_SUP[3]]), '#C9B458', 'screen_sup_b_v1_2b', 2, 'P'),
        ('无线模块夹块 ×2 (同一件)', lambda: M.WH.H, '#FFD966', 'wireless_holder_v1_2', 2, 'P'),
        ('无线供电模块 (占位)', lambda: M.WH.module, '#3D85C6', None, 1, 'E'),
        ('V2 底板 (交付 STEP)', lambda: M.LS.bb_step, '#1E8449', None, 1, 'E'),
        ('转子罩 侧环 (整圈)', lambda: M.RSB.shr_a, '#A4C2F4', 'rotor_shroud_b_a_v1_2b', 1, 'P'),   # 11-27 侧环整圈一件 (原 ±y 两半, −y 件 rotor_shroud_b_b_v1_2b 取消)
        ('转子罩 +y 顶盖', lambda: M.RSB.lid_a, '#CFE2F3', 'rotor_shroud_lid_a_v1_2b', 1, 'P'),   # 11-25 侧环 / 顶盖分开
        ('转子罩 −y 顶盖', lambda: M.RSB.lid_b, '#D9EAD3', 'rotor_shroud_lid_b_v1_2b', 1, 'P'),
    ]),
    3: ('灯组件', '灯板 + 夹持件 + 桥板/FPC', [
        ('灯板 A (+y)', lambda: M.LS.led_a, '#145A32', None, 1, 'E'),
        ('灯板 B (−y)', lambda: M.LS.led_b, '#0E3B22', None, 1, 'E'),
        ('MIP LED (两板)', _leds, '#D35400', None, 1, 'E'),
        ('灯板夹条 led_bar', lambda: M.LS.bar_s, '#8E7CC3', 'led_bar_v1_2', 1, 'P'),
        ('灯板梳齿 led_comb', lambda: M.LS.comb_s, '#9FC5E8', 'led_comb_v1_2', 1, 'P'),
        ('灯板顶部件 led_top', lambda: M.LS.top, '#6FA8DC', 'led_top_v1_2', 1, 'P'),
        ('中心轴 Φ8/Φ5 (占位, 以顶部连接为准)' if B.GT_ACR else 'Φ8 钢轴', lambda: M.LS.rod, '#999999', None, 1, 'E'),
        *([] if B.GT_ACR else [('688 轴承', lambda: M.LS.brg, '#666666', None, 1, 'E')]),   # 11-27 亚克力顶: 轴承 MR105 归 ④
        ('桥板 A/B', lambda: M.LS.comp([M.F.bridge_a, M.F.bridge_b]), '#1E8449', None, 2, 'E'),
        ('FPC A/B', lambda: M.LS.comp([M.F.fpc_a, M.F.fpc_b]), '#E67E22', 'fpc_v1_2', 2, 'E'),
        ('FPC 座 J5/J6', lambda: M.LS.comp([M.F.seat_j5, M.F.seat_j6]), '#7F8C8D', None, 2, 'E'),
        ('天线软板 ×2', lambda: M.LS.comp([M.LS.ant_a, M.LS.ant_b]), '#C0392B', None, 2, 'E'),
    ]),
    4: ('玻璃及上盖', '分体下罩 + 玻璃罩 + 顶部', [
        ('玻璃下-底座 glass_shroud_lower', lambda: B.shroud_lo, '#7FB3D5', 'glass_shroud_lower_v1_2', 1, 'P'),
        ('玻璃下-玻璃座 glass_shroud_upper', lambda: B.shroud_hi, '#5DADE2', 'glass_shroud_upper_v1_2', 1, 'P'),
        ('外卡环 glass_clamp_ring', lambda: B.clamp_ring, '#2E86C1', 'glass_clamp_ring_v1_2', 1, 'P'),
        ('玻璃罩 OD200×5 (外购)', lambda: B.tube, '#D6EAF8', None, 1, 'E'),
        *([('玻璃上 外卡环 (红绿合一) glass_top_ring', lambda: B.glass_top_ring, '#7FB3D5', 'glass_top_ring_v1_2', 1, 'P'),   # 11-27 亚克力顶 (build_v1_2 GT_ACR)
           ('管内弧形件 glass_top_lug ×8', lambda: M.LS.comp(B.glass_top_lugs), '#F1C232', 'glass_top_lug_v1_2', 8, 'P'),
           ('亚克力顶 Ø200×8 (外协)', lambda: B.acrylic, '#AED6F1', 'glass_top_acrylic_v1_2', 1, 'E'),
           ('MR105ZZ 轴承 (Φ5×Φ10×3)', lambda: B.brg_mr105, '#666666', None, 1, 'E'),
           ('中心盖子 top_cap', lambda: B.top_cap, '#2E86C1', 'top_cap_v1_2', 1, 'P'),
           ] if B.GT_ACR else [
           ('玻璃上 下件 (红) glass_top', lambda: B.glass_top, '#7FB3D5', 'glass_top_v1_2', 1, 'P'),
           ('玻璃上 上件 (绿) glass_top_clamp', lambda: B.glass_top_clamp, '#1B4F72', 'glass_top_clamp_v1_2', 1, 'P'),
           ('管内弧形件 glass_top_lug ×8', lambda: M.LS.comp(B.glass_top_lugs), '#F1C232', 'glass_top_lug_v1_2', 8, 'P'),   # 11-25 横锁
           ('中心堵头 glass_top_hub', lambda: B.glass_top_hub, '#2E86C1', 'glass_top_hub_v1_2', 1, 'P'),
           ('圆环玻璃 OD180×10 (外购)', lambda: B.glass_disc, '#AED6F1', None, 1, 'E')]),
    ]),
}
CODE_GROUP = {code: g for g, (_, _, items) in GROUPS.items() for _, _, _, code, _, _ in items if code}
FOLDER = {g: V12 / '分组' / f'{g}_{name}' for g, (name, _, _) in GROUPS.items()}


def fastener_group(name):
    """紧固件 (fasteners_v1_2.F 的名称) → 组号。组间接口螺丝归后装的那组。"""
    if '玻璃' in name or '下罩' in name: return 4
    if any(k in name for k in ('立板→夹条', '梳齿', '灯板顶帽')): return 3
    if any(k in name for k in ('底板', '转子罩', '玻纤板→', '承载盘', '固定件', '支撑件', '无线')): return 2
    return 1


def part_files(code):
    """件代号 → [(源文件, 目标名)]: 装配 STEP + 打印 STL (优先打印姿态) + 图纸 (取最新的那份)。"""
    d = V12 / 'models' / code; out = []
    if (d / f'{code}.step').exists(): out.append((d / f'{code}.step', f'{code}.step'))
    for s in (d / f'{code}_print.stl', V12 / 'out' / '打印STL' / f'{code}.stl', d / f'{code}.stl'):
        if s.exists(): out.append((s, f'{code}.stl')); break
    dw = sorted(d.glob(f'{code}_drawing*.pdf'), key=lambda f: f.stat().st_mtime)
    if dw: out.append((dw[-1], f'{code}_drawing.pdf'))
    for x in d.glob('*.dxf'): out.append((x, x.name))
    return out


def copy_safe(src, dst):
    try: shutil.copy2(src, dst); return dst.name
    except PermissionError:
        for s in ('NEW', 'NEW2', 'NEW3'):
            alt = dst.with_name(f'{dst.stem}.{s}{dst.suffix}')
            try: shutil.copy2(src, alt); return alt.name + ' (原文件被占用)'
            except PermissionError: continue
    return None


def sync_part(code):
    """quick_v1_2 出完一个件后调: 把它的文件同步到所属组文件夹。"""
    g = CODE_GROUP.get(code)
    if g is None: return None
    pd = FOLDER[g] / '零件'; pd.mkdir(parents=True, exist_ok=True)
    for src, nm in part_files(code): copy_safe(src, pd / nm)
    return FOLDER[g].name


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    want = sorted(GROUPS) if not args or 'all' in args else sorted({int(a) for a in args})
    FIG, COPY = '--no-fig' not in sys.argv, '--no-copy' not in sys.argv
    from mf3_v1_2 import write3mf
    fs = None
    for g in want:
        name, desc, items = GROUPS[g]; gd = FOLDER[g]; gd.mkdir(parents=True, exist_ok=True)
        parts, miss = [], []
        for n, get, col, code, qty, kind in items:
            if get is None: continue
            try:
                sh = get()
                if sh is None or sh.IsNull(): raise ValueError('空')
                parts.append((n, sh, col, kind))
            except Exception as e:
                miss.append(f'{n}: {e!r}')
        lap(f'{g} {name}: {len(parts)} 件几何' + (f', 缺 {miss}' if miss else ''))
        if fs is None:
            os_ = __import__('os'); os_.environ.pop('FASTENERS_REPORT', None); fs = M.FS
        fast = [(n, sh, c) for n, sh, c in fs.F if fastener_group(n) == g]
        scr, nut = {}, {}
        for n, _, c in fast:
            k = n.rsplit(' #', 1)[0]; dd = scr if c.upper() == '#C0C0C0' else nut; dd[k] = dd.get(k, 0) + 1
        sig = B.GC._h('grp1', g, [B.GC.key(sh) for _, sh, _, _ in parts], [B.GC.key(sh) for _, sh, _ in fast], [(n, c) for n, _, c, _ in parts]) if B.GC.ON else None
        sf = gd / '.签名'; same = sig and sf.exists() and sf.read_text() == sig and (gd / f'{name}.3mf').exists() and (not FIG or (gd / f'{name}_组合图.png').exists())
        if same and '--force' not in sys.argv:
            lap(f'{g} {name}: 件和螺丝都没变, 3MF / 组合图沿用 (--force 强制重出)')
        else:
          write3mf(str(gd / f'{name}.3mf'), [(n, s, c, 0.05) for n, s, c, _ in parts] + [(n, s, c, 0.05) for n, s, c in fast])
          lap(f'{g} {name}: 3MF ({len(parts)} 件 + {len(fast)} 紧固件)')
          if FIG:
              render_fig(g, name, parts, fast, scr, nut, gd)
              lap(f'{g} {name}: 组合图')
          if sig: sf.write_text(sig)
        copied = []
        if COPY:
            pd = gd / '零件'; pd.mkdir(exist_ok=True)
            for n, _, _, code, qty, kind in items:
                if not code: continue
                for src, nm in part_files(code):
                    r = copy_safe(src, pd / nm)
                    if r: copied.append(r)
            lap(f'{g} {name}: 零件文件 {len(copied)} 个 → {gd.relative_to(V12)}/零件/')
        write_list(g, name, desc, items, scr, nut, gd)
    lap('完成')


def render_fig(g, name, parts, fast, scr, nut, gd):
    import numpy as np
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    from matplotlib import font_manager, colors as mcolors
    from mf3_v1_2 import mesh
    font_manager.fontManager.addfont('/mnt/c/Windows/Fonts/simhei.ttf'); plt.rcParams['font.family'] = 'SimHei'; plt.rcParams['axes.unicode_minus'] = False
    def tris(s, defl):
        try: V, T = mesh(s, defl)
        except ValueError: return np.zeros((0, 3, 3))
        return V[T]
    items = [(tris(s, 0.3), np.array(mcolors.to_rgb(c))) for _, s, c, _ in parts] + [(tris(s, 0.2), np.array(mcolors.to_rgb('#B0B0B0' if c.upper() == '#C0C0C0' else c))) for _, s, c in fast]
    allz = np.concatenate([P.reshape(-1, 3)[:, 2] for P, _ in items if len(P)]); z0 = allz.min()
    def render(ax, its, az, el, explode=0.0):
        a, e = math.radians(az), math.radians(el)
        d = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)]); u = np.array([-math.sin(a), math.cos(a), 0.0]); v = np.cross(d, u)
        lt = 0.6 * d + 0.4 * np.array([0, 0, 1.0]); lt /= np.linalg.norm(lt)
        PP, CC, DD = [], [], []
        for P, rgb in its:
            if not len(P): continue
            if explode: P = P + np.array([0, 0, (P[:, :, 2].mean() - z0) * explode])
            n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
            PP.append(P); CC.append(np.clip(rgb[None, :] * (0.4 + 0.6 * np.abs(n @ lt))[:, None], 0, 1)); DD.append(P.mean(1) @ d)
        P = np.concatenate(PP); C = np.concatenate(CC); D = np.concatenate(DD); o = np.argsort(D)
        ax.add_collection(PolyCollection(np.stack([P[o] @ u, P[o] @ v], axis=-1), facecolors=C[o], edgecolors='none', antialiased=False, rasterized=True))
        ax.set_aspect('equal'); ax.axis('off'); ax.autoscale_view(); ax.margins(0.02)
    fig = plt.figure(figsize=(16.54, 11.69)); fig.suptitle(f'POV3D V1.2 — 第 {g} 组 {name}', fontsize=15, y=0.985)
    axs = [fig.add_axes(r) for r in ([0.0, 0.48, 0.38, 0.46], [0.38, 0.48, 0.38, 0.46], [0.0, 0.02, 0.38, 0.44], [0.38, 0.02, 0.38, 0.44])]
    render(axs[0], items, -60, 22); axs[0].set_title('装配 (轴测)')
    render(axs[1], items, -60, 22, explode=1.2); axs[1].set_title('爆炸 (按高度拉开)')
    render(axs[2], items, -90, 89.99); axs[2].set_title('俯视')
    render(axs[3], items, -90, 0.01); axs[3].set_title('正视 (看 +y)')
    tx = fig.add_axes([0.77, 0.02, 0.22, 0.92]); tx.axis('off')
    L = ['件'] + [f'  · {n}' for n, _, _, _ in parts] + ['', '螺丝 (每台)'] + [f'  · {k} ×{v}' for k, v in sorted(scr.items())] + \
        ['', '螺母 / 铜螺母 / 垫柱'] + [f'  · {k} ×{v}' for k, v in sorted(nut.items())]
    tx.text(0, 1, '\n'.join(L), va='top', fontsize=7.2, linespacing=1.4)
    fig.text(0.99, 0.006, f'v1.2/scripts/group_asm_v1_2.py  {time.strftime("%Y-%m-%d %H:%M")}', fontsize=7, ha='right', color='#666')
    for ext, dpi in (('png', 110), ('pdf', 200)):
        try: fig.savefig(gd / f'{name}_组合图.{ext}', dpi=dpi)
        except PermissionError: fig.savefig(gd / f'{name}_组合图.NEW.{ext}', dpi=dpi)
    plt.close(fig)


def write_list(g, name, desc, items, scr, nut, gd):
    L = [f'# 第 {g} 组 {name}', '', f'{desc}。由 `v1.2/scripts/group_asm_v1_2.py {g}` 生成 ({time.strftime("%Y-%m-%d %H:%M")}), 改表请改脚本里的 GROUPS。', '',
         f'- 装配图: `{name}.3mf` (装配坐标, 含本组螺丝螺母) / `{name}_组合图.png`', '- 打印件文件: `零件/` (STEP = 装配坐标, STL = 打印姿态, 图纸 PDF)', '',
         '## 打印件', '| 件 | 代号 | 数量 |', '|---|---|---|']
    L += [f'| {n} | `{code or "—"}` | {q} |' for n, _, _, code, q, k in items if k == 'P']
    L += ['', '## 外购 / 电子件 / 参考', '| 件 | 数量 |', '|---|---|'] + [f'| {n} | {q} |' for n, _, _, code, q, k in items if k == 'E']
    L += ['', '## 螺丝 (每台)', '| 规格 / 位置 | 数量 |', '|---|---|'] + [f'| {k} | {v} |' for k, v in sorted(scr.items())]
    L += ['', '## 螺母 / 铜螺母 / 垫柱', '| 规格 / 位置 | 数量 |', '|---|---|'] + [f'| {k} | {v} |' for k, v in sorted(nut.items())]
    L += ['', '组间接口螺丝归后装的那组: ①→② 承载盘→电机 / ②→③ 屏幕固定件、夹条 / ③→④ Φ8 轴进堵头 688 / ④→① 下罩从盘底 4×M3。']
    (gd / '清单.md').write_text('\n'.join(L) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
