"""定子线圈隔磁片 (100x100 片) 扇形裁切模板, A4 1:1 打印。
线圈腔 r39.9–72.5 (见 reference_v1_2_dims_cheatsheet)。3 条带 x 每条 N 块梯形正倒交替, 侧边为径向线。"""
import math, sys
from fpdf import FPDF

SHEET = 100.0
R_WALL_IN, R_WALL_OUT = 39.9, 72.5
CLR = 0.4                      # 离腔壁余量
D_IN = R_WALL_IN + CLR         # 内边(短边)到圆心距离
R_CORNER = R_WALL_OUT - CLR    # 外角最大半径
N = int(sys.argv[1]) if len(sys.argv) > 1 else 6   # 每条块数
STRIPS = 3
END_M = 0.5                    # 条带两端留边

# 解 beta: 外角落在 R_CORNER, 长度用满 SHEET-2*END_M
lo, hi = 0.01, 0.5
for _ in range(80):
    b = (lo + hi) / 2
    d_o = R_CORNER * math.cos(b)
    need = math.tan(b) * (N * (d_o + D_IN) + (d_o - D_IN))
    lo, hi = (b, hi) if need <= SHEET - 2 * END_M else (lo, b)
beta = lo
d_o = R_CORNER * math.cos(beta)
H = d_o - D_IN
S = 2 * D_IN * math.tan(beta)
L = 2 * d_o * math.tan(beta)
total = N * STRIPS
slot = 360 / total
cover = 2 * math.degrees(beta) / slot
gap_out = 2 * math.pi * R_CORNER / total - 2 * R_CORNER * math.sin(beta)
gap_in = 2 * math.pi * D_IN / total - S
used = N * (L + S) / 2 + (L - S) / 2
assert STRIPS * H <= SHEET
area_ring = math.pi * (R_CORNER**2 - D_IN**2)
print(f"N={N} total={total} beta={math.degrees(beta):.3f} H={H:.2f} S={S:.2f} L={L:.2f} "
      f"used={used:.2f} cover={cover*100:.1f}% gap_out≈{gap_out:.2f} gap_in≈{gap_in:.2f} "
      f"片面积用到 {total*(L+S)/2*H/1e4*100:.1f}% 环面积需 {area_ring:.0f}")

pdf = FPDF('P', 'mm', 'A4'); pdf.set_auto_page_break(False); pdf.add_page()
pdf.add_font('hei', '', '/mnt/c/Windows/Fonts/simhei.ttf')
def txt(x, y, s, size=8, align='L'):
    pdf.set_font('hei', size=size); w = pdf.get_string_width(s)
    dx = {'L': 0, 'C': -w / 2, 'R': -w}[align]
    pdf.text(x + dx, y, s)

RED, BLK, GRY = (220, 0, 0), (0, 0, 0), (150, 150, 150)
# ---- 标题
txt(105, 12, f"定子线圈隔磁片 裁切模板 (1:1, 打印选「实际大小/100%」)", 12, 'C')
txt(105, 17.5, f"100×100 片 → 3 条 × {N} 块 = {total} 块扇形梯形, 贴线圈腔 r{R_WALL_IN}–{R_WALL_OUT}", 8.5, 'C')

# ---- 片 (左上)
X0, Y0 = 12, 24
pdf.set_draw_color(*BLK); pdf.set_line_width(0.4); pdf.rect(X0, Y0, SHEET, SHEET)
pdf.set_draw_color(*RED); pdf.set_line_width(0.25)
tb = math.tan(beta)
pieces_sheet = []
for k in range(STRIPS):
    yt = Y0 + k * H; yb = yt + H
    if k > 0:
        pdf.line(X0, yt, X0 + SHEET, yt)
    if k == STRIPS - 1:
        pdf.line(X0, yb, X0 + SHEET, yb)
    x = X0 + END_M + (SHEET - 2 * END_M - used) / 2
    # 第一块: 短边在上 (正), 左上角 x+(L-S)/2
    for i in range(N):
        up = (i % 2 == 0)       # 短边在上
        if up:
            tl, tr = x + (L - S) / 2, x + (L - S) / 2 + S
            bl, br = x, x + L
        else:
            tl, tr = x, x + L
            bl, br = x + (L - S) / 2, x + (L - S) / 2 + S
        pdf.line(tl, yt, bl, yb); pdf.line(tr, yt, br, yb)
        cx = (tl + tr + bl + br) / 4
        num = k * N + i + 1
        txt(cx, yt + H * (0.62 if up else 0.42), str(num), 9, 'C')
        txt(cx, yt + H * (0.16 if up else 0.90), "内", 5.5, 'C')
        x += (L + S) / 2        # 正倒交替, 相邻块共用斜边
