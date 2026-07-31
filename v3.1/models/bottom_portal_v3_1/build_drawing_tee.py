"""
A3 drawing — portal_tee_v3_1 (v3 屏幕底部支撑 T 型件, 2026-07-22 深夜终版:
筋齐外侧面 + 顶平板托梯形, 平躺打印)。参数 import 自 build_tee.py。GB 1st-angle。
"""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from fpdf import FPDF

from build_tee import (BAR_X, BAR_H, THK_Y0, THK_Y1, FOOT_HOLES, FOOT_HOLE_D,
                       STEM_HW, STEM_Z1, GUS_T, WELL_D, WELL_Z1,
                       PAD_T, PAD_Z0, PAD_Y0, PAD_WI, PAD_WO, SCR_D, SCR_Y,
                       SCR_XS, SCR_ECC)

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
text(PAGE_W/2,15,"POV 3D v3 — portal_tee_v3_1 屏幕底部支撑 T 型件 (×2, 180° 对放)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,f"底横条 67×10×5 装转子两颗 M3 (±29.658, R77.5 环孔, Φ{WELL_D:g} 工艺井) / 竖梃 5×10 / 梯形加强壁 厚 {GUS_T:g} 齐外侧面 (±33.5→±10) / "
     f"顶平板托**等宽** ±{PAD_WO:g}×深{THK_Y1-PAD_Y0:g}×{PAD_T:g}, 托面 Z{STEM_Z1:g}=屏底一整平面; "
     f"屏孔 {len(SCR_XS)}×Φ{SCR_D:g} @ X{tuple(round(v,1) for v in SCR_XS)} (M3×12 自下; 居中/偏心可切换) / "
     f"平躺打印: 外侧面贴床, 全特征落床零支撑  (GB 1st-angle, 2:1, mm)",
     size=TXT_I,anchor="middle")

S = 2.0
Y_MID = (THK_Y0 + THK_Y1) / 2
# ===== 正视图 (X-Z, 2:1) =====
FX, FYB = 120.0, 200.0
def fv(x,z): return (FX+x*S, FYB-z*S)
text(FX,48.0,"正视图 (2:1)",size=TXT_L,anchor="middle")
rect(*fv(-BAR_X,BAR_H),*fv(BAR_X,0))
rect(*fv(-STEM_HW,PAD_Z0),*fv(STEM_HW,BAR_H))
_w(GEOM_W)
pdf.line(*fv(BAR_X,BAR_H),*fv(PAD_WO,PAD_Z0))         # 梯形壁斜边 (到托外缘)
pdf.line(*fv(-BAR_X,BAR_H),*fv(-PAD_WO,PAD_Z0))
rect(*fv(-PAD_WO,STEM_Z1),*fv(PAD_WO,PAD_Z0))         # 顶平板托 (前视 ±10)
for (hx,hy) in FOOT_HOLES:
    drect(*fv(hx-FOOT_HOLE_D/2,BAR_H),*fv(hx+FOOT_HOLE_D/2,0))
    drect(*fv(hx-WELL_D/2,WELL_Z1),*fv(hx+WELL_D/2,BAR_H))
for _sx in SCR_XS:                                    # v3.1: 3 个离散屏孔
    drect(*fv(_sx-SCR_D/2,STEM_Z1),*fv(_sx+SCR_D/2,PAD_Z0))
drect(*fv(-7.5/2,PAD_Z0),*fv(7.5/2,PAD_Z0-4.0))       # Φ7.5×4 帽让位窝 (隐藏)
yb = fv(0,0)[1]
hdim(fv(-BAR_X,0)[0],fv(BAR_X,0)[0],yb,yb+DIM_O1,f"{2*BAR_X:g}")
hdim(fv(FOOT_HOLES[1][0],0)[0],fv(FOOT_HOLES[0][0],0)[0],yb,yb+DIM_O2,"59.32 (孔距)")
hdim(fv(-PAD_WO,0)[0],fv(PAD_WO,0)[0],fv(0,STEM_Z1)[1],fv(0,STEM_Z1)[1]-DIM_O1,f"{2*PAD_WO:g} (托外边)")
xl = fv(-BAR_X,0)[0]
vdim(fv(0,STEM_Z1)[1],fv(0,0)[1],xl,xl-DIM_O1,f"{STEM_Z1:g}")
vdim(fv(0,BAR_H)[1],fv(0,0)[1],xl,xl-DIM_O2,f"{BAR_H:g}")
note(*fv(FOOT_HOLES[0][0],2.5),fv(45,0)[0],fv(0,14)[1],f"2×Φ{FOOT_HOLE_D:g} 通 (转子 M3) + Φ{WELL_D:g} 工艺井到 Z{WELL_Z1:g}",anchor="start")
note(*fv(PAD_WO,47.5),fv(45,0)[0],fv(0,42)[1],f"顶平板托 (等宽 ±{PAD_WO:g}), {len(SCR_XS)}×Φ{SCR_D:g} @ X{tuple(round(v,1) for v in SCR_XS)}",anchor="start")
note(*fv(23,22),fv(45,0)[0],fv(0,28)[1],f"梯形加强壁, 厚 {GUS_T:g}, 齐外侧面 (±{BAR_X:g}→±{PAD_WO:g})",anchor="start")
note(*fv(3.75,43),fv(45,0)[0],fv(0,35)[1],"Φ7.5×4 帽让位窝 (Φ7 帽沉入)",anchor="start")

