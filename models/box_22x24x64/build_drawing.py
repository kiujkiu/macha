"""
A3 landscape drawing — box open on the +X long side (5 faces), windowed
asymmetric front panel + M4 holes.  External 22×24×64.

Three views (GB first-angle, 2:1):
  1) 主视图  Front (looking +Y)         — -Y 1 mm panel: window 14×35 + 2 M4 holes
  2) 左视全剖 A-A (looking +X, X=0)      — YZ section: ends/walls, window height 35
  3) 横剖 B-B (looking -Z, Z=32)         — XY section: OPEN +X side, window width 14
"""
import math, os
from pathlib import Path
from fpdf import FPDF

# ===== Geometry =====
EXT_L, EXT_W, EXT_H = 22.0, 24.0, 64.0
WALL_FRONT, WALL_BACK, WALL_SIDE, WALL_END = 1.0, 2.0, 2.0, 2.0
WIN_X, WIN_Z, WIN_ZC, WIN_XC = 14.0, 35.0, 32.0, 4.0   # window shifted +4 in X
WZ0, WZ1 = WIN_ZC - WIN_Z/2, WIN_ZC + WIN_Z/2   # 14.5, 49.5
WX0, WX1 = WIN_XC - WIN_X/2, WIN_XC + WIN_X/2     # -3, 11 (right edge = +X panel edge)
HOLE_DIAM, HOLE_CC = 4.5, 44.0
HOLE_Z = [EXT_H/2 - HOLE_CC/2, EXT_H/2 + HOLE_CC/2]   # 10, 54
CAV_X0, CAV_Y0, CAV_Y1 = -EXT_L/2+WALL_SIDE, -EXT_W/2+WALL_FRONT, EXT_W/2-WALL_BACK  # -9,-11,10
CAV_Z0, CAV_Z1 = WALL_END, EXT_H-WALL_END         # 2, 62
xo, yo = EXT_L/2, EXT_W/2                          # 11, 12
S = 2.0

# ===== PDF =====
PAGE_W, PAGE_H = 420.0, 297.0
pdf = FPDF(orientation="L", unit="mm", format="A3"); pdf.set_auto_page_break(False); pdf.add_page()
_font = next((f for f in ["/mnt/c/Windows/Fonts/simhei.ttf"] if os.path.exists(f)), None)
if _font is None: raise FileNotFoundError("SimHei not found")
pdf.add_font("SimHei", "", _font)
GEOM_W, DIM_W, EXT_W_, HID_W = 0.50, 0.20, 0.20, 0.30
ARR_L, ARR_W, EXT_OV, EXT_GP = 4.2, 1.5, 2.4, 1.0
TXT_D, TXT_L, TXT_T, TXT_I = 4.5, 6.5, 8.0, 4.0
DIM_O1, DIM_O2, DIM_O3 = 12.0, 22.0, 34.0

def _w(v): pdf.set_line_width(v)
def line(x1,y1,x2,y2,w=DIM_W): _w(w); pdf.line(x1,y1,x2,y2)
def arrow(tx,ty,dx,dy):
    L=math.hypot(dx,dy); ux,uy=dx/L,dy/L; bx,by=tx-ARR_L*ux,ty-ARR_L*uy; px,py=-uy,ux
    pdf.set_fill_color(0,0,0)
    pdf.polygon([(tx,ty),(bx+ARR_W*px,by+ARR_W*py),(bx-ARR_W*px,by-ARR_W*py)],style="F")
def text(x,y,s,size=TXT_D,anchor="start",halo=False):
    pdf.set_font("SimHei","",size)
    if anchor=="middle": x-=pdf.get_string_width(s)/2
    elif anchor=="end": x-=pdf.get_string_width(s)
    if halo:
        sw,fh=pdf.get_string_width(s),pdf.font_size
        pdf.set_fill_color(255,255,255); pdf.rect(x-0.4,y-fh*0.85,sw+0.8,fh*1.1,style="F"); pdf.set_fill_color(0,0,0)
    pdf.text(x,y,s)
