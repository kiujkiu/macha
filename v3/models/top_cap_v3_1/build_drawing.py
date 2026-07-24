"""
A3 drawing — top_cap_v3_1 薄压条 (v3 双面屏顶部, 2026-07-22 终版 18×140×7)。
参数 import 自 build_stl.py。GB 1st-angle。
"""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from fpdf import FPDF

from build_stl import (BLK_X, BLK_Y, BAR_Z0, BAR_Z1, AXIS_BORE,
                       HEAD_D, HEAD_T, SCREW_YS, SCREW_D,
                       SEN_HOLES, SEN_CB_D, SEN_CB_T, SEN_LEAD_SLOT)

H = BAR_Z1 - BAR_Z0
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
def cross(cx,cy,r=4.0):
    pdf.set_dash_pattern(dash=1.2,gap=0.6); _w(0.13)
    pdf.line(cx-r,cy,cx+r,cy); pdf.line(cx,cy-r,cx,cy+r); pdf.set_dash_pattern(); _w(GEOM_W)

_w(0.3); pdf.rect(5,5,PAGE_W-10,PAGE_H-10,style="D")
text(PAGE_W/2,15,"POV 3D v3 — top_cap_v3_1 双面屏顶部薄压条",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,f"扁条 {2*BLK_X:g}×{2*BLK_Y:g}×{H:g} (装配 {BAR_Z0:g}..{BAR_Z1:g}, 底面压双面屏顶) / "
     f"轴: Φ{AXIS_BORE:g} 通孔 + Φ{HEAD_D:g}×{HEAD_T:g} 底面头窝 (M6×20 平头, 注意: 先装 M6 再压屏) / "
     f"2×Φ{SCREW_D:g} 平面通孔 @ (0,±64) 盘头 M3×12 锁屏顶 (中央孔被轴占, 空置) / "
     f"光电位 (18 宽正中, 模块中心 capY−45): 2×Φ3.2 平通 @ {SEN_HOLES} + 底面 Φ{SEN_CB_D:g}×{SEN_CB_T:g} 头窝 (M3×12 先装后压屏, 螺母锁 PCB 上) + 排针尾避空槽挖穿; 梁线 (capX+17, capY−45) r_v≈48.1, 刀片 r46.8..49.8 在 frame_B, 全周扫掠余量 ~2.1/侧 / "
     f"配套: Φ8×40 螺柱 + 688×2 + 柱 Φ8×290×4 @±75 / 平躺打印零支撑  (GB 1st-angle, 2:1, mm)",
     size=TXT_I,anchor="middle")

S = 2.0
def zr(z): return z - BAR_Z0
# ===== 俯视图 (2:1, 长边横放: 图X=件Y, 图Y=件X) =====
TX, TYC = 210.0, 105.0
def pv(x,y): return (TX+y*S, TYC-x*S)
text(TX,62.0,"俯视图 (2:1) — 长边横放",size=TXT_L,anchor="middle")
rect(*pv(-BLK_X,-BLK_Y),*pv(BLK_X,BLK_Y))
for sy in SCREW_YS:
    cx,cy = pv(0.0,sy); pdf.circle(cx,cy,SCREW_D/2*S,style="D"); cross(cx,cy)
# 光电区: 排针尾避空槽 (穿透) + 2×Φ3.2 + 底面头窝 (隐藏)
_w(GEOM_W)
rect(*pv(SEN_LEAD_SLOT[0],SEN_LEAD_SLOT[2]),*pv(SEN_LEAD_SLOT[1],SEN_LEAD_SLOT[3]))
for (sx,sy) in SEN_HOLES:
    cx2,cy2 = pv(sx,sy)
    pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
    pdf.circle(cx2,cy2,SEN_CB_D/2*S,style="D")
    pdf.set_dash_pattern(); _w(GEOM_W)
    pdf.circle(cx2,cy2,3.2/2*S,style="D"); cross(cx2,cy2)
note(*pv(SEN_HOLES[0][0],SEN_HOLES[0][1]),pv(-9,-8)[0],pv(-30,0)[1]+30,
     f"光电模块位: 2×Φ3.2 平通 + 底面 Φ{SEN_CB_D:g}×{SEN_CB_T:g} 头窝 (M3×12 自下, 螺母在 PCB 上); 避空槽挖穿",anchor="start")
