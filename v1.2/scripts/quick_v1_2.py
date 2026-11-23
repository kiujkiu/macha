"""
V1.2 快速出单件 (甲级小改动用, 11-17 晚): 几何只建 1 遍, 只写点名件的 STL/STEP + 出它的图; 不写 3MF / 整机 / 其它件。
原来 build → export → drawings 三个脚本各 import 一遍 build_v1_2 (整套几何建 3 遍), 这里合成 1 个进程。

    cd v1.2/scripts && ../../.venv/bin/python quick_v1_2.py base_disc_v1_2_gf [其它件 ...] [--no-draw]
    ../../.venv/bin/python quick_v1_2.py --list          # 看支持哪些件

什么时候不能用 (按 feedback 分级): 动了孔位 / Z 高 / 被多件读的常量 (乙/丙级) 仍要跑 check 或全流程;
整机 3MF 不会更新, 需要看整机时再跑 export_3mf_v1_2.py。
"""
import sys, io, time, runpy, shutil, contextlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

# 1) build_v1_2 里直接有形体的件: 代号 → (build_v1_2 变量名, out/ 下的旧名或 None, out 打印姿态翻面?)
B_PARTS = {
    'base_disc_v1_2_gf': ('disc_print', 'base_disc_D220x4p5_v1_2_gf', False),   # 11-18 玻纤板方案 (旧 base_disc_v1_2 一体 6 厚冻结)
    'coil_ring_v1_2': ('ring', None, False),
    'flange_disc_v1_2': ('flange_disc', None, False),
    'mounting_flange_v1_2': ('mounting_flange', None, False),
    'ir_clamp_v1_2': ('ir_clamp', None, False),   # 11-23 光电发射板压片 (定子盘底面, 2 颗 B 螺丝夹住)
    'hub_disc_v1_2': ('hub', 'hub_disc_v1_2', False),
    'rim_ring_v1_2_D170': ('rim', 'rim_ring_v1_2_D170', True),
    'glass_shroud_v1_2': ('seat', None, False),
    'glass_shroud_lower_v1_2': ('shroud_lo', None, False),
    'glass_shroud_upper_v1_2': ('shroud_hi', None, False),
    'glass_clamp_ring_v1_2': ('clamp_ring', None, False),
    'glass_top_v1_2': ('glass_top', None, False),
    'glass_top_hub_v1_2': ('glass_top_hub', None, False),
    'glass_top_clamp_v1_2': ('glass_top_clamp', None, False),
}
NO_MODELS = {'hub_disc_v1_2'}            # 同 export_3mf: 毂盘只写 out/ (图纸自己写装配 STL)
# 2) 各自有生成脚本的件: 代号 → 脚本 (跑它的 __main__, build_v1_2 已在内存里不再重建)
S_PARTS = {
    **{k: 'led_support_v1_2.py' for k in ('led_post_a_v1_2', 'led_post_b_v1_2', 'led_bar_v1_2', 'led_top_v1_2', 'led_comb_v1_2')},
    **{k: 'rotor_shroud_v1_2.py' for k in ('rotor_shroud_a_v1_2', 'rotor_shroud_b_v1_2', 'rotor_lid_v1_2', 'rotor_lid_b_v1_2')},
    'wireless_holder_v1_2': 'wireless_holder_v1_2.py',
    'mr30_seat_v1_2': 'motor_wire_v1_2.py', 'motor_wire_clamp_v1_2': 'motor_wire_v1_2.py',
    'mr30_seat_v1_2_old': 'motor_wire_v1_2.py', 'motor_wire_clamp_v1_2_old': 'motor_wire_v1_2.py',   # 11-18 旧一体底盘版
    'mr30_floor_v1_2': 'motor_wire_v1_2.py', 'mr30_floor_v1_2_old': 'motor_wire_v1_2.py',   # 11-18 MR30 座下片 (拆 2 件)
    'rim_ring_v1_2b': 'rotor_b_v1_2.py', 'screen_sup_a_v1_2b': 'rotor_b_v1_2.py', 'screen_sup_b_v1_2b': 'rotor_b_v1_2.py',   # 11-21 屏幕支撑件 PETG 打印 A ×2 + B ×2 (取代 11-20 玻纤板 ×4 + 侧立件 ×2; rotor_b 一次写全部)
    'rotor_shroud_b_a_v1_2b': 'rotor_shroud_b_v1_2.py', 'rotor_shroud_b_b_v1_2b': 'rotor_shroud_b_v1_2.py',
    'base_fr4_v1_2': 'fr4_base_v1_2.py',
    'mos_clamp_v1_2': 'mos_clamp_v1_2.py', 'cap_clamp_v1_2': 'cap_clamp_v1_2.py',
    'key_bracket_v1_2': 'key_bracket_v1_2.py', 'key_cap_v1_2': 'key_cap_v1_2.py', 'light_pipe_v1_2': 'light_pipe_v1_2.py',
}
# 成品文件夹 (同 export_3mf / build_drawings 的 _GROUPS / _FOLDER)
GROUP = {'flange_disc_v1_2': '定子盘', 'mounting_flange_v1_2': '定子盘', 'rim_ring_v1_2_D170': '转子盘', 'hub_disc_v1_2': '转子盘'}

