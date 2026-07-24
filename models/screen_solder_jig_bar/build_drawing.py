"""
A3 landscape drawing — screen_solder_jig_bar: screen_solder_jig 的可卸底条,
L 形全宽条 (端壁 + 底唇), 端壁含 3×M3。切在下排方孔下沿 Y=62。

Three views (GB first-angle, 1:1):
  1) 主视图  Front (looking +Y)  — 端壁面 158.3×18, 3×M3 @ X=-64/0/64, Z9.6
  2) 侧视 L 截面 (looking +X)     — YZ: 端壁 4×18 + 底唇 22.525×3, 孔 Z9.6
  3) 俯视图  Top (looking -Z)     — 足印 158.3×26.525, 孔中心线
"""
import math, os
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (mirror build_stl.py) =====
CAV_W, CAV_H, DEPTH = 150.3, 169.05, 15.0
WALL, FLOOR = 4.0, 3.0
OUT_W, OUT_Z = CAV_W + 2*WALL, DEPTH + FLOOR          # 158.3, 18
OUT_H = CAV_H + 2*WALL                                 # 177.05
HOLE_D, HOLE_XS = 3.2, [-64.0, 0.0, 64.0]
HOLE_Z = FLOOR + 6.6                                   # 9.6
HOLE_H_ABOVE = HOLE_Z - FLOOR                          # 6.6
BAR_DEPTH_Y = 10.0                                    # 用户 2026-07-21: 26.525→10
yo = OUT_H/2                                           # 88.525
CUT_Y = yo - BAR_DEPTH_Y                               # 78.525
DEPTH_Y = BAR_DEPTH_Y                                  # 10 (bar depth in Y)
LIP = DEPTH_Y - WALL                                   # 6 (floor lip width)
xo = OUT_W/2                                           # 79.15
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

# ===== header =====
_w(0.3); pdf.rect(5,5,PAGE_W-10,PAGE_H-10,style="D")
text(PAGE_W/2,15,"POV 3D 焊接托盘可卸底条  Screen Solder Jig — Bottom Bar (L 形)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,
     f"从 screen_solder_jig 切下外缘 {DEPTH_Y:g}mm (Y={CUT_Y:g}) / 全宽 {OUT_W:g} × 深 {DEPTH_Y:g} × 高 {OUT_Z:g} / "
     f"端壁 {WALL:g}×{OUT_Z:g} (3×Φ{HOLE_D:g} M3 间距64 距底{HOLE_H_ABOVE:g}) + 底唇 {LIP:g}×{FLOOR:g}  (GB 1st-angle, 1:1, mm)",
     size=TXT_I,anchor="middle")

# ===================== 1) FRONT VIEW (looking +Y, wall face) =====================
fv_cx, fv_z0 = 150.0, 88.0
def fv(x,z): return (fv_cx + x*S, fv_z0 - z*S)
text(fv_cx, 40, "主视图  Front (1:1)  (沿 +Y 看端壁, 3×M3)", size=TXT_L, anchor="middle")
_w(GEOM_W)
c=[fv(-xo,0),fv(xo,0),fv(xo,OUT_Z),fv(-xo,OUT_Z)]
for i in range(4): line(*c[i],*c[(i+1)%4],GEOM_W)
# floor-top reference dashed (Z=FLOOR)
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
pdf.line(*fv(-xo,FLOOR), *fv(xo,FLOOR)); pdf.set_dash_pattern(); _w(GEOM_W)
for x in HOLE_XS:
    hx,hy=fv(x,HOLE_Z); pdf.circle(hx,hy,HOLE_D/2*S,style="D"); cross(hx,hy,4.5)
hdim(fv(-xo,0)[0],fv(xo,0)[0],fv(0,0)[1],fv(0,0)[1]+DIM_O1,f"{OUT_W:g}")
hdim(fv(-64,0)[0],fv(0,0)[0],fv(0,0)[1],fv(0,0)[1]+DIM_O2,"64")
hdim(fv(0,0)[0],fv(64,0)[0],fv(0,0)[1],fv(0,0)[1]+DIM_O2,"64")
vdim(fv(0,OUT_Z)[1],fv(0,0)[1],fv(xo,0)[0],fv(xo,0)[0]+DIM_O1,f"{OUT_Z:g}")
vdim(fv(0,HOLE_Z)[1],fv(0,FLOOR)[1],fv(-xo,0)[0],fv(-xo,0)[0]-DIM_O1,f"{HOLE_H_ABOVE:g}")
note(*fv(64,HOLE_Z), fv(xo,HOLE_Z)[0]+16, fv(0,HOLE_Z)[1]-8, f"3 × Φ{HOLE_D:g} 通孔 (M3)")
text(fv(-xo,FLOOR)[0]-2, fv(0,FLOOR)[1]+0.5, "底唇顶面", size=TXT_I, anchor="end", halo=True)

# ===================== 2) SIDE VIEW — L profile (looking +X) =====================
sv_cx, sv_z0 = 300.0, 120.0
def sv(yy,z): return (sv_cx + yy*S, sv_z0 - z*S)   # yy = Y-CUT_Y (0..DEPTH_Y), up=Z
text(sv_cx, 40, "侧视 L 截面 (1:1)  (沿 +X 看)", size=TXT_L, anchor="middle")
# L outline (yy: 0 = 切口/底唇前缘, DEPTH_Y = 外缘; 壁在 yy=LIP..DEPTH_Y)
_w(GEOM_W)
Lpts=[(0,0),(DEPTH_Y,0),(DEPTH_Y,OUT_Z),(LIP,OUT_Z),(LIP,FLOOR),(0,FLOOR),(0,0)]
for i in range(len(Lpts)-1): line(*sv(*Lpts[i]),*sv(*Lpts[i+1]),GEOM_W)
# M3 bore (dashed) in the wall at Z=HOLE_Z (wall spans yy LIP..DEPTH_Y)
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
for dz in (-HOLE_D/2, HOLE_D/2):
    pdf.line(*sv(LIP,HOLE_Z+dz), *sv(DEPTH_Y,HOLE_Z+dz))
pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.18)
pdf.line(*sv(LIP-3,HOLE_Z), *sv(DEPTH_Y+3,HOLE_Z)); pdf.set_dash_pattern(); _w(GEOM_W)
# dims
hdim(sv(0,0)[0],sv(DEPTH_Y,0)[0],sv(0,0)[1],sv(0,0)[1]+DIM_O1,f"{DEPTH_Y:g}")       # depth 26.525
hdim(sv(LIP,0)[0],sv(DEPTH_Y,0)[0],sv(0,0)[1],sv(0,0)[1]+DIM_O2,f"{WALL:g}")        # wall 4
vdim(sv(0,OUT_Z)[1],sv(0,0)[1],sv(0,0)[0],sv(0,0)[0]-DIM_O1,f"{OUT_Z:g}")           # height 18
vdim(sv(0,HOLE_Z)[1],sv(0,0)[1],sv(0,0)[0],sv(0,0)[0]-DIM_O2,f"{HOLE_Z:g}")         # hole Z 9.6
vdim(sv(DEPTH_Y,FLOOR)[1],sv(DEPTH_Y,0)[1],sv(DEPTH_Y,0)[0],sv(DEPTH_Y,0)[0]+DIM_O1,f"{FLOOR:g}")  # floor 3
note(*sv(LIP/2,FLOOR), sv(0,0)[0]-4, sv(0,FLOOR)[1]-8, f"底唇 {LIP:g} 宽×{FLOOR:g} 厚", anchor="start")

# ===================== 3) TOP VIEW (looking -Z) =====================
tv_cx, tv_cy = 150.0, 200.0
def tv(x,yy): return (tv_cx + x*S, tv_cy + (yy - DEPTH_Y/2)*S)   # x=X, down=Y
text(tv_cx, 156, "俯视图  Top (1:1)  (沿 -Z, 足印 158.3×26.525)", size=TXT_L, anchor="middle")
_w(GEOM_W)
c=[tv(-xo,0),tv(xo,0),tv(xo,DEPTH_Y),tv(-xo,DEPTH_Y)]
for i in range(4): line(*c[i],*c[(i+1)%4],GEOM_W)
# wall inner face edge (step between lip Z0..3 and wall Z0..18) at yy=LIP
line(*tv(-xo,LIP), *tv(xo,LIP), GEOM_W)
# hole centerlines (holes in the wall band)
for x in HOLE_XS:
    pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.18)
    pdf.line(*tv(x,LIP-2), *tv(x,DEPTH_Y+3)); pdf.set_dash_pattern(); _w(HID_W)
    pdf.set_dash_pattern(dash=2.0,gap=1.2)
    for dx in (-HOLE_D/2,HOLE_D/2): pdf.line(*tv(x+dx,LIP), *tv(x+dx,DEPTH_Y))
    pdf.set_dash_pattern(); _w(GEOM_W)
hdim(tv(-xo,DEPTH_Y)[0],tv(xo,DEPTH_Y)[0],tv(0,DEPTH_Y)[1],tv(0,DEPTH_Y)[1]+DIM_O1,f"{OUT_W:g}")
vdim(tv(-xo,0)[1],tv(-xo,DEPTH_Y)[1],tv(-xo,0)[0],tv(-xo,0)[0]-DIM_O1,f"{DEPTH_Y:g}")
vdim(tv(xo,LIP)[1],tv(xo,DEPTH_Y)[1],tv(xo,0)[0],tv(xo,0)[0]+DIM_O1,f"{WALL:g}")
text(tv_cx, tv(0,LIP/2)[1], "底唇 (Z0..3)", size=TXT_I, anchor="middle", halo=True)
text(tv_cx, tv(0,LIP+WALL/2)[1]+1.5, "端壁 (Z0..18)", size=TXT_I, anchor="middle", halo=True)

# ===== Title block =====
tb_y=PAGE_H-28; tb_x,tb_w,tb_h=20,PAGE_W-40,18
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+6,"POV 3D 结构件 — 焊接托盘可卸底条 (Screen Solder Jig Bottom Bar)",size=TXT_L,anchor="start")
text(tb_x+tb_w-4,tb_y+6,"投影 1st-angle  /  比例 1:1 (主 / 侧 L / 俯)",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+14.5,
     f"全宽 {OUT_W:g}×深 {DEPTH_Y:g}×高 {OUT_Z:g} / 端壁 {WALL:g} (3×Φ{HOLE_D:g} M3 间距64 距底{HOLE_H_ABOVE:g}) + 底唇 {LIP:g}×{FLOOR:g} / 切自 Y={CUT_Y:g} / mm",
     size=TXT_I,anchor="start")
text(tb_x+tb_w-4,tb_y+14.5,"2026-07-21  /  POV3D / models / screen_solder_jig_bar / screen_solder_jig_bar.stl",size=TXT_I,anchor="end")

out=Path(__file__).with_name("screen_solder_jig_bar_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt=Path(__file__).with_name("screen_solder_jig_bar_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
