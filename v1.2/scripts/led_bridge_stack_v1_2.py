"""V1.2 灯板 + MIP LED + 桥板堆叠 3MF (用户 11-19「灯板和桥板堆叠的3mf」「把 led 装上, 装昨晚 2 个版本的 6 层桥板」)。
世界坐标同整机 (转轴原点, Z0 底盘顶); 夹条/梳齿/顶部件单独成件, 可在切片软件里隐藏。
桥板版本用参数选 (走 fpc_v1_2 的 FPC_BRIDGE_W 开关, 6 层 W v3, pcb/.../layout/r11/B6F/W):
    cd v1.2/scripts && ../../.venv/bin/python led_bridge_stack_v1_2.py flash      # W_flash.step  + final_flash.kicad_pcb
    cd v1.2/scripts && ../../.venv/bin/python led_bridge_stack_v1_2.py noflash    # W_noflash.step + final_noflash.kicad_pcb
    cd v1.2/scripts && ../../.venv/bin/python led_bridge_stack_v1_2.py old        # 11-11 结构简版 (8 层旧)
输出: ../assembly_v1_2_灯板+LED+桥板_<版本>.3mf
"""
import io, os, sys, contextlib
from pathlib import Path
VER = sys.argv[1] if len(sys.argv) > 1 else 'flash'
W = Path('/mnt/d/claude_workspace/pov3d/pcb/projects/POV3D_GW5A_Bridge_V2.0/layout/r11/B6F/W')
if VER in ('flash', 'noflash'):
    os.environ['FPC_BRIDGE_W'] = str(W / 'step' / f'W_{VER}.step')
    os.environ['FPC_BRIDGE_W_PCB'] = str(W / f'final_{VER}.kicad_pcb')
    os.environ.setdefault('FPC_OSC1_H', '1.1')       # 同 11-19 定稿 (STEP 无 OSC1 模型)
else: assert VER == 'old', VER
with contextlib.redirect_stdout(io.StringIO()):
    import build_v1_2 as B
    import v2_boards_v1_2 as V
    import led_support_v1_2 as L
    import fpc_v1_2 as F
from mf3_v1_2 import write3mf
_mb, _mt = V.led_mip(B)
LED_BASE = L.comp(list(L.pair(_mb))); LED_TOP = L.comp(list(L.pair(_mt)))
NM = {'flash': '6层 W v3 带flash', 'noflash': '6层 W v3 无flash', 'old': '11-11 结构简版'}[VER]
PARTS = [('灯板 A (+y)', L.led_a, '#145A32', 0.05), ('灯板 B (-y)', L.led_b, '#0E3B22', 0.05),
         ('MIP LED 4合1 基板部分 (黑) ×2×10368', LED_BASE, '#151515', 0.05), ('MIP LED 4合1 发光面 (红) ×2×10368', LED_TOP, '#FF2020', 0.05),
         (f'桥板 A ({NM})', F.bridge_a, '#1E8449', 0.05), (f'桥板 B ({NM})', F.bridge_b, '#27AE60', 0.05),
         ('灯板夹条 led_bar', L.bar_s, '#8E7CC3', 0.05), ('灯板梳齿 led_comb', L.comb_s, '#9FC5E8', 0.05),
         ('灯板顶部件 led_top', L.top, '#6FA8DC', 0.05)]
for n, s, _, _ in PARTS: print(n, [round(x, 2) for x in B.bbox(s)], flush=True)
write3mf(str(B.V12 / f'assembly_v1_2_灯板+LED+桥板_{VER}.3mf'), PARTS)
