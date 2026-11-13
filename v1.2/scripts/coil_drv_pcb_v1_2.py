"""POV3D V1.2 定子线圈驱动小板 XKT-801-49 元件级模型 (按照片估 ±0.5).

用户 11-12 晚: 参考正/背面照片把小板重建到元件级, 让支撑筋 / 压边 / 电容坑真正避开元件。
- 照片 (codexflow assets): 正面 image-20261112-193414-lbuy.jpg, 背面 image-20261112-193518-t7of.jpg
- 板外形 16.5×28 定比例尺; 两张照片都用板子 4 个角求单应矩阵拉正 (numpy DLT + PIL PERSPECTIVE)
- 板系 (= 装配俯视): x 横跨板宽, 板中心 x=0, +x = 装配 +X; y 沿板长, MOS 端 y=0, 功率端 y=−28
  正面照片 (从上看): 照片左 = −x; 背面照片 (从下看, 镜像): 照片左 = +x  → 拉正后两张都是"从上往下看"的板系
- 高度 (用户实测): PCB 0.8, 背面贴片电容 2.5 (4.8 沿板宽 × 3.3 沿板长), 正面最高件 1.7 (= 1206 电容);
  其余按常规封装估: SOIC8 1.5, SOT-23 1.1, SOD 二极管 1.2, 0603/0805/1206 电阻 0.6, 焊点 / 通孔露头 1.0, 白线焊点 (带线头) 1.2
- 元件表全部 "按照片估 ±0.5" (标注图 out/coil_drv_pcb_map.png 供用户核对)

不 import build_v1_2。coil_drv_geom 用: COMP, PCB_W/L/T, MOS_DX, make_pcb(), free_segments()
单跑: 出 STEP models/mos_clamp_v1_2/coil_drv_pcb_v1_2.step (装配位置, 需 build_v1_2 的 CD 位置) + 标注图
    cd v1.2/scripts && ../../.venv/bin/python coil_drv_pcb_v1_2.py
"""
import math
from pathlib import Path
from OCP.gp import gp_Pnt
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse

HERE = Path(__file__).resolve().parent
V12 = HERE.parent
PHOTO_DIR = Path('/mnt/c/Users/wanqi.liu/AppData/Roaming/codexflow/assets/macha')
PHOTO_F = 'image-20261112-193414-lbuy.jpg'
PHOTO_B = 'image-20261112-193518-t7of.jpg'
# 板 4 角 (照片像素, 手点 ±1 px ≈ ±0.15 mm), 顺序: 板系 (−x,0) (+x,0) (+x,−28) (−x,−28)
CORNERS_F = [(477.5, 561.25), (605.0, 543.75), (635.75, 755.75), (513.0, 774.5)]
CORNERS_B = [(556.25, 523.75), (423.75, 522.5), (425.0, 743.75), (555.0, 742.5)]   # 背面镜像: 照片右上 = (−x, 0)

PCB_W, PCB_L, PCB_T = 16.5, 28.0, 0.8      # 用户实测
MOS_DX = 2.95                              # ** 按照片估: MOS 中心线 (中脚) 在板中心 +x 2.95 (正/背面三脚焊点中心 0.05/3.0/5.9)

