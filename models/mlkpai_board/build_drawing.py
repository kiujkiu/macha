"""
A3 INTERFACE / REFERENCE drawing for the 米联派 MLKPAI-FS03 core board twin
(BOUGHT part — not a fab sheet). Scoped to what the user asked for (2026-07-01):
board outline + 4 corner M3 holes + the two 2×25 pin headers (J11 top / J12 bottom).
All dims measured off the official 位号图 (scale 25.52 px/mm). Board thickness 1.6
is assumed (not on the drawing). GB first-angle, mm.
"""
import math, os
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (centred frame, +Y up) =====
BW, BH = 85.0, 56.0
HX, HY = BW/2, BH/2
THICK  = 1.6
CHX, CHY = 39.5, 25.0
CORNER = [(-CHX, CHY), (CHX, CHY), (-CHX, -CHY), (CHX, -CHY)]
M3 = 3.2
PITCH, NCOL, ROW_DY = 2.54, 25, 2.54
HDR_YC = 24.15
SPAN   = (NCOL-1)*PITCH                 # 60.96 pad-centre span
BASE_L = NCOL*PITCH                      # 63.5
BASE_W = ROW_DY + 3.0                    # 5.54
BASE_H = 2.6                            # plastic base thickness (user-confirmed)
PIN_UP = 5.6                            # exposed pin length beyond base (user-confirmed)
PIN_LEN = 11.0                          # total pin length, pokes both sides (user-confirmed)
PIN_BOT = -(BASE_H + PIN_UP)            # -8.2
PIN_TOP = PIN_BOT + PIN_LEN             #  2.8 (1.2 above PCB top)

PAGE_W, PAGE_H = 420.0, 297.0
pdf = FPDF(orientation="L", unit="mm", format="A3"); pdf.set_auto_page_break(False); pdf.add_page()
_font = next((f for f in ["/mnt/c/Windows/Fonts/simhei.ttf"] if os.path.exists(f)), None)
if _font is None: raise FileNotFoundError("SimHei not found")
pdf.add_font("SimHei", "", _font)
GEOM_W, DIM_W, EXT_W_, HID_W = 0.50, 0.20, 0.20, 0.30
ARR_L, ARR_W, EXT_OV, EXT_GP = 4.2, 1.5, 2.4, 1.0
TXT_D, TXT_L, TXT_T, TXT_I = 4.5, 6.5, 8.0, 4.0
DIM_O1, DIM_O2, DIM_O3 = 12.0, 22.0, 32.0

def _w(v): pdf.set_line_width(v)
def line(x1,y1,x2,y2,w=DIM_W): _w(w); pdf.line(x1,y1,x2,y2)
def arrow(tx,ty,dx,dy):
    L=math.hypot(dx,dy); ux,uy=dx/L,dy/L; bx,by=tx-ARR_L*ux,ty-ARR_L*uy; px,py=-uy,ux
    pdf.set_fill_color(0,0,0); pdf.polygon([(tx,ty),(bx+ARR_W*px,by+ARR_W*py),(bx-ARR_W*px,by-ARR_W*py)],style="F")
def text(x,y,s,size=TXT_D,anchor="start",halo=False):
    pdf.set_font("SimHei","",size)
    if anchor=="middle": x-=pdf.get_string_width(s)/2
    elif anchor=="end": x-=pdf.get_string_width(s)
    if halo:
        sw,fh=pdf.get_string_width(s),pdf.font_size
        pdf.set_fill_color(255,255,255); pdf.rect(x-0.4,y-fh*0.85,sw+0.8,fh*1.1,style="F"); pdf.set_fill_color(0,0,0)
    pdf.text(x,y,s)
def rot_text(cx,cy,s,ang,size=TXT_D,anchor="middle",halo=False):
    pdf.set_font("SimHei","",size); sw=pdf.get_string_width(s)
    with pdf.rotation(angle=ang,x=cx,y=cy):
        dx=-sw/2 if anchor=="middle" else (-sw if anchor=="end" else 0)
        if halo:
            fh=pdf.font_size; pdf.set_fill_color(255,255,255); pdf.rect(cx+dx-0.4,cy-fh*0.85,sw+0.8,fh*1.1,style="F"); pdf.set_fill_color(0,0,0)
        pdf.text(cx+dx,cy,s)
def _u(label,unit="mm"):
    s=str(label).strip(); return s if (not s or unit in s or "°" in s or "×" in s) else f"{s} {unit}"
def hdim(x1,x2,yg,yd,label):
    label=_u(label)
    if yd>yg: ey1,ey2=yg+EXT_GP,yd+EXT_OV
    else: ey1,ey2=yg-EXT_GP,yd-EXT_OV
    line(x1,ey1,x1,ey2,EXT_W_); line(x2,ey1,x2,ey2,EXT_W_)
    xl,xr=(x1,x2) if x1<x2 else (x2,x1)
    if xr-xl>=2*ARR_L+1: line(xl,yd,xr,yd,DIM_W); arrow(xl,yd,-1,0); arrow(xr,yd,1,0)
    else:
        e=ARR_L+1.0; line(xl-e,yd,xr+e,yd,DIM_W); arrow(xl,yd,1,0); arrow(xr,yd,-1,0)
    text((xl+xr)/2,yd-1.8,label,anchor="middle",halo=True)
