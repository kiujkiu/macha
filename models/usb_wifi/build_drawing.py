"""
A3 drawing — wifi_box 倒扣盒 (2026-07-09 第三版定稿 + 整条翼板/加强筋)。
全部孔为平面通孔 (Φ3.4×4), 出口窗/扎带槽为穿墙通口 → 无需详图。
基准 = 盘心 (孔位为盘 R35/R77.5 环孔 @±22.5°) + 盘顶面 Z0。GB first-angle。
"""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from fpdf import FPDF

from wifi_common import (XC, IX0, IX1, IY1, IZ1, OX0, OX1, OY1, OZ1, WALL,
                         WIN_W, WIN_H, ZC_PORT, TIE_W, TIE_H, TIE_ZLO, TIE_ZHI,
                         DISC_M3, M3_THRU, FLANGE_T, WFL_X0, EFL_X1, EFL_HY,
                         GUS_T, WGUS_YS, EGUS_YS)

FONT = "/mnt/c/Windows/Fonts/simhei.ttf"
GEOM_W, DIM_W, EXT_W_, HID_W = 0.50, 0.20, 0.20, 0.30
ARR_L, ARR_W, EXT_OV, EXT_GP = 4.2, 1.5, 2.4, 1.0
TXT_D, TXT_L, TXT_T, TXT_I = 4.5, 6.5, 8.0, 4.0
DIM_O1, DIM_O2, DIM_O3 = 12.0, 22.0, 32.0
PAGE_W, PAGE_H = 420.0, 297.0

def new_pdf():
    pdf = FPDF(orientation="L", unit="mm", format="A3"); pdf.set_auto_page_break(False); pdf.add_page()
    pdf.add_font("SimHei", "", FONT)
    return pdf

def mk_helpers(pdf):
    H = {}
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
    def cross(cx,cy,r=4.0):
        pdf.set_dash_pattern(dash=1.2,gap=0.6); _w(0.13)
        pdf.line(cx-r,cy,cx+r,cy); pdf.line(cx,cy-r,cx,cy+r); pdf.set_dash_pattern(); _w(GEOM_W)
    def pl(pts,w=GEOM_W):
        _w(w)
        for i in range(len(pts)-1): pdf.line(*pts[i],*pts[i+1])
    def rect(x0,y0,x1,y1,w=GEOM_W):
        pl([(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)],w)
    def drect(x0,y0,x1,y1,w=HID_W):
        pdf.set_dash_pattern(dash=2.0,gap=1.2); rect(x0,y0,x1,y1,w); pdf.set_dash_pattern()
    def frame(title, sub):
        _w(0.3); pdf.rect(5,5,PAGE_W-10,PAGE_H-10,style="D")
        text(PAGE_W/2,15,title,size=TXT_T,anchor="middle")
        text(PAGE_W/2,21,sub,size=TXT_I,anchor="middle")
    def tblock(l1,r1,l2,r2):
        tb_y=PAGE_H-28; tb_x,tb_w,tb_h=20,PAGE_W-40,18
        _w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
        text(tb_x+4,tb_y+6,l1,size=TXT_L,anchor="start"); text(tb_x+tb_w-4,tb_y+6,r1,size=TXT_I,anchor="end")
        text(tb_x+4,tb_y+14.5,l2,size=TXT_I,anchor="start"); text(tb_x+tb_w-4,tb_y+14.5,r2,size=TXT_I,anchor="end")
    for k,v in locals().items():
        if callable(v): H[k]=v
    return H

pdf = new_pdf(); h = mk_helpers(pdf)
h['frame']("POV 3D v2 — wifi_box USB WiFi 网卡倒扣盒 (装 mlkpai_carrier_disc, 随转子)",
    "模块侧立整块 14.5×40×70 (天线反折在内) 直接坐盘面, 插头朝 +Y (米联派 J6 方向) / 壁 3, 内腔 15.1×70.6×40.4 / "
    "两侧整条翼板 3 厚 + 45° 加强筋 2.5 厚 ×10 / 4×Φ3.4 = 盘 R35 & R77.5 环孔 @±22.5° (M3×14, 环底垫片+螺母) / "
    "全部平面通孔无详图 / 基准 = 盘心 + 盘顶面  (GB 1st-angle, 2:1, mm)")

