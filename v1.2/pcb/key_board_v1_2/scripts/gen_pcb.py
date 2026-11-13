# -*- coding: utf-8 -*-
"""POV3D V1.2 按键板 PCB 生成器 (pcbnew API, KiCad 10.0.7 系统 python3).
    python3 gen_pcb.py  →  ../key_board_v1_2.kicad_pcb (摆件 + 栅格迷宫布线 + 双面 GND 铺铜 + 缝合孔)
网表 / 封装名: gen_sch.PARTS / FP。元件位置: 正面 6 件 = key_board_outline_v1_2.py 常数; J1 = ../mech_constraints.json (结构 agent 给)。
板系 (X, Y): 原点板左下角, 从机器外面看正面 (= KiCad 顶视), Y 向上; KiCad: kx = OX + X, ky = OY − Y。
"""
import heapq
import json
import math
import os
import sys

import numpy as np
import pcbnew as P

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_sch as S  # noqa: E402

PRJ = S.PRJ
V12 = os.path.normpath(os.path.join(PRJ, '..', '..'))
sys.path.insert(0, os.path.join(V12, 'scripts'))
import key_board_outline_v1_2 as KB  # noqa: E402

OX, OY = 100.0, 100.0 + KB.H
KLIB = '/usr/share/kicad/footprints'
PLIB = os.path.join(PRJ, 'lib', 'key_board.pretty')
CLR, MARGIN = 0.15, 0.06          # 规则间隙 / 栅格离散余量
W_SIG, W_PWR = 0.2, 0.3
VIA_D, VIA_DR = 0.6, 0.3
EDGE_CLR = 0.3
G = 0.05                           # 布线栅格


def mm(v):
    return P.FromMM(v)


def V(x, y):
    return P.VECTOR2I(mm(x), mm(y))


def k(X, Y):
    return OX + X, OY - Y


def b(kx, ky):
    return kx - OX, OY - ky


# ---------------- 封装 ----------------
def _gen_fp(kind):
    """lib 没到之前的占位封装 (按手册焊盘)"""
    f = P.FOOTPRINT(None)
    f.SetFPID(P.LIB_ID('placeholder', kind))
    def pad(num, x, y, w, h, shape=P.PAD_SHAPE_RECT):
        p = P.PAD(f); p.SetNumber(num); p.SetAttribute(P.PAD_ATTRIB_SMD); p.SetShape(shape)
        p.SetSize(V(w, h)); p.SetPosition(V(x, y)); p.SetLayerSet(P.PAD.SMDMask()); f.Add(p)
    if kind == 'SW':   # ZX-QC66-7.5TP: 焊盘 3.0×2.2, 中心距 6.5 × 3.4; 1 左上 2 右上 3 左下 4 右下 (顶视)
        for n, sx, sy in (('1', -1, -1), ('2', 1, -1), ('3', -1, 1), ('4', 1, 1)):
            pad(n, sx * 3.25, sy * 1.7, 3.0, 2.2)
    elif kind == 'RGB':  # XL-1615RGBC: 焊盘 0.45×0.65, X 间隙 0.8 / Y 间隙 0.3; 1 左上 2 左下 3 右上 4 右下
        for n, sx, sy in (('1', -1, -1), ('2', -1, 1), ('3', 1, -1), ('4', 1, 1)):
            pad(n, sx * 0.625, sy * 0.475, 0.45, 0.65)
    return f


def load_fp(key):
    name = S.FP[key]
    lib, fp = name.split(':')
    if lib == 'key_board':
        if os.path.exists(os.path.join(PLIB, fp + '.kicad_mod')):
            return P.FootprintLoad(PLIB, fp), name
        stock = dict(J=('Connector_JST', 'JST_GH_SM12B-GHS-TB_1x12-1MP_P1.25mm_Horizontal'), LED=('LED_SMD', 'LED_0603_1608Metric'))
        if key in stock:
            l2, f2 = stock[key]
            return P.FootprintLoad(os.path.join(KLIB, l2 + '.pretty'), f2), f'{l2}:{f2}'
        return _gen_fp(key), f'placeholder:{key}'
    return P.FootprintLoad(os.path.join(KLIB, lib + '.pretty'), fp), name


def mech():
    f = os.path.join(PRJ, 'mech_constraints.json')
    if os.path.exists(f):
        return json.load(open(f, encoding='utf-8'))
    return None