pdf.set_text_color(*GRY)
txt(X0, Y0 + SHEET + 4, "红线 = 切线;  黑框 = 100×100 片边;  「内」= 贴靠内墙 (Φ79.8) 的短边", 7)
pdf.set_text_color(0, 0, 0)

# ---- 右栏: 尺寸 + 比例校验
RX = 120
lines = [
    "单块尺寸 (等腰梯形):",
    f"  短边(内) S = {S:.1f}",
    f"  长边(外) L = {L:.1f}",
    f"  高(径向) H = {H:.1f}  (条带宽)",
    f"  夹角 {2*math.degrees(beta):.2f}°, 每块占位 {slot:.1f}°",
    "",
    "贴法:",
    f"  短边朝圆心, 内边离圆心 {D_IN:.1f}",
    f"  {total} 块均分一圈, 块间留径向缝",
    f"  缝: 内圈约 {gap_in:.1f}, 外圈约 {gap_out:.1f}",
    f"  角向覆盖 {cover*100:.0f}% (片面积不够铺满)",
    "",
    "径向缝顺着磁通方向 (圆线圈下",
    "磁通在隔磁片里沿径向走), 影响小;",
    "缝要均匀, 别集中在一边。",
]
for j, s in enumerate(lines):
    txt(RX, Y0 + 3 + j * 4.4, s, 8)
# 比例尺
by = Y0 + 3 + len(lines) * 4.4 + 4
txt(RX, by, "打印校验: 下面这条应量出 50.0 mm", 7.5)
pdf.set_draw_color(*BLK); pdf.set_line_width(0.3)
pdf.line(RX, by + 4, RX + 50, by + 4)
for t in range(0, 51, 10):
    pdf.line(RX + t, by + 2.5, RX + t, by + 5.5); txt(RX + t, by + 8.5, str(t), 6, 'C')
txt(RX, by + 13, "片框也应量出 100.0 × 100.0", 7.5)

# ---- 下方: 1:1 圆环贴放图
CX, CY = 105, Y0 + SHEET + 9 + R_WALL_OUT + 1
pdf.set_draw_color(*GRY); pdf.set_line_width(0.3)
for r in (R_WALL_OUT, R_WALL_IN):
    pdf.ellipse(CX - r, CY - r, 2 * r, 2 * r, style='D')
pdf.set_draw_color(*RED); pdf.set_line_width(0.25)
for m in range(total):
    a = math.radians(90 + m * slot)   # 第 1 块在正上方, 逆时针
    ux, uy = math.cos(a), -math.sin(a)       # 径向 (pdf y 向下)
    vx, vy = -uy, ux                         # 切向
    pts = [(D_IN, -S/2), (D_IN, S/2), (d_o, L/2), (d_o, -L/2)]
    P = [(CX + r * ux + t * vx, CY + r * uy + t * vy) for r, t in pts]
    pdf.polygon(P, style='D')
    rm = (D_IN + d_o) / 2
    txt(CX + rm * ux, CY + rm * uy + 1.2, str(m + 1), 6.5, 'C')
pdf.set_draw_color(*BLK); pdf.set_line_width(0.2)
pdf.line(CX - 3, CY, CX + 3, CY); pdf.line(CX, CY - 3, CX, CY + 3)
pdf.set_text_color(*GRY)
txt(CX, CY - 4, f"1:1 贴放图  灰圈 = 腔壁 Φ{2*R_WALL_IN:.1f} / Φ{2*R_WALL_OUT:.0f}", 7, 'C')
txt(CX, CY + 7, "可直接把切好的块摆在这张纸上核对", 7, 'C')
pdf.set_text_color(0, 0, 0)
out = f"/mnt/d/claude_workspace/macha/pov3d/v1.2/定子盘/隔磁片/隔磁片裁切模板_{total}块_A4_1比1.pdf"
pdf.output(out); print(out, "ring bottom y=", CY + R_WALL_OUT)