# ===== 侧视图 (Y-Z, 2:1, 从 +X 看; 左 = 外侧平整面) =====
SX, SYB = 300.0, 200.0
def sv(y,z): return (SX+(THK_Y1-y)*S, SYB-z*S)     # 外侧面在左
text(SX+16,48.0,"侧视图 (2:1) — 左 = 外侧平整面 (打印贴床)",size=TXT_L,anchor="middle")
rect(*sv(THK_Y1,BAR_H),*sv(THK_Y0,0))
rect(*sv(THK_Y1,PAD_Z0),*sv(THK_Y0,BAR_H))
rect(*sv(THK_Y1,STEM_Z1),*sv(PAD_Y0,PAD_Z0))               # 顶平板托 (内伸)
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
pdf.line(*sv(THK_Y1-GUS_T,BAR_H),*sv(THK_Y1-GUS_T,PAD_Z0)) # 壁内面 (隐藏)
pdf.set_dash_pattern()
drect(*sv(SCR_Y+SCR_D/2,STEM_Z1),*sv(SCR_Y-SCR_D/2,PAD_Z0))     # 屏孔
drect(*sv(71.601+WELL_D/2,WELL_Z1),*sv(71.601-WELL_D/2,0))      # 脚孔+井
yb2 = sv(THK_Y1,0)[1]
hdim(sv(THK_Y1,0)[0],sv(THK_Y0,0)[0],yb2,yb2+DIM_O1,"10")
hdim(sv(THK_Y1,0)[0],sv(PAD_Y0,0)[0],yb2,yb2+DIM_O2,f"{THK_Y1-PAD_Y0:g} (托深)")
xr = sv(PAD_Y0,0)[0]
vdim(sv(Y_MID,STEM_Z1)[1],sv(Y_MID,0)[1],xr,xr+DIM_O1,f"{STEM_Z1:g}")
vdim(sv(Y_MID,STEM_Z1)[1],sv(Y_MID,PAD_Z0)[1],xr,xr+DIM_O2,f"{PAD_T:g}")

# ===== 俯视图 (X-Y, 2:1; 上 = 外侧) =====
TX, TYC = 120.0, 245.0
def pv(x,y): return (TX+x*S, TYC-(y-Y_MID)*S)
text(TX,222.0,"俯视图 (2:1) — 上 = 外侧",size=TXT_L,anchor="middle")
rect(*pv(-BAR_X,THK_Y1),*pv(BAR_X,THK_Y0))
_w(GEOM_W)
pdf.line(*pv(-PAD_WO,THK_Y1),*pv(-PAD_WI,PAD_Y0))          # 托梯形斜边
pdf.line(*pv(PAD_WO,THK_Y1),*pv(PAD_WI,PAD_Y0))
pdf.line(*pv(-PAD_WI,PAD_Y0),*pv(PAD_WI,PAD_Y0))           # 托内边
drect(*pv(-BAR_X,THK_Y1),*pv(BAR_X,THK_Y1-GUS_T))          # 筋带 (齐外侧, 隐藏)
drect(*pv(-STEM_HW,THK_Y1),*pv(STEM_HW,THK_Y0))            # 梃 (隐藏)
for (hx,hy) in FOOT_HOLES:
    cx,cy = pv(hx,hy); pdf.circle(cx,cy,WELL_D/2*S,style="D")
    pdf.circle(cx,cy,FOOT_HOLE_D/2*S,style="D"); cross(cx,cy)
cx,cy = pv(0.0,SCR_Y); pdf.circle(cx,cy,SCR_D/2*S,style="D"); cross(cx,cy)
yb3 = pv(0,PAD_Y0)[1]
hdim(pv(FOOT_HOLES[1][0],0)[0],pv(FOOT_HOLES[0][0],0)[0],yb3,yb3+DIM_O1,"59.32 (孔距)")
hdim(pv(-PAD_WI,0)[0],pv(PAD_WI,0)[0],yb3,yb3+DIM_O2,f"{2*PAD_WI:g} (托内边=屏厚)")
xr3 = pv(BAR_X,0)[0]
vdim(pv(0,THK_Y1)[1],pv(0,THK_Y0)[1],xr3,xr3+DIM_O1,"10")
vdim(pv(0,THK_Y1)[1],pv(0,PAD_Y0)[1],xr3,xr3+DIM_O2,f"{THK_Y1-PAD_Y0:g} (托深)")

tb_y=PAGE_H-28; tb_x,tb_w,tb_h=20,PAGE_W-40,18
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+6,"POV 3D v3 结构件 — portal_tee_v3_1 (×2, 180° 对放; 托面 Z50 = 屏幕安装高度)",size=TXT_L)
text(tb_x+tb_w-4,tb_y+6,"投影 1st-angle / 比例 2:1",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+14.5,f"底横条 {2*BAR_X:g}×10×{BAR_H:g} / 竖梃 {2*STEM_HW:g}×10×{PAD_Z0-BAR_H:g} / 筋厚 {GUS_T:g}×2 齐外侧 / "
     f"托梯形 外{2*PAD_WO:g}·内{2*PAD_WI:g}×{THK_Y1-PAD_Y0:g}×{PAD_T:g} / 2×Φ{FOOT_HOLE_D:g}@59.32+Φ{WELL_D:g}井 / 屏孔 Φ{SCR_D:g}+Φ7.5×4 帽窝 / "
     f"BOM: 脚 M3×20×2 + 屏 M3×12×1 / 平躺打印 (外侧面贴床) / 单位 mm",size=TXT_I)
text(tb_x+tb_w-4,tb_y+14.5,"2026-07-22  /  POV3D / v3 / bottom_portal_v3 / portal_tee_v3_1.stl",size=TXT_I,anchor="end")

out = Path(__file__).with_name("portal_tee_v3_1_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt = Path(__file__).with_name("portal_tee_v3_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