# ---------------- 栅格 ----------------
NX, NY = int(round(KB.W / G)) + 1, int(round(KB.H / G)) + 1


def gi(X, Y):
    return int(round(X / G)), int(round(Y / G))


def disk_offsets(r):
    n = int(math.ceil(r / G))
    return [(dx, dy) for dx in range(-n, n + 1) for dy in range(-n, n + 1) if (dx * G) ** 2 + (dy * G) ** 2 <= r * r + 1e-9]


_DCACHE = {}


def dilate(m, r):
    if r <= 0:
        return m.copy()
    offs = _DCACHE.setdefault(round(r, 4), disk_offsets(r))
    out = np.zeros_like(m)
    H, W = m.shape
    for dx, dy in offs:
        xs0, xs1 = max(0, dx), W + min(0, dx)
        ys0, ys1 = max(0, dy), H + min(0, dy)
        out[ys0:ys1, xs0:xs1] |= m[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
    return out


class Grid:
    """occ[layer][iy, ix] = 网号 (>0), 0 空, −1 硬禁"""
    def __init__(self):
        self.occ = [np.zeros((NY, NX), np.int32), np.zeros((NY, NX), np.int32)]
        self.pad = np.zeros((NY, NX), bool)        # 任意焊盘 (过孔不进焊盘)

    def rect(self, L, x0, y0, x1, y1, val):
        i0, j0 = int(math.floor(x0 / G)), int(math.floor(y0 / G))
        i1, j1 = int(math.ceil(x1 / G)), int(math.ceil(y1 / G))
        i0, j0, i1, j1 = max(i0, 0), max(j0, 0), min(i1, NX - 1), min(j1, NY - 1)
        for l in L:
            sl = self.occ[l][j0:j1 + 1, i0:i1 + 1]
            if val < 0:
                sl[...] = val
            else:
                sl[sl == 0] = val
        return (j0, j1, i0, i1)

    def circle(self, L, X, Y, r, val):
        yy, xx = np.mgrid[0:NY, 0:NX]
        m = (xx * G - X) ** 2 + (yy * G - Y) ** 2 <= r * r
        for l in L:
            if val < 0:
                self.occ[l][m] = val
            else:
                self.occ[l][m & (self.occ[l] == 0)] = val

    def stamp_path(self, cells, w, net):
        r = w / 2
        offs = _DCACHE.setdefault(('s', round(r, 4)), disk_offsets(r))
        for (l, i, j) in cells:
            for dx, dy in offs:
                ii, jj = i + dx, j + dy
                if 0 <= ii < NX and 0 <= jj < NY and self.occ[l][jj, ii] == 0:
                    self.occ[l][jj, ii] = net


def astar(grid, net, w, starts, goals, front_cost=2.5, via_cost=40):
    """starts / goals: set of (l, i, j). 8 邻域, 层间换层 = 过孔."""
    rr = w / 2 + CLR + MARGIN
    blk = []
    for l in (0, 1):
        o = grid.occ[l]
        other = (o != 0) & (o != net)
        blk.append(dilate(other, rr) | (o == -1))
    vblk = dilate((grid.occ[0] != 0) & (grid.occ[0] != net), VIA_D / 2 + CLR + MARGIN) | \
        dilate((grid.occ[1] != 0) & (grid.occ[1] != net), VIA_D / 2 + CLR + MARGIN) | dilate(grid.pad, VIA_D / 2 + 0.1) | \
        dilate((grid.occ[0] == -1) | (grid.occ[1] == -1), VIA_D / 2 + 0.05)
    gl = np.array([(i, j) for (_, i, j) in goals])
    gx0, gx1, gy0, gy1 = gl[:, 0].min(), gl[:, 0].max(), gl[:, 1].min(), gl[:, 1].max()

    def h(i, j):
        dx = max(gx0 - i, 0, i - gx1); dy = max(gy0 - j, 0, j - gy1)
        return (max(dx, dy) + 0.4142 * min(dx, dy))
    dist = {}
    prev = {}
    pq = []
    for s in starts:
        dist[s] = 0.0
        heapq.heappush(pq, (h(s[1], s[2]), 0.0, s))
    D8 = [(1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1), (1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]
    while pq:
        f, d, c = heapq.heappop(pq)
        if d > dist.get(c, 1e18):
            continue
        if c in goals:
            path = [c]
            while path[-1] in prev:
                path.append(prev[path[-1]])
            return path[::-1]
        l, i, j = c
        lc = front_cost if l == 0 else 1.0
        nb = []
        for dx, dy, cst in D8:
            ii, jj = i + dx, j + dy
            if 0 <= ii < NX and 0 <= jj < NY and (not blk[l][jj, ii] or (l, ii, jj) in goals):
                # 换方向轻罚 (少折线)
                pc = prev.get(c)
                turn = 0.0
                if pc is not None and pc[0] == l and (i - pc[1], j - pc[2]) != (dx, dy):
                    turn = 0.3
                nb.append(((l, ii, jj), cst * lc + turn))
        if not vblk[j, i]:
            nb.append(((1 - l, i, j), via_cost))
        for n2, cst in nb:
            nd = d + cst
            if nd < dist.get(n2, 1e18):
                dist[n2] = nd
                prev[n2] = c
                heapq.heappush(pq, (nd + h(n2[1], n2[2]), nd, n2))
    return None


def path_to_segments(path):
    """→ [('seg', l, (i0,j0), (i1,j1)) | ('via', (i,j))]"""
    out = []
    run = [path[0]]
    for c in path[1:]:
        p = run[-1]
        if c[0] != p[0]:
            if len(run) > 1:
                out.append(('seg', p[0], run[0][1:], p[1:]))
            out.append(('via', p[1:]))
            run = [c]
            continue
        if len(run) >= 2:
            d0 = (run[-1][1] - run[-2][1], run[-1][2] - run[-2][2])
            d1 = (c[1] - p[1], c[2] - p[2])
            if d0 != d1:
                out.append(('seg', p[0], run[0][1:], p[1:]))
                run = [p]
        run.append(c)
    if len(run) > 1:
        out.append(('seg', run[-1][0], run[0][1:], run[-1][1:]))
    return out


# ---------------- 主流程 ----------------
def main():
    bd = P.BOARD()
    ds = bd.GetDesignSettings()
    ds.SetCopperLayerCount(2)
    ds.m_TrackMinWidth = mm(0.15); ds.m_MinClearance = mm(0.15); ds.m_ViasMinSize = mm(0.6); ds.m_MinThroughDrill = mm(0.3)
    ds.m_CopperEdgeClearance = mm(EDGE_CLR); ds.m_HoleClearance = mm(0.25); ds.m_HoleToHoleMin = mm(0.25)
    ds.m_ViasMinAnnularWidth = mm(0.15)
    # 板框
    for (x0, y0), (x1, y1) in [((0, 0), (KB.W, 0)), ((KB.W, 0), (KB.W, KB.H)), ((KB.W, KB.H), (0, KB.H)), ((0, KB.H), (0, 0))]:
        s = P.PCB_SHAPE(bd); s.SetShape(P.SHAPE_T_SEGMENT); s.SetLayer(P.Edge_Cuts); s.SetWidth(mm(0.05))
        s.SetStart(V(*k(x0, y0))); s.SetEnd(V(*k(x1, y1))); bd.Add(s)
    # 网
    nets = {}
    for ref, (_l, _n, _v, _f, _s, pn) in S.PARTS.items():
        for n in pn.values():
            if n not in nets:
                ni = P.NETINFO_ITEM(bd, n); bd.Add(ni); nets[n] = ni
    NID = {n: i + 1 for i, n in enumerate(nets)}          # 栅格用网号
    GND = NID['GND']

    m = mech()
    jpos = dict(X=20.0, Y=3.5, rot=0.0)                   # 默认: 板中间, 插口朝下 (Y=0 边), 背面
    if m:
        c = m.get('connector') or m.get('J1') or {}
        if 'origin_board_XY' in c:
            jpos['X'], jpos['Y'] = map(float, c['origin_board_XY'])
        try:
            jpos['rot'] = float(c.get('rotation', c.get('rot', 0.0)))
        except (TypeError, ValueError):
            jpos['rot'] = 0.0                                  # 文字说明 "B.Cu 上 rotation 0"
        JP1 = c.get('pin1_board_XY')
    # 背面电阻位 (板系, 竖放, 管脚 1 朝上 = 接 LED 侧)
    # 电阻按 J1 管脚顺序排在插座焊盘正上方 (翻面后 pin1 在右), 两排错开; 管脚 2 (IO 侧) 朝下
    pinX = lambda n: jpos['X'] + 6.875 - 1.25 * (n - 1)
    YA, YB = jpos['Y'] + 4.85, jpos['Y'] + 7.95     # J1 庭院到 Y+3.2; 0603 竖放庭院 ±1.48
    RPOS = {'R1': (pinX(1), YA), 'R2': (pinX(2), YB), 'R3': (pinX(6), YA), 'R4': (pinX(4), YB),
            'R5': (pinX(3), YA), 'R6': (pinX(11), YA), 'C1': (pinX(8), YA)}
    if m and 'back_parts' in m:
        RPOS.update({r: tuple(v) for r, v in m['back_parts'].items()})
    FRONT = {'SW1': KB.BTN[0], 'SW2': KB.BTN[1], 'D1': KB.RGB, 'D2': KB.LED[0], 'D3': KB.LED[1], 'D4': KB.LED[2]}

    fps = {}
    fpnames = {}
    for ref, (_l, _n, val, fpk, side, pn) in S.PARTS.items():
        f, nm = load_fp(fpk)
        fpnames[ref] = nm
        f.SetReference(ref); f.SetValue(val)
        f.SetFPID(P.LIB_ID(*nm.split(':')))
        f.SetPath(P.KIID_PATH('/' + S.U('sym' + ref)))           # 与原理图符号 uuid 关联 (parity)
        bd.Add(f)
        f.SetField('Description', S.DESC[ref] + (' [背面]' if side == 'B' else ' [正面]'))
        f.SetField('LCSC', S.LCSC[ref][0]); f.SetField('MPN', S.LCSC[ref][1])
        for fn in ('LCSC', 'MPN'):
            fl = f.GetField(fn)
            if fl is not None:
                fl.SetVisible(False); fl.SetLayer(P.F_Fab if side == 'F' else P.B_Fab)
        # 取向: 按键 / LED 让焊盘长向沿 X; 电阻竖放
        if ref in FRONT:
            X, Y = FRONT[ref]
            f.SetPosition(V(*k(X, Y)))
            pads = list(f.Pads())
            xs = [p.GetPosition().x for p in pads]; ys = [p.GetPosition().y for p in pads]
            if (max(ys) - min(ys)) > (max(xs) - min(xs)):
                f.SetOrientationDegrees(90)
        elif ref == 'J1':
            f.SetPosition(V(*k(jpos['X'], jpos['Y'])))
            f.SetOrientationDegrees(jpos['rot'])
        else:
            X, Y = RPOS[ref]
            f.SetPosition(V(*k(X, Y)))
            f.SetOrientationDegrees(270 if ref.startswith('R') else 90)   # R: 脚 2 (IO) 朝下; C1: 脚 1 (3V3) 朝下
        if side == 'B':
            f.Flip(f.GetPosition(), P.FLIP_DIRECTION_LEFT_RIGHT)
        for p in f.Pads():
            n = pn.get(p.GetNumber())
            if n is None and p.GetNumber() == '':
                continue
            assert n is not None, (ref, p.GetNumber())
            p.SetNet(nets[n])
        fps[ref] = f
    # 正面件: 丝印全拿掉 (平板压正面, 不要任何凸起); 位号放 F.Fab
    for ref, f in fps.items():
        if f.GetLayer() == P.F_Cu:
            for it in list(f.GraphicalItems()):
                if it.GetLayer() == P.F_SilkS:
                    it.SetLayer(P.F_Fab)          # 不 Remove (SWIG 会释放导致堆坏)
            f.Reference().SetLayer(P.F_Fab); f.Value().SetLayer(P.F_Fab)
        else:
            f.Value().SetVisible(False)
            if ref == 'J1':
                f.Reference().SetPosition(V(*k(jpos['X'] - 3.0, jpos['Y'] - 2.45 - 0.9)))
            if ref == 'C1':                                  # 和 R5 位号挤一起 → 放到 C1 上方, 横排
                cx, cy = b(P.ToMM(f.GetPosition().x), P.ToMM(f.GetPosition().y))
                f.Reference().SetPosition(V(*k(cx, cy + 2.1))); f.Reference().SetTextAngleDegrees(0)
            f.Reference().SetTextSize(V(0.7, 0.7)); f.Reference().SetTextThickness(mm(0.12))
    # 安装孔 (NPTH Φ3.2)
    for i, (X, Y) in enumerate(KB.MH, 1):
        h = P.FootprintLoad(os.path.join(KLIB, 'MountingHole.pretty'), 'MountingHole_3.2mm_M3')
        h.SetReference(f'H{i}'); h.SetPosition(V(*k(X, Y))); h.SetBoardOnly(True); h.SetExcludedFromBOM(True); bd.Add(h)
        h.Reference().SetVisible(False); h.Value().SetVisible(False)
        for it in list(h.GraphicalItems()):
            if it.GetLayer() in (P.F_SilkS, P.Cmts_User, P.F_CrtYd, P.B_CrtYd) and it.Type() != P.PCB_FIELD_T:   # NPTH 孔: 禁布另用规则区
                it.SetLayer(P.Cmts_User)
        # 禁布: 正面 Φ4.8 (平板压环) / 背面 Φ8 (法兰螺母): 不走线 / 不打孔 (铺铜可以)
        for lay, d in ((P.F_Cu, KB.FRONT_KO_D), (P.B_Cu, KB.BACK_KO_D)):
            z = P.ZONE(bd); z.SetIsRuleArea(True); z.SetLayer(lay)
            z.SetDoNotAllowTracks(True); z.SetDoNotAllowVias(True); z.SetDoNotAllowZoneFills(False)
            z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(True if lay == P.B_Cu else False)
            ol = z.Outline(); ol.NewOutline()
            for a in range(32):
                t = 2 * math.pi * a / 32
                ol.Append(mm(OX + X + d / 2 * math.cos(t)), mm(OY - Y + d / 2 * math.sin(t)))
            z.SetZoneName(f'KO_{"F" if lay == P.F_Cu else "B"}_H{i}')
            bd.Add(z)

    # ---------- 栅格占用 ----------
    gr = Grid()
    ec = EDGE_CLR
    for l in (0, 1):
        o = gr.occ[l]
        n_e = int(math.ceil(ec / G))
        o[:n_e, :] = -1; o[-n_e:, :] = -1; o[:, :n_e] = -1; o[:, -n_e:] = -1
    for X, Y in KB.MH:
        gr.circle((0,), X, Y, KB.FRONT_KO_D / 2, -1)
        gr.circle((1,), X, Y, KB.BACK_KO_D / 2, -1)
    padinfo = {}      # (ref, num) -> list of (l, cells set)
    for ref, f in fps.items():
        for p in f.Pads():
            if p.GetNumber() == '':
                continue
            bb = p.GetBoundingBox()
            kx0, ky0, kx1, ky1 = P.ToMM(bb.GetLeft()), P.ToMM(bb.GetTop()), P.ToMM(bb.GetRight()), P.ToMM(bb.GetBottom())
            X0, Y1 = b(kx0, ky0); X1, Y0 = b(kx1, ky1)
            L = (0,) if p.IsOnLayer(P.F_Cu) else (1,)
            net = NID[p.GetNetname()]
            j0, j1, i0, i1 = gr.rect(L, X0, Y0, X1, Y1, net)
            ii0, jj0 = int(math.ceil(X0 / G)), int(math.ceil(Y0 / G))
            ii1, jj1 = int(math.floor(X1 / G)), int(math.floor(Y1 / G))
            gr.pad[jj0:jj1 + 1, ii0:ii1 + 1] = True
            cells = {(L[0], i, j) for i in range(ii0, ii1 + 1) for j in range(jj0, jj1 + 1)}
            padinfo.setdefault(p.GetNetname(), []).append(((ref, p.GetNumber()), cells, ((X0 + X1) / 2, (Y0 + Y1) / 2)))

    # ---------- J1 地脚 (5/7/12) 先打 GND 过孔: 信号短线直上会把这些焊盘围成孤岛 ----------
    pre = []
    for p in fps['J1'].Pads():
        if p.GetNetname() == 'GND' and p.GetNumber() != 'MP':
            px, py = b(P.ToMM(p.GetPosition().x), P.ToMM(p.GetPosition().y))
            top = py + P.ToMM(p.GetBoundingBox().GetHeight()) / 2
            vx, vy = px, top + 0.15 + VIA_D / 2 - 0.05
            pre.append((px, py, vx, vy))
            i0, j0 = gi(px, py); i1, j1 = gi(vx, vy)
            gr.stamp_path([(1, i0, j) for j in range(j0, j1 + 1)], 0.3, GND)
            gr.stamp_path([(0, i1, j1), (1, i1, j1)], VIA_D, GND)
            t_ = P.PCB_TRACK(bd); t_.SetLayer(P.B_Cu); t_.SetWidth(mm(0.3)); t_.SetNet(nets['GND'])
            t_.SetStart(V(*k(px, py))); t_.SetEnd(V(*k(vx, vy))); bd.Add(t_)
            v_ = P.PCB_VIA(bd); v_.SetPosition(V(*k(vx, vy))); v_.SetWidth(mm(VIA_D)); v_.SetDrill(mm(VIA_DR)); v_.SetNet(nets['GND']); bd.Add(v_)
    # ---------- 布线 ----------
    order = ['LED_IO1', 'LED_IO2', 'LED_IO3', 'LED_IO4', 'LED_MOSI', 'KEY4',      # 插座 ↔ 电阻 (直下, 先占)
             '+3V3', 'KEY2', 'KEY3', 'D1_RK', 'D1_GK', 'D1_BK', 'D2_K', 'D3_K', 'D4_K']
    routed = {}
    fails = []
    for net in order:
        w = W_PWR if net == '+3V3' else W_SIG
        pads = padinfo[net]
        # 同一封装内同网焊盘 (按键 1/2) 只需连一个
        seen = set(); groups = []
        for (ref, num), cells, c in pads:
            seen.add(ref); groups.append(((ref, num), cells, c))
        tree = set(groups[0][1])
        rest = groups[1:]
        allcells = []
        while rest:
            # 最近的下一个焊盘
            tc = np.array([(i * G, j * G) for (_, i, j) in list(tree)[::7] or list(tree)])
            rest.sort(key=lambda g: np.min(np.hypot(tc[:, 0] - g[2][0], tc[:, 1] - g[2][1])))
            g = rest.pop(0)
            path = astar(gr, NID[net], w, set(g[1]), tree)
            if path is None:
                fails.append((net, g[0])); continue
            gr.stamp_path(path, w, NID[net])
            # 过孔也印到两层
            for a, c2 in zip(path, path[1:]):
                if a[0] != c2[0]:
                    gr.stamp_path([(0, a[1], a[2]), (1, a[1], a[2])], VIA_D, NID[net])
            tree |= set(path)
            allcells.append(path)
        routed[net] = allcells
    # 写进板
    for net, paths in routed.items():
        w = W_PWR if net == '+3V3' else W_SIG
        for path in paths:
            for it in path_to_segments(path):
                if it[0] == 'seg':
                    _, l, (i0, j0), (i1, j1) = it
                    t = P.PCB_TRACK(bd); t.SetLayer(P.F_Cu if l == 0 else P.B_Cu); t.SetWidth(mm(w))
                    t.SetStart(V(*k(i0 * G, j0 * G))); t.SetEnd(V(*k(i1 * G, j1 * G))); t.SetNet(nets[net]); bd.Add(t)
                else:
                    i, j = it[1]
                    v = P.PCB_VIA(bd); v.SetPosition(V(*k(i * G, j * G))); v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DR))
                    v.SetNet(nets[net]); bd.Add(v)
    # ---------- GND 缝合孔 (两层都空的地方, 2.5 栅格) + GND 焊盘旁 ----------
    vfree = ~(dilate((gr.occ[0] != 0) & (gr.occ[0] != GND), VIA_D / 2 + CLR + 0.15) |
              dilate((gr.occ[1] != 0) & (gr.occ[1] != GND), VIA_D / 2 + CLR + 0.15) |
              dilate(gr.pad, VIA_D / 2 + 0.2) | dilate((gr.occ[0] == -1) | (gr.occ[1] == -1), VIA_D / 2 + 0.2))
    stitch = []
    def ok(i, j):
        return 0 <= i < NX and 0 <= j < NY and vfree[j, i] and all(math.hypot((i - a) * G, (j - c) * G) >= 1.6 for a, c in stitch)
    # 每个 GND 焊盘旁一颗 (最近可用点)
    for (_ref, _num), cells, (cx, cy) in padinfo['GND']:
        ci, cj = gi(cx, cy)
        best = None
        for r in np.arange(0.5, 4.0, 0.1):
            for a in range(0, 360, 15):
                i, j = gi(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
                if ok(i, j):
                    best = (i, j); break
            if best:
                break
        if best:
            stitch.append(best)
    for Xs in np.arange(2.0, KB.W - 1.0, 2.5):
        for Ys in np.arange(2.0, KB.H - 1.0, 2.5):
            i, j = gi(Xs, Ys)
            if ok(i, j):
                stitch.append((i, j))
    for i, j in stitch:
        v = P.PCB_VIA(bd); v.SetPosition(V(*k(i * G, j * G))); v.SetWidth(mm(VIA_D)); v.SetDrill(mm(VIA_DR))
        v.SetNet(nets['GND']); bd.Add(v)
    # ---------- GND 铺铜 两层 ----------
    for lay in (P.F_Cu, P.B_Cu):
        z = P.ZONE(bd); z.SetLayer(lay); z.SetNet(nets['GND'])
        ol = z.Outline(); ol.NewOutline()
        for X, Y in ((0, 0), (KB.W, 0), (KB.W, KB.H), (0, KB.H)):
            ol.Append(mm(OX + X), mm(OY - Y))
        z.SetMinThickness(mm(0.2)); z.SetLocalClearance(mm(0.2)); z.SetThermalReliefGap(mm(0.25))
        z.SetThermalReliefSpokeWidth(mm(0.3)); z.SetPadConnection(P.ZONE_CONNECTION_THERMAL)
        z.SetIslandRemovalMode(P.ISLAND_REMOVAL_MODE_ALWAYS)
        z.SetAssignedPriority(0); z.SetZoneName(f'GND_{"F" if lay == P.F_Cu else "B"}')
        bd.Add(z)
    # ---------- 丝印 (只在背面) ----------
    def btext(s, X, Y, size=0.8, lay=P.B_SilkS):
        t = P.PCB_TEXT(bd); t.SetText(s); t.SetLayer(lay); t.SetPosition(V(*k(X, Y)))
        t.SetTextSize(V(size, size)); t.SetTextThickness(mm(0.12)); t.SetMirrored(lay == P.B_SilkS); bd.Add(t)
    btext('POV3D KEY V1.2', 20.0, 21.0, 0.9)
    btext('J1 GH1.25-12P  cable pin1<->pin1', 20.0, 19.3, 0.7)
    # 引脚 1 标记 + 与结构 agent 的 pin1 位置核对
    p1 = [p for p in fps['J1'].Pads() if p.GetNumber() == '1'][0]
    px, py = b(P.ToMM(p1.GetPosition().x), P.ToMM(p1.GetPosition().y))
    if m and m.get('connector', {}).get('pin1_board_XY'):
        ex, ey = m['connector']['pin1_board_XY']
        assert abs(px - ex) < 0.01 and abs(py - ey) < 0.01, f'J1 pin1 ({px:.3f},{py:.3f}) != mech {ex},{ey}'
        print(f'J1 pin1 = ({px:.3f}, {py:.3f}) 与 mech_constraints 一致')
    btext('1', px, jpos['Y'] - 2.45 - 0.9, 0.8)        # 插口下方 (板下沿侧)

    # 背面件外包 (板系, 庭院 bbox) + 高度 → back_parts.json (给结构核让位; 铺铜由 kicad-cli 原生 refill)
    HGT = {'J1': 4.25, 'C1': 0.9}
    bp = {}
    for ref, f in fps.items():
        if f.GetLayer() != P.B_Cu:
            continue
        cy = f.GetCourtyard(P.B_CrtYd).BBox()
        X0, Y1 = b(P.ToMM(cy.GetLeft()), P.ToMM(cy.GetTop())); X1, Y0 = b(P.ToMM(cy.GetRight()), P.ToMM(cy.GetBottom()))
        bp[ref] = dict(courtyard_board_XY=[round(X0, 3), round(Y0, 3), round(X1, 3), round(Y1, 3)], height=HGT.get(ref, 0.6))
    json.dump(dict(_note='背面件 庭院外包 [X0,Y0,X1,Y1] 板系 (正视, 原点左下) + 离板背面高度 mm; J1 插口朝 Y=0, 插口面 Y=%.2f' % (jpos['Y'] - 2.45),
                   parts=bp), open(os.path.join(PRJ, 'back_parts.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    out = os.path.join(PRJ, S.NAME + '.kicad_pcb')
    bd.Save(out) if hasattr(bd, 'Save') else P.SaveBoard(out, bd)
    print('写出', out)
    print('J1', jpos, '封装', fpnames)
    print('布线失败', fails if fails else '无')
    print('缝合孔', len(stitch))
    return fails


if __name__ == '__main__':
    sys.exit(1 if main() else 0)