def vdim(y1,y2,xg,xd,label):
    label=_u(label)
    if xd>xg: ex1,ex2,to=xg+EXT_GP,xd+EXT_OV,4.0
    else: ex1,ex2,to=xg-EXT_GP,xd-EXT_OV,-4.0
    line(ex1,y1,ex2,y1,EXT_W_); line(ex1,y2,ex2,y2,EXT_W_)
    yt,yb=(y1,y2) if y1<y2 else (y2,y1)
    if yb-yt>=2*ARR_L+1: line(xd,yt,xd,yb,DIM_W); arrow(xd,yt,0,-1); arrow(xd,yb,0,1)
    else:
        e=ARR_L+1.0; line(xd,yt-e,xd,yb+e,DIM_W); arrow(xd,yt,0,1); arrow(xd,yb,0,-1)
    lh=pdf.get_string_width(label)
    if yb-yt>=lh+1.0: rot_text(xd+to,(yt+yb)/2,label,90,anchor="middle",halo=True)
    else: rot_text(xd+to,yb+(ARR_L+1.0)+lh/2+1.0,label,90,anchor="middle",halo=True)
def note(xf,yf,xt,yt,label,anchor="start"):
    line(xf,yf,xt,yt,EXT_W_); arrow(xf,yf,xf-xt,yf-yt)
    text(xt+(1.0 if anchor=="start" else -1.0),yt+1.2,label,size=TXT_I,anchor=anchor,halo=True)
def cross(cx,cy,r=3.0):
    pdf.set_dash_pattern(dash=1.2,gap=0.6); _w(0.13); pdf.line(cx-r,cy,cx+r,cy); pdf.line(cx,cy-r,cx,cy+r); pdf.set_dash_pattern(); _w(GEOM_W)

_w(0.3); pdf.rect(5,5,PAGE_W-10,PAGE_H-10,style="D")
text(PAGE_W/2,15,"POV 3D — 米联派 MLKPAI-FS03 ZYNQ 核心板 数字孪生 (买来板 · 参考尺寸图)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,
     f"板 {BW:g}×{BH:g}×{THICK:g}(厚为假定) / 4×M3 Φ{M3:g} 角孔 矩形 {2*CHX:g}×{2*CHY:g}(3mm 内缩) / "
     f"J11(上)·J12(下) 各 2×{NCOL} 排针 @{PITCH:g} 居中  (GB 1st-angle, 2:1, mm)",
     size=TXT_I,anchor="middle")

S = 2.3
# ===================== TOP =====================
tv_cx, tv_cy = 150.0, 150.0
def tv(x,y): return (tv_cx + x*S, tv_cy - y*S)
text(tv_cx,70,"俯视图  Top (2.3:1)   (元件面, 沿 -Z 看)",size=TXT_L,anchor="middle")
_w(GEOM_W); pdf.rect(*tv(-HX,HY),BW*S,BH*S,style="D")
# corner M3 holes
for (x,y) in CORNER: cxp,cyp=tv(x,y); pdf.circle(cxp,cyp,M3/2*S,style="D"); cross(cxp,cyp,4)
# headers: body outline + 2×25 pad grid
def draw_header(yc):
    _w(GEOM_W); pdf.rect(*tv(-BASE_L/2,yc+BASE_W/2),BASE_L*S,BASE_W*S,style="D")
    xs=[(i-(NCOL-1)/2)*PITCH for i in range(NCOL)]
    ys=[yc-ROW_DY/2, yc+ROW_DY/2]
    for x in xs:
        for y in ys:
            cxp,cyp=tv(x,y); pdf.circle(cxp,cyp,0.5*S,style="D")
draw_header(HDR_YC); draw_header(-HDR_YC)
# centre lines
pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.15)
pdf.line(*tv(0,-HY-4),*tv(0,HY+4)); pdf.line(*tv(-HX-4,0),*tv(HX+4,0)); pdf.set_dash_pattern(); _w(GEOM_W)
# ---- dims ----
hdim(tv(-HX,-HY)[0],tv(HX,-HY)[0],tv(0,-HY)[1],tv(0,-HY)[1]+DIM_O2,f"{BW:g}")
hdim(tv(-CHX,-HY)[0],tv(CHX,-HY)[0],tv(0,-HY)[1],tv(0,-HY)[1]+DIM_O1,f"{2*CHX:g}")
vdim(tv(-HX,HY)[1],tv(-HX,-HY)[1],tv(-HX,0)[0],tv(-HX,0)[0]-DIM_O2,f"{BH:g}")
vdim(tv(-CHX,CHY)[1],tv(-CHX,-CHY)[1],tv(-HX,0)[0],tv(-HX,0)[0]-DIM_O1,f"{2*CHY:g}")
# header pin-field span (above J11) + centre-line Y + one 2.54 pitch
hdim(tv(-SPAN/2,HY)[0],tv(SPAN/2,HY)[0],tv(0,HY)[1],tv(0,HY)[1]-DIM_O1,f"{SPAN:.2f}")
vdim(tv(HX,0)[1],tv(HX,HDR_YC)[1],tv(HX,0)[0],tv(HX,0)[0]+DIM_O1,f"{HDR_YC:g}")
vdim(tv(HX,0)[1],tv(HX,-HDR_YC)[1],tv(HX,0)[0],tv(HX,0)[0]+DIM_O2,f"{HDR_YC:g}")
# one pitch (leftmost two J11 pins, top row)
x0p=-(NCOL-1)/2*PITCH
hdim(tv(x0p,HDR_YC+ROW_DY/2)[0],tv(x0p+PITCH,HDR_YC+ROW_DY/2)[0],
     tv(0,HDR_YC+ROW_DY/2+1.5)[1],tv(0,HDR_YC+ROW_DY/2+4)[1],f"{PITCH:g}")
