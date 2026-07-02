"""
A3 drawing — mlkpai_carrier_disc (Φ170×6 转子承载盘, 更新 2026-07-01).
俯视图 + 凸台铜螺母孔详图。承载 pi2hub75e: 6×Φ10 凸台(带铜螺母孔) + 3×Φ3 托。
GB first-angle, mm.
"""
import math, os
from pathlib import Path
from fpdf import FPDF

DISC_OD, THICK = 170.0, 6.0
INNER_R, OUTER_R = 35.0, 77.5
BOSS_XY = [(-39.5,25),(39.5,25),(-39.5,-25),(39.5,-25),(-39.5,-55),(39.5,-55)]
BOSS_D, BOSS_H = 10.0, 2.0
THRU_D, INSERT_D, INSERT_DEEP = 3.2, 4.2, 4.0
TUO_XY = [(-48.5,37),(-4,37),(45,40)]
TUO_D, TUO_H = 3.0, 2.0
M3, CB_D, CB_DEEP = 3.2, 7.0, 2.5

PAGE_W, PAGE_H = 420.0, 297.0
pdf = FPDF(orientation="L", unit="mm", format="A3"); pdf.set_auto_page_break(False); pdf.add_page()
_font = "/mnt/c/Windows/Fonts/simhei.ttf"
if not os.path.exists(_font): raise FileNotFoundError("SimHei not found")
pdf.add_font("SimHei", "", _font)
GEOM_W, DIM_W, EXT_W_, HID_W = 0.5, 0.2, 0.2, 0.3
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
def _u(l,unit="mm"):
    s=str(l).strip(); return s if (not s or unit in s or "°" in s or "Φ" in s) else f"{s} {unit}"
def hdim(x1,x2,yg,yd,label):
    label=_u(label)
    ey1,ey2=(yg+EXT_GP,yd+EXT_OV) if yd>yg else (yg-EXT_GP,yd-EXT_OV)
    line(x1,ey1,x1,ey2,EXT_W_); line(x2,ey1,x2,ey2,EXT_W_)
    xl,xr=(x1,x2) if x1<x2 else (x2,x1)
    if xr-xl>=2*ARR_L+1: line(xl,yd,xr,yd,DIM_W); arrow(xl,yd,-1,0); arrow(xr,yd,1,0)
    else:
        e=ARR_L+1.0; line(xl-e,yd,xr+e,yd,DIM_W); arrow(xl,yd,1,0); arrow(xr,yd,-1,0)
    text((xl+xr)/2,yd-1.8,label,anchor="middle",halo=True)
def vdim(y1,y2,xg,xd,label):
    label=_u(label)
    ex1,ex2,to=(xg+EXT_GP,xd+EXT_OV,4.0) if xd>xg else (xg-EXT_GP,xd-EXT_OV,-4.0)
    line(ex1,y1,ex2,y1,EXT_W_); line(ex1,y2,ex2,y2,EXT_W_)
    yt,yb=(y1,y2) if y1<y2 else (y2,y1)
    if yb-yt>=2*ARR_L+1: line(xd,yt,xd,yb,DIM_W); arrow(xd,yt,0,-1); arrow(xd,yb,0,1)
    else:
        e=ARR_L+1.0; line(xd,yt-e,xd,yb+e,DIM_W); arrow(xd,yt,0,1); arrow(xd,yb,0,-1)
    lh=pdf.get_string_width(label)
    rot_text(xd+to,(yt+yb)/2 if yb-yt>=lh+1 else yb+ARR_L+1+lh/2+1,label,90,anchor="middle",halo=True)
def note(xf,yf,xt,yt,label,anchor="start"):
    line(xf,yf,xt,yt,EXT_W_); arrow(xf,yf,xf-xt,yf-yt)
    text(xt+(1.0 if anchor=="start" else -1.0),yt+1.2,label,size=TXT_I,anchor=anchor,halo=True)
def cross(cx,cy,r=2.6):
    pdf.set_dash_pattern(dash=1.2,gap=0.6); _w(0.13); pdf.line(cx-r,cy,cx+r,cy); pdf.line(cx,cy-r,cx,cy+r); pdf.set_dash_pattern(); _w(GEOM_W)

