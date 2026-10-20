"""
A3 drawing — vane_slider_v3 (v3 光电挡光滑片, 刀片印长装机剪短版, 锁 frame_B 45°臂筋, 2026-07-24)。
参数 import 自 build_vane_slider.py。GB 1st-angle, 2.5:1。
主视图 X-Z (板+全长刀片+名义剪裁线), 左视图 Y-Z, 俯视图 X-Y。
"""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from fpdf import FPDF

from build_vane_slider import (PLATE_X0, PLATE_X1, PLATE_Y0, PLATE_Y1, PLATE_Z1,
                               HOLE_XS, HOLE_D, HOLE_Z,
                               BLADE_X0, BLADE_X1, BLADE_Z0, TRIM_Z0)

FONT = "/mnt/c/Windows/Fonts/simhei.ttf"
GEOM_W, DIM_W, EXT_W_, HID_W = 0.50, 0.20, 0.20, 0.30
ARR_L, ARR_W, EXT_OV, EXT_GP = 4.2, 1.5, 2.4, 1.0
TXT_D, TXT_L, TXT_T, TXT_I = 4.5, 6.5, 8.0, 4.0
DIM_O1, DIM_O2 = 12.0, 22.0
PAGE_W, PAGE_H = 420.0, 297.0

pdf = FPDF(orientation="L", unit="mm", format="A3"); pdf.set_auto_page_break(False); pdf.add_page()
pdf.add_font("SimHei", "", FONT)

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
def rot_text(cx,cy,s,ang,size=TXT_D,halo=False):
    pdf.set_font("SimHei","",size); sw=pdf.get_string_width(s)
    with pdf.rotation(angle=ang,x=cx,y=cy):
        if halo:
            fh=pdf.font_size; pdf.set_fill_color(255,255,255); pdf.rect(cx-sw/2-0.4,cy-fh*0.85,sw+0.8,fh*1.1,style="F"); pdf.set_fill_color(0,0,0)
        pdf.text(cx-sw/2,cy,s)
def _u(s): s=str(s).strip(); return s if ("mm" in s or "°" in s) else f"{s} mm"
def hdim(x1,x2,yg,yd,label):
    label=_u(label)
    e1,e2=(yg+EXT_GP,yd+EXT_OV) if yd>yg else (yg-EXT_GP,yd-EXT_OV)
    line(x1,e1,x1,e2,EXT_W_); line(x2,e1,x2,e2,EXT_W_)
    xl,xr=min(x1,x2),max(x1,x2)
    if xr-xl>=2*ARR_L+1: line(xl,yd,xr,yd); arrow(xl,yd,-1,0); arrow(xr,yd,1,0)
    else:
        e=ARR_L+1.0; line(xl-e,yd,xr+e,yd); arrow(xl,yd,1,0); arrow(xr,yd,-1,0)
    text((xl+xr)/2,yd-1.8,label,anchor="middle",halo=True)
def vdim(y1,y2,xg,xd,label):
    label=_u(label)
    e1,e2,to=(xg+EXT_GP,xd+EXT_OV,4.0) if xd>xg else (xg-EXT_GP,xd-EXT_OV,-4.0)
    line(e1,y1,e2,y1,EXT_W_); line(e1,y2,e2,y2,EXT_W_)
    yt,yb=min(y1,y2),max(y1,y2)
    if yb-yt>=2*ARR_L+1: line(xd,yt,xd,yb); arrow(xd,yt,0,-1); arrow(xd,yb,0,1)
    else:
        e=ARR_L+1.0; line(xd,yt-e,xd,yb+e); arrow(xd,yt,0,1); arrow(xd,yb,0,-1)
    lh=pdf.get_string_width(label)
    if yb-yt>=lh+1.0: rot_text(xd+to,(yt+yb)/2,label,90,halo=True)
    else: rot_text(xd+to,yb+ARR_L+1.0+lh/2+1.0,label,90,halo=True)
def note(xf,yf,xt,yt,label,anchor="start"):
    line(xf,yf,xt,yt,EXT_W_); arrow(xf,yf,xf-xt,yf-yt)
    text(xt+(1.0 if anchor=="start" else -1.0),yt+1.2,label,size=TXT_I,anchor=anchor,halo=True)
