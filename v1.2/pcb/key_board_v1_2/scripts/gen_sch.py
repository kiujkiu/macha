# -*- coding: utf-8 -*-
"""POV3D V1.2 按键板 (key_board_v1_2) 原理图生成器.
    python3 gen_sch.py   →  ../key_board_v1_2.kicad_sch
网表真值在本文件 PARTS / NETS (gen_pcb.py 也 import 这里)。
符号: KiCad 标准库 (引脚号与手册一致, 已核):
  Device:LED_RAGB  1=R阴 2=公共阳 3=G阴 4=B阴 (= XL-1615RGBC-RF 手册 p8: 1 R / 2 + / 3 G / 4 B)
  Device:LED       1=K 2=A (= A-SP192YR6AC 手册 p7: 1 −, 2 +)
  Switch:SW_MEC_5G 1,2 一侧 / 3,4 一侧 (= ZX-QC66-7.5TP 电路图: 1–2 通, 3–4 通, 按下两组接通)
  Connector_Generic_MountingPin:Conn_01x12_MountingPin (SM12B-GHS-TB, MP = 两个固定焊盘)
"""
import os
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sexp import Str, dump, lib_symbol, pin_xy  # noqa: E402

PRJ = os.path.normpath(os.path.join(HERE, '..'))
NAME = 'key_board_v1_2'
SYMDIR = '/usr/share/kicad/symbols'
NS = uuid.UUID('4b1e0c2a-1d2c-4a12-9b00-0000000000a2')


def U(k):
    return str(uuid.uuid5(NS, k))


# 封装 (库 key_board = lib/key_board.pretty, 由封装 agent 出; gen_pcb 读同一份)
FP = dict(
    SW='key_board:SW_ZX-QC66-7.5TP',
    RGB='key_board:LED_XL-1615RGBC',
    LED='key_board:LED_0603_A-SP192YR6AC',
    J='key_board:JST_GH_SM12B-GHS-TB',
    R='Resistor_SMD:R_0603_1608Metric',
    C='Capacitor_SMD:C_0603_1608Metric',
)
if os.path.exists(os.path.join(PRJ, 'lib', 'fp_map.py')):     # 封装 agent 若给了名字映射就用它
    exec(open(os.path.join(PRJ, 'lib', 'fp_map.py')).read(), {'FP': FP})

