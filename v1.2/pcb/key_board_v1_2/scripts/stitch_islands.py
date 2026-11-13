# -*- coding: utf-8 -*-
"""铺铜后补缝合孔: 每层 GND 填充里没有 GND 过孔 / 没连到主体的碎块, 找一个合法点打 GND 过孔 (两层都落在 GND 填充里, 离异网铜 ≥ 0.15+余量)。
    python3 stitch_islands.py <board.kicad_pcb>   (之后要再 kicad-cli --refill-zones)
返回码 = 新加过孔数 (0 = 已无孤岛)"""
import sys

import pcbnew as P

f = sys.argv[1]
bd = P.LoadBoard(f)
mm, FM = P.ToMM, P.FromMM
VIA_D, VIA_DR, CLR = 0.6, 0.3, 0.15 + 0.05
gnd = bd.FindNet('GND')
zones = {z.GetLayer(): z for z in bd.Zones() if not z.GetIsRuleArea() and z.GetNetname() == 'GND'}
rule = [z for z in bd.Zones() if z.GetIsRuleArea()]
fills = {l: z.GetFilledPolysList(l) for l, z in zones.items()}
gvias = [t for t in bd.GetTracks() if t.GetClass() == 'PCB_VIA' and t.GetNetCode() == gnd.GetNetCode()]
gpads = [p for fp in bd.GetFootprints() for p in fp.Pads() if p.GetNetCode() == gnd.GetNetCode()]


def items_other():
    out = []
    for t in bd.GetTracks():
        if t.GetNetCode() != gnd.GetNetCode():
            out.append(t)
    for fp in bd.GetFootprints():
        for p in fp.Pads():
            if p.GetNetCode() != gnd.GetNetCode():
                out.append(p)
    return out


OTH = items_other()
HOLES = [p for fp in bd.GetFootprints() for p in fp.Pads() if p.GetDrillSize().x > 0]
ALLPADS = [p for fp in bd.GetFootprints() for p in fp.Pads()]


def legal(pt):
    c = P.SHAPE_CIRCLE(pt, FM(VIA_D / 2))
    for it in OTH:
        for l in (P.F_Cu, P.B_Cu):
            if it.IsOnLayer(l) and it.GetEffectiveShape(l).Collide(c, FM(CLR)):
                return False
    for p in ALLPADS:                       # 不打在任何焊盘上 / 旁 (含 GND 焊盘, 防吸锡)
        for l in (P.F_Cu, P.B_Cu):
            if p.IsOnLayer(l) and p.GetEffectiveShape(l).Collide(c, FM(0.1)):
                return False
    for h in HOLES:
        if (h.GetPosition() - pt).EuclideanNorm() < FM(VIA_D / 2 + mm(h.GetDrillSize().x) / 2 + 0.3):
            return False
    for v in gvias:
        if (v.GetPosition() - pt).EuclideanNorm() < FM(VIA_D + 0.3):
            return False
    for z in rule:
        if z.GetDoNotAllowVias() and z.Outline().Contains(pt):
            return False
    # 两层都得落在 GND 填充里 (离填充边留 via 半径)
    for l in (P.F_Cu, P.B_Cu):
        if not fills[l].Contains(pt, -1, 0):
            return False
        sh = P.SHAPE_CIRCLE(pt, FM(VIA_D / 2 - 0.05))
        ok = False
        for i in range(fills[l].OutlineCount()):
            o = fills[l].Outline(i)
            if o.PointInside(pt) and all(o.PointInside(pt + P.VECTOR2I(int(FM(VIA_D / 2) * dx), int(FM(VIA_D / 2) * dy)))
                                         for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                ok = True
        if not ok:
            return False
    return True


added = 0
for l in (P.B_Cu, P.F_Cu):
    fp_ = fills[l]
    for i in range(fp_.OutlineCount()):
        o = fp_.Outline(i)
        has = any(o.PointInside(v.GetPosition()) for v in gvias)
        if has:
            continue
        # 有 GND 焊盘在里面 = 靠焊盘连 (另一层可能没连上) —— 一样补一个过孔
        bb = o.BBox()
        best = None
        step = FM(0.1)
        cx, cy = bb.Centre().x, bb.Centre().y
        cands = []
        for x in range(bb.GetLeft(), bb.GetRight(), step):
            for y in range(bb.GetTop(), bb.GetBottom(), step):
                pt = P.VECTOR2I(x, y)
                if o.PointInside(pt):
                    cands.append(((x - cx) ** 2 + (y - cy) ** 2, pt))
        for _, pt in sorted(cands, key=lambda q: q[0]):
            if legal(pt):
                best = pt
                break
        if best is None:
            print(f'层 {bd.GetLayerName(l)} 碎块 #{i} bbox ({mm(bb.GetLeft()):.2f},{mm(bb.GetTop()):.2f}) 找不到合法过孔点')
            continue
        v = P.PCB_VIA(bd); v.SetPosition(best); v.SetWidth(FM(VIA_D)); v.SetDrill(FM(VIA_DR)); v.SetNet(gnd); bd.Add(v)
        gvias.append(v); added += 1
        print(f'层 {bd.GetLayerName(l)} 碎块 #{i}: 补 GND 过孔 @ KiCad ({mm(best.x):.2f}, {mm(best.y):.2f})')
if added:
    P.SaveBoard(f, bd)
sys.exit(added)