# 元件表: (编号, 面 F/B, 名称, x0, x1, y0, y1, 高, 类)   x/y 板系 mm, 高 = 离板面; 全部按照片估 ±0.5
#   类: part 元件 / sj 焊点或露头 / pad 平焊盘 (高 ≤0.3)
COMP = [
    ('F1', 'F', '白线焊点 1 (方焊盘+焊锡+线头)', -8.0, -4.5, -5.0, -1.6, 1.2, 'sj'),
    ('F2', 'F', '白线焊点 2 (焊锡+线头)', -8.0, -5.0, -16.75, -11.25, 1.2, 'sj'),
    ('F3', 'F', 'MOS 脚焊点 G', -0.9, 1.0, -4.25, -1.0, 1.0, 'sj'),
    ('F4', 'F', 'MOS 脚焊点 D', 2.1, 3.9, -4.25, -1.0, 1.0, 'sj'),
    ('F5', 'F', 'MOS 脚焊点 S', 5.1, 6.75, -4.25, -1.0, 1.0, 'sj'),
    ('F6', 'F', 'SOIC8 (含脚)', -0.4, 4.9, -13.0, -6.0, 1.5, 'part'),
    ('F7', 'F', '0603 电阻', -2.75, -1.0, -10.0, -7.25, 0.6, 'part'),
    ('F8', 'F', '0603 电阻', -2.75, -1.0, -13.0, -10.1, 0.6, 'part'),
    ('F9', 'F', '0603 电阻', -2.75, -1.0, -16.5, -13.4, 0.6, 'part'),
    ('F10', 'F', '0603 电阻', -0.75, 2.4, -16.0, -14.25, 0.6, 'part'),
    ('F11', 'F', '0603 电阻', 3.1, 6.25, -15.9, -14.1, 0.6, 'part'),
    ('F12', 'F', '1206 电容 (正面最高 1.7)', 1.5, 6.9, -18.75, -16.6, 1.7, 'part'),
    ('F13', 'F', '1206 电阻', -7.5, -3.5, -20.4, -18.1, 0.6, 'part'),
    ('F14', 'F', '1206 电阻', -7.5, -3.4, -23.5, -21.4, 0.6, 'part'),
    ('F15', 'F', 'SOT-23', -2.6, 0.5, -21.25, -17.9, 1.1, 'part'),
    ('F16', 'F', '二极管 (SOD)', 1.1, 7.5, -22.0, -19.5, 1.2, 'part'),
    ('F17', 'F', '0805 电阻', 1.9, 6.0, -24.5, -22.5, 0.6, 'part'),
    ('F18', 'F', '红线焊点 (+)', -7.6, -5.1, -28.0, -25.25, 1.0, 'sj'),
    ('F19', 'F', '黑线焊点 (−)', 5.9, 8.0, -28.0, -25.25, 1.0, 'sj'),
    ('F20', 'F', '电解电容脚焊点 (IN+)', -4.6, -3.25, -27.5, -25.5, 1.0, 'sj'),
    ('F21', 'F', '电解电容脚焊点 (−)', 3.1, 4.1, -27.5, -25.5, 1.0, 'sj'),
    ('F22', 'F', '方焊盘', -2.0, -0.25, -27.6, -25.5, 0.3, 'pad'),
    ('F23', 'F', '方焊盘', 1.0, 2.9, -27.6, -25.5, 0.3, 'pad'),
    ('B1', 'B', '白线方焊盘焊锡', -7.6, -4.4, -5.0, -1.5, 1.0, 'sj'),
    ('B2', 'B', '白线圆焊盘焊锡', -7.9, -5.1, -15.0, -11.0, 1.0, 'sj'),
    ('B3', 'B', 'MOS 脚露头 G', -0.9, 1.1, -4.0, -1.1, 1.0, 'sj'),
    ('B4', 'B', 'MOS 脚露头 D', 2.0, 3.9, -4.0, -1.1, 1.0, 'sj'),
    ('B5', 'B', 'MOS 脚露头 S', 5.0, 6.75, -4.0, -1.1, 1.0, 'sj'),
    ('B6', 'B', '贴片电容 4.8×3.3 (本体, 实测厚 2.5)', -0.75 - 2.4, -0.75 + 2.4, -12.25 - 1.65, -12.25 + 1.65, 2.5, 'part'),
    ('B6s', 'B', '贴片电容 1 两端焊锡', -4.0, 2.5, -14.25, -10.25, 1.2, 'sj'),
    ('B7', 'B', '贴片电容 4.8×3.3 (本体, 实测厚 2.5)', -0.7 - 2.4, -0.7 + 2.4, -16.9 - 1.65, -16.9 + 1.65, 2.5, 'part'),
    ('B7s', 'B', '贴片电容 2 两端焊锡', -3.9, 2.5, -18.75, -15.1, 1.2, 'sj'),
    ('B8', 'B', '空焊盘 (未贴)', -4.0, -1.9, -22.75, -19.25, 0.2, 'pad'),
    ('B9', 'B', '空焊盘 (未贴)', 0.4, 2.5, -22.75, -19.25, 0.2, 'pad'),
    ('B10', 'B', '左下焊点 (红线 + 电解电容脚)', -7.75, -3.0, -27.9, -24.25, 1.0, 'sj'),
    ('B11', 'B', '右下焊点 (黑线 + 电解电容脚)', 3.4, 7.75, -27.9, -24.4, 1.0, 'sj'),
]
# 背面镀锡走线 (平, 不算元件, 支撑筋可以托在上面; 只画在标注图上)
TRACES = [('T1', 'B', '−x 侧镀锡走线', -7.25, -5.9, -27.0, -15.0), ('T2', 'B', '+x 侧镀锡走线', 6.0, 7.4, -24.0, -5.0)]
FRONT_MAX = max(c[7] for c in COMP if c[1] == 'F')
BACK_MAX = max(c[7] for c in COMP if c[1] == 'B')
assert abs(FRONT_MAX - 1.7) < 1e-9 and abs(BACK_MAX - 2.5) < 1e-9


