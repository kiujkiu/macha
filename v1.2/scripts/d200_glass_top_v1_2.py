"""V1.2 玻璃上 圆环玻璃 OD200×ID20×5 版 (2026-11-26 用户「顶部玻璃改成外径200，内径20，厚度5mm，出一个版本」)。
主模型默认仍 180×10; 本脚本设 GT_DISC=200 重建玻璃上三件 (红 / 绿 / 堵头), 出到单独文件夹, 不覆盖 180 版:
    cd v1.2/scripts && ../../.venv/bin/python d200_glass_top_v1_2.py
输出 v1.2/分组/4_玻璃及上盖/圆环玻璃200x5版/ : 零件/*_d200.{stl,step,pdf} + 组合图 + 3MF
"""
import os, sys, io, contextlib, math, shutil
os.environ['GT_DISC'] = '200'
from pathlib import Path
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
with contextlib.redirect_stdout(io.StringIO()):
    import build_drawings_v1_2 as BD
B, L, F = BD.B, BD.L, BD.F
assert B.GT_DISC == 200
OUT = B.V12 / '分组' / '4_玻璃及上盖' / '圆环玻璃200x5版'; PD = OUT / '零件'; PD.mkdir(parents=True, exist_ok=True)
from helpers import write_doc
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.gp import gp_Trsf, gp_Vec, gp_Ax1, gp_Pnt, gp_Dir
def wstl(sh, f):
    BRepMesh_IncrementalMesh(sh, 0.02, False, 0.2, True); w = StlAPI_Writer(); w.ASCIIMode = False; w.Write(sh, str(f))
def flip(sh):                                    # 翻面贴床 (三件都是顶面朝下打)
    fx = gp_Trsf(); fx.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.pi); t = B.xf(sh, fx)
    tz = gp_Trsf(); tz.SetTranslation(gp_Vec(0, 0, -B.bbox(t)[2])); return B.xf(t, tz)
X = dict(glass_top_v1_2=B.glass_top, glass_top_clamp_v1_2=B.glass_top_clamp, glass_top_hub_v1_2=B.glass_top_hub)
for code, sh in X.items():
    n = code + '_d200'
    write_doc([(n, sh, '#8A8F98', None, False)], PD / f'{n}.step', n); t = flip(sh); wstl(t, PD / f'{n}.stl'); print(n, '打印高', round(B.bbox(t)[5], 2))
nut_z = (B.GC_NUT_Z[1] - B.GC_NUT_FL_H, B.GC_NUT_Z[1])
for sp in BD.SPECS:
    if sp['code'] not in X: continue
    sp = dict(sp); sp['code'] += '_d200'; sp['date'] = '2026-11-26'
    sp['stl'] = B.V12 / 'out' / 'dwg_stl' / f"{sp['code']}.stl"; sp['src'] = f"v1.2/out/dwg_stl/{sp['code']}.stl (装配坐标; 打印件 分组/4_玻璃及上盖/圆环玻璃200x5版/零件/)"
    sp['short'] = sp['short'] + ' [圆环玻璃200×5版]'
    if sp['code'].startswith('glass_top_v1_2'):
        sp['title'] = sp['title'].replace('法兰螺母沉孔', '法兰螺母窝 (r105.2)')
        sp['holes'] = [dict(tag='N', pts=B.GC_PTS, spec=f"Φ{F(B.GC_HOLE)} 通 + 从外卡斜面往上: 六角窝 AF{F(B.GC_NUT_AF)} 到 Z{F(round(nut_z[0], 2))}, 顶 Φ{F(B.GC_NUT_D)}×{F(B.GC_NUT_FL_H)} 法兰窝 (顶 Z{F(round(nut_z[1], 2))})",
                            where=BD.ring_txt(B.GC_PTS) + f"  M3 法兰螺母法兰朝上从斜面塞进去顶到窝顶 (平边朝径向, 不转); 窝内壁离玻璃管外壁 r{F(B.go)} 约 1")] + sp['holes'][1:]
        sp['notes'] = [n_ for n_ in sp['notes'] if '沉孔底以上' not in n_] + [f"圆环玻璃 OD{F(B.GD_OD)}×{F(B.GD_T)} 直接放本件顶面 (r{F(B.GT_LEDGE_R)}–{F(B.SH_OUT)} 整面托); 8×M3 r{F(B.GC_R)} 在玻璃外"]
    if sp['code'].startswith('glass_top_clamp'):
        sp['notes'] = [f"玻璃窝 r{F(B.GD_POCKET_R)} 深 {F(round(B.GC_ZP - B.GC_Z0, 2))} = 玻璃 {F(B.GD_T)} + 余量 {F(B.GC_GAP)}; 窝口倒角 0.5; 顶外缘倒角 {F(B.GC_CH)}, 内缘 {F(B.GC_IN_CH)}",
                       f"红 {F(B.GT_TOP_T)} + 本件 {F(round(B.GC_Z1 - B.GC_Z0, 2))} = {F(round(B.GT_TOP_T + B.GC_Z1 - B.GC_Z0, 2))}; M3×{F(B.GC_SCREW_L)} 吃满螺母 {F(B.GC_ENG)}, 尾落进红件六角窝 (不碰玻璃管)",
                       "装配 (桌上): 红件翻面塞 8 颗法兰螺母 (点胶防掉) → 翻正 → 放圆环玻璃 (带堵头) → 本件 → 8 颗对角拧到绿件贴红件 → 整组套上玻璃管"]
    sp['stl'].parent.mkdir(parents=True, exist_ok=True); wstl(sp['shape'], sp['stl'])
    sp['out'] = PD / f"{sp['code']}_drawing.pdf"
    out, png, sl = BD.draw(sp); print('wrote', out)
src = B.V12 / 'models' / 'glass_top_disc_v1_2'                                   # 圆环玻璃询价图 (drawing_glass_top_disc_v1_2.py, 已是 200/20/5)
for f in ('glass_top_disc_v1_2_drawing.pdf', 'glass_top_disc_v1_2.dxf'):
    if (src / f).exists(): shutil.copy2(src / f, PD / f.replace('_v1_2', '_v1_2_200x5'))
# 组合图 + 3MF (glass_top_asm_v1_2 改输出名)
s = (HERE / 'glass_top_asm_v1_2.py').read_text(encoding='utf-8').replace("B.V12 / 'assembly_v1_2_玻璃上", "OUT_ASM / '玻璃上_圆环玻璃200x5")\
    .replace("8×M3×20 拧到底", f"8×M3×{B.GC_SCREW_L:g} 拧到绿件贴红件")\
    .replace("(红件底面圆沉孔 Φ{B.GC_NUT_D:g}×{B.GC_NUT_H:g}, 法兰朝上)", "(红件 r105.2 六角窝, 从外卡斜面塞, 法兰朝上)")\
    .replace("被管端面挡住", "螺丝尾落进六角窝")\
    .replace("glass_top_asm_v1_2.py  2026-11-25", "d200_glass_top_v1_2.py  2026-11-26  圆环玻璃 200×5 版")\
    .replace("POV3D V1.2 — 玻璃上 2 件组合", "POV3D V1.2 — 玻璃上 [圆环玻璃 OD200×ID20×5 版] 2 件组合")
exec(compile(s, 'glass_top_asm_v1_2.py[d200]', 'exec'), dict(__name__='d200', __file__=str(HERE / 'glass_top_asm_v1_2.py'), OUT_ASM=OUT))
print('rod', L.ROD_L, 'boss', L.BOSS_Z1)
