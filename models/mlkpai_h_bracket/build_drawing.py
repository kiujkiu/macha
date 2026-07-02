"""
A3 drawing — rotated-H MLKPAI-FS03 ZYNQ bracket (3 mm): slots open LEFT/RIGHT,
central 5 holes centred on the board. Bolts to the 85×56 board's 4 corner M3 holes;
central Φ24 + 24 mm-square 4×M3. Two views (GB first-angle).
Corner-hole positions ESTIMATED (verify pitch).
"""
import math, os
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (centred frame, +Y up) =====
BW, BH = 85.0, 56.0
HX, HY = BW/2, BH/2
SLOT_W, SLOT_H = 25.0, 44.0            # slot left-right × top-bottom (both sides)
BAR_IN, SPINE_X = SLOT_H/2, HX-SLOT_W  # 22, 17.5
CX, CY = 0.0, 0.0                      # central group centred
M3C, M3S = 3.4, 3.4
CENTER_D, SQ = 24.0, 24.0
SQH = [(CX + sx*SQ/2, CY + sy*SQ/2) for sx in (-1, 1) for sy in (-1, 1)]
CHX, CHY = 39.5, 25.0                  # corner |X|,|Y| (pitch 79×50, user-confirmed)
CORNER = [(-CHX, CHY), (CHX, CHY), (-CHX, -CHY), (CHX, -CHY)]
THICK = 3.0
S = 2.0

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
    s=str(label).strip(); return s if (not s or unit in s or "°" in s) else f"{s} {unit}"
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
def cross(cx,cy,r=3.5):
    pdf.set_dash_pattern(dash=1.2,gap=0.6); _w(0.13); pdf.line(cx-r,cy,cx+r,cy); pdf.line(cx,cy-r,cx,cy+r); pdf.set_dash_pattern(); _w(GEOM_W)

_w(0.3); pdf.rect(5,5,PAGE_W-10,PAGE_H-10,style="D")
text(PAGE_W/2,15,"POV 3D — 米联派 MLKPAI-FS03 ZYNQ 板 H 形支架 (左右开槽, t=3)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,
     f"对位板 85×56: 4×M3 角孔(矩形 {2*CHX:g}×{2*CHY:g}) / 中心 Φ{CENTER_D:g}+{SQ:g}方阵 4×M3 居中(0,0) / 两侧凹槽 {SLOT_W:g}×{SLOT_H:g} 缺口开左右 / 板厚 {THICK:g}"
     f"  (GB 1st-angle, 2:1, mm)", size=TXT_I,anchor="middle")

# ===================== TOP =====================
tv_cx, tv_cy = 145.0, 150.0
def tv(x,y): return (tv_cx + x*S, tv_cy - y*S)
text(tv_cx,82,"俯视图  Top (2:1)   (沿 -Z 看)",size=TXT_L,anchor="middle")
op=[(-HX,HY),(HX,HY),(HX,BAR_IN),(SPINE_X,BAR_IN),(SPINE_X,-BAR_IN),(HX,-BAR_IN),(HX,-HY),
    (-HX,-HY),(-HX,-BAR_IN),(-SPINE_X,-BAR_IN),(-SPINE_X,BAR_IN),(-HX,BAR_IN),(-HX,HY)]