# callouts
note(*tv(CHX,CHY),tv(HX,HY)[0]+8,tv(0,HY)[1]+4,f"4 × Φ{M3:g} (M3) 通孔 角孔")
note(*tv(SPAN/2*0.5,HDR_YC+BASE_W/2),tv(HX,0)[0]+8,tv(0,14)[1],f"J11: 2×{NCOL} 排针 @{PITCH:g}")
note(*tv(SPAN/2*0.5,-HDR_YC-BASE_W/2),tv(HX,0)[0]+8,tv(0,-14)[1],f"J12: 2×{NCOL} 排针 @{PITCH:g}")
text(tv_cx,tv(0,-HY)[1]+DIM_O3,"排针 J11 引脚1在左端 / J12 引脚1在右端 (编号方向, 几何相同) · 行距 2.54",size=TXT_I,anchor="middle")

# ===================== SIDE (right) =====================
sv_x0, sv_cy = 350.0, 150.0
def sv(z,y): return (sv_x0 + z*S, sv_cy - y*S)
text(sv_x0+6*S,70,"右视图  Side (2.3:1)   (板厚 + 排针朝下)",size=TXT_L,anchor="middle")
_w(GEOM_W)
pdf.rect(*sv(0,HY),THICK*S,BH*S,style="D")                                   # PCB edge (Z 0..THICK)
for yc in (HDR_YC,-HDR_YC):                                                    # header body + pins (DOWN, −Z)
    pdf.rect(*sv(-BASE_H,yc+BASE_W/2),BASE_H*S,BASE_W*S,style="D")            # base under board
    for dy in (-ROW_DY/2,ROW_DY/2):
        pdf.rect(*sv(PIN_BOT,yc+dy+0.32),PIN_LEN*S,0.64*S,style="D")         # full 11 pin (both sides)
hdim(sv(0,HY)[0],sv(THICK,HY)[0],sv(0,HY)[1],sv(0,HY)[1]-DIM_O1,f"{THICK:g}")                   # PCB 1.6 (top)
hdim(sv(-BASE_H,-HY)[0],sv(0,-HY)[0],sv(0,-HY)[1],sv(0,-HY)[1]+DIM_O1,f"{BASE_H:g}")            # 座厚 2.6
hdim(sv(PIN_BOT,-HY)[0],sv(-BASE_H,-HY)[0],sv(0,-HY)[1],sv(0,-HY)[1]+DIM_O1,f"{PIN_UP:g}")      # 针露出 5.6
hdim(sv(PIN_BOT,-HY)[0],sv(PIN_TOP,-HY)[0],sv(0,-HY)[1],sv(0,-HY)[1]+DIM_O2,f"{PIN_LEN:g}")     # 针全长 11
vdim(sv(0,HY)[1],sv(0,-HY)[1],sv(THICK,0)[0],sv(THICK,0)[0]+DIM_O1,f"{BH:g}")
text(sv_x0+6*S,sv(0,-HY)[1]+DIM_O3,"排针朝下: 针全长 11 穿板 (座厚 2.6 + 板底露 5.6 + 板顶露 1.2)",size=TXT_I,anchor="middle")

# ===================== title block =====================
tb_y=PAGE_H-26; tb_x,tb_w,tb_h=20,PAGE_W-40,16
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+5.5,"POV 3D — 米联派 MLKPAI-FS03 ZYNQ 核心板 数字孪生 (买来板)",size=TXT_L,anchor="start")
text(tb_x+tb_w-4,tb_y+5.5,"投影 1st-angle  /  比例 2.3:1 (俯, 右)",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+12.5,
     f"板 {BW:g}×{BH:g}×{THICK:g}(厚假定) / 4×M3 Φ{M3:g} ({2*CHX:g}×{2*CHY:g}) / J11·J12 2×{NCOL}排针@{PITCH:g} / mm",
     size=TXT_I,anchor="start")
text(tb_x+tb_w-4,tb_y+12.5,"2026-07-01  /  POV3D / models / mlkpai_board",size=TXT_I,anchor="end")

out=Path(__file__).with_name("mlkpai_board_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt=Path(__file__).with_name("mlkpai_board_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
