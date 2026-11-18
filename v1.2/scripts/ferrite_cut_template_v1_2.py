"""定子线圈隔磁片 完全铺满线圈腔 裁切模板, A4 1:1 打印 (用户 11-18: 三等分 + 拼 + 修弧, 要完全平铺)。
腔 r39.9–72.5。18 块等腰梯形 (20°) 成环, 内外都修圆弧 ⇒ r R_IN–R_OUT 无缝全覆盖。
面积: 腔环 ≈ 11.2k mm² > 一张片 10k ⇒ 必须两张片。
条带当作一条连续"带子": 梯形正倒交替排下去, 每 100 切一条 (三等分), 跨条的块用竖缝拼。"""
import math
from fpdf import FPDF

SHEET = 100.0
R_WALL_IN, R_WALL_OUT = 39.9, 72.5
R_IN, R_OUT = R_WALL_IN + 0.4, R_WALL_OUT - 0.4      # 修弧半径
N = 18
beta = math.pi / N; tb = math.tan(beta)
H = SHEET / 3
lo_di, hi_di = R_OUT - H, R_IN * math.cos(beta)       # 外弦≥R_OUT, 内角≤R_IN 才能全盖
assert lo_di < hi_di
d_i = round((lo_di + hi_di) / 2, 2); d_o = d_i + H
S, L = 2 * d_i * tb, 2 * d_o * tb
P = (L + S) / 2
print(f"d_i {d_i} (允许 {lo_di:.2f}–{hi_di:.2f}) d_o {d_o:.2f} S {S:.2f} L {L:.2f} 节距 {P:.2f}")

RED, BLU, BLK, GRY = (220, 0, 0), (0, 70, 220), (0, 0, 0), (140, 140, 140)
pdf = FPDF('P', 'mm', 'A4'); pdf.set_auto_page_break(False)
pdf.add_font('hei', '', '/mnt/c/Windows/Fonts/simhei.ttf')
def txt(x, y, s, size=8, align='L', col=BLK):
    pdf.set_text_color(*col); pdf.set_font('hei', size=size); w = pdf.get_string_width(s)
    pdf.text(x + {'L': 0, 'C': -w / 2, 'R': -w}[align], y, s); pdf.set_text_color(0, 0, 0)
def poly(pts, dashed=False):
    if dashed: pdf.set_dash_pattern(dash=1.2, gap=0.8)
    for a, b in zip(pts, pts[1:]): pdf.line(*a, *b)
    if dashed: pdf.set_dash_pattern()

PER = 5                                              # 每条: 从块 m 轴线切到块 m+5 轴线 (两端各半块)
STRIP_SPANS = [(m, min(m + PER, N)) for m in range(0, N, PER)]   # 块 N ≡ 块 0 (环首尾)
n_strips = len(STRIP_SPANS)
for m0, m1 in STRIP_SPANS: assert (m1 - m0) * P <= SHEET - 1
X_OFF = (SHEET - PER * P) / 2

def draw_sheet(sh, X0, Y0):
    pdf.set_draw_color(*BLK); pdf.set_line_width(0.4); pdf.rect(X0, Y0, SHEET, SHEET)
    for k in range(3):
        s = sh * 3 + k
        yt, yb = Y0 + k * H, Y0 + (k + 1) * H
        if s >= n_strips:
            txt(X0 + 50, yt + H / 2 + 1.5, "(余料, 不用)", 8, 'C', GRY); continue
        m0, m1 = STRIP_SPANS[s]
        u0, u1 = X0 + X_OFF, X0 + X_OFF + (m1 - m0) * P
        pdf.set_draw_color(*RED); pdf.set_line_width(0.3)
        pdf.line(X0, yb, X0 + SHEET, yb)
        pdf.line(u0, yt, u0, yb); pdf.line(u1, yt, u1, yb)          # 两端竖切 (半块的拼缝)
        for m in range(m0, m1 + 1):
            c = u0 + (m - m0) * P; up = (m % 2 == 0)
            top, bot = (S, L) if up else (L, S)
            for sg in (-1, 1):
                a, b = c + sg * top / 2, c + sg * bot / 2
                if u0 - 1e-6 <= min(a, b) and max(a, b) <= u1 + 1e-6:
                    pdf.line(a, yt, b, yb)
            for R in (R_IN, R_OUT):
                pts = []
                for q in range(-50, 51):
                    th = beta * q / 50
                    u = c + R * math.sin(th); dy = R * math.cos(th) - d_i
                    if u0 - 1e-6 <= u <= u1 + 1e-6: pts.append((u, yt + dy if up else yb - dy))
                pdf.set_draw_color(*BLU); pdf.set_line_width(0.3); poly(pts, True)
                pdf.set_draw_color(*RED); pdf.set_line_width(0.3)
            no = m % N + 1
            half = m in (m0, m1)
            lx = c + (0 if not half else (L / 5 if m == m0 else -L / 5))
            txt(lx, yt + H * (0.55 if up else 0.50), f"{no}" + ("半" if half else ""), 6.5 if half else 8, 'C', RED)
            if not half: txt(c, yt + (2.4 if up else H - 1.0), "内", 5, 'C', RED)
        txt(X0 - 1.5, yt + 4, f"条{s+1}", 6.5, 'R', GRY)