_w(GEOM_W)
for i in range(len(op)-1): line(*tv(*op[i]),*tv(*op[i+1]),GEOM_W)
for (x,y) in CORNER: cxp,cyp=tv(x,y); pdf.circle(cxp,cyp,M3C/2*S,style="D"); cross(cxp,cyp,5)
for (x,y) in SQH:    cxp,cyp=tv(x,y); pdf.circle(cxp,cyp,M3S/2*S,style="D"); cross(cxp,cyp,4)
cxp,cyp=tv(CX,CY); pdf.circle(cxp,cyp,CENTER_D/2*S,style="D"); cross(cxp,cyp,8)
pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.15)
pdf.line(*tv(0,-HY-4),*tv(0,HY+4)); pdf.line(*tv(-HX-4,0),*tv(HX+4,0)); pdf.set_dash_pattern(); _w(GEOM_W)
# dims — overall + corner pitch
hdim(tv(-HX,-HY)[0],tv(HX,-HY)[0],tv(0,-HY)[1],tv(0,-HY)[1]+DIM_O2,f"{BW:g}")
hdim(tv(-CHX,-HY)[0],tv(CHX,-HY)[0],tv(0,-HY)[1],tv(0,-HY)[1]+DIM_O1,f"{2*CHX:g}")
vdim(tv(-HX,HY)[1],tv(-HX,-HY)[1],tv(-HX,0)[0],tv(-HX,0)[0]-DIM_O2,f"{BH:g}")
vdim(tv(-CHX,CHY)[1],tv(-CHX,-CHY)[1],tv(-HX,0)[0],tv(-HX,0)[0]-DIM_O1,f"{2*CHY:g}")
# central square 24×24
hdim(tv(-SQ/2,SQ/2)[0],tv(SQ/2,SQ/2)[0],tv(0,SQ/2)[1],tv(0,SQ/2)[1]-7,f"{SQ:g}")
vdim(tv(SQ/2,SQ/2)[1],tv(SQ/2,-SQ/2)[1],tv(SQ/2,0)[0],tv(SQ/2,0)[0]+7,f"{SQ:g}")
# slot dims (right slot): width 25 (X) + height 44 (Y), inside the slot
sxc = (SPINE_X + HX) / 2               # right-slot centre X
hdim(tv(SPINE_X,BAR_IN)[0],tv(HX,BAR_IN)[0],tv(sxc,BAR_IN)[1],tv(sxc,BAR_IN-5)[1],f"{SLOT_W:g}")
vdim(tv(sxc,BAR_IN)[1],tv(sxc,-BAR_IN)[1],tv(sxc,0)[0],tv(sxc+5,0)[0],f"{SLOT_H:g}")
text(tv(sxc,0)[0],tv(sxc,-BAR_IN)[1]-3,"两侧凹槽相同",size=TXT_I,anchor="middle",halo=True)
# callouts into the empty L slot
note(*tv(-CENTER_D/2*0.7,CENTER_D/2*0.7),tv(-SPINE_X,0)[0]-12,tv(0,9)[1],f"Φ{CENTER_D:g} 窗口 居中",anchor="end")
note(*tv(-SQ/2,-SQ/2),tv(-SPINE_X,0)[0]-12,tv(0,-9)[1],f"4 × Φ{M3S:g} (M3) {SQ:g}方阵",anchor="end")
note(*tv(CHX,CHY),tv(HX,HY)[0]+6,tv(0,HY)[1]-2,f"4 × Φ{M3C:g} (M3) 角孔")
text(tv_cx,tv(0,-HY)[1]+DIM_O3+4,"缺口开左右 / 上下横梁各 6mm,角孔壁较薄(~1.3mm) / 中心 5 孔居中(芯片实际+3.7)",size=TXT_I,anchor="middle")

# ===================== SIDE =====================
sv_x0, sv_cy = 330.0, 150.0
def sv(z,y): return (sv_x0 + z*S, sv_cy - y*S)
text(sv_x0+THICK*S/2,82,"右视图  Side (2:1)   (板厚)",size=TXT_L,anchor="middle")
_w(GEOM_W); pdf.rect(*sv(0,HY),THICK*S,BH*S,style="D")
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
for y in sorted({yy for _,yy in CORNER}|{yy for _,yy in SQH}|{CY}):
    pdf.line(*sv(0,y),*sv(THICK,y))
pdf.set_dash_pattern(); _w(GEOM_W)
hdim(sv(0,-HY)[0],sv(THICK,-HY)[0],sv(0,-HY)[1],sv(0,-HY)[1]+DIM_O1,f"{THICK:g}")
vdim(sv(0,HY)[1],sv(0,-HY)[1],sv(THICK,0)[0],sv(THICK,0)[0]+DIM_O1,f"{BH:g}")
text(sv_x0+THICK*S/2,sv(0,-HY)[1]+DIM_O2,"板厚 3 (虚线=各通孔)",size=TXT_I,anchor="middle")

tb_y=PAGE_H-26; tb_x,tb_w,tb_h=20,PAGE_W-40,16
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+5.5,"POV 3D 结构件 — MLKPAI-FS03 ZYNQ H 形支架 (左右开槽, t3)",size=TXT_L,anchor="start")
text(tb_x+tb_w-4,tb_y+5.5,"投影 1st-angle  /  比例 2:1 (俯, 右)",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+12.5,
     f"外形 {BW:g}×{BH:g}×{THICK:g} / 4×M3 角孔({2*CHX:g}×{2*CHY:g} 估算) / Φ{CENTER_D:g}+{SQ:g}方阵 4×M3 居中 / mm",
     size=TXT_I,anchor="start")
text(tb_x+tb_w-4,tb_y+12.5,"2026-06-23  /  POV3D / models / mlkpai_h_bracket",size=TXT_I,anchor="end")

out=Path(__file__).with_name("mlkpai_h_bracket_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt=Path(__file__).with_name("mlkpai_h_bracket_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
