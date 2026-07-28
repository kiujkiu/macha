"""
A3 drawing — wifi_shell 新 WiFi 壳子 v1 (2026-07-21, 侧开口五面盒)。
出口窗为穿墙通口, 无孔无沉孔 → 无详图。零件系基准 = 封闭壁外面 X0 /
外底面 Z0 / Y 中面。装配位/固定方式待定。GB first-angle, 2:1。
参数 import 自 build_shell.py (单一数据源)。
"""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from fpdf import FPDF

from build_shell import (CAV_X, CAV_Y, CAV_Z, WALL, IX0, IX1, IY0, IY1,
                         IZ0, IZ1, OX0, OX1, OY0, OY1, OZ0, OZ1,
                         WIN_W, WIN_H, WIN_XC, WIN_ZC,
                         FLG_L, FLG_T, FLG_X0, FLG_Y1, M3_D, HOLE_YC, HOLE_CC,
                         HOLE_ZS, GUS_T, GUS_ARM, GUS_ZS,
                         TRIM_R, TRIM_CX_Z, TRIM_CY_Y)

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
    def dline(x1,y1,x2,y2,w=HID_W):
        pdf.set_dash_pattern(dash=2.0,gap=1.2); line(x1,y1,x2,y2,w); pdf.set_dash_pattern()
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
h['frame']("POV 3D — wifi_shell 新 WiFi 壳子 v1 (侧开口五面盒 + 双端沿)",
    "内腔 15.1×70.6×40.4 / 壁 3 / 开口面 = +X 侧 70.6×40.4 (无壁) / +Y 端壁出口窗 10.7×19.1 / "
    "±Y 端沿外伸 10×厚 3 (X15.1..18.1, 与开口面共面) 各 2×Φ3.2 + 2 三角筋 2.5 厚 45° / "
    f"2026-07-27 盘缘裁切: -Y 端角按 R{TRIM_R:g} 圆弧切齐 (弧心在零件系 y={TRIM_CY_Y:g}, z=-{TRIM_CX_Z:g} = 转子轴), 见侧视图 / "
    "基准 = 封闭壁外面 X0 + 外底面 Z0 + Y 中面 / 安装 = 倒扣: 开口/沿朝下贴盘, 罩住放平的模块 (40×70 面贴盘, 14.5 高)  (GB 1st-angle, 2:1, mm)")

S = 2.0
# ================= 俯视图 (2:1) — X 横, Y 纵 (+Y = 图上) =================
TX, TYC = 60.0, 146.0
def pv(x,y): return (TX+x*S, TYC-y*S)
h['text'](pv(OX1/2,0)[0]+18,36.0,"俯视图 (2:1)   (+Y = 出口窗端 = 图上方, 开口朝 +X = 图右)",size=TXT_L,anchor="middle")
h['rect'](*pv(OX0,OY1),*pv(OX1,OY0))                       # 盒体外廓
h['pl']([pv(IX0,IY1),pv(IX0,IY0)],GEOM_W)                  # 封闭壁内面
h['pl']([pv(IX0,IY1),pv(IX1,IY1)],GEOM_W)                  # +Y 壁内面
h['pl']([pv(IX0,IY0),pv(IX1,IY0)],GEOM_W)                  # -Y 壁内面
h['drect'](*pv(WIN_XC-WIN_W/2,OY1),*pv(WIN_XC+WIN_W/2,IY1))  # 出口窗 (+Y 壁内, 隐藏)
h['rect'](*pv(FLG_X0,FLG_Y1),*pv(OX1,OY1))                 # +Y 沿 (开口面侧)
h['rect'](*pv(FLG_X0,OY0),*pv(OX1,-FLG_Y1))                # -Y 沿
h['pl']([pv(FLG_X0,FLG_Y1),pv(FLG_X0-GUS_ARM,OY1)],GEOM_W)   # +Y 筋斜边 (顶层可见)
h['pl']([pv(FLG_X0,-FLG_Y1),pv(FLG_X0-GUS_ARM,OY0)],GEOM_W)  # -Y 筋斜边
for yc in (HOLE_YC, -HOLE_YC):                             # M3 孔 (孔轴沿 X, 俯视为隐藏带)
    h['drect'](*pv(FLG_X0,yc+M3_D/2),*pv(OX1,yc-M3_D/2))
