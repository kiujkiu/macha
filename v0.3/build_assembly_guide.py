"""
POV3D v3 组装指引图 (assembly guide, 2026-07-13) — A3 横向 1 页。
非加工图: 供人工对齐 组装顺序 + 螺丝用量。三栏:
  左  = 整机堆叠立面示意 (XZ 侧视, 1:0.42 缩放, 关键 Z 标高) + 1)..12) 步骤气泡
  中  = 组装顺序 12 步 (每步动作 + 所用螺丝)
  右  = 紧固件汇总清单 (规格 × 数量 × 用处)
数据基准 = assembly_v3.py 的 Z 链与各件 BOM 注释。输出:
  v3/print/assembly/assembly_v3_guide.pdf
"""
import math
from pathlib import Path
from fpdf import FPDF

PAGE_W, PAGE_H = 420.0, 297.0
pdf = FPDF(orientation="L", unit="mm", format="A3")
pdf.set_auto_page_break(False)
pdf.add_page()
pdf.add_font("SimHei", "", "/mnt/c/Windows/Fonts/simhei.ttf")

def _w(v): pdf.set_line_width(v)
def text(x, y, s, size=4.6, anchor="start"):
    pdf.set_font("SimHei", "", size)
    if   anchor == "middle": x -= pdf.get_string_width(s)/2
    elif anchor == "end":    x -= pdf.get_string_width(s)
    pdf.text(x, y, s)

# ===== 页框 + 标题 =====
_w(0.3)
pdf.rect(5, 5, PAGE_W - 10, PAGE_H - 10, style="D")
text(PAGE_W/2, 13, "POV 3D v3 组装指引 (双面屏)  Assembly Guide", size=9.5, anchor="middle")
text(PAGE_W/2, 18.5, "对齐用示意, 非加工图 / 立面为 XZ 侧视示意 / 标高为装配 Z (洞洞板顶面=0) / 单位: mm",
     size=5.0, anchor="middle")

# ===== 左: 立面示意 =====
S   = 0.42
EX  = 105.0          # x=0 位置
EZ0 = 262.0          # z=0 位置 (页面 y)
def W(x, z): return (EX + x * S, EZ0 - z * S)
def rect(x0, z0, x1, z1, w=0.35, fill=None):
    px0, py1 = W(x0, z0); px1, py0 = W(x1, z1)
    if fill:
        pdf.set_fill_color(*fill)
        pdf.rect(px0, py0, px1 - px0, py1 - py0, style="FD")
        pdf.set_fill_color(0, 0, 0)
    else:
        _w(w); pdf.rect(px0, py0, px1 - px0, py1 - py0, style="D")

text(EX, 27, "整机堆叠立面 (示意)", size=7.0, anchor="middle")

G = (235, 235, 235)   # 浅灰填充 (外购件)
_w(0.35)
# 静止侧
rect(-150, -12, 150, 0, fill=G)                    # 洞洞板
rect(-50, 0, 50, 5)                                 # d100 底盘
rect(-42, 5, 42, 18)                                # 套环 Φ84
rect(-32.5, 5, 32.5, 28)                            # 凸台
rect(-82.5, 18, 82.5, 25)                           # flange_disc
rect(-85, 25, 85, 28)                               # mounting_flange 底板
rect(-25, 5, 25, 31.7, fill=G)                      # 电机
for sx in (-1, 1):                                  # 4×Φ8×350 柱 (画 2)
    rect(sx*121, 0, sx*129, 350)
rect(-134, 350, -22, 364); rect(22, 350, 134, 364)  # frame_A_v2 两臂 (示意)
rect(-8, 353, 8, 358, fill=G); rect(-8, 361, 8, 366, fill=G)   # 688 ×2
# 转子侧
rect(-85, 31.7, 85, 40.7)                           # hub+rim 同层
rect(-85, 40.7, 85, 45.7)                           # 承载盘
rect(-50, 50.7, 50, 52.3, fill=G)                   # pi2hub
rect(-28, 60.8, 28, 63.4, fill=G)                   # 米联派
rect(-13, 45.7, -3, 135.7); rect(3, 45.7, 13, 135.7)  # gantry 塔柱 ×2 (对角)
rect(-3, 66.7, 3, 280.7)                            # screen_plate_v3 (含顶舌)
rect(-10.27, 95.7, -3, 264.7, fill=G)               # 前屏
rect(3, 95.7, 10.27, 264.7, fill=G)                 # 后屏
rect(28, 45.7, 76, 89.1)                            # wifi 盒
rect(-113, 45.7, -64, 50.7)                         # 光电支架
rect(-108, 0, -92, 39)                              # 挡光片 (静止)
rect(-65, 283.7, 65, 292.7)                         # top_cap_v3 板
rect(-7, 267, -3, 283.7); rect(3, 267, 7, 283.7)    # 帽双腿
rect(-3, 286.4, 3, 326.4, fill=G)                   # M6×40
rect(-4, 316.4, 4, 366.4, fill=G)                   # Φ8×50 螺柱
# 定子锁紧长螺丝 ×8 (画 2, 加粗)
_w(0.7)
for sx in (-1, 1):
    p0 = W(sx*36.25, 0); p1 = W(sx*36.25, 28)
    pdf.line(p0[0], p0[1], p1[0], p1[1])