cx,cy = pv(0.0,0.0)
pdf.circle(cx,cy,AXIS_BORE/2*S,style="D")
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
pdf.circle(cx,cy,HEAD_D/2*S,style="D")               # 底面头窝 (隐藏)
pdf.set_dash_pattern(); _w(GEOM_W); cross(cx,cy,6.5)
yb = pv(BLK_X,0)[1]
hdim(pv(0,-BLK_Y)[0],pv(0,BLK_Y)[0],yb,yb+DIM_O1,f"{2*BLK_Y:g}")
hdim(pv(0,SCREW_YS[1])[0],pv(0,SCREW_YS[0])[0],yb,yb+DIM_O2,"128 (孔距)")
xl = pv(0,-BLK_Y)[0]
vdim(pv(-BLK_X,0)[1],pv(BLK_X,0)[1],xl,xl-DIM_O1,f"{2*BLK_X:g}")
note(*pv(0,SCREW_YS[0]),pv(0,36)[0],pv(-BLK_X,0)[1]-14,
     f"2×Φ{SCREW_D:g} 通 @ (0,±64), 盘头 M3×12 锁屏顶",anchor="start")
note(*pv(0,-4),pv(0,-42)[0],pv(-BLK_X,0)[1]-14,
     f"轴 Φ{AXIS_BORE:g} 通 + Φ{HEAD_D:g}×{HEAD_T:g} 底面头窝 (隐藏)",anchor="end")

# ===== 正视图 (件 Y-Z, 2:1) =====
EX, EYB = 210.0, 190.0
def ev(y,z): return (EX+y*S, EYB-zr(z)*S)
text(EX,150.0,"正视图 (2:1)",size=TXT_L,anchor="middle")
rect(*ev(-BLK_Y,BAR_Z1),*ev(BLK_Y,BAR_Z0))
drect(*ev(-AXIS_BORE/2,BAR_Z1),*ev(AXIS_BORE/2,BAR_Z0))
drect(*ev(-HEAD_D/2,BAR_Z0+HEAD_T),*ev(HEAD_D/2,BAR_Z0))
for sy in SCREW_YS:
    drect(*ev(sy-SCREW_D/2,BAR_Z1),*ev(sy+SCREW_D/2,BAR_Z0))
yb2 = ev(0,BAR_Z0)[1]
hdim(ev(-HEAD_D/2,BAR_Z0)[0],ev(HEAD_D/2,BAR_Z0)[0],yb2,yb2+DIM_O1,f"Φ{HEAD_D:g} 头窝")
xl2 = ev(-BLK_Y,BAR_Z0)[0]
vdim(ev(0,BAR_Z1)[1],ev(0,BAR_Z0)[1],xl2,xl2-DIM_O1,f"{H:g}")
xr2 = ev(BLK_Y,BAR_Z0)[0]
vdim(ev(0,BAR_Z0+HEAD_T)[1],ev(0,BAR_Z0)[1],xr2,xr2+DIM_O1,f"{HEAD_T:g} (头窝深)")

# ===== 侧视图 (件 X-Z, 2:1) =====
SX2, SYB2 = 55.0, 190.0
def sv2(x,z): return (SX2+x*S, SYB2-zr(z)*S)
text(SX2,150.0,"侧视图 (2:1)",size=TXT_L,anchor="middle")
rect(*sv2(-BLK_X,BAR_Z1),*sv2(BLK_X,BAR_Z0))
drect(*sv2(-AXIS_BORE/2,BAR_Z1),*sv2(AXIS_BORE/2,BAR_Z0))
drect(*sv2(-HEAD_D/2,BAR_Z0+HEAD_T),*sv2(HEAD_D/2,BAR_Z0))
yb3 = sv2(0,BAR_Z0)[1]
hdim(sv2(-BLK_X,BAR_Z0)[0],sv2(BLK_X,BAR_Z0)[0],yb3,yb3+DIM_O1,f"{2*BLK_X:g}")

tb_y=PAGE_H-28; tb_x,tb_w,tb_h=20,PAGE_W-40,18
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+6,"POV 3D v3 结构件 — top_cap_v3_1 薄压条 (底面 = 屏顶压面 260.95)",size=TXT_L)
text(tb_x+tb_w-4,tb_y+6,"投影 1st-angle / 比例 2:1",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+14.5,f"{2*BLK_X:g}×{2*BLK_Y:g}×{H:g} / 轴 Φ{AXIS_BORE:g}+Φ{HEAD_D:g}×{HEAD_T:g} 底头窝 / 2×Φ{SCREW_D:g}@±64 / "
     f"BOM: M6×20 平头 + Φ8×30 螺柱 + M3×12×2 / 平躺打印 / 单位 mm",size=TXT_I)
text(tb_x+tb_w-4,tb_y+14.5,"2026-07-23  /  POV3D / v3 / top_cap_v3_1 / top_cap_v3_1.stl",size=TXT_I,anchor="end")

out = Path(__file__).with_name("top_cap_v3_1_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt = Path(__file__).with_name("top_cap_v3_1_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