yb_f = pv(0,-FLG_Y1)[1]
h['hdim'](pv(OX0,0)[0],pv(OX1,0)[0],yb_f,yb_f+DIM_O1,f"{OX1-OX0:g}")
h['hdim'](pv(IX0,0)[0],pv(IX1,0)[0],yb_f,yb_f+DIM_O2,f"{IX1-IX0:g} (内腔)")
xl = pv(OX0,0)[0]; xr = pv(OX1,0)[0]
h['vdim'](pv(0,OY1)[1],pv(0,OY0)[1],xl,xl-DIM_O1,f"{OY1-OY0:g} (盒体)")
h['vdim'](pv(0,IY1)[1],pv(0,OY1)[1],xl,xl-DIM_O2,f"{WALL:g}")
h['vdim'](pv(0,FLG_Y1)[1],pv(0,OY1)[1],xr,xr+DIM_O1,f"{FLG_L:g} (沿)")
h['vdim'](pv(0,FLG_Y1)[1],pv(0,-FLG_Y1)[1],xr,xr+DIM_O2,f"{2*FLG_Y1:g}")
h['vdim'](pv(0,IY1)[1],pv(0,IY0)[1],xr,xr+DIM_O3,f"{IY1-IY0:g} (内腔)")
h['note'](*pv(FLG_X0+1.5,44),pv(19,0)[0]+3,45.0,
          f"沿 {FLG_T:g} 厚 ×2 + 三角筋 {GUS_T:g} 厚 ×4 (45°, 臂 {GUS_ARM:g})",anchor="start")

# ================= 侧视图 (从 +X 开口侧看, 2:1) — Y 横, Z 纵 =================
SX, SYB = 200.0, 136.0
def sv(y,z): return (SX+(y+FLG_Y1)*S, SYB-z*S)
h['text'](sv(0,0)[0],36.0,"侧视图 (从 +X 开口侧看进腔, 2:1), +Y = 图右",size=TXT_L,anchor="middle")
h['rect'](*sv(OY0,OZ1),*sv(OY1,OZ0))                       # 盒体外廓
h['rect'](*sv(IY0,IZ1),*sv(IY1,IZ0))                       # 腔口 (开口面可见)
h['rect'](*sv(-FLG_Y1,OZ1),*sv(OY0,OZ0))                   # -Y 沿 (后方, X0..3)
h['rect'](*sv(OY1,OZ1),*sv(FLG_Y1,OZ0))                    # +Y 沿
# --- 盘缘裁切弧 (2026-07-27): 本视图 = 零件系 Y-Z 面, 裁切圆柱轴平行 X
#     → 在此视图里是真圆弧: (z+TRIM_CX_Z)^2 + (y-TRIM_CY_Y)^2 = TRIM_R^2
import math as _m
_zc = [OZ0 + (OZ1-OZ0)*i/120.0 for i in range(121)]
_arc = []
for _z in _zc:
    _dx = TRIM_R**2 - (_z + TRIM_CX_Z)**2
    if _dx <= 0:
        continue
    _y = TRIM_CY_Y - _m.sqrt(_dx)
    if _y > -FLG_Y1:                    # 只画真正切到料的那一段
        _arc.append(sv(_y, _z))
