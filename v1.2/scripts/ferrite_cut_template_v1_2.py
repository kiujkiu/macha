"""定子线圈隔磁片 (100x100 片) 无缝裁切模板, A4 1:1 打印 (用户 11-18 定的切法)。
片横向 3 等分 (条宽 33.33), 每条梯形正倒交替、共用斜边、整条用满; 两端各半块拼成 1 块。
18 块拼成正 18 边形环 (相邻块共径向边, 无缝), 再把伸进内墙的部分修成内圆弧 r=R_TRIM。
几何被「整条用满」唯一确定: pitch = 100/6 = tan10°·(2·d_i + H)。"""
import math
from fpdf import FPDF

SHEET = 100.0
R_WALL_IN, R_WALL_OUT = 39.9, 72.5     # 定子盘线圈腔 (reference_v1_2_dims_cheatsheet)
R_TRIM = R_WALL_IN + 0.4               # 内圆弧修到这里
STRIPS, PER = 3, 6
N = STRIPS * PER                       # 18
beta = math.pi / N
tb = math.tan(beta)
H = SHEET / STRIPS
P = SHEET / PER                        # 节距 (L+S)/2
d_i = (P / tb - H) / 2                 # 内边(短边)到圆心
d_o = d_i + H                          # 外边(长边)到圆心
S, L = 2 * d_i * tb, 2 * d_o * tb
R_OC = d_o / math.cos(beta)            # 外角半径
assert R_OC <= R_WALL_OUT - 0.3, R_OC
waste = N * (tb * (d_i + R_TRIM * math.cos(beta)) * 0)  # 占位
def ring_area(r1, r2): return math.pi * (r2**2 - r1**2)
cover_full = ring_area(R_TRIM, d_o)
print(f"N={N} H={H:.3f} S={S:.3f} L={L:.3f} d_i={d_i:.3f} d_o={d_o:.3f} 外角 r{R_OC:.2f} "
      f"内修 r{R_TRIM} 修掉 {R_TRIM-d_i:.2f}(轴线上)")

RED, BLU, BLK, GRY = (220, 0, 0), (0, 70, 220), (0, 0, 0), (140, 140, 140)
pdf = FPDF('P', 'mm', 'A4'); pdf.set_auto_page_break(False); pdf.add_page()
pdf.add_font('hei', '', '/mnt/c/Windows/Fonts/simhei.ttf')
def txt(x, y, s, size=8, align='L', col=BLK):
    pdf.set_text_color(*col); pdf.set_font('hei', size=size); w = pdf.get_string_width(s)
    pdf.text(x + {'L': 0, 'C': -w / 2, 'R': -w}[align], y, s); pdf.set_text_color(0, 0, 0)

def dashed_poly(pts, dash=1.2, gap=0.8):
    pdf.set_dash_pattern(dash=dash, gap=gap)
    for a, b in zip(pts, pts[1:]): pdf.line(*a, *b)
    pdf.set_dash_pattern()

txt(105, 12, "定子线圈隔磁片 无缝裁切模板 (1:1, 打印选「实际大小/100%」)", 12, 'C')
txt(105, 17.5, f"100×100 片三等分 → 每条 6 块 (两端半块拼 1 块) → 18 块拼成环 → 修内圆弧 R{R_TRIM}", 8.5, 'C')

# ---------- 片: 1:1 ----------
X0, Y0 = 12, 24
pdf.set_draw_color(*BLK); pdf.set_line_width(0.4); pdf.rect(X0, Y0, SHEET, SHEET)
for k in range(STRIPS):
    yt = Y0 + k * H; yb = yt + H
    pdf.set_draw_color(*RED); pdf.set_line_width(0.3)
    if k: pdf.line(X0, yt, X0 + SHEET, yt)
    # 块中心: 正块(短边在上) x = 0, 2P, 4P, 6P(=100); 倒块 x = P, 3P, 5P
    for j in range(PER + 1):
        cx = X0 + j * P
        up = (j % 2 == 0)
        top, bot = (S, L) if up else (L, S)
        # 斜边: 只画右侧 (左侧由前一块的右侧画), 第 0 块也画左侧 (在片外的部分裁掉)
        for sgn in ((+1,) if j else (-1, +1)):
            x1, x2 = cx + sgn * top / 2, cx + sgn * bot / 2
            # 裁到片内
            xa, ya, xb, yb2 = x1, yt, x2, yb
            if min(xa, xb) < X0 or max(xa, xb) > X0 + SHEET:
                continue
            pdf.line(xa, ya, xb, yb2)
        # 内圆弧修线 (蓝虚线): 圆心在短边外侧 d_i 处
        ccy = (yt - d_i) if up else (yb + d_i)
        arc = []
        for q in range(-40, 41):
            th = beta * q / 40
            px = cx + R_TRIM * math.sin(th)
            py = ccy + (R_TRIM * math.cos(th) if up else -R_TRIM * math.cos(th))
            if X0 - 1e-6 <= px <= X0 + SHEET + 1e-6: arc.append((px, py))
        pdf.set_draw_color(*BLU); pdf.set_line_width(0.3); dashed_poly(arc)
        pdf.set_draw_color(*RED); pdf.set_line_width(0.3)
        num = k * PER + (j if j < PER else 0) + 1
        lab = f"{num}" if 0 < j < PER else f"{k*PER+1}半"
        lx = cx + (0 if 0 < j < PER else (3.2 if j == 0 else -3.2))
        txt(lx, yt + H * (0.62 if up else 0.40), lab, 8 if 0 < j < PER else 6.5, 'C', RED)
        if 0 < j < PER:
            txt(cx, yt + (2.5 if up else H - 1.2), "内", 5, 'C', RED)
