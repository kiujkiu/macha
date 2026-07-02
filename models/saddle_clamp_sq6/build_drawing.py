"""
A3 landscape drawing — square-bridge saddle clamp for a 6×6 object, 2×M6 @ 25, t=3.
Three views (GB first-angle, 4:1):
  1) 主视图 Front (looking +Y) — square inverted-U profile + feet + M6 holes + 6×6 object
  2) 俯视图 Top  (looking -Z)  — footprint, 2 × Φ6.5 M6 (c-c 25), width 14
  3) 左视图 Side (looking +X)  — width × height, 6×6 object channel hidden
"""
import math, os
from pathlib import Path
from fpdf import FPDF

# ===== Geometry =====
INNER = 6.0
HALF = INNER/2.0       # 3
ZIN = INNER            # 6
T = 3.0
OHALF = HALF + T       # 6
HTOP = ZIN + T         # 9
W = 14.0
M6 = 6.5
CC = 25.0
HX = CC/2.0           # 12.5
FOOT = HX + 6.0       # 18.5
S = 4.0

# ===== PDF =====
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
def cross(cx,cy,r=4.0):
    pdf.set_dash_pattern(dash=1.2,gap=0.6); _w(0.13); pdf.line(cx-r,cy,cx+r,cy); pdf.line(cx,cy-r,cx,cy+r); pdf.set_dash_pattern(); _w(GEOM_W)

# ===== header =====
_w(0.3); pdf.rect(5,5,PAGE_W-10,PAGE_H-10,style="D")
text(PAGE_W/2,15,"POV 3D 马鞍压条 / 抱箍  Saddle Clamp  (方形过桥, 夹持 6×6)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,
     f"内腔 {INNER:g}×{INNER:g} 方 / 料厚 {T:g} / 压条宽 {W:g} / 外形 {2*FOOT:g}×{W:g}×{HTOP:g} / 2×Φ{M6:g} M6 通孔 (孔距 {CC:g}) / "
     f"物体贴板,顶部方形压住,两脚 M6 固定  (GB 1st-angle, 4:1, mm)",
     size=TXT_I,anchor="middle")

# ===================== 1) FRONT (looking +Y) =====================
fv_cx, fv_z0 = 115.0, 150.0
def fv(x,z): return (fv_cx+x*S, fv_z0-z*S)
text(fv_cx,84,"主视图  Front (4:1)   (沿 +Y 看, 物体轴线方向)",size=TXT_L,anchor="middle")
# square inverted-U outline + feet (single closed path)
op=[(-FOOT,0),(-FOOT,T),(-OHALF,T),(-OHALF,HTOP),(OHALF,HTOP),(OHALF,T),(FOOT,T),(FOOT,0),
    (HALF,0),(HALF,ZIN),(-HALF,ZIN),(-HALF,0),(-FOOT,0)]
_w(GEOM_W)
for i in range(len(op)-1): line(*fv(*op[i]),*fv(*op[i+1]),GEOM_W)
# inner 6×6 opening is the object passage (solid outline above); mark its centre
cross(*fv(0,ZIN/2),5)
# M6 holes hidden (edge-on) in feet
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
for sx in (-1,1):
    for e in (-M6/2,M6/2): pdf.line(*fv(sx*HX+e,0),*fv(sx*HX+e,T))
pdf.set_dash_pattern(); _w(GEOM_W)
for sx in (-1,1):
    pdf.set_dash_pattern(dash=3.0,gap=1.2,phase=1.0); _w(0.15); pdf.line(*fv(sx*HX,-3),*fv(sx*HX,T+3)); pdf.set_dash_pattern(); _w(GEOM_W)
# dims
hdim(fv(-HX,0)[0],fv(HX,0)[0],fv(0,0)[1],fv(0,0)[1]+DIM_O1,f"{CC:g}")
hdim(fv(-FOOT,0)[0],fv(FOOT,0)[0],fv(0,0)[1],fv(0,0)[1]+DIM_O2,f"{2*FOOT:g}")
vdim(fv(0,HTOP)[1],fv(0,0)[1],fv(-FOOT,0)[0],fv(-FOOT,0)[0]-DIM_O2,f"{HTOP:g}")
vdim(fv(0,T)[1],fv(0,0)[1],fv(-FOOT,0)[0],fv(-FOOT,0)[0]-DIM_O1,f"{T:g}")
hdim(fv(-HALF,ZIN)[0],fv(HALF,ZIN)[0],fv(0,ZIN)[1],fv(0,ZIN)[1]-DIM_O1,f"{INNER:g}")    # inner width 6
vdim(fv(0,ZIN)[1],fv(0,0)[1],fv(-HALF,0)[0],fv(-HALF,0)[0]+5,f"{ZIN:g}")                 # inner height 6 (inside channel)
note(*fv(OHALF*0.6,HTOP),fv(OHALF,HTOP)[0]+10,fv(0,HTOP)[1]+1,f"壁厚 {T:g}")
note(*fv(HALF,ZIN*0.5),fv(OHALF,HTOP)[0]+10,fv(0,HTOP)[1]+8,f"夹持 {INNER:g}×{INNER:g} 方 (内腔)")
note(*fv(HX,T),fv(FOOT,T)[0]+8,fv(0,T)[1]-8,f"2 × Φ{M6:g} 通孔 (M6)")

