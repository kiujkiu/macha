# -*- coding: utf-8 -*-
"""Minimal KiCad s-expression reader + symbol extractor (key_board_v1_2 generators)."""
import math
import re

_TOK = re.compile(r'\s*(?:(\()|(\))|("(?:\\.|[^"\\])*")|([^\s()"]+))')


def parse(text):
    stack = [[]]
    pos = 0
    n = len(text)
    while pos < n:
        m = _TOK.match(text, pos)
        if not m or m.end() == pos:
            if text[pos:].strip() == '':
                break
            raise ValueError(f'parse error at {pos}: {text[pos:pos + 40]!r}')
        pos = m.end()
        o, c, s, a = m.groups()
        if o:
            stack.append([])
        elif c:
            t = stack.pop()
            stack[-1].append(t)
        elif s is not None:
            stack[-1].append(Str(s[1:-1].replace('\\"', '"').replace('\\\\', '\\')))
        elif a is not None:
            stack[-1].append(a)
    return stack[0][0]


class Str(str):
    """quoted string atom"""


def dump(e, ind=0):
    if isinstance(e, list):
        if not e:
            return '()'
        simple = all(not isinstance(x, list) for x in e)
        if simple:
            return '(' + ' '.join(dump(x) for x in e) + ')'
        pad = '\t' * (ind + 1)
        head = []
        rest = []
        for i, x in enumerate(e):
            if not rest and not isinstance(x, list):
                head.append(dump(x))
            else:
                rest.append(x)
        return '(' + ' '.join(head) + ''.join('\n' + pad + dump(x, ind + 1) for x in rest) + '\n' + '\t' * ind + ')'
    if isinstance(e, Str):
        return '"' + e.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'
    return str(e)


def find(e, key):
    return [x for x in e if isinstance(x, list) and x and x[0] == key]


def lib_symbol(lib_path, name, lib_nick):
    """Return (embedded symbol s-expr renamed lib_nick:name, pins[{num,name,x,y,ang,unit}])"""
    root = parse(open(lib_path, encoding='utf-8').read())
    syms = {x[1]: x for x in find(root, 'symbol')}
    s = syms[name]
    assert not find(s, 'extends'), f'{name} extends — not supported'
    s = list(s)
    s[1] = Str(f'{lib_nick}:{name}')
    pins = []
    for sub in find(s, 'symbol'):
        unit = int(str(sub[1]).rsplit('_', 2)[-2])
        for p in find(sub, 'pin'):
            at = find(p, 'at')[0]
            pins.append(dict(num=str(find(p, 'number')[0][1]), name=str(find(p, 'name')[0][1]),
                             x=float(at[1]), y=float(at[2]), ang=int(float(at[3])) if len(at) > 3 else 0, unit=unit))
    return s, pins


def pin_xy(sx, sy, rot, p):
    """schematic connection point of pin p for symbol at (sx, sy, rot) — lib y-up, sch y-down"""
    r = math.radians(rot)
    x = p['x'] * math.cos(r) - p['y'] * math.sin(r)
    y = p['x'] * math.sin(r) + p['y'] * math.cos(r)
    return round(sx + x, 4), round(sy - y, 4), (p['ang'] + rot) % 360