_w(0.35)

# 关键 Z 标高 (右缘小字)
for z, lbl in [(0, "0"), (28, "28"), (31.7, "31.7"), (45.7, "45.7 盘面"),
               (95.7, "95.7 屏底"), (264.7, "264.7 屏顶"), (292.7, "292.7"),
               (350, "350 柱顶"), (366.4, "366.4")]:
    px, py = W(152, z)
    _w(0.12); pdf.line(px - 4, py, px, py)
    text(px + 1.2, py + 1.2, lbl, size=3.8)

# 步骤气泡 1)..12)
def balloon(n, x, z, dx=0.0, dz=0.0):
    px, py = W(x, z)
    px += dx; py += dz
    _w(0.3); pdf.circle(px, py, 2.6, style="D")
    text(px, py + 1.5, str(n), size=4.6, anchor="middle")
BAL = [(1, -60, 2.5), (2, 55, 2.5), (3, 0, 15), (4, -36.25, 22),
       (5, -60, 36), (6, 92, 43), (7, -40, 57), (8, 83, 67),
       (9, -120, 25), (10, -20, 120), (11, 18, 180), (12, -73, 288)]
for (n, bx, bz) in BAL:
    balloon(n, bx, bz)

# ===== 中: 组装顺序 =====
CX = 190.0
text(CX, 27, "组装顺序 (1)..12) 对应立面气泡)", size=7.0)
STEPS = [
 ("1) 压铜花螺母 (烙铁热压, 最先做)",
  "   d100 底面 8 颗 + 承载盘底面 7 颗 (M3×4×4.5); d100 顶面沉孔留空不压"),
 ("2) d100 底座上板", "   转 45° 对脚, 4×M6×16 锁洞洞板 (±50,0)/(0,±50) 网格孔"),
 ("3) 装电机", "   C4110 入凸台孔, 底面沉孔 4×M3×8 从下向上; 电机线走 75°-105° 开口 (内外同高8)"),
 ("4) 定子锁紧 (新)", "   flange_disc 放套环顶 → mounting_flange 翻扣 → 8×M3×30+2mm垫圈"),
 ("", "   PCD Φ72.5 孔一插到底, 锁进 d100 底面铜花螺母 (夹持 3+7+13+5=28)"),
 ("5) 转子毂", "   hub_disc 翻扣 4×M3×8 锁电机转子面; rim_ring 同层嵌套互锁"),
 ("6) 承载盘", "   放上 rim_ring, R35 空余 6 孔 M3×12+螺母 锁紧 (R77.5 8孔留给8)9)10))"),
 ("7) 盘上电子", "   7×尼龙垫柱5 + pi2hub → 7×M3×12 入盘底螺母; 4×尼龙柱8.5 → 米联派插排座"),
 ("8) WiFi 盒", "   模块侧立入盒 → 母头穿 +Y 窗对插 → 倒扣上盘 4×M3×14+螺母 → 扎带"),
 ("9) 光电同步", "   支架 2×M3×16 (板3+盘5+环3.5, 随转子) / 模块 2×M3×8+螺母 (槽口朝下) / 挡光片 2×M6×16 (静止)"),
 ("10) 屏幕支架", "   gantry_v3 ×2 对角放 (件2 转180°) 4×M3×20+螺母; 立板竖起 6×M3×18/20+垫片螺母"),
 ("11) 双面屏", "   先插好两屏排线! 再对头 8×M3×6/8 (每孔两颗, 各入板 ≤2.5) 贴板两面"),
 ("12) 顶帽+轴承", "   M6×40 先装入帽头窝(之后舌挡住装不进!) + Φ8×50 螺柱拧上锁 →"),
 ("", "   双腿夹舌 4×M3×18+垫片螺母 → 4×Φ8×350 柱竖起 → 688×2 入 frame 座 →"),
 ("", "   frame_A (M6×16×2) / frame_B (M6×30×2) 架柱顶, 毂 4×M3×20+螺母 →"),
 ("", "   柱顶 M6 螺母锁紧 → 慢转试机, 配重 M6 平头+螺母 按需调平 (±X 两排对称)"),
]
y = 33.0
for (h, b) in STEPS:
    if h:
        text(CX, y, h, size=4.8); y += 4.6
    if b:
        text(CX, y, b, size=4.3); y += 4.6
    y += 0.8