S = 2.0
# ================= 俯视图 (2:1) =================
TX, TYC = 42.0, 136.0
def pv(x,y): return (TX+(x-WFL_X0)*S, TYC-y*S)
h['text'](pv(52,0)[0],40.0,"俯视图 (2:1)   (+Y = 出口/米联派 J6 方向 = 图上方)",size=TXT_L,anchor="middle")
h['rect'](*pv(WFL_X0,OY1),*pv(OX0,-OY1))                 # 西翼板
h['rect'](*pv(OX0,OY1),*pv(OX1,-OY1))                    # 盒体
h['rect'](*pv(OX1,EFL_HY),*pv(EFL_X1,-EFL_HY))           # 东翼板
for yc in WGUS_YS:                                       # 加强筋 (俯视为翼板上矩形)
    h['rect'](*pv(WFL_X0,yc+GUS_T/2),*pv(OX0,yc-GUS_T/2),HID_W)
for yc in EGUS_YS:
    h['rect'](*pv(OX1,yc+GUS_T/2),*pv(EFL_X1,yc-GUS_T/2),HID_W)
h['drect'](*pv(IX0,IY1),*pv(IX1,-IY1))                   # 内腔 (隐藏)
h['drect'](*pv(XC-WIN_W/2,OY1),*pv(XC+WIN_W/2,IY1))      # 出口窗 (隐藏, +Y 墙内)
for (hx,hy) in DISC_M3:
    cx,cy=pv(hx,hy); pdf.circle(cx,cy,M3_THRU/2*S,style="D"); h['cross'](cx,cy,5.5)
# 尺寸
yb = pv(0,-OY1)[1]; yt = pv(0,OY1)[1]
h['hdim'](pv(WFL_X0,0)[0],pv(EFL_X1,0)[0],yb,yb+DIM_O2,f"{EFL_X1-WFL_X0:g}")
h['hdim'](pv(OX0,0)[0],pv(OX1,0)[0],yb,yb+DIM_O1,f"{OX1-OX0:g}")
h['hdim'](pv(DISC_M3[0][0],0)[0],pv(DISC_M3[2][0],0)[0],yt,yt-DIM_O1,f"{DISC_M3[2][0]-DISC_M3[0][0]:.2f} (孔列距)")
h['hdim'](pv(WFL_X0,0)[0],pv(OX0,0)[0],yb,yb+DIM_O3,f"{OX0-WFL_X0:g}")
h['hdim'](pv(OX1,0)[0],pv(EFL_X1,0)[0],yb,yb+DIM_O3,f"{EFL_X1-OX1:g}")
xl = pv(WFL_X0,0)[0]; xr = pv(EFL_X1,0)[0]
h['vdim'](pv(0,DISC_M3[0][1])[1],pv(0,DISC_M3[1][1])[1],xl,xl-DIM_O1,f"{2*DISC_M3[0][1]:.2f}")
h['vdim'](pv(0,OY1)[1],pv(0,-OY1)[1],xr,xr+DIM_O1,f"{2*OY1:g}")
h['vdim'](pv(0,DISC_M3[2][1])[1],pv(0,DISC_M3[3][1])[1],xr,xr+DIM_O2,f"{2*DISC_M3[2][1]:.2f}")
h['vdim'](pv(0,EFL_HY)[1],pv(0,-EFL_HY)[1],xr,xr+DIM_O3,f"{2*EFL_HY:g}")
h['note'](*pv(DISC_M3[0][0],DISC_M3[0][1]),pv(31.5,0)[0]+1,pv(0,25)[1],
          "4×Φ3.4 通 (= 盘环孔)",anchor="start")
