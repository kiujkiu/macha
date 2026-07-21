"""
A3 landscape drawing — screen_solder_jig: 5-face locating pocket (open +Z top)
for the screen_150x169 module, with 3×M3 through-holes in each ±Y end wall.

Three views (GB first-angle, 1:1):
  1) 俯视图  Top   (looking -Z)      — outer 160×178.75, cavity 150×168.75, hole X
  2) 主视图  Front (looking +Y)      — -Y end wall face 160×18, 3×M3 @ X=-64/0/64, Z9.6
  3) 剖视 A—A     (looking +X, X=0)  — YZ section: floor 3, depth 15, wall 5, hole bore
"""
import math, os
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (mirror build_stl.py) =====
CAV_W, CAV_H, DEPTH = 150.0, 168.75, 15.0
WALL, FLOOR = 4.0, 3.0
OUT_W, OUT_H, OUT_Z = CAV_W + 2*WALL, CAV_H + 2*WALL, DEPTH + FLOOR   # 160,178.75,18
HOLE_D, HOLE_XS = 3.2, [-64.0, 0.0, 64.0]
HOLE_Z = FLOOR + 6.6                                   # 9.6 (6.6 above internal floor)
HOLE_H_ABOVE = HOLE_Z - FLOOR                          # 6.6
xo, yo = OUT_W/2, OUT_H/2                              # 80, 89.375
cx, cy = CAV_W/2, CAV_H/2                              # 75, 84.375
S = 1.0

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
def rot_text(cx_,cy_,s,angle_deg,size=TXT_D,anchor="middle",halo=False):
    pdf.set_font("SimHei","",size); sw=pdf.get_string_width(s)
    with pdf.rotation(angle=angle_deg,x=cx_,y=cy_):
        dx=-sw/2 if anchor=="middle" else (-sw if anchor=="end" else 0)
        if halo:
            fh=pdf.font_size; pdf.set_fill_color(255,255,255); pdf.rect(cx_+dx-0.4,cy_-fh*0.85,sw+0.8,fh*1.1,style="F"); pdf.set_fill_color(0,0,0)
        pdf.text(cx_+dx,cy_,s)
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
def hatch(x0,y0,x1,y1,spacing=2.5,w=0.13):
    xmin,xmax=min(x0,x1),max(x0,x1); ymin,ymax=min(y0,y1),max(y0,y1); _w(w); span=(xmax-xmin)+(ymax-ymin); c=-span
    while c<=span:
        seg=_lb(xmin,xmin-c,xmax,xmax-c,xmin,ymin,xmax,ymax)
        if seg: pdf.line(*seg)
        c+=spacing
def cross(cx_,cy_,r=4.0):
    pdf.set_dash_pattern(dash=1.2,gap=0.6); _w(0.13)
    pdf.line(cx_-r,cy_,cx_+r,cy_); pdf.line(cx_,cy_-r,cx_,cy_+r); pdf.set_dash_pattern(); _w(GEOM_W)
def wrect(vf, x0, y0, x1, y1, hatched=True):
    c=[vf(x0,y0),vf(x1,y0),vf(x1,y1),vf(x0,y1)]; _w(GEOM_W)
    for i in range(4): line(*c[i],*c[(i+1)%4],GEOM_W)
    if hatched: hatch(*vf(x0,y0),*vf(x1,y1))

# ===== header =====
_w(0.3); pdf.rect(5,5,PAGE_W-10,PAGE_H-10,style="D")
text(PAGE_W/2,15,"POV 3D 焊接定位托盘  Screen Solder Jig (5 面开口, +Z 敞开)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,
     f"外形 {OUT_W:g}×{OUT_H:g}×{OUT_Z:g} / 内腔 {CAV_W:g}(X)×{CAV_H:g}(Y)×深 {DEPTH:g} / 壁 {WALL:g}·底 {FLOOR:g} / "
     f"±Y 端壁各 3×Φ{HOLE_D:g} M3 通孔 (X 间距 64, 距内腔底 {HOLE_H_ABOVE:g})  (GB 1st-angle, 1:1, mm)",
     size=TXT_I,anchor="middle")

# ===================== 1) TOP VIEW (looking -Z) =====================
tv_cx, tv_cy = 112.0, 140.0
def tv(x,y): return (tv_cx + x*S, tv_cy + y*S)     # PDF x = world X, down = world +Y
text(tv_cx, 44, "俯视图  Top (1:1)  (沿 -Z 俯视, 开口朝上)", size=TXT_L, anchor="middle")
# outer + cavity rectangles
_w(GEOM_W)
for (x0,y0,x1,y1) in [(-xo,-yo,xo,yo), (-cx,-cy,cx,cy)]:
    c=[tv(x0,y0),tv(x1,y0),tv(x1,y1),tv(x0,y1)]
    for i in range(4): line(*c[i],*c[(i+1)%4],GEOM_W)