def rot_text(cx,cy,s,angle_deg,size=TXT_D,anchor="middle",halo=False):
    pdf.set_font("SimHei","",size); sw=pdf.get_string_width(s)
    with pdf.rotation(angle=angle_deg,x=cx,y=cy):
        dx=-sw/2 if anchor=="middle" else (-sw if anchor=="end" else 0)
        if halo:
            fh=pdf.font_size; pdf.set_fill_color(255,255,255); pdf.rect(cx+dx-0.4,cy-fh*0.85,sw+0.8,fh*1.1,style="F"); pdf.set_fill_color(0,0,0)
        pdf.text(cx+dx,cy,s)
def _u(label,unit="mm"):
    s=str(label).strip()
    return s if (not s or unit in s or "°" in s) else f"{s} {unit}"
def hdim(x1,x2,yg,yd,label):
    label=_u(label)
    if yd>yg: ey1,ey2=yg+EXT_GP,yd+EXT_OV
    else: ey1,ey2=yg-EXT_GP,yd-EXT_OV
    line(x1,ey1,x1,ey2,EXT_W_); line(x2,ey1,x2,ey2,EXT_W_)
    xl,xr=(x1,x2) if x1<x2 else (x2,x1)
    if xr-xl>=2*ARR_L+1:
        line(xl,yd,xr,yd,DIM_W); arrow(xl,yd,-1,0); arrow(xr,yd,1,0)
    else:
        e=ARR_L+1.0; line(xl-e,yd,xr+e,yd,DIM_W); arrow(xl,yd,1,0); arrow(xr,yd,-1,0)
    text((xl+xr)/2,yd-1.8,label,anchor="middle",halo=True)
def vdim(y1,y2,xg,xd,label):
    label=_u(label)
    if xd>xg: ex1,ex2,to=xg+EXT_GP,xd+EXT_OV,4.0
    else: ex1,ex2,to=xg-EXT_GP,xd-EXT_OV,-4.0
    line(ex1,y1,ex2,y1,EXT_W_); line(ex1,y2,ex2,y2,EXT_W_)
    yt,yb=(y1,y2) if y1<y2 else (y2,y1)
    if yb-yt>=2*ARR_L+1:
        line(xd,yt,xd,yb,DIM_W); arrow(xd,yt,0,-1); arrow(xd,yb,0,1)
    else:
        e=ARR_L+1.0; line(xd,yt-e,xd,yb+e,DIM_W); arrow(xd,yt,0,1); arrow(xd,yb,0,-1)
    lh=pdf.get_string_width(label)
    if yb-yt>=lh+1.0: rot_text(xd+to,(yt+yb)/2,label,90,anchor="middle",halo=True)
    else: rot_text(xd+to,yb+(ARR_L+1.0)+lh/2+1.0,label,90,anchor="middle",halo=True)
def note(xf,yf,xt,yt,label,anchor="start"):
    line(xf,yf,xt,yt,EXT_W_); arrow(xf,yf,xf-xt,yf-yt)
    text(xt+(1.0 if anchor=="start" else -1.0),yt+1.2,label,size=TXT_I,anchor=anchor,halo=True)
def _lb(x0,y0,x1,y1,xmin,ymin,xmax,ymax):
    dx,dy=x1-x0,y1-y0; p=[-dx,dx,-dy,dy]; q=[x0-xmin,xmax-x0,y0-ymin,ymax-y0]; u0,u1=0.0,1.0
    for pi,qi in zip(p,q):
        if pi==0:
            if qi<0: return None
        else:
            t=qi/pi
            if pi<0: u0=max(u0,t)
            else: u1=min(u1,t)
    if u0>u1: return None
    return (x0+u0*dx,y0+u0*dy,x0+u1*dx,y0+u1*dy)