def _box(x0, y0, z0, x1, y1, z1):
    return BRepPrimAPI_MakeBox(gp_Pnt(min(x0, x1), min(y0, y1), min(z0, z1)), gp_Pnt(max(x0, x1), max(y0, y1), max(z0, z1))).Shape()


def make_pcb(xc, y_end, z0):
    """板中心 x = xc, MOS 端 y = y_end, PCB 底面 Z = z0 → 元件级实体 (板 + 两面元件盒)。"""
    z1 = z0 + PCB_T
    sh = _box(xc - PCB_W / 2, y_end - PCB_L, z0, xc + PCB_W / 2, y_end, z1)
    for n, side, _, x0, x1, y0, y1, h, k in COMP:
        if h < 0.05: continue
        za, zb = (z1, z1 + h) if side == 'F' else (z0 - h, z0)
        o = BRepAlgoAPI_Fuse(sh, _box(xc + x0, y_end + y0, za, xc + x1, y_end + y1, zb)); o.Build(); sh = o.Shape()
    return sh


def free_segments(sx, w_front=1.0, w_back=1.5, clr=0.5, min_len=2.0):
    """板长边 sx=±1 上, 正面压边 (宽 w_front) 与 背面支撑筋 (宽 w_back) 都离所有元件/焊点 ≥clr 的 y 段 (板系)。
    平焊盘 (pad, ≤0.3) 和镀锡走线不挡。返回 [(y0, y1)] (y0<y1)。"""
    blocked = []
    for n, side, _, x0, x1, y0, y1, h, k in COMP:
        if k == 'pad': continue
        w = w_front if side == 'F' else w_back
        s0, s1 = (PCB_W / 2 - w, PCB_W / 2) if sx > 0 else (-PCB_W / 2, -PCB_W / 2 + w)
        if x1 + clr > s0 + 1e-9 and x0 - clr < s1 - 1e-9:
            blocked.append((y0 - clr, y1 + clr))
    segs, y = [], -PCB_L
    for b0, b1 in sorted(blocked):
        if b0 > y: segs.append((y, min(b0, 0.0)))
        y = max(y, b1)
    if y < 0: segs.append((y, 0.0))
    return [(a, b) for a, b in segs if b - a >= min_len - 1e-9]


# ---------------- 标注图 ----------------
def _H(src, dst):
    import numpy as np
    a = []
    for (x, y), (u, v) in zip(src, dst):
        a.append([x, y, 1, 0, 0, 0, -u * x, -u * y, -u]); a.append([0, 0, 0, x, y, 1, -v * x, -v * y, -v])
    h = np.linalg.svd(np.array(a))[2][-1]
    return (h / h[-1]).reshape(3, 3)


def rectify(photo, corners, S=40, M=3.0):
    """拉正到板系俯视: 像素 u = (x + W/2 + M)·S, v = (−y + M)·S。返回 PIL 图。"""
    from PIL import Image
    out = lambda x, y: ((x + PCB_W / 2 + M) * S, (-y + M) * S)
    H = _H([out(-PCB_W / 2, 0), out(PCB_W / 2, 0), out(PCB_W / 2, -PCB_L), out(-PCB_W / 2, -PCB_L)], corners)
    size = (int((PCB_W + 2 * M) * S), int((PCB_L + 2 * M) * S))
    return Image.open(PHOTO_DIR / photo).transform(size, Image.PERSPECTIVE, H.flatten()[:8].tolist(), Image.BICUBIC), out