_w(0.3); pdf.rect(5,5,PAGE_W-10,PAGE_H-10,style="D")
text(PAGE_W/2,15,"POV 3D — mlkpai_carrier_disc  转子承载盘 Φ170×6 (承载 pi2hub75e + 米联派)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,
     "16×M3 挂环孔(PCD Φ70+Φ155)装 rim_ring / 6×Φ10 凸台(铜螺母孔,固定pi2hub)@(±39.5,25/−25/−55) / 3×Φ3 托(顶连接器)"
     "  GB 1st-angle, mm", size=TXT_I,anchor="middle")

# ===== TOP view =====
S=1.15; tv_cx, tv_cy = 148.0, 158.0
def tv(x,y): return (tv_cx + x*S, tv_cy - y*S)
text(tv_cx,44,"俯视图  Top (1.15:1)",size=TXT_L,anchor="middle")
_w(GEOM_W); pdf.circle(tv_cx,tv_cy,DISC_OD/2*S,style="D")
pdf.set_dash_pattern(dash=3,gap=2); _w(0.15)
pdf.circle(tv_cx,tv_cy,INNER_R*S,style="D"); pdf.circle(tv_cx,tv_cy,OUTER_R*S,style="D"); pdf.set_dash_pattern(); _w(GEOM_W)
for R in (INNER_R,OUTER_R):
    for k in range(8):
        a=math.radians(22.5+45*k); x,y=R*math.cos(a),R*math.sin(a)
        cxp,cyp=tv(x,y); pdf.circle(cxp,cyp,M3/2*S,style="D")
# 6 bosses: Φ14 outer + Φ4.2 + Φ3.2 concentric
for (x,y) in BOSS_XY:
    cxp,cyp=tv(x,y)
    pdf.circle(cxp,cyp,BOSS_D/2*S,style="D"); pdf.circle(cxp,cyp,INSERT_D/2*S,style="D"); pdf.circle(cxp,cyp,THRU_D/2*S,style="D"); cross(cxp,cyp,4)
# 3 tuo Φ6
for (x,y) in TUO_XY:
    cxp,cyp=tv(x,y); pdf.circle(cxp,cyp,TUO_D/2*S,style="D"); cross(cxp,cyp,3)
# centre lines
pdf.set_dash_pattern(dash=4,gap=1.5); _w(0.15)
pdf.line(*tv(-DISC_OD/2-6,0),*tv(DISC_OD/2+6,0)); pdf.line(*tv(0,-DISC_OD/2-6),*tv(0,DISC_OD/2+6)); pdf.set_dash_pattern(); _w(GEOM_W)
# dims
hdim(tv(-DISC_OD/2,-DISC_OD/2)[0],tv(DISC_OD/2,-DISC_OD/2)[0],tv(0,-DISC_OD/2)[1],tv(0,-DISC_OD/2)[1]+DIM_O2,f"Φ{DISC_OD:g}")
hdim(tv(-39.5,-55)[0],tv(39.5,-55)[0],tv(0,-55)[1],tv(0,-55)[1]-DIM_O1,"79")
vdim(tv(-39.5,25)[1],tv(-39.5,-25)[1],tv(-39.5,0)[0],tv(-39.5,0)[0]-DIM_O1,"50")
vdim(tv(39.5,-25)[1],tv(39.5,-55)[1],tv(39.5,0)[0],tv(39.5,0)[0]+DIM_O1,"30")
note(tv(-39.5,25)[0],tv(-39.5,25)[1],tv(-DISC_OD/2,0)[0]-4,tv(0,44)[1],"6×Φ10 凸台 (h2) / Φ3.2通+Φ4.2铜螺母沉",anchor="end")
note(tv(-48.5,37)[0],tv(-48.5,37)[1],tv(-DISC_OD/2,0)[0]-4,tv(0,30)[1],"3×Φ3 托 (h2) 让开排针 T1/T2/T3",anchor="end")
note(tv(OUTER_R*math.cos(math.radians(157.5)),OUTER_R*math.sin(math.radians(157.5)))[0],
     tv(OUTER_R*math.cos(math.radians(157.5)),OUTER_R*math.sin(math.radians(157.5)))[1],
     tv(DISC_OD/2,0)[0]+6,tv(0,20)[1],"16×Φ3.2+Φ7沉 (PCD Φ70/Φ155) 装 rim_ring")