def hatch(x0,y0,x1,y1,spacing=2.0,w=0.13):
    xmin,xmax=min(x0,x1),max(x0,x1); ymin,ymax=min(y0,y1),max(y0,y1); _w(w); span=(xmax-xmin)+(ymax-ymin); c=-span
    while c<=span:
        seg=_lb(xmin,xmin-c,xmax,xmax-c,xmin,ymin,xmax,ymax)
        if seg: pdf.line(*seg)
        c+=spacing
def cross(cx,cy,r=5.0):
    pdf.set_dash_pattern(dash=1.2,gap=0.6); _w(0.13)
    pdf.line(cx-r,cy,cx+r,cy); pdf.line(cx,cy-r,cx,cy+r); pdf.set_dash_pattern(); _w(GEOM_W)
def wrect(vf, x0, y0, x1, y1, hatched=True):
    """outline (+hatch) of a world-rect via view fn vf(a,b)->(px,py)."""
    c=[vf(x0,y0),vf(x1,y0),vf(x1,y1),vf(x0,y1)]; _w(GEOM_W)
    for i in range(4): line(*c[i],*c[(i+1)%4],GEOM_W)
    if hatched: hatch(*vf(x0,y0),*vf(x1,y1))

# ===== header =====
_w(0.3); pdf.rect(5,5,PAGE_W-10,PAGE_H-10,style="D")
text(PAGE_W/2,15,"POV 3D 盒子  Box 22×24×64  (单侧开口 +X, 前面板开窗)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,
     f"外形 {EXT_L:g}×{EXT_W:g}×{EXT_H:g} / +X 侧({EXT_H:g}×{EXT_W:g}) 敞开 / 前(-Y){WALL_FRONT:g}·后(+Y){WALL_BACK:g}·侧(-X){WALL_SIDE:g}·顶底{WALL_END:g} / "
     f"前面板中央开穿窗口 {WIN_X:g}(宽X)×{WIN_Z:g}(高Z) / 前后各 2×Φ{HOLE_DIAM:g} M4 (中心距 {HOLE_CC:g})  (GB 1st-angle, 2:1, mm)",
     size=TXT_I,anchor="middle")

# ===================== 1) FRONT VIEW (looking +Y) =====================
fv_cx, fv_z0 = 72.0, 214.0
def fv(x,z): return (fv_cx+x*S, fv_z0-z*S)
text(fv_cx,62,"主视图  Front (2:1)  (沿 +Y 看 -Y 1mm 前面板)",size=TXT_L,anchor="middle")
# C-notch outline: window now reaches the +X (right, open-side) edge
_w(GEOM_W)
op=[(-xo,0),(xo,0),(xo,WZ0),(WX0,WZ0),(WX0,WZ1),(xo,WZ1),(xo,EXT_H),(-xo,EXT_H),(-xo,0)]
for i in range(len(op)-1): line(*fv(*op[i]),*fv(*op[i+1]),GEOM_W)
pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.18)
pdf.line(*fv(0,-4),*fv(0,EXT_H+4)); pdf.set_dash_pattern(); _w(GEOM_W)  # hole centerline X=0
for hz in HOLE_Z:
    cx,cy=fv(0,hz); pdf.circle(cx,cy,HOLE_DIAM/2*S,style="D"); cross(cx,cy,5)