args = [a for a in sys.argv[1:] if not a.startswith('--')]
if '--list' in sys.argv or not args:
    print('盘类/玻璃件 (build_v1_2):', ' '.join(B_PARTS)); print('独立脚本件:', ' '.join(S_PARTS)); sys.exit(0)
bad = [a for a in args if a not in B_PARTS and a not in S_PARTS]
if bad: sys.exit(f'不认识的件: {bad}  (--list 看列表)')
DRAW = '--no-draw' not in sys.argv

T0 = time.time()
def lap(msg): print(f'[{time.time() - T0:5.1f}s] {msg}', flush=True)

with contextlib.redirect_stdout(io.StringIO()):
    import build_v1_2 as B
lap('几何建好 (build_v1_2, 1 遍)')

from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.gp import gp_Trsf, gp_Vec, gp_Ax1, gp_Pnt, gp_Dir
def stl(sh, f):
    BRepMesh_IncrementalMesh(sh, 0.02, False, 0.2, True); w = StlAPI_Writer(); w.ASCIIMode = False; w.Write(sh, str(f))
_fx = gp_Trsf(); _fx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), 3.141592653589793)

for code in args:
    if code in B_PARTS:
        var, outname, flip = B_PARTS[code]; sh = getattr(B, var)
        assert B.vol(sh) > 1, f'{code} 体积为 0 (布尔失败), 不写文件'
        if code not in NO_MODELS:
            d = B.V12 / 'models' / code; d.mkdir(parents=True, exist_ok=True)
            stl(sh, d / f'{code}.stl'); B.write_doc([(code, sh, '#8A8F98', None, False)], d / f'{code}.step', code)
        if outname:                                  # out/零件 (装配位) + out/打印STL (打印姿态, 落床)
            B.write_doc([(outname, sh, '#8A8F98', None, False)], B.OUT / '零件' / f'{outname}.step', outname)
            t = B.xf(sh, _fx) if flip else sh
            tt = gp_Trsf(); tt.SetTranslation(gp_Vec(0, 0, -B.bbox(t)[2])); stl(B.xf(t, tt), B.OUT / '打印STL' / f'{outname}.stl')
        lap(f'{code}: STL/STEP 已写')
for scr in dict.fromkeys(S_PARTS[c] for c in args if c in S_PARTS):
    _argv = sys.argv; sys.argv = [scr]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(HERE / scr), run_name='__main__')
    finally:
        sys.argv = _argv
    lap(f'{scr} 已跑 (写它自己的件)')

if DRAW:
    _argv = sys.argv; sys.argv = ['build_drawings_v1_2.py', *args]
    try:
        g = runpy.run_path(str(HERE / 'build_drawings_v1_2.py'), run_name='__main__')
    finally:
        sys.argv = _argv
    nod = [c for c in args if c not in {s['code'] for s in g['SPECS']}]
    if nod: print('  (这些件不在 build_drawings_v1_2 里, 没出图:', nod, ')')
    lap('出图完成')

for code in args:                                    # 成品文件夹同步 STEP/STL (图纸 build_drawings 已拷)
    if code not in GROUP: continue
    gd = B.V12 / GROUP[code]; gd.mkdir(exist_ok=True)
    src = [B.V12 / 'models' / code / f'{code}.{e}' for e in ('step', 'stl')] if B_PARTS[code][1] is None else \
          [B.OUT / '零件' / f'{B_PARTS[code][1]}.step', B.OUT / '打印STL' / f'{B_PARTS[code][1]}.stl']
    for f in src:
        if not f.exists(): continue
        try: shutil.copy2(f, gd / f.name)
        except PermissionError: shutil.copy2(f, gd / f'{f.stem}.NEW{f.suffix}'); print('  被占用, 另存 .NEW:', f.name)
    lap(f'{code} → {GROUP[code]}/')
lap('完成')