# ref: (lib, symbol, value, fp key, side, LCSC/MPN 注释, {pin: net})
PARTS = {
    'J1': ('Connector_Generic_MountingPin', 'Conn_01x12_MountingPin', 'SM12B-GHS-TB(LF)(SN)', 'J', 'B',
           {'1': 'LED_IO1', '2': 'LED_IO2', '3': 'LED_IO3', '4': 'LED_IO4', '5': 'GND', '6': 'LED_MOSI',
            '7': 'GND', '8': '+3V3', '9': 'KEY2', '10': 'KEY3', '11': 'KEY4', '12': 'GND', 'MP': 'GND'}),
    'SW1': ('Switch', 'SW_MEC_5G', 'ZX-QC66-7.5TP', 'SW', 'F', {'1': 'KEY2', '2': 'KEY2', '3': 'GND', '4': 'GND'}),
    'SW2': ('Switch', 'SW_MEC_5G', 'ZX-QC66-7.5TP', 'SW', 'F', {'1': 'KEY3', '2': 'KEY3', '3': 'GND', '4': 'GND'}),
    'D1': ('Device', 'LED_RAGB', 'XL-1615RGBC-RF', 'RGB', 'F', {'1': 'D1_RK', '2': '+3V3', '3': 'D1_GK', '4': 'D1_BK'}),
    'D2': ('Device', 'LED', 'A-SP192YR6AC-A01-4T', 'LED', 'F', {'1': 'D2_K', '2': '+3V3'}),
    'D3': ('Device', 'LED', 'A-SP192YR6AC-A01-4T', 'LED', 'F', {'1': 'D3_K', '2': '+3V3'}),
    'D4': ('Device', 'LED', 'A-SP192YR6AC-A01-4T', 'LED', 'F', {'1': 'D4_K', '2': '+3V3'}),
    'R1': ('Device', 'R', '2.7k', 'R', 'F', {'1': 'D1_RK', '2': 'LED_IO1'}),
    'R2': ('Device', 'R', '1k', 'R', 'F', {'1': 'D1_GK', '2': 'LED_IO2'}),
    'R3': ('Device', 'R', '1k', 'R', 'F', {'1': 'D1_BK', '2': 'LED_MOSI'}),
    'R4': ('Device', 'R', '2.7k', 'R', 'F', {'1': 'D2_K', '2': 'LED_IO4'}),
    'R5': ('Device', 'R', '2.7k', 'R', 'F', {'1': 'D3_K', '2': 'LED_IO3'}),
    'R6': ('Device', 'R', '2.7k', 'R', 'F', {'1': 'D4_K', '2': 'KEY4'}),
    'C1': ('Device', 'C', '100n', 'C', 'F', {'1': '+3V3', '2': 'GND'}),
}
# LCSC / MPN (lib/parts.csv, 封装 agent 核; 阻容全 0603 JLC Basic)
LCSC = {'J1': ('C265421', 'SM12B-GHS-TB(LF)(SN)'), 'SW1': ('C7470157', 'ZX-QC66-7.5TP'), 'SW2': ('C7470157', 'ZX-QC66-7.5TP'),
        'D1': ('C965840', 'XL-1615RGBC-RF'), 'D2': ('C5355430', 'A-SP192YR6AC-A01-4T'), 'D3': ('C5355430', 'A-SP192YR6AC-A01-4T'),
        'D4': ('C5355430', 'A-SP192YR6AC-A01-4T'), 'R1': ('C13167', '0603WAF2701T5E'), 'R2': ('C21190', '0603WAF1001T5E'),
        'R3': ('C21190', '0603WAF1001T5E'), 'R4': ('C13167', '0603WAF2701T5E'), 'R5': ('C13167', '0603WAF2701T5E'),
        'R6': ('C13167', '0603WAF2701T5E'), 'C1': ('C14663', 'CC0603KRX7R9BB104')}
DESC = {
    'J1': 'JST GH 1.25 12P SMD 卧式, 背面 手焊 (JLC 不贴, 不进 CPL/JLC BOM); 接电机板 U24',
    'SW1': '上键 (板 11,18.5) → KEY2', 'SW2': '下键 (板 11,7.5) → KEY3',
    'D1': '三色 1615 共阳 (板 17,13)', 'D2': '单色1 红 0603 (板 21.5,13) → LED_IO4',
    'D3': '单色2 红 0603 (板 26,13) → LED_IO3', 'D4': '单色3 红 0603 (板 30.5,13) → KEY4 (改作输出)',
    'R1': 'RGB-R 限流', 'R2': 'RGB-G 限流', 'R3': 'RGB-B 限流', 'R4': '单色1 限流', 'R5': '单色2 限流', 'R6': '单色3 限流',
    'C1': '3V3 就近去耦',
}

# 原理图摆放 (x, y, rot) A3, mm, 1.27 栅格
PLACE = {
    'J1': (63.5, 88.9, 0),
    'SW1': (152.4, 50.8, 0), 'SW2': (152.4, 71.12, 0),
    'D1': (152.4, 106.68, 0),
    'R1': (198.12, 99.06, 90), 'R2': (198.12, 106.68, 90), 'R3': (198.12, 114.3, 90),
    'D2': (152.4, 134.62, 0), 'D3': (152.4, 147.32, 0), 'D4': (152.4, 160.02, 0),
    'R4': (198.12, 134.62, 90), 'R5': (198.12, 147.32, 90), 'R6': (198.12, 160.02, 90),
    'C1': (88.9, 152.4, 0),
}