if len(_arc) > 1:
    pdf.set_line_width(GEOM_W)
    for _i in range(len(_arc)-1):
        pdf.line(_arc[_i][0], _arc[_i][1], _arc[_i+1][0], _arc[_i+1][1])
    h['note'](_arc[len(_arc)//2][0], _arc[len(_arc)//2][1], sv(-FLG_Y1,0)[0]-6, 60.0,
              f"盘缘裁切 R{TRIM_R:g} (弧心 = 转子轴, 零件系 y{TRIM_CY_Y:g}/z-{TRIM_CX_Z:g}) — "
              f"切掉原 -Y 沿外角 (装配系 r90.22 -> 83.50, 收进 Φ170 盘缘内)", anchor="end")

for z0 in GUS_ZS:                                          # 筋 Z 带 (沿后方 X5.1..15.1, 隐藏)
    h['drect'](*sv(-FLG_Y1,z0+GUS_T),*sv(OY0,z0))
    h['drect'](*sv(OY1,z0+GUS_T),*sv(FLG_Y1,z0))
h['drect'](*sv(IY1,WIN_ZC+WIN_H/2),*sv(OY1,WIN_ZC-WIN_H/2))  # 出口窗 (+Y 壁内, 隐藏)
for zc in HOLE_ZS:                                         # 4×Φ3.2 (此视图为真圆)
    for yc in (HOLE_YC, -HOLE_YC):
        cx,cy = sv(yc,zc); pdf.circle(cx,cy,M3_D/2*S,style="D"); h['cross'](cx,cy,5.0)
yb3 = sv(0,OZ0)[1]
h['hdim'](sv(-FLG_Y1,0)[0],sv(FLG_Y1,0)[0],yb3,yb3+DIM_O1,f"{2*FLG_Y1:g}")
h['hdim'](sv(OY1,0)[0],sv(HOLE_YC,0)[0],yb3,yb3+DIM_O2,f"{HOLE_YC-OY1:g}")
xl3 = sv(-FLG_Y1,0)[0]; xr3 = sv(FLG_Y1,0)[0]
h['vdim'](sv(0,HOLE_ZS[1])[1],sv(0,HOLE_ZS[0])[1],sv(-HOLE_YC,0)[0],xl3-DIM_O1,f"{HOLE_CC:g} (孔距)")
h['vdim'](sv(0,IZ1)[1],sv(0,IZ0)[1],xr3,xr3+DIM_O1,f"{IZ1-IZ0:g} (内腔)")
h['note'](*sv(-HOLE_YC,HOLE_ZS[1]),xl3-14,148.0,
          f"4×Φ{M3_D:g} 通 (M3, 孔轴沿 X, Z {HOLE_ZS[0]:g}/{HOLE_ZS[1]:g} 对称中面)",anchor="end")

# ================= 正视图 (从 +Y 端看, 2:1) — X 横, Z 纵 =================
EX, EYB = 225.0, 252.0
def ev(x,z): return (EX+x*S, EYB-z*S)
h['text'](ev(OX1/2,0)[0],157.0,"正视图 (从 +Y 端看, 2:1) — 出口窗",size=TXT_L,anchor="middle")
h['rect'](*ev(OX0,OZ1),*ev(OX1,OZ0))                       # 外廓 (端壁 + 前方沿投影重合)
h['pl']([ev(FLG_X0,OZ1),ev(FLG_X0,OZ0)],GEOM_W)            # 沿内面边 X=15.1 (前方)
for z0 in GUS_ZS:                                          # 筋 (前方) X 5.1..15.1
    h['rect'](*ev(FLG_X0-GUS_ARM,z0+GUS_T),*ev(FLG_X0,z0))
h['rect'](*ev(WIN_XC-WIN_W/2,WIN_ZC+WIN_H/2),*ev(WIN_XC+WIN_W/2,WIN_ZC-WIN_H/2))  # 出口窗
h['drect'](*ev(IX0,IZ1),*ev(IX1,IZ0))                      # 内腔 (隐藏)
xw = ev(OX0,0)[0]; xe = ev(OX1,0)[0]; yb2 = ev(0,0)[1]
h['vdim'](ev(0,OZ1)[1],ev(0,OZ0)[1],xw,xw-DIM_O1,f"{OZ1-OZ0:g}")
h['vdim'](ev(0,WIN_ZC+WIN_H/2)[1],ev(0,WIN_ZC-WIN_H/2)[1],xe,xe+DIM_O1,f"{WIN_H:g}")
h['vdim'](ev(0,WIN_ZC)[1],ev(0,OZ0)[1],xe,xe+DIM_O2,f"{WIN_ZC:g} (窗中心)")
h['hdim'](ev(WIN_XC-WIN_W/2,0)[0],ev(WIN_XC+WIN_W/2,0)[0],yb2,yb2+DIM_O1,f"{WIN_W:g}")
h['note'](*ev(WIN_XC-WIN_W/2,WIN_ZC),ev(OX1,0)[0]+29,175.0,
          f"出口窗 = 母头壳 10.3×18.7 +0.4, 对准放平模块口轴线 (X{WIN_XC:g}, 离开口面 7.25), 切穿 +Y 沿板",anchor="start")

h['tblock']("POV 3D 结构件 — wifi_shell 新 WiFi 壳子 v1 (侧开口五面盒 + 双端沿)",
    "投影 1st-angle / 比例 2:1 / 全平面通孔无详图",
    f"盒体 {OX1-OX0:g}×{OY1-OY0:g}×{OZ1-OZ0:g} (含沿总长 {2*FLG_Y1:g}) / 内腔 {CAV_X:g}×{CAV_Y:g}×{CAV_Z:g} / 壁 {WALL:g} / "
    f"开口 = +X 侧 / 窗 {WIN_W:g}×{WIN_H:g} @ (X{WIN_XC:g}, Z{WIN_ZC:g}) / 沿 {FLG_L:g}×{FLG_T:g} ×2 + 筋 {GUS_T:g} ×4 + "
    f"4×Φ{M3_D:g} (距壁 5, c-c {HOLE_CC:g}) / 盘缘裁切 R{TRIM_R:g} / 打印/安装姿态 = 倒扣 (开口/沿朝下) 零支撑 / PETG / mm",
    "2026-07-27  /  POV3D / models / usb_wifi / wifi_shell.stl")

out = Path(__file__).with_name("wifi_shell_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt = Path(__file__).with_name("wifi_shell_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