def draw_map(path, segs=None, extra=None):
    """正 / 背面拉正照片 + 元件框/编号 + 压边 / 支撑筋段 (segs = {sx: [(y0,y1)]})。"""
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib import font_manager as fm
    fm.fontManager.addfont('/mnt/c/Windows/Fonts/msyh.ttc')
    plt.rcParams['font.family'] = fm.FontProperties(fname='/mnt/c/Windows/Fonts/msyh.ttc').get_name()
    M = 3.0
    fig, axs = plt.subplots(1, 2, figsize=(18, 11))
    COLK = dict(part='#00e5ff', sj='#ff3d00', pad='#ffd600')
    for ax, side, photo, cor, ttl in ((axs[0], 'F', PHOTO_F, CORNERS_F, '正面 (从上看, 照片拉正)'), (axs[1], 'B', PHOTO_B, CORNERS_B, '背面 (从上透视看 = 背面照片镜像后拉正)')):
        im, _ = rectify(photo, cor)
        ext = (-PCB_W / 2 - M, PCB_W / 2 + M, -PCB_L - M, M)
        ax.imshow(im, extent=ext)
        ax.add_patch(Rectangle((-PCB_W / 2, -PCB_L), PCB_W, PCB_L, fc='none', ec='w', lw=1.2, ls='--'))
        for n, s, name, x0, x1, y0, y1, h, k in COMP:
            if s != side: continue
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc='none', ec=COLK[k], lw=1.4))
            ax.text(x0 + 0.1, y1 - 0.1, f'{n}', color=COLK[k], fontsize=8, va='top', weight='bold',
                    bbox=dict(fc='black', alpha=.45, pad=0.5, lw=0))
        for n, s, name, x0, x1, y0, y1 in TRACES:
            if s == side: ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc='none', ec='#bdbdbd', lw=1, ls=':'))
        if segs:
            w = 1.0 if side == 'F' else 1.5
            for sx, ss in segs.items():
                for a, b in ss:
                    x0 = PCB_W / 2 - w if sx > 0 else -PCB_W / 2
                    ax.add_patch(Rectangle((x0, a), w, b - a, fc='#76ff03', alpha=.45, ec='#76ff03', lw=1.5))
        ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect('equal')
        ax.set_xticks(range(-11, 12)); ax.set_yticks(range(-31, 4)); ax.tick_params(labelsize=6); ax.grid(alpha=.25, color='y')
        ax.set_title(f'{ttl}\n绿 = {"压盖压边 1.0" if side == "F" else "底盘支撑筋 1.5"}; 青 = 元件, 红 = 焊点/露头, 黄 = 平焊盘, 灰点 = 镀锡走线', fontsize=10)
        ax.set_xlabel('板系 x (mm, +x = 装配 +X, 板中心 0)'); ax.set_ylabel('板系 y (mm, MOS 端 0)')
        rows = [f'{n} {name}  h{h:g}' for n, s, name, x0, x1, y0, y1, h, k in COMP if s == side]
        ax.text(1.02, 1.0, '\n'.join(rows), transform=ax.transAxes, fontsize=7.5, va='top')
    note = '元件表全部按照片估 ±0.5 (板 16.5×28 定比例尺, 四角单应拉正); 高度: PCB 0.8 / 背面电容 2.5 / 正面最高 1.7 实测, 其余按常规封装估'
    if extra: note += '\n' + extra
    fig.suptitle('XKT-801-49 线圈驱动小板 元件级模型 (coil_drv_pcb_v1_2.py)\n' + note, fontsize=11)
    fig.tight_layout(rect=(0, 0, 0.93, 0.95)); fig.savefig(path, dpi=100); plt.close(fig)


if __name__ == '__main__':
    import sys
    sys.path.insert(0, str(HERE))
    import build_v1_2 as B
    C = B.CD
    draw_map(B.OUT / 'coil_drv_pcb_map.png', None, '用户 11-12「mos锁住就可以」: 压盖不压 PCB, 无压边 / 支撑筋')
    MD = V12 / 'models' / 'mos_clamp_v1_2'; MD.mkdir(parents=True, exist_ok=True)
    B.write_doc([('coil_drv_pcb_v1_2', C.pcb, '#38761d', None, False)], MD / 'coil_drv_pcb_v1_2.step', 'coil_drv_pcb_v1_2')