NOTE_CALC = """限流电阻 (3V3 供电, IO 拉低灌电流, V_OL ≈ 0.1 V; 用户 11-13: 原 270/100 Ω 太亮, 全部 ×10, 目标 ≈0.3–0.5 mA 指示亮度):
  I = (3.3 − Vf − 0.1) / R
  红 (单色 D2–D4, RGB-R): Vf ≈ 1.7–1.8 V @ <1 mA
      R = 2.7 kΩ (C13167) → (3.3 − 1.75 − 0.1) / 2700 ≈ 0.54 mA
  绿 / 蓝 (RGB-G/B): Vf ≈ 2.5–2.7 V @ <1 mA
      R = 1 kΩ (C21190) → (3.3 − 2.6 − 0.1) / 1000 ≈ 0.6 mA (Vf 2.8 → 0.4 mA; Vf 2.9 → 0.3 mA)
  G/B 在 3V3 下对 Vf 敏感, 三色比例按实测调 (固件 PWM 或换电阻); 太暗可回到 G/B 330–470 Ω / 红 1 kΩ。"""

NOTE_IF = """接口 J1 = GH1.25 12P (SM12B-GHS-TB), 对电机板 U24 同型座; 板上不加上拉 (电机板每个 KEY 已有 10k 上拉到 3V3 + 电容):
  1 LED_IO1 → RGB-R (R1)      5 GND        9  KEY2  ← 上键 SW1 (按下接地, 低有效)
  2 LED_IO2 → RGB-G (R2)      6 LED_MOSI → RGB-B (R3)   10 KEY3  ← 下键 SW2
  3 LED_IO3 → 单色2 (R5)      7 GND        11 KEY4  → 单色3 (R6) (KEY 线改作输出; 电机板上的 10k 上拉无害, 其电容会让边沿变慢, 只做开关/低频 PWM)
  4 LED_IO4 → 单色1 (R4)      8 +3V3 (电机板选 3V3)   12 GND     MP 固定焊盘 = GND
  LED 全部 3V3 → LED → 电阻 → IO, IO 输出低 = 亮。
  用户 11-13: RGB-B 与单色2 对调, 使 RGB 三色都在硬件 PWM 脚: R=P4_10 TIM3_CH0, G=P4_9 TIM3_CH1, B=P1_9 TIM0_CH1/TIM2_CH0 (P4_7 无定时器)。

!! 线序: 本板 J1 第 n 脚必须接电机板 U24 第 n 脚 (1↔1 … 12↔12), 两头的信号定义才对得上。
   线要 "1 对 1" (pin1↔pin1) 的 GH1.25 12P 双头线 = 两头卡扣分在扁平线两面 (平放时一头卡扣朝上、一头朝下; 商家多叫 "反向线")。
   两头卡扣在同一面的平直线 (商家多叫 "同向线") 是 pin n ↔ pin 13−n —— 不能用: 电机板 3V3 (pin8) 会落到本板 pin5 = GND, 直接短路。
   各家 "同向 / 反向" 叫法不统一, 下单按 "1 对 1 (pin1-pin1)" 写明; 首次上电前用万用表核: 本板 pin8 ↔ 电机板 U24 pin8 通, 本板 pin5/7/12 = GND。"""


def sym_instance(ref, lib, name, value, fp, x, y, rot, pins, desc):
    if name == 'R':
        rp, vp = (x, y - 2.54), (x, y + 2.54)
    elif name == 'C':
        rp, vp = (x + 2.54, y - 1.27), (x + 2.54, y + 1.27)
    elif name == 'LED':
        rp, vp = (x, y - 3.81), (x, y + 3.81)
    elif name == 'LED_RAGB':
        rp, vp = (x, y - 8.89), (x, y + 8.89)
    elif name.startswith('SW'):
        rp, vp = (x, y - 3.81), (x, y + 3.81)
    else:
        rp, vp = (x + 2.54, y - 17.78), (x + 2.54, y + 24.13)
    props = [('Reference', ref, rp, False), ('Value', value, vp, False),
             ('Footprint', fp, (x, y), True), ('Datasheet', '', (x, y), True), ('Description', desc, (x, y), True),
             ('LCSC', LCSC[ref][0], (x, y), True), ('MPN', LCSC[ref][1], (x, y), True)]
    e = ['symbol', ['lib_id', Str(f'{lib}:{name}')], ['at', x, y, rot], ['unit', 1],
         ['exclude_from_sim', 'no'], ['in_bom', 'yes'], ['on_board', 'yes'], ['dnp', 'no'], ['uuid', Str(U('sym' + ref))]]
    for k, v, (px, py), hide in props:
        p = ['property', Str(k), Str(v), ['at', round(px, 2), round(py, 2), rot], ['effects', ['font', ['size', 1.27, 1.27]]] + ([['hide', 'yes']] if hide else [])]
        e.append(p)
    for pn in sorted({p['num'] for p in pins}):
        e.append(['pin', Str(pn), ['uuid', Str(U(f'pin{ref}.{pn}'))]])
    e.append(['instances', ['project', Str(NAME), ['path', Str('/' + U('root')), ['reference', Str(ref)], ['unit', 1]]]])
    return e