txt(X0, Y0 + SHEET + 4, "红实线 = 先切;  蓝虚线 = 再修内圆弧 (圆弧外侧那小块不要);", 7, 'L', GRY)
txt(X0, Y0 + SHEET + 7.5, "「1半/7半/13半」= 每条两端的半块, 两半沿竖边对拼成一块", 7, 'L', GRY)

# ---------- 右栏 ----------
RX, yy = 119, Y0 + 3
for s in [
    "单块 (修弧前, 等腰梯形):",
    f"  短边(内) S = {S:.2f}",
    f"  长边(外) L = {L:.2f}",
    f"  高 H = {H:.2f} (= 100/3)",
    f"  夹角 20°, 18 块正好一圈",
    "",
    "拼环后:",
    f"  多边形内边离圆心 {d_i:.1f} (伸进内墙)",
    f"  → 修成内圆弧 R{R_TRIM}, 贴内墙 Φ{2*R_WALL_IN}",
    f"  外边离圆心 {d_o:.1f}, 外角 r{R_OC:.1f}",
    f"  外圈不用修 (离外墙 Φ{2*R_WALL_OUT:.0f} 还有余)",
    f"  无缝覆盖 r{R_TRIM}–{d_o:.1f}",
    f"  外侧 r{d_o:.1f}–{R_WALL_OUT} 一张片不够盖",
]:
    txt(RX, yy, s, 8); yy += 4.4
yy += 3
txt(RX, yy, "打印校验: 下面这条应量出 50.0 mm", 7.5)
pdf.set_draw_color(*BLK); pdf.set_line_width(0.3); pdf.line(RX, yy + 4, RX + 50, yy + 4)
for q in range(0, 51, 10):
    pdf.line(RX + q, yy + 2.5, RX + q, yy + 5.5); txt(RX + q, yy + 8.5, str(q), 6, 'C')
txt(RX, yy + 13, "片框也应量出 100.0 × 100.0", 7.5)

# ---------- 1:1 贴放图 ----------
CX, CY = 105, Y0 + SHEET + 12 + R_WALL_OUT
pdf.set_draw_color(*GRY); pdf.set_line_width(0.3)
for r in (R_WALL_OUT, R_WALL_IN):
    pdf.ellipse(CX - r, CY - r, 2 * r, 2 * r, style='D')
order = []                                   # 环上依次: 条1 的 1..6, 条2 7..12, 条3 13..18 (正倒交替自然对上)
for m in range(N):
    a = math.radians(90 + (m + 0.5) * 360 / N)
    ux, uy = math.cos(a), -math.sin(a); vx, vy = -uy, ux
    def W(r, q): return (CX + r * ux + q * vx, CY + r * uy + q * vy)
    # 修弧后的块: 内弧 R_TRIM (±beta) + 两径向边 + 外弦
    pts = [W(R_TRIM * math.cos(beta * q / 20), R_TRIM * math.sin(beta * q / 20)) for q in range(-20, 21)]
    pts += [W(d_o, L / 2), W(d_o, -L / 2), pts[0]]
    pdf.set_draw_color(*RED); pdf.set_line_width(0.22)
    for p1, p2 in zip(pts, pts[1:]): pdf.line(*p1, *p2)
    # 修掉的部分 (虚线)
    pdf.set_draw_color(*BLU); pdf.set_line_width(0.15)
    dashed_poly([W(R_TRIM * math.cos(beta), -R_TRIM * math.sin(beta)), W(d_i, -S / 2), W(d_i, S / 2),
                 W(R_TRIM * math.cos(beta), R_TRIM * math.sin(beta))], 0.8, 0.6)
    rm = (R_TRIM + d_o) / 2
    lab = str(m + 1) if (m % PER) else f"{m+1}拼"
    txt(*W(rm, 0)[:1], W(rm, 0)[1] + 1.0, lab, 6, 'C', RED) if False else txt(W(rm, 0)[0], W(rm, 0)[1] + 1.0, lab, 6, 'C', RED)
pdf.set_draw_color(*BLK); pdf.set_line_width(0.2)
pdf.line(CX - 3, CY, CX + 3, CY); pdf.line(CX, CY - 3, CX, CY + 3)
txt(CX, CY - 8, "1:1 贴放图", 7.5, 'C', GRY)
txt(CX, CY - 4, f"灰圈 = 腔壁 Φ{2*R_WALL_IN} / Φ{2*R_WALL_OUT:.0f}", 7, 'C', GRY)
txt(CX, CY + 5, "蓝虚线 = 修掉的内侧", 7, 'C', GRY)
txt(CX, CY + 9, "切好的块可摆在纸上核对", 7, 'C', GRY)

out = "/mnt/d/claude_workspace/macha/pov3d/v1.2/定子盘/隔磁片/隔磁片裁切模板_三等分18块_修内弧_A4_1比1.pdf"
pdf.output(out); print(out, "环底 y", CY + R_WALL_OUT)