# ===== 右: 紧固件汇总 =====
RX = 302.0
text(RX, 27, "紧固件汇总 (v3 整机)", size=7.0)
BOM = [
 ("M3×4×4.5 铜花螺母", "15", "盘底 7 / d100 底 8 (热压)"),
 ("M3×8",              "10", "电机底 4 / hub→电机 4 / 光电模块 2(+螺母)"),
 ("M3×6/8 (按屏螺母)",  "8",  "双屏对头固定, 每孔 2 颗"),
 ("M3×12",             "13", "盘→rim_ring 6(+螺母) / pi2hub 7"),
 ("M3×14",             "4",  "wifi 盒耳 (+垫片螺母)"),
 ("M3×16",             "2",  "光电支架 (穿板3+盘+环)"),
 ("M3×18",             "4",  "顶帽夹舌 (+垫片螺母)"),
 ("M3×18/20",          "6",  "立板-塔柱贯通 (+垫片螺母)"),
 ("M3×20",             "8",  "gantry 脚 4(+螺母) / frame 毂 4(+螺母)"),
 ("M3×30 +2mm垫圈",     "8",  "定子锁紧→d100底面螺母 (25不够/30裸装凸底)"),
 ("M3 尼龙柱 8.5",      "4",  "pi2hub-米联派 (+配套尼龙螺丝)"),
 ("M3 尼龙垫柱 ~5",     "7",  "盘-pi2hub"),
 ("M3 螺母",           "~30", "各贯通处 (含垫片)"),
 ("M6×16",             "8",  "d100 脚 4 / 挡光片 2 / frame_A 2"),
 ("M6×30",             "2",  "frame_B 垫柱脚"),
 ("M6×40 平头",         "1",  "转轴 (帽Φ12.5, 12)先装!)"),
 ("Φ8×50 螺柱 M6内丝",  "1",  "轴上段, 穿双 688"),
 ("M6 螺母",           "1+",  "柱顶锁紧 (+柱底/配重按需)"),
 ("Φ8×350 M6螺纹柱",    "4",  "顶轴承立柱 @(±125,±125)"),
 ("688 轴承 8×16×5",   "2",  "frame_A/B 座"),
 ("M6 平头配重+螺母",    "按需", "帽 ±X 两排 19+19 孔调平"),
 ("扎带",              "1",  "wifi 母头防脱"),
]
y = 33.0
text(RX, y, "规格", size=4.8); text(RX + 40, y, "数量", size=4.8); text(RX + 52, y, "用处", size=4.8)
y += 2.0
_w(0.15); pdf.line(RX, y, 413, y)
y += 4.2
for (spec, qty, use) in BOM:
    text(RX, y, spec, size=4.4)
    text(RX + 40, y, qty, size=4.4)
    text(RX + 52, y, use, size=4.0)
    y += 5.3
y += 1.0
_w(0.15); pdf.line(RX, y, 413, y)
text(RX, y + 4.5, "注: d100 顶面 8 沉孔在长螺丝方案下留空;", size=4.2)
text(RX, y + 8.7, "    屏幕螺丝长度装前按屏自带螺母实高确认。", size=4.2)

# ===== 标题栏 =====
tb_y = PAGE_H - 20
_w(0.3)
pdf.rect(20, tb_y, PAGE_W - 40, 12, style="D")
text(24, tb_y + 5, "POV 3D v3 — 组装指引 (组装顺序 + 紧固件清单)  非加工图", size=6.5)
text(24, tb_y + 10, "外购件灰色填充 / 打印件白色 / 粗竖线 = 8×M3×30 定子锁紧螺丝  /  单位 mm", size=4.4)
text(PAGE_W - 24, tb_y + 5, "2026-07-13  /  POV3D / v3 / print / assembly", size=4.6, anchor="end")
text(PAGE_W - 24, tb_y + 10, "数据源: assembly_v3.py + 各件 build 脚本 BOM", size=4.4, anchor="end")

out = Path(__file__).parent / "print/assembly/assembly_v3_guide.pdf"
pdf.output(str(out))
print(f"wrote {out}")