def label(net, x, y, ang):
    just = ['justify', 'left', 'bottom'] if ang in (0, 90) else ['justify', 'right', 'bottom']
    return ['global_label', Str(net), ['shape', 'passive'], ['at', x, y, ang], ['fields_autoplaced', 'yes'], ['effects', ['font', ['size', 1.27, 1.27]], just], ['uuid', Str(U(f'lbl{net}{x}{y}'))]]


def text(t, x, y, size=1.5):
    return ['text', Str(t), ['exclude_from_sim', 'no'], ['at', x, y, 0],
            ['effects', ['font', ['size', size, size]], ['justify', 'left', 'top']], ['uuid', Str(U('txt' + t[:30]))]]


def main():
    libsyms = {}
    pins_of = {}
    for ref, (lib, name, *_rest) in PARTS.items():
        key = f'{lib}:{name}'
        if key not in libsyms:
            libsyms[key], pins_of[key] = lib_symbol(os.path.join(SYMDIR, lib + '.kicad_sym'), name, lib)
    items = []
    done = set()
    for ref, (lib, name, value, fpk, side, nets) in PARTS.items():
        key = f'{lib}:{name}'
        x, y, rot = PLACE[ref]
        pins = pins_of[key]
        assert {p['num'] for p in pins} == set(nets), (ref, {p['num'] for p in pins}, set(nets))
        items.append(sym_instance(ref, lib, name, value, FP[fpk], x, y, rot, pins, DESC[ref] + (' [背面]' if side == 'B' else ' [正面]')))
        for p in pins:
            px, py, a = pin_xy(x, y, rot, p)
            if (px, py) in done:          # 叠放隐藏脚 (SW 2/4) 与可见脚同点同网
                continue
            done.add((px, py))
            items.append(label(nets[p['num']], px, py, (a + 180) % 360))
    items.append(text(NOTE_IF, 25.4, 190.5, 1.4))
    items.append(text(NOTE_CALC, 228.6, 40.64, 1.4))
    items.append(text('单面贴 (用户 11-13): JLC 只贴顶面 (F) —— SW1 SW2 D1–D4 + R1–R6 C1 全在正面 (支架平板背面: 按键让位腔 / 每颗 LED Φ3.2 隔光孔 / R/C 共用让位腔)。\n'
                      '!! J1 (SM12B-GHS-TB) 在背面, 手焊: 平板盖住正面, J1 放不了正面。J1 不在 CPL 里 (封装标 exclude from pos), JLC BOM 也去掉 J1 (fab/*_手焊.csv)。\n'
                      '板系: 原点 = 板左下角 (从机器外面看正面), 整机 x = 20 − X, Z = 3 + Y。', 228.6, 25.4, 1.6))
    sch = ['kicad_sch', ['version', 20260306], ['generator', Str('claude-gen')], ['generator_version', Str('10.0')],
           ['uuid', Str(U('root'))], ['paper', Str('A3')],
           ['title_block', ['title', Str('POV3D V1.2 按键板 key_board_v1_2')], ['date', Str('2026-11-13')], ['rev', Str('V1.2')],
            ['company', Str('POV3D')], ['comment', 1, Str('2 键 + 1615 RGB + 3×0603 红; GH1.25 12P 接电机板 U24 (同向线 pin1↔pin1)')]],
           ['lib_symbols', *libsyms.values()], *items,
           ['sheet_instances', ['path', Str('/'), ['page', Str('1')]]], ['embedded_fonts', 'no']]
    out = os.path.join(PRJ, NAME + '.kicad_sch')
    open(out, 'w', encoding='utf-8').write(dump(sch) + '\n')
    print('写出', out)


if __name__ == '__main__':
    main()