def rect(x0,y0,x1,y1,w=GEOM_W):
    _w(w); pdf.line(x0,y0,x1,y0); pdf.line(x1,y0,x1,y1); pdf.line(x1,y1,x0,y1); pdf.line(x0,y1,x0,y0)
def drect(x0,y0,x1,y1):
    pdf.set_dash_pattern(dash=2.0,gap=1.2); rect(x0,y0,x1,y1,HID_W); pdf.set_dash_pattern()
def dline(x1,y1,x2,y2):
    pdf.set_dash_pattern(dash=2.0,gap=1.2); line(x1,y1,x2,y2,HID_W); pdf.set_dash_pattern()
def cline(x1,y1,x2,y2):
    pdf.set_dash_pattern(dash=1.2,gap=0.6); line(x1,y1,x2,y2,0.13); pdf.set_dash_pattern()
def circle(cx,cy,r,w=GEOM_W,n=48):
    _w(w); prev=None
    for i in range(n+1):
        th=2*math.pi*i/n; p=(cx+r*math.cos(th),cy+r*math.sin(th))
        if prev: pdf.line(*prev,*p)
        prev=p

_w(0.3); pdf.rect(5,5,PAGE_W-10,PAGE_H-10,style="D")
text(PAGE_W/2,15,"POV 3D v3 — vane_slider_v3 光电挡光滑片 (×1, 刀片印长装机剪短)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,f"锁 frame_B 45°臂筋侧 (筋孔居中 z4), M3x20+螺母 x2 (穿板4+筋4, 全通孔) / 高度调节 = 刀片印长装机剪短, "
     f"剪裁目标: 刀尖距压条顶面 12mm (名义剪至垂长 {-TRIM_Z0:g}) / 刀片真实半径 46.80..49.80 (光电叉净通道 44.7..51.9 内) / "
     f"平躺打印零支撑 (Y2 面贴床) / PLA  (GB 1st-angle, 2.5:1, 单位 mm)",
     size=TXT_I,anchor="middle")

S = 2.5
XC = (PLATE_X0 + PLATE_X1) / 2         # 48.3
Z0Y = 95.0                             # 板底 Z=0 的页面 y

# ===== 主视图 (X-Z, 2.5:1) =====
FX = 110.0
def fv(x,z): return (FX+(x-XC)*S, Z0Y-z*S)
text(FX,45.0,"主视图 (2.5:1)",size=TXT_L,anchor="middle")
_w(GEOM_W)
pdf.line(*fv(PLATE_X0,PLATE_Z1),*fv(PLATE_X1,PLATE_Z1))       # 板顶
pdf.line(*fv(PLATE_X0,PLATE_Z1),*fv(PLATE_X0,0))              # 板左
pdf.line(*fv(PLATE_X1,PLATE_Z1),*fv(PLATE_X1,0))              # 板右
pdf.line(*fv(PLATE_X0,0),*fv(BLADE_X0,0))                     # 板底 (刀片两侧)
pdf.line(*fv(BLADE_X1,0),*fv(PLATE_X1,0))
pdf.line(*fv(BLADE_X0,0),*fv(BLADE_X0,BLADE_Z0))              # 刀片左/底/右 (全长印长)
pdf.line(*fv(BLADE_X0,BLADE_Z0),*fv(BLADE_X1,BLADE_Z0))
pdf.line(*fv(BLADE_X1,BLADE_Z0),*fv(BLADE_X1,0))
# 2×Φ3.2 圆通孔 (板正中) + 中心线
r = HOLE_D/2*S
for hx in HOLE_XS:
    cx,cy = fv(hx,HOLE_Z)
    circle(cx,cy,r)
    cline(cx,cy-r-1.4,cx,cy+r+1.4)