# ===== DETAIL: boss insert hole section (4:1) =====
DS=4.0; dx0, dcy = 340.0, 150.0
def dv(x,z): return (dx0 + x*DS, dcy - z*DS)   # z up; disc bottom z=0, boss top z=8
text(dx0,44,"凸台铜螺母孔 详图 (4:1, 剖)",size=TXT_L,anchor="middle")
_w(GEOM_W)
halfb=BOSS_D/2   # boss half-width (Φ10 → 5)
halfd=11.0       # show a disc chunk each side
# disc slab 0..6, boss 6..8; hole: Φ4.2 pocket at BOTTOM (0..4), Φ3.2 neck to top (4..8)
def profile(sgn):
    xo=sgn*halfd; xb=sgn*halfb; xi42=sgn*INSERT_D/2; xi32=sgn*THRU_D/2
    # outer edge up, disc top to boss, up boss, boss top to Φ3.2 neck, down to shoulder z4, out to Φ4.2, down to bottom
    pts=[dv(xo,0),dv(xo,6),dv(xb,6),dv(xb,8),dv(xi32,8),dv(xi32,4),dv(xi42,4),dv(xi42,0)]
    for i in range(len(pts)-1): line(*pts[i],*pts[i+1],GEOM_W)
profile(-1); profile(1)
line(*dv(-halfd,0),*dv(-INSERT_D/2,0),GEOM_W); line(*dv(INSERT_D/2,0),*dv(halfd,0),GEOM_W)  # bottom face (Φ4.2 open)
# centre line
pdf.set_dash_pattern(dash=3,gap=1.5); _w(0.15); pdf.line(*dv(0,-2),*dv(0,10)); pdf.set_dash_pattern(); _w(GEOM_W)
# dims
hdim(dv(-INSERT_D/2,0)[0],dv(INSERT_D/2,0)[0],dv(0,0)[1],dv(0,0)[1]+DIM_O1,f"Φ{INSERT_D:g}")   # Φ4.2 at bottom
hdim(dv(-THRU_D/2,8)[0],dv(THRU_D/2,8)[0],dv(0,8)[1],dv(0,8)[1]-DIM_O1,f"Φ{THRU_D:g}")         # Φ3.2 at top
hdim(dv(-halfb,8)[0],dv(halfb,8)[0],dv(0,8)[1],dv(0,8)[1]-DIM_O2,f"Φ{BOSS_D:g}")
vdim(dv(halfd,0)[1],dv(halfd,6)[1],dv(halfd,0)[0],dv(halfd,0)[0]+DIM_O1,f"{THICK:g}")
vdim(dv(halfb,6)[1],dv(halfb,8)[1],dv(halfb,6)[0],dv(halfb,6)[0]+DIM_O1,f"{BOSS_H:g}")
vdim(dv(-INSERT_D/2,0)[1],dv(-INSERT_D/2,4)[1],dv(-halfd,0)[0]-6,dv(-halfd,0)[0]-6,f"{INSERT_DEEP:g}")  # depth 4 from bottom
text(dx0,dv(0,0)[1]+DIM_O2,"Φ4.2 从盘底向上沉 4 深 (Z0..4, 压铜螺母, Z4 台肩挡住); Φ3.2 通到凸台顶",size=TXT_I,anchor="middle")
text(dx0,dv(0,0)[1]+DIM_O2+6,"盘6 + 凸台2 = 8; 顶上螺丝穿 pi2hub 拧入铜螺母把它拉紧",size=TXT_I,anchor="middle")

# ===== title block =====
tb_y=PAGE_H-24; tb_x,tb_w,tb_h=20,PAGE_W-40,14
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+5,"POV 3D — mlkpai_carrier_disc 转子承载盘 (承载 pi2hub75e)",size=TXT_L,anchor="start")
text(tb_x+tb_w-4,tb_y+5,"1st-angle / 俯 1.15:1, 详 4:1",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+11,f"Φ{DISC_OD:g}×{THICK:g} / 16×M3挂环 / 6×Φ{BOSS_D:g}凸台(Φ{THRU_D:g}+Φ{INSERT_D:g}沉{INSERT_DEEP:g}) / 3×Φ{TUO_D:g}托 / mm",size=TXT_I,anchor="start")
text(tb_x+tb_w-4,tb_y+11,"2026-07-01 / POV3D / models / mlkpai_carrier_disc",size=TXT_I,anchor="end")

out=Path(__file__).with_name("mlkpai_carrier_disc_drawing.pdf")
try: pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt=Path(__file__).with_name("mlkpai_carrier_disc_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
