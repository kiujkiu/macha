"""转子盘B 第一版预览 (从 models/ 的装配位 STL 渲染): 上方斜视 / 下方斜视 (翻看底面线圈腔) / 半剖。"""
import struct, numpy as np, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib import font_manager
FONT = "/mnt/c/Windows/Fonts/simhei.ttf"; font_manager.fontManager.addfont(FONT)
plt.rcParams["font.family"] = font_manager.FontProperties(fname=FONT).get_name(); plt.rcParams["axes.unicode_minus"] = False
M = '/mnt/d/claude_workspace/macha/pov3d/v1.2/models/'
def stl(p, dz=0.0):
    b = open(p, 'rb').read(); n = struct.unpack('<I', b[80:84])[0]
    a = np.frombuffer(b[84:84 + 50 * n], dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')]))
    t = a['v'].reshape(-1, 3, 3).astype(float); t[:, :, 2] += dz; return t
P = [('玻纤板 3mm', stl(M + 'fr4_plate_v1_2b/fr4_plate_v1_2b.stl', 21.5), '#C9B458'),
     ('承载盘 (并入毂盘)', stl(M + 'rim_ring_v1_2b/rim_ring_v1_2b.stl'), '#6AA84F'),
     ('屏幕固定件 A', stl(M + 'screen_holder_v1_2b_a/screen_holder_v1_2b_a.stl'), '#F1C232'),
     ('屏幕固定件 B', stl(M + 'screen_holder_v1_2b_b/screen_holder_v1_2b_b.stl'), '#E69138')]
L = np.array([0.3, -0.4, 0.85]); L /= np.linalg.norm(L)
def shade(t, c, elev_sign=1):
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]); n /= (np.linalg.norm(n, axis=1)[:, None] + 1e-12)
    k = 0.35 + 0.65 * np.abs(n @ (L * [1, 1, elev_sign]))
    rgb = np.array(matplotlib.colors.to_rgb(c)); return np.clip(rgb[None, :] * k[:, None], 0, 1)
fig = plt.figure(figsize=(22, 15))
VIEWS = ((32, -55, '上方斜视 (含屏幕固定件)', None, False), (-30, -55, '下方斜视 (看承载盘底面: 线圈腔 / 底板螺丝沉孔; 玻纤板隐藏)', None, False),
         (12, 90, '半剖 (切掉 y>0 一半, 从切面看叠层: 玻纤板 + 承载盘 + 固定件)', 'half', True), (60, -90, '俯视偏斜 (固定件弧形带 + 锚点/罩子锁点)', None, False))
for i, (elev, azim, title, clip, show_fr4) in enumerate(VIEWS):
    ax = fig.add_subplot(2, 2, i + 1, projection='3d'); ax.set_title(title, fontsize=15)
    tris, cols = [], []
    for name, t, c in P:
        if name.startswith('玻纤') and not show_fr4: continue
        if i == 1 and name.startswith('屏幕'): continue
        tt = t[t[:, :, 1].max(axis=1) < 0.5] if clip == 'half' else t
        if not name.startswith('屏幕'): tt = tt[tt[:, :, 2].max(axis=1) < 60]
        tris.append(tt); cols.append(shade(tt, c, 1 if elev > 0 else -1))
    pc = Poly3DCollection(np.concatenate(tris), facecolors=np.concatenate(cols), edgecolors='none'); ax.add_collection3d(pc)
    ax.set_xlim(-88, 88); ax.set_ylim(-88, 88); ax.set_zlim(-30, 85); ax.set_box_aspect((1, 1, 0.65)); ax.view_init(elev, azim); ax.axis('off')
fig.subplots_adjust(left=0, right=1, top=0.96, bottom=0.04, wspace=0, hspace=0.05)
fig.text(0.01, 0.02, '黄 = 玻纤板 Φ165×3 (下方斜视里隐藏, 好看承载盘底面)   绿 = 承载盘单件   黄/橙 = 屏幕固定件 A/B (弧形带 ±44°, 横杆托灯板下沿)', fontsize=12)
out = __file__.replace('.py', '.png'); fig.savefig(out, dpi=95, bbox_inches='tight'); print(out)