# hole bores (hidden) + centerlines through both ±Y wall bands
for x in HOLE_XS:
    pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.18)
    pdf.line(*tv(x,-yo-4), *tv(x,yo+4)); pdf.set_dash_pattern(); _w(HID_W)   # centerline
    pdf.set_dash_pattern(dash=2.0,gap=1.2)
    for dx in (-HOLE_D/2, HOLE_D/2):
        pdf.line(*tv(x+dx,-yo), *tv(x+dx,-cy))      # -Y wall band
        pdf.line(*tv(x+dx, cy), *tv(x+dx, yo))      # +Y wall band
    pdf.set_dash_pattern(); _w(GEOM_W)
# dims
hdim(tv(-xo,yo)[0],tv(xo,yo)[0],tv(0,yo)[1],tv(0,yo)[1]+DIM_O1,f"{OUT_W:g}")       # 160
hdim(tv(-cx,-yo)[0],tv(cx,-yo)[0],tv(0,-yo)[1],tv(0,-yo)[1]-DIM_O1,f"{CAV_W:g}")   # cavity 150
hdim(tv(-64,-yo)[0],tv(0,-yo)[0],tv(0,-yo)[1],tv(0,-yo)[1]-DIM_O2,"64")            # spacing
hdim(tv(0,-yo)[0],tv(64,-yo)[0],tv(0,-yo)[1],tv(0,-yo)[1]-DIM_O2,"64")
vdim(tv(-xo,-yo)[1],tv(-xo,yo)[1],tv(-xo,0)[0],tv(-xo,0)[0]-DIM_O1,f"{OUT_H:g}")   # 178.75
vdim(tv(cx,-cy)[1],tv(cx,cy)[1],tv(xo,0)[0],tv(xo,0)[0]+DIM_O1,f"{CAV_H:g}")       # cavity 168.75
note(*tv(-xo+WALL/2,cy-20), tv(-xo,0)[0]-14, tv(-xo,0)[1]+40, f"壁厚 {WALL:g}", anchor="end")
text(tv_cx, tv(0,0)[1], "内腔 150×168.75 (屏落入)", size=TXT_I, anchor="middle", halo=True)

# ===================== 2) FRONT VIEW (looking +Y, -Y end wall) =====================
fv_cx, fv_z0 = 305.0, 96.0
def fv(x,z): return (fv_cx + x*S, fv_z0 - z*S)      # PDF x = world X, up = world Z
text(fv_cx, 44, "主视图  Front (1:1)  (沿 +Y 看 -Y 端壁, 3×M3)", size=TXT_L, anchor="middle")
# outer wall face
_w(GEOM_W)
c=[fv(-xo,0),fv(xo,0),fv(xo,OUT_Z),fv(-xo,OUT_Z)]
for i in range(4): line(*c[i],*c[(i+1)%4],GEOM_W)
# internal floor reference (Z=FLOOR) dashed
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
pdf.line(*fv(-xo,FLOOR), *fv(xo,FLOOR)); pdf.set_dash_pattern(); _w(GEOM_W)
# holes
for x in HOLE_XS:
    hx,hy=fv(x,HOLE_Z); pdf.circle(hx,hy,HOLE_D/2*S,style="D"); cross(hx,hy,4.5)
# dims
hdim(fv(-xo,0)[0],fv(xo,0)[0],fv(0,0)[1],fv(0,0)[1]+DIM_O1,f"{OUT_W:g}")           # 160
hdim(fv(-64,0)[0],fv(0,0)[0],fv(0,0)[1],fv(0,0)[1]+DIM_O2,"64")
hdim(fv(0,0)[0],fv(64,0)[0],fv(0,0)[1],fv(0,0)[1]+DIM_O2,"64")
vdim(fv(0,OUT_Z)[1],fv(0,0)[1],fv(xo,0)[0],fv(xo,0)[0]+DIM_O1,f"{OUT_Z:g}")        # 18
vdim(fv(0,HOLE_Z)[1],fv(0,FLOOR)[1],fv(-xo,0)[0],fv(-xo,0)[0]-DIM_O1,f"{HOLE_H_ABOVE:g}")  # 6.6
note(*fv(64,HOLE_Z), fv(xo,HOLE_Z)[0]+16, fv(0,HOLE_Z)[1]-8, f"6 × Φ{HOLE_D:g} 通孔 (M3)")
text(fv(xo,HOLE_Z)[0]+16, fv(0,HOLE_Z)[1]-3.5, "两端壁各 3, 沿 Y 穿壁", size=TXT_I, anchor="start")
text(fv(-xo,FLOOR)[0]-2, fv(0,FLOOR)[1]+0.5, "内腔底", size=TXT_I, anchor="end", halo=True)