# dims
hdim(fv(-xo,0)[0],fv(xo,0)[0],fv(0,0)[1],fv(0,0)[1]+DIM_O1,f"{EXT_L:g}")                 # 22
hdim(fv(WX0,0)[0],fv(xo,0)[0],fv(0,0)[1],fv(0,0)[1]+DIM_O2,f"{WIN_X:g}")                 # window width 14 (to +X edge)
vdim(fv(0,EXT_H)[1],fv(0,0)[1],fv(-xo,0)[0],fv(-xo,0)[0]-DIM_O3,f"{EXT_H:g}")            # 64
vdim(fv(0,HOLE_Z[0])[1],fv(0,0)[1],fv(-xo,0)[0],fv(-xo,0)[0]-DIM_O1,f"{HOLE_Z[0]:g}")    # 10
vdim(fv(0,HOLE_Z[1])[1],fv(0,HOLE_Z[0])[1],fv(-xo,0)[0],fv(-xo,0)[0]-DIM_O2,f"{HOLE_CC:g}")  # 44
vdim(fv(0,WZ1)[1],fv(0,WZ0)[1],fv(xo,0)[0],fv(xo,0)[0]+DIM_O1,f"{WIN_Z:g}")              # window height 35
note(*fv(0,HOLE_Z[1]),fv(xo,HOLE_Z[1])[0]+14,fv(0,HOLE_Z[1])[1]-5,f"4 × Φ{HOLE_DIAM:g} 通孔 (M4)")
text(fv(xo,HOLE_Z[1])[0]+14,fv(0,HOLE_Z[1])[1]+0.5,"前后面板各 2 · X 居中",size=TXT_I,anchor="start")
text(*fv(WIN_XC,WIN_ZC),"开穿窗口",size=TXT_I,anchor="middle",halo=True)
text(fv(WX0,WZ0)[0],fv(WX0,WZ0)[1]+5,f"右移{WIN_XC:g},右缘平齐+X开口边 (左实体 {xo+WX0:g})",size=TXT_I,anchor="start",halo=True)

# ===================== 2) A-A SECTION (looking +X, X=0) =====================
sv_cx, sv_z0 = 188.0, 214.0
def sv(y,z): return (sv_cx+y*S, sv_z0-z*S)   # PDF x = world Y, up = world Z
text(sv_cx,62,"左视图 — 全剖 A—A (2:1)  (沿 +X 看, 即开口方向)",size=TXT_L,anchor="middle")
# material rects: bottom, top, back wall, front wall lower, front wall upper
wrect(sv,-yo,0,yo,CAV_Z0)               # bottom 2mm
wrect(sv,-yo,CAV_Z1,yo,EXT_H)           # top 2mm
wrect(sv,CAV_Y1,CAV_Z0,yo,CAV_Z1)       # back wall 2mm
wrect(sv,-yo,CAV_Z0,CAV_Y0,WZ0)         # front wall lower segment
wrect(sv,-yo,WZ1,CAV_Y0,CAV_Z1)         # front wall upper segment
# hole bores (dashed) + centerlines through both walls
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
for hz in HOLE_Z:
    for dz in (-HOLE_DIAM/2,HOLE_DIAM/2): pdf.line(*sv(-yo,hz+dz),*sv(yo,hz+dz))
pdf.set_dash_pattern(); _w(GEOM_W)
for hz in HOLE_Z:
    pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.18)
    pdf.line(*sv(-yo-3,hz),*sv(yo+3,hz)); pdf.set_dash_pattern(); _w(GEOM_W)
# dims
hdim(sv(-yo,0)[0],sv(yo,0)[0],sv(0,0)[1],sv(0,0)[1]+DIM_O1,f"{EXT_W:g}")
vdim(sv(0,EXT_H)[1],sv(0,0)[1],sv(yo,0)[0],sv(yo,0)[0]+DIM_O2,f"{EXT_H:g}")
vdim(sv(0,WZ1)[1],sv(0,WZ0)[1],sv(-yo,0)[0],sv(-yo,0)[0]-DIM_O1,f"{WIN_Z:g}")   # window height 35
note(*sv(-yo+WALL_FRONT/2,WZ0),sv(-yo,0)[0]-12,sv(0,WZ0)[1]+6,f"前面板 {WALL_FRONT:g} (薄,开窗)")
note(*sv(yo-WALL_BACK/2,EXT_H-6),sv(yo,0)[0]+12,sv(0,EXT_H)[1]-2,f"后面板 {WALL_BACK:g}",anchor="end")
text(sv_cx,sv(0,EXT_H)[1]-3,f"顶/底 {WALL_END:g}",size=TXT_I,anchor="middle",halo=True)
text(sv_cx,sv(0,0)[1]+DIM_O1+7,"窗口 35 高 · 2×M4 @ Z=10/54 (孔在窗上下)",size=TXT_I,anchor="middle")