h['note'](*pv(47,-36.5),pv(33,0)[0],yb+DIM_O3+10,"加强筋 2.5 厚 ×10 (45°, 筋顶 Z16.2/16.3)",anchor="start")
h['text'](pv(52,0)[0],TYC+1.5,"盒中线 X=52 (盘系); 内腔 15.1×70.6 (虚线)",size=TXT_I,anchor="middle",halo=True)

# ================= 正视图 (+Y 端视, 2:1) =================
EX, EYB = 225.0, 132.0
def ev(x,z): return (EX+(x-WFL_X0)*S, EYB-z*S)
h['text'](ev(58,0)[0],50.0,"正视图 (从 +Y 端看, 2:1) — 出口窗 + 扎带槽",size=TXT_L,anchor="middle")
h['pl']([ev(WFL_X0,0),ev(WFL_X0,FLANGE_T),ev(OX0,FLANGE_T),ev(OX0,OZ1),ev(OX1,OZ1),
         ev(OX1,FLANGE_T),ev(EFL_X1,FLANGE_T),ev(EFL_X1,0),ev(WFL_X0,0)])
h['pl']([ev(OX0,FLANGE_T),ev(OX0,FLANGE_T+ (OX0-WFL_X0)),ev(WFL_X0,FLANGE_T)],GEOM_W)   # 西端筋轮廓
h['pl']([ev(OX1,FLANGE_T),ev(OX1,FLANGE_T+ (EFL_X1-OX1)),ev(EFL_X1,FLANGE_T)],GEOM_W)   # 东端筋轮廓
h['rect'](*ev(XC-WIN_W/2,ZC_PORT+WIN_H/2),*ev(XC+WIN_W/2,ZC_PORT-WIN_H/2))              # 出口窗
h['rect'](*ev(XC-TIE_W/2,TIE_ZLO+TIE_H),*ev(XC+TIE_W/2,TIE_ZLO))                        # 下扎带槽
h['rect'](*ev(XC-TIE_W/2,TIE_ZHI+TIE_H),*ev(XC+TIE_W/2,TIE_ZHI))                        # 上扎带槽
h['drect'](*ev(IX0,IZ1),*ev(IX1,0))                                                     # 内腔 (隐藏)
xw = ev(WFL_X0,0)[0]; xe = ev(EFL_X1,0)[0]; yb2 = ev(0,0)[1]
h['vdim'](ev(0,OZ1)[1],ev(0,0)[1],xw,xw-DIM_O1,f"{OZ1:g}")
h['vdim'](ev(0,ZC_PORT+WIN_H/2)[1],ev(0,ZC_PORT-WIN_H/2)[1],xe,xe+DIM_O1,f"{WIN_H:g}")
h['vdim'](ev(0,ZC_PORT)[1],ev(0,0)[1],xe,xe+DIM_O2,f"{ZC_PORT:g} (窗中心)")
h['vdim'](ev(0,FLANGE_T)[1],ev(0,0)[1],xw,xw-DIM_O2,f"{FLANGE_T:g}")
h['hdim'](ev(XC-WIN_W/2,0)[0],ev(XC+WIN_W/2,0)[0],yb2,yb2+DIM_O1,f"{WIN_W:g}")
h['hdim'](ev(IX0,0)[0],ev(IX1,0)[0],ev(0,OZ1)[1],ev(0,OZ1)[1]-DIM_O1,f"{IX1-IX0:g} (内腔)")
h['note'](*ev(XC+TIE_W/2,TIE_ZHI+TIE_H/2),ev(EFL_X1,0)[0]+6,ev(0,38)[1],
          f"扎带槽 {TIE_W:g}×{TIE_H:g} ×2 (距窗 1)")
h['note'](*ev(XC-WIN_W/2,ZC_PORT),ev(30,0)[0]-2,ev(0,30)[1],
          "出口窗 = 母头壳 10.3×18.7 +0.4",anchor="end")