# ===================== 3) A-A SECTION (looking +X, X=0) =====================
av_cx, av_z0 = 305.0, 220.0
def av(y,z): return (av_cx + y*S, av_z0 - z*S)      # PDF x = world Y, up = world Z
text(av_cx, 168, "剖视 A—A (1:1)  (沿 +X 看 @ X=0, 穿中心孔)", size=TXT_L, anchor="middle")
# material: floor + two end walls (cavity empty between)
wrect(av, -yo, 0.0, yo, FLOOR)               # floor 3
wrect(av, -yo, FLOOR, -cy, OUT_Z)            # -Y end wall
wrect(av,  cy, FLOOR,  yo, OUT_Z)            # +Y end wall
# hole bore (dashed) through both end walls at Z=HOLE_Z
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
for dz in (-HOLE_D/2, HOLE_D/2):
    pdf.line(*av(-yo,HOLE_Z+dz), *av(-cy,HOLE_Z+dz))
    pdf.line(*av( cy,HOLE_Z+dz), *av( yo,HOLE_Z+dz))
pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.18)
pdf.line(*av(-yo-3,HOLE_Z), *av(-cy+2,HOLE_Z))
pdf.line(*av( cy-2,HOLE_Z), *av( yo+3,HOLE_Z))
pdf.set_dash_pattern(); _w(GEOM_W)
# dims
hdim(av(-yo,0)[0],av(yo,0)[0],av(0,0)[1],av(0,0)[1]+DIM_O1,f"{OUT_H:g}")           # 178.75
hdim(av(-cy,0)[0],av(cy,0)[0],av(0,0)[1],av(0,0)[1]+DIM_O2,f"{CAV_H:g}")           # cavity 168.75
hdim(av(-yo,OUT_Z)[0],av(-cy,OUT_Z)[0],av(0,OUT_Z)[1],av(0,OUT_Z)[1]-DIM_O1,f"{WALL:g}")   # wall 5
vdim(av(0,OUT_Z)[1],av(0,0)[1],av(yo,0)[0],av(yo,0)[0]+DIM_O1,f"{OUT_Z:g}")        # 18
vdim(av(0,OUT_Z)[1],av(0,FLOOR)[1],av(yo,0)[0],av(yo,0)[0]+DIM_O2,f"{DEPTH:g}")    # depth 15
vdim(av(0,HOLE_Z)[1],av(0,0)[1],av(-yo,0)[0],av(-yo,0)[0]-DIM_O1,f"{HOLE_Z:g}")    # 9.6 from bottom
note(*av(-cy,FLOOR/2), av(-yo,0)[0]-14, av(0,0)[1]+2, f"底 {FLOOR:g}", anchor="end")
text(av(-yo,HOLE_Z)[0]-2, av(0,HOLE_Z)[1]-1.5, f"(距内腔底 {HOLE_H_ABOVE:g})", size=TXT_I, anchor="end", halo=True)
text(av_cx, av(0,0)[1]+DIM_O2+7, "屏正面朝下落入, 深 15 > 屏厚 7.27 · M3 沿 Y 穿端壁", size=TXT_I, anchor="middle")

# ===== Title block =====
tb_y=PAGE_H-28; tb_x,tb_w,tb_h=20,PAGE_W-40,18
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+6,"POV 3D 结构件 — 焊接定位托盘 (Screen Solder Jig, screen_150x169)",size=TXT_L,anchor="start")
text(tb_x+tb_w-4,tb_y+6,"投影 1st-angle  /  比例 1:1 (俯 / 主 / A—A 剖)",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+14.5,
     f"外形 {OUT_W:g}×{OUT_H:g}×{OUT_Z:g} / 内腔 {CAV_W:g}×{CAV_H:g}×深{DEPTH:g} / 壁{WALL:g}·底{FLOOR:g} / 6×Φ{HOLE_D:g} M3 (±Y壁各3, 间距64, 距底{HOLE_H_ABOVE:g}) / mm",
     size=TXT_I,anchor="start")
text(tb_x+tb_w-4,tb_y+14.5,"2026-07-21  /  POV3D / models / screen_solder_jig / screen_solder_jig.stl",size=TXT_I,anchor="end")

out=Path(__file__).with_name("screen_solder_jig_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt=Path(__file__).with_name("screen_solder_jig_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