cline(fv(HOLE_XS[0],HOLE_Z)[0]-r-1.4,fv(0,HOLE_Z)[1],fv(HOLE_XS[1],HOLE_Z)[0]+r+1.4,fv(0,HOLE_Z)[1])
# 名义剪裁线 (点划线, 距板底 -TRIM_Z0)
tly = fv(0,TRIM_Z0)[1]
cline(fv(BLADE_X0,0)[0]-2.5,tly,fv(BLADE_X1,0)[0]+2.5,tly)
# 尺寸: 上方 6.2 (孔中心距, 近) / 12.2 (板宽, 远)
yt_ = fv(0,PLATE_Z1)[1]
yct = fv(0,HOLE_Z)[1]-r                 # 孔顶
hdim(fv(HOLE_XS[0],0)[0],fv(HOLE_XS[1],0)[0],yct,yt_-DIM_O1,f"{HOLE_XS[1]-HOLE_XS[0]:g}")
hdim(fv(PLATE_X0,0)[0],fv(PLATE_X1,0)[0],yt_,yt_-DIM_O2,f"{PLATE_X1-PLATE_X0:g}")
# 左侧: 孔心距板顶 (近) / 板高 (远)
xl_ = fv(PLATE_X0,0)[0]
vdim(yt_,fv(0,HOLE_Z)[1],xl_,xl_-DIM_O1,f"{PLATE_Z1-HOLE_Z:g}")
vdim(yt_,fv(0,0)[1],xl_,xl_-DIM_O2,f"{PLATE_Z1:g}")
# 左侧下方: 名义剪裁 (近) / 刀片印长 (远)
xbl = fv(BLADE_X0,0)[0]
vdim(fv(0,0)[1],tly,xbl,xbl-DIM_O1,f"{-TRIM_Z0:g}")
vdim(fv(0,0)[1],fv(0,BLADE_Z0)[1],xbl,xbl-DIM_O2,f"{-BLADE_Z0:g}")
# 下方: 4.56 (板左到刀片左) + 2.68 (刀片厚) 链式
yb_ = fv(0,BLADE_Z0)[1]
hdim(fv(PLATE_X0,0)[0],fv(BLADE_X0,0)[0],yb_,yb_+DIM_O1,f"{BLADE_X0-PLATE_X0:g}")
hdim(fv(BLADE_X0,0)[0],fv(BLADE_X1,0)[0],yb_,yb_+DIM_O1,f"{BLADE_X1-BLADE_X0:g}")
# 引注
note(fv(HOLE_XS[1],HOLE_Z)[0]+r*0.7,fv(0,HOLE_Z)[1]-r*0.7,158.0,68.0,
     f"2×Φ{HOLE_D:g} 通孔 (板正中, 对筋孔), M3x20+螺母 x2")
note(fv(BLADE_X1,0)[0]+2.0,tly,146.0,131.0,
     f"名义剪裁线 (距板底 {-TRIM_Z0:g}) — 装机剪裁: 刀尖距压条顶面 12mm")
note(fv(BLADE_X1,0)[0],fv(0,-32.0)[1],146.0,168.0,
     f"刀片 厚 {BLADE_X1-BLADE_X0:g}, X {BLADE_X0:g}..{BLADE_X1:g} (真实半径 46.80..49.80)")

# ===== 左视图 (Y-Z, 2.5:1, 1st-angle 置右; 右 = 贴筋面 Y2) =====
SX = 250.0
def sv(y,z): return (SX+(PLATE_Y1-y)*S, Z0Y-z*S)
text(SX+(PLATE_Y1-PLATE_Y0)/2*S,45.0,"左视图 (2.5:1) — 右 = 贴筋面 Y2 (打印贴床)",size=TXT_L,anchor="middle")
rect(*sv(PLATE_Y1,PLATE_Z1),*sv(PLATE_Y0,BLADE_Z0))
_w(GEOM_W); pdf.line(*sv(PLATE_Y1,0),*sv(PLATE_Y0,0))         # 板底/刀顶棱线
dline(*sv(PLATE_Y1,HOLE_Z-HOLE_D/2),*sv(PLATE_Y0,HOLE_Z-HOLE_D/2))   # 孔下缘 (隐藏)
dline(*sv(PLATE_Y1,HOLE_Z+HOLE_D/2),*sv(PLATE_Y0,HOLE_Z+HOLE_D/2))   # 孔上缘 (隐藏)
cline(sv(PLATE_Y1,HOLE_Z)[0]-2.0,sv(0,HOLE_Z)[1],sv(PLATE_Y0,HOLE_Z)[0]+2.0,sv(0,HOLE_Z)[1])
yb2 = sv(PLATE_Y1,BLADE_Z0)[1]
hdim(sv(PLATE_Y1,0)[0],sv(PLATE_Y0,0)[0],yb2,yb2+DIM_O1,f"{PLATE_Y1-PLATE_Y0:g}")
xr2 = sv(PLATE_Y0,0)[0]
vdim(sv(0,PLATE_Z1)[1],sv(0,BLADE_Z0)[1],xr2,xr2+DIM_O1,f"{PLATE_Z1-BLADE_Z0:g}")

