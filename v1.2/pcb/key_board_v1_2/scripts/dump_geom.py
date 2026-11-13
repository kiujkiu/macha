# -*- coding: utf-8 -*-
"""dump pads / tracks / vias of key_board_v1_2.kicad_pcb to JSON (board coords) for plot_layers.py"""
import json
import os
import sys

import pcbnew as P

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen_pcb as G  # noqa: E402

bd = P.LoadBoard(os.path.join(G.PRJ, G.S.NAME + '.kicad_pcb'))
mm = P.ToMM
out = dict(pads=[], tracks=[], vias=[], fps=[], W=G.KB.W, H=G.KB.H, MH=G.KB.MH, KO_F=G.KB.FRONT_KO_D, KO_B=G.KB.BACK_KO_D)
for f in bd.GetFootprints():
    X, Y = G.b(mm(f.GetPosition().x), mm(f.GetPosition().y))
    out['fps'].append(dict(ref=f.GetReference(), X=X, Y=Y, side='F' if f.GetLayer() == P.F_Cu else 'B'))
    for p in f.Pads():
    	bb = p.GetBoundingBox()
    	X0, Y1 = G.b(mm(bb.GetLeft()), mm(bb.GetTop())); X1, Y0 = G.b(mm(bb.GetRight()), mm(bb.GetBottom()))
    	out['pads'].append(dict(ref=f.GetReference(), num=p.GetNumber(), net=p.GetNetname(), box=[X0, Y0, X1, Y1],
    	                        F=p.IsOnLayer(P.F_Cu), B=p.IsOnLayer(P.B_Cu), hole=mm(p.GetDrillSize().x)))
for t in bd.GetTracks():
    if t.GetClass() == 'PCB_VIA':
        out['vias'].append(dict(p=G.b(mm(t.GetPosition().x), mm(t.GetPosition().y)), net=t.GetNetname()))
    else:
        out['tracks'].append(dict(a=G.b(mm(t.GetStart().x), mm(t.GetStart().y)), b=G.b(mm(t.GetEnd().x), mm(t.GetEnd().y)),
                                  w=mm(t.GetWidth()), L='F' if t.GetLayer() == P.F_Cu else 'B', net=t.GetNetname()))
json.dump(out, open(sys.argv[1], 'w'))