# ===================== 2) TOP (looking -Z) =====================
tv_cx, tv_cy = 115.0, 218.0
def tv(x,y): return (tv_cx+x*S, tv_cy+y*S)
text(tv_cx,196,"俯视图  Top (4:1)   (沿 -Z 看)",size=TXT_L,anchor="middle")
_w(GEOM_W); pdf.rect(*tv(-FOOT,-W/2),2*FOOT*S,W*S,style="D")
for sx in (-1,1):
    line(*tv(sx*OHALF,-W/2),*tv(sx*OHALF,W/2),GEOM_W)        # bridge-foot edge (visible)
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
for X in (-HALF,HALF): pdf.line(*tv(X,-W/2),*tv(X,W/2))      # object channel (hidden)
pdf.set_dash_pattern(); _w(GEOM_W)
for sx in (-1,1):
    cx,cy=tv(sx*HX,0); pdf.circle(cx,cy,M6/2*S,style="D"); cross(cx,cy,6)
hdim(tv(-HX,0)[0],tv(HX,0)[0],tv(0,W/2)[1],tv(0,W/2)[1]+DIM_O1,f"{CC:g}")
hdim(tv(-FOOT,0)[0],tv(FOOT,0)[0],tv(0,W/2)[1],tv(0,W/2)[1]+DIM_O2,f"{2*FOOT:g}")
vdim(tv(0,-W/2)[1],tv(0,W/2)[1],tv(FOOT,0)[0],tv(FOOT,0)[0]+DIM_O1,f"{W:g}")
note(*tv(HX,-M6/2),tv(FOOT,0)[0]+8,tv(0,-W/2)[1]-6,f"2 × Φ{M6:g} (M6)")
text(tv_cx,tv(0,W/2)[1]+DIM_O2+6,f"压条/物体居中 (虚线为 {INNER:g}×{INNER:g} 方通道)",size=TXT_I,anchor="middle")

# ===================== 3) SIDE (looking +X) =====================
sv_cx, sv_z0 = 305.0, 150.0
def sv(y,z): return (sv_cx+y*S, sv_z0-z*S)
text(sv_cx,84,"左视图  Side (4:1)   (沿 +X 看)",size=TXT_L,anchor="middle")
_w(GEOM_W); pdf.rect(*sv(-W/2,HTOP),W*S,HTOP*S,style="D")
line(*sv(-W/2,T),*sv(W/2,T),GEOM_W)
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
pdf.line(*sv(-W/2,ZIN),*sv(W/2,ZIN))                          # channel ceiling (hidden)
pdf.set_dash_pattern(); _w(GEOM_W)
pdf.set_dash_pattern(dash=3.0,gap=1.2,phase=1.0); _w(0.15); pdf.line(*sv(0,-3),*sv(0,HTOP+3)); pdf.set_dash_pattern(); _w(GEOM_W)
hdim(sv(-W/2,0)[0],sv(W/2,0)[0],sv(0,0)[1],sv(0,0)[1]+DIM_O1,f"{W:g}")
vdim(sv(0,HTOP)[1],sv(0,0)[1],sv(W/2,0)[0],sv(W/2,0)[0]+DIM_O1,f"{HTOP:g}")
vdim(sv(0,ZIN)[1],sv(0,0)[1],sv(-W/2,0)[0],sv(-W/2,0)[0]-DIM_O1,f"{ZIN:g}")
text(sv_cx,sv(0,0)[1]+DIM_O1+7,f"物体 {INNER:g}×{INNER:g} 沿 Y 穿过 (虚线)",size=TXT_I,anchor="middle")

# ===== Title block =====
tb_y=PAGE_H-26; tb_x,tb_w,tb_h=20,PAGE_W-40,16
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+5.5,"POV 3D 结构件 — 马鞍压条/抱箍 (方形过桥, 夹持 6×6)",size=TXT_L,anchor="start")
text(tb_x+tb_w-4,tb_y+5.5,"投影 1st-angle  /  比例 4:1 (主, 俯, 左)",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+12.5,
     f"内腔 {INNER:g}×{INNER:g} 方 / 料厚 {T:g} / 宽 {W:g} / 外形 {2*FOOT:g}×{W:g}×{HTOP:g} / 2×Φ{M6:g} M6 (孔距 {CC:g}) / mm",
     size=TXT_I,anchor="start")
text(tb_x+tb_w-4,tb_y+12.5,"2026-06-23  /  POV3D / models / saddle_clamp_sq6 / saddle_clamp_sq6.stl",size=TXT_I,anchor="end")

out=Path(__file__).with_name("saddle_clamp_sq6_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt=Path(__file__).with_name("saddle_clamp_sq6_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