# ===== 俯视图 (X-Y, 2.5:1, 1st-angle 置下; 下 = 贴筋面 Y2) =====
TX, TYC = 110.0, 240.0
def pv(x,y): return (TX+(x-XC)*S, TYC-(y-(PLATE_Y0+PLATE_Y1)/2)*S)
text(TX,228.0,"俯视图 (2.5:1) — 下 = 贴筋面 Y2",size=TXT_L,anchor="middle")
rect(*pv(PLATE_X0,PLATE_Y1),*pv(PLATE_X1,PLATE_Y0))
for hx in HOLE_XS:                                            # 孔 (Y 向通, 隐藏)
    dline(*pv(hx-HOLE_D/2,PLATE_Y1),*pv(hx-HOLE_D/2,PLATE_Y0))
    dline(*pv(hx+HOLE_D/2,PLATE_Y1),*pv(hx+HOLE_D/2,PLATE_Y0))
    cline(*pv(hx,PLATE_Y1+0.8),*pv(hx,PLATE_Y0-0.8))
dline(*pv(BLADE_X0,PLATE_Y1),*pv(BLADE_X0,PLATE_Y0))          # 刀片棱 (板下, 隐藏)
dline(*pv(BLADE_X1,PLATE_Y1),*pv(BLADE_X1,PLATE_Y0))
xr3 = pv(PLATE_X1,0)[0]
vdim(pv(0,PLATE_Y1)[1],pv(0,PLATE_Y0)[1],xr3,xr3+DIM_O1,f"{PLATE_Y1-PLATE_Y0:g}")

# ===== 标题栏 =====
tb_y=PAGE_H-28; tb_x,tb_w,tb_h=20,PAGE_W-40,18
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+6,"POV 3D v3 结构件 — vane_slider_v3 光电挡光滑片 (×1, PLA, 刀片印长装机剪短)",size=TXT_L)
text(tb_x+tb_w-4,tb_y+6,"投影 1st-angle / 比例 2.5:1",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+14.5,f"总长 {PLATE_Z1-BLADE_Z0:g} / 板 {PLATE_X1-PLATE_X0:g}×{PLATE_Z1:g}×{PLATE_Y1-PLATE_Y0:g} / 2×Φ{HOLE_D:g} 通孔 中心距 {HOLE_XS[1]-HOLE_XS[0]:g}, 孔心距板顶 {PLATE_Z1-HOLE_Z:g} / "
     f"刀片 {BLADE_X1-BLADE_X0:g} 厚 × 印长 {-BLADE_Z0:g} @ X {BLADE_X0:g}..{BLADE_X1:g} / BOM: M3x20+螺母 x2 (穿板4+筋4, 全通孔) / "
     f"装机剪裁: 刀尖距压条顶面 12mm (名义剪至 {-TRIM_Z0:g}) / 平躺打印零支撑 / 单位 mm",size=TXT_I)
text(tb_x+tb_w-4,tb_y+14.5,"2026-07-24  /  POV3D / v3 / photo_sensor_v3 / vane_slider_v3.stl",size=TXT_I,anchor="end")

out = Path(__file__).with_name("vane_slider_v3_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt = Path(__file__).with_name("vane_slider_v3_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