def side(RX, yy, sh):
    lines = [f"第 {sh+1}/2 张片",
             "",
             "单块 (修弧前, 等腰梯形):",
             f"  短边(内) S = {S:.2f}",
             f"  长边(外) L = {L:.2f}",
             f"  高 H = {H:.2f} (= 100/3)",
             f"  夹角 20°, 18 块一圈",
             "",
             "步骤:",
             "  1 片三等分切条",
             "  2 沿红线切梯形 (刀走线中间)",
             "  3 同号「n半」两个半块沿竖边对拼",
             f"  4 沿蓝虚线修内弧 R{R_IN} / 外弧 R{R_OUT}",
             "  5 按 1→18 顺序贴, 短边朝圆心, 挨紧",
             "",
             f"铺满 r{R_IN}–{R_OUT} (离两墙各 0.4), 无缝",
             f"一张片 10000 mm2 < 腔环 {math.pi*(R_OUT**2-R_IN**2):.0f} mm2",
             "所以必须两张片"]
    for s in lines:
        txt(RX, yy, s, 8); yy += 4.3
    yy += 2
    txt(RX, yy, "打印校验: 下面这条应量出 50.0 mm", 7.5)
    pdf.set_draw_color(*BLK); pdf.set_line_width(0.3); pdf.line(RX, yy + 4, RX + 50, yy + 4)
    for q in range(0, 51, 10):
        pdf.line(RX + q, yy + 2.5, RX + q, yy + 5.5); txt(RX + q, yy + 8.5, str(q), 6, 'C')
    txt(RX, yy + 13, "片框也应量出 100.0 × 100.0", 7.5)

for sh in range(2):
    pdf.add_page()
    txt(105, 12, "定子线圈隔磁片 铺满裁切模板 (1:1, 打印选「实际大小/100%」)", 12, 'C')
    txt(105, 17.5, f"两张 100×100 片, 各三等分 → 18 块梯形拼环 → 内外修弧 → 铺满线圈腔 Φ{2*R_WALL_IN}–Φ{2*R_WALL_OUT:.0f}", 8.5, 'C')
    X0, Y0 = 14, 24
    draw_sheet(sh, X0, Y0)
    txt(X0, Y0 + SHEET + 4, "红实线 = 切线;  蓝虚线 = 修弧线 (弧外那小块不要)", 7, 'L', GRY)
    side(119, Y0 + 3, sh)
    if sh == 0:
        CX, CY = 105, Y0 + SHEET + 11 + R_WALL_OUT
        pdf.set_draw_color(*GRY); pdf.set_line_width(0.3)
        for r in (R_WALL_OUT, R_WALL_IN): pdf.ellipse(CX - r, CY - r, 2 * r, 2 * r, style='D')
        for m in range(N):
            a = math.radians(90 + (m + 0.5) * 360 / N)
            ux, uy = math.cos(a), -math.sin(a); vx, vy = -uy, ux
            W = lambda r, q: (CX + r * ux + q * vx, CY + r * uy + q * vy)
            arc = lambda R, rev=False: [W(R * math.cos(beta * q / 20), R * math.sin(beta * q / 20))
                                        for q in (range(20, -21, -1) if rev else range(-20, 21))]
            pts = arc(R_IN) + arc(R_OUT, True); pts.append(pts[0])
            pdf.set_draw_color(*RED); pdf.set_line_width(0.22); poly(pts)
            pdf.set_draw_color(*BLU); pdf.set_line_width(0.15)
            poly([arc(R_IN)[0], W(d_i, -S / 2), W(d_i, S / 2), arc(R_IN)[-1]], True)
            poly([arc(R_OUT)[0], W(d_o, -L / 2), W(d_o, L / 2), arc(R_OUT)[-1]], True)
            cx, cy = W((R_IN + R_OUT) / 2, 0); txt(cx, cy + 1, str(m + 1), 6.5, 'C', RED)
        pdf.set_draw_color(*BLK); pdf.set_line_width(0.2)
        pdf.line(CX - 3, CY, CX + 3, CY); pdf.line(CX, CY - 3, CX, CY + 3)
        txt(CX, CY - 6, "1:1 贴放图 (灰圈 = 腔壁)", 7.5, 'C', GRY)
        txt(CX, CY + 6, "蓝虚线 = 修掉的部分", 7, 'C', GRY)

out = "/mnt/d/claude_workspace/macha/pov3d/v1.2/定子盘/隔磁片/隔磁片铺满模板_两张片_18块_A4_1比1.pdf"
pdf.output(out); print(out)