# ===================== 3) B-B SECTION (looking -Z, Z=32) =====================
bv_cx, bv_cy = 332.0, 175.0
def bv(x,y): return (bv_cx+x*S, bv_cy+y*S)   # PDF x = world X, down = world Y
text(bv_cx,118,"横剖 B—B (2:1)  (沿 -Z 看 @ Z=32)",size=TXT_L,anchor="middle")
# material rects at Z=32: back wall, side(-X) wall, front wall L/R (window gap)
wrect(bv,-xo,CAV_Y1,xo,yo)          # back wall (+Y) 2mm
wrect(bv,-xo,-yo,CAV_X0,yo)         # side (-X) 2mm
wrect(bv,-xo,-yo,WX0,CAV_Y0)        # front wall left of window (only segment; window now reaches +X edge)
# OPEN +X side: dashed break + arrow note (no wall)
pdf.set_dash_pattern(dash=3.0,gap=2.0); _w(0.3)
pdf.line(*bv(xo,-yo),*bv(xo,yo)); pdf.set_dash_pattern(); _w(GEOM_W)
note(*bv(xo,0),bv(xo,0)[0]+14,bv(0,-yo)[1]-3,f"+X 此侧开口 ({EXT_H:g}×{EXT_W:g})")
# dims
hdim(bv(-xo,yo)[0],bv(xo,yo)[0],bv(0,yo)[1],bv(0,yo)[1]+DIM_O1,f"{EXT_L:g}")
hdim(bv(WX0,-yo)[0],bv(WX1,-yo)[0],bv(0,-yo)[1],bv(0,-yo)[1]-DIM_O1,f"{WIN_X:g}")   # window width 14
vdim(bv(-xo,-yo)[1],bv(-xo,yo)[1],bv(-xo,0)[0],bv(-xo,0)[0]-DIM_O1,f"{EXT_W:g}")
note(*bv(-xo+WALL_SIDE/2,yo-4),bv(-xo,0)[0]-12,bv(0,yo)[1]+4,f"侧 {WALL_SIDE:g}",anchor="end")
text(bv_cx,bv(0,yo)[1]+DIM_O1+7,f"前(上){WALL_FRONT:g}·后(下){WALL_BACK:g}·侧{WALL_SIDE:g} / 窗宽 {WIN_X:g}",size=TXT_I,anchor="middle")

# ===== Title block =====
tb_y=PAGE_H-28; tb_x,tb_w,tb_h=20,PAGE_W-40,18
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+6,"POV 3D 结构件 — 单侧开口盒 (Box 22×24×64, 开窗前板)",size=TXT_L,anchor="start")
text(tb_x+tb_w-4,tb_y+6,"投影 1st-angle  /  比例 2:1 (主, 左-全剖, 横剖)",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+14.5,
     f"外形 {EXT_L:g}×{EXT_W:g}×{EXT_H:g} / +X侧开 / 前1·后2·侧2·顶底2 / 窗 {WIN_X:g}×{WIN_Z:g} / 4×Φ{HOLE_DIAM:g} M4 (中心距{HOLE_CC:g}) / mm",
     size=TXT_I,anchor="start")
text(tb_x+tb_w-4,tb_y+14.5,"2026-06-22  /  POV3D / models / box_22x24x64 / box_22x24x64.stl",size=TXT_I,anchor="end")

out=Path(__file__).with_name("box_22x24x64_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt=Path(__file__).with_name("box_22x24x64_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