# ================= 侧视图 (从 +X 看, 2:1) =================
SX, SYB = 182.0, 252.0
def sv(y,z): return (SX+(y+OY1)*S, SYB-z*S)
h['text'](210.0,150.0,"侧视图 (从 +X 看, 2:1)",size=TXT_L,anchor="middle")
h['text'](210.0,156.0,"东翼板/加强筋分布 (西侧同布置), +Y = 图右",size=TXT_I,anchor="middle")
h['pl']([sv(-OY1,0),sv(-OY1,OZ1),sv(OY1,OZ1),sv(OY1,0)])
h['pl']([sv(-EFL_HY,0),sv(-OY1+0.0,0)],GEOM_W)
h['pl']([sv(-EFL_HY,0),sv(-EFL_HY,FLANGE_T)],GEOM_W)
h['pl']([sv(-EFL_HY,FLANGE_T),sv(-OY1,FLANGE_T)],HID_W)
h['line'](*sv(-OY1,0),*sv(OY1,0),GEOM_W)
h['pl']([sv(EFL_HY,0),sv(EFL_HY,FLANGE_T),sv(-EFL_HY,FLANGE_T)],GEOM_W)
gtop = FLANGE_T + (EFL_X1-OX1)
for yc in EGUS_YS:                                       # 5 条加强筋 (正面矩形)
    h['rect'](*sv(yc-GUS_T/2,gtop),*sv(yc+GUS_T/2,FLANGE_T))
h['drect'](*sv(-IY1,IZ1),*sv(IY1,0))                     # 内腔
h['drect'](*sv(IY1,ZC_PORT+WIN_H/2),*sv(OY1,ZC_PORT-WIN_H/2))   # 出口窗 (在 +Y 墙内, 隐藏)
yb3 = sv(0,0)[1]
h['hdim'](sv(-OY1,0)[0],sv(OY1,0)[0],yb3,yb3+DIM_O1,f"{2*OY1:g}")
h['hdim'](sv(-IY1,0)[0],sv(IY1,0)[0],yb3,yb3+DIM_O2,f"{2*IY1:g} (内腔)")
h['hdim'](sv(0,0)[0],sv(20,0)[0],sv(0,gtop)[1],sv(0,OZ1)[1]-DIM_O1,"20 (筋距)")
h['hdim'](sv(20,0)[0],sv(35.75,0)[0],sv(0,gtop)[1],sv(0,OZ1)[1]-DIM_O1,"15.75")
xr3 = sv(OY1,0)[0]
h['vdim'](sv(0,OZ1)[1],sv(0,0)[1],xr3,xr3+DIM_O1,f"{OZ1:g}")
h['vdim'](sv(0,gtop)[1],sv(0,0)[1],xr3,xr3+DIM_O2,f"{gtop:.2f} (筋顶)")
h['note'](*sv(-35.75,8),sv(-OY1,0)[0]-6,sv(0,24)[1],"加强筋 2.5 厚 (西侧同布置, 端筋 ±37.05)",anchor="end")

h['tblock']("POV 3D v2 结构件 — wifi_box USB WiFi 网卡倒扣盒",
    "投影 1st-angle / 比例 2:1 / 全平面通孔无详图",
    f"外廓 {OX1-OX0:g}×{2*OY1:g}×{OZ1:g} + 翼板全宽 {EFL_X1-WFL_X0:g} / 内腔 {IX1-IX0:g}×{2*IY1:g}×{IZ1:g} / 壁 {WALL:g} / "
    f"4×Φ{M3_THRU:g} 孔列距 {DISC_M3[2][0]-DISC_M3[0][0]:.2f}, 距 {2*DISC_M3[0][1]:.2f}/{2*DISC_M3[2][1]:.2f} / "
    f"窗 {WIN_W:g}×{WIN_H:g}@Z{ZC_PORT:g} / 扎带槽 {TIE_W:g}×{TIE_H:g}×2 / 倒扣姿态打印零支撑 / PETG / mm",
    "2026-07-09  /  POV3D / models / usb_wifi / wifi_box.stl")

out = Path(__file__).with_name("wifi_box_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt = Path(__file__).with_name("wifi_box_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
