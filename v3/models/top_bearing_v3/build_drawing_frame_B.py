"""
A3 drawing — frame_B_v3 (v3 顶轴承架 B, 上层架, PLA ×1)。
参数 import 自 build_frame.py (单一数据源; import 会幂等重建两个 frame STL)。
GB 1st-angle: 主视图 (X-Z, 2:1) 上, 俯视图 (X-Y, 1:1) 下, 毂局部放大 I (2.5:1) 右。
本地坐标 = 装配姿态 (asm = local + 290)。2026-07-24: 筋加高 4×8 (z 0..8, 底与垫柱底平齐);
ang=90 臂筋新增 2×Φ3.2 挡光滑片挂孔 @r45.2/51.4, 孔心 z4.0 (筋 8 高正中, asm 294;
vane_slider_v3, M3×20+螺母, 刀片印长 50 装机剪短)。
"""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from fpdf import FPDF

from build_frame import (ARM_W, ARM_T, RIB_W, RIB_T, HUB_D, BOLT_R,
                         BRG_POCKET_D, BRG_POCKET_DEPTH, BRG_SHOULDER_D,
                         PAD_D, POST_R, RIB_R0, RIB_R1, M3_TIGHT, M6_CLEAR,
                         VANE_BOLT_RS, VANE_BOLT_Z)

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
def dline(x1,y1,x2,y2):
    pdf.set_dash_pattern(dash=2.0,gap=1.2); line(x1,y1,x2,y2,HID_W); pdf.set_dash_pattern()
def cline(x1,y1,x2,y2):
    pdf.set_dash_pattern(dash=1.2,gap=0.6); line(x1,y1,x2,y2,0.13); pdf.set_dash_pattern()
def circ(cx,cy,r,w=GEOM_W):
    _w(w); pdf.circle(cx,cy,r,style="D")
def dccirc(cx,cy,r):
    pdf.set_dash_pattern(dash=1.2,gap=0.6); _w(0.13); pdf.circle(cx,cy,r,style="D"); pdf.set_dash_pattern()
def arc(cx,cy,r,a0,a1,w=GEOM_W,seg=60):
    _w(w); prev=None
    for i in range(seg+1):
        a=math.radians(a0+(a1-a0)*i/seg)
        p=(cx+r*math.cos(a), cy-r*math.sin(a))
        if prev: pdf.line(*prev,*p)
        prev=p
def cross(cx,cy,r=4.0):
    pdf.set_dash_pattern(dash=1.2,gap=0.6); _w(0.13)
    pdf.line(cx-r,cy,cx+r,cy); pdf.line(cx,cy-r,cx,cy+r); pdf.set_dash_pattern(); _w(GEOM_W)

# ===== 派生几何 (本地坐标 = 装配姿态) =====
Z_TOP   = 16.0                      # 垫柱/毂/臂 顶面
Z_ARM0  = 8.0                       # 臂/毂 底面 (臂 z 8..16)
Z_RIB0  = Z_ARM0 - RIB_T            # 筋 z 0..8 (RIB_T=8, 底与垫柱底平齐)
PK_Z0   = Z_TOP - BRG_POCKET_DEPTH  # 688 窝 z 11..16
X0      = -HUB_D/2                  # -22
X1      = POST_R + PAD_D/2          # 115.066
XMID    = (X0 + X1)/2
FOOT    = X1 - X0                   # 137.066
ARM_XT  = math.sqrt((HUB_D/2)**2 - (ARM_W/2)**2)   # 臂侧面与毂圆交点 x = 20.07
A_T     = math.degrees(math.asin((ARM_W/2)/(HUB_D/2)))  # 24.16°

_w(0.3); pdf.rect(5,5,PAGE_W-10,PAGE_H-10,style="D")
text(PAGE_W/2,15,"POV 3D v3 — frame_B_v3 顶轴承架 B (上层架, ×1)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,f"毂 Φ{HUB_D:g} / 臂 {ARM_W:g} 宽 × {ARM_T:g} 厚 ×2 (0°/90° L 形) / 臂底筋 {RIB_W:g}×{RIB_T:g} / 垫柱 Φ{PAD_D:g}×{Z_TOP:g} @POST_R {POST_R:.2f} / "
     f"688 压入窝 Φ{BRG_POCKET_D:g}×{BRG_POCKET_DEPTH:g} + Φ{BRG_SHOULDER_D:g} 台肩通孔 / 4×Φ{M3_TIGHT:g} @R{BOLT_R:g} 45°+90k° / 翻转姿态打印零支撑 (STL 已是打印姿态, 轴承窝朝上) / "
     f"2026-07-24 ang=90 臂筋带 2×Φ{M3_TIGHT:g} 挡光滑片挂孔 (M3×20+螺母, 滑片刀片印长 50 装机剪短) / PLA  (GB 1st-angle, 主视 2:1 / 俯视 1:1 / 放大 2.5:1, mm)",
     size=TXT_I,anchor="middle")

# ===== 主视图 (X-Z, 从 -Y 视向, 2:1) =====
S2, FX, FZ0 = 2.0, 200.0, 92.0
def fv(x,z): return (FX+(x-XMID)*S2, FZ0-z*S2)
text(FX,46.0,"主视图 (从 -Y 视向, 2:1)",size=TXT_L,anchor="middle")
_w(GEOM_W)
pdf.line(*fv(X0,Z_TOP),*fv(X1,Z_TOP))                     # 顶 z16 (毂/臂/垫柱共面)
pdf.line(*fv(X0,Z_TOP),*fv(X0,Z_ARM0))                    # 毂左缘
pdf.line(*fv(X0,Z_ARM0),*fv(POST_R,Z_ARM0))               # 毂/臂底 z8 (至臂与垫柱切点)
pdf.line(*fv(ARM_XT,Z_TOP),*fv(ARM_XT,Z_ARM0))            # +X 臂前侧面与毂圆交线
pdf.line(*fv(RIB_R0,Z_ARM0),*fv(RIB_R0,Z_RIB0))           # +X 筋 前立面
pdf.line(*fv(RIB_R1,Z_ARM0),*fv(RIB_R1,Z_RIB0))
pdf.line(*fv(RIB_R0,Z_RIB0),*fv(RIB_R1,Z_RIB0))           # 筋底 z2
pdf.line(*fv(POST_R-PAD_D/2,0),*fv(POST_R-PAD_D/2,Z_ARM0))# +X 垫柱左缘 (z0..8 可见)
pdf.line(*fv(POST_R-PAD_D/2,0),*fv(X1,0))                 # 垫柱底 z0
pdf.line(*fv(X1,0),*fv(X1,Z_TOP))                         # 垫柱右缘
# 90° 臂的垫柱/筋 (投影 x -9..9 / -2..2)
pdf.line(*fv(-ARM_W/2,0),*fv(ARM_W/2,0))                  # 远端垫柱底 z0
pdf.line(*fv(-ARM_W/2,0),*fv(-ARM_W/2,Z_ARM0))            # 远端垫柱侧缘 z0..8 可见
pdf.line(*fv(ARM_W/2,0),*fv(ARM_W/2,Z_ARM0))
dline(*fv(-ARM_W/2,Z_ARM0),*fv(-ARM_W/2,Z_TOP))           # z8..16 藏于毂后 (隐藏)
dline(*fv(ARM_W/2,Z_ARM0),*fv(ARM_W/2,Z_TOP))
pdf.line(*fv(-RIB_W/2,Z_ARM0),*fv(-RIB_W/2,Z_RIB0))       # 90° 筋近端面
pdf.line(*fv(RIB_W/2,Z_ARM0),*fv(RIB_W/2,Z_RIB0))
pdf.line(*fv(-RIB_W/2,Z_RIB0),*fv(RIB_W/2,Z_RIB0))
# 隐藏: 90° 臂筋上 2×Φ3.2 挡光滑片挂孔 (沿 X 贯穿, 投影 x -2..2, z 4+-1.6)
dline(*fv(-RIB_W/2,VANE_BOLT_Z-M3_TIGHT/2),*fv(RIB_W/2,VANE_BOLT_Z-M3_TIGHT/2))
dline(*fv(-RIB_W/2,VANE_BOLT_Z+M3_TIGHT/2),*fv(RIB_W/2,VANE_BOLT_Z+M3_TIGHT/2))
cline(*fv(-RIB_W/2-2,VANE_BOLT_Z),*fv(RIB_W/2+2,VANE_BOLT_Z))
# 隐藏: 688 窝 Φ15.8 (z11..16) + Φ13 台肩 (z8..11)
dline(*fv(-BRG_POCKET_D/2,PK_Z0),*fv(-BRG_POCKET_D/2,Z_TOP))
dline(*fv( BRG_POCKET_D/2,PK_Z0),*fv( BRG_POCKET_D/2,Z_TOP))
dline(*fv(-BRG_SHOULDER_D/2,Z_ARM0),*fv(-BRG_SHOULDER_D/2,PK_Z0))
dline(*fv( BRG_SHOULDER_D/2,Z_ARM0),*fv( BRG_SHOULDER_D/2,PK_Z0))
dline(*fv(-BRG_POCKET_D/2,PK_Z0),*fv(-BRG_SHOULDER_D/2,PK_Z0))
dline(*fv( BRG_SHOULDER_D/2,PK_Z0),*fv( BRG_POCKET_D/2,PK_Z0))
# 隐藏: +X 垫柱 M6 Φ6.5 通孔
dline(*fv(POST_R-M6_CLEAR/2,0),*fv(POST_R-M6_CLEAR/2,Z_TOP))
dline(*fv(POST_R+M6_CLEAR/2,0),*fv(POST_R+M6_CLEAR/2,Z_TOP))
# 中心线
cline(*fv(0,-2),*fv(0,18))
cline(*fv(POST_R,-2),*fv(POST_R,18))
# 尺寸
xr_=fv(X1,0)[0]
vdim(fv(0,Z_TOP)[1],fv(0,0)[1],xr_,xr_+15.0,f"{Z_TOP:g} (总高)")
xl_=fv(X0,0)[0]
vdim(fv(0,Z_TOP)[1],fv(0,Z_ARM0)[1],xl_,xl_-15.0,f"{ARM_T:g}")
vdim(fv(0,Z_ARM0)[1],fv(0,0)[1],xl_,xl_-15.0,f"{RIB_T:g} (筋)")
yb_=fv(0,0)[1]
hdim(fv(RIB_R0,0)[0],fv(RIB_R1,0)[0],fv(0,Z_RIB0)[1],yb_+DIM_O1,f"{RIB_R1-RIB_R0:.2f} (筋 R{RIB_R0:g}..R{RIB_R1:.2f})")
vdim(fv(0,VANE_BOLT_Z)[1],fv(0,0)[1],fv(RIB_W/2,0)[0],117.0,f"{VANE_BOLT_Z:g}")
# 引注
note(*fv(-BRG_POCKET_D/2,13.0),70.0,44.0,f"688 窝 Φ{BRG_POCKET_D:g}×{BRG_POCKET_DEPTH:g} + Φ{BRG_SHOULDER_D:g} 通 (隐藏)")
note(*fv(POST_R+M6_CLEAR/2,11.0),362.0,44.0,f"Φ{M6_CLEAR:g} M6 通 ×2 (M6×30)")
note(*fv(61.5,Z_RIB0),255.0,116.0,f"筋 {RIB_W:g}×{RIB_T:g} ×2 (z 0..8, 底与垫柱底平齐)")
note(*fv(-RIB_W/2,VANE_BOLT_Z),78.0,108.0,f"2×Φ{M3_TIGHT:g} 孔心 z{VANE_BOLT_Z:g} 居中 (沿X, 见俯视)")
note(*fv(X1,4.0),365.0,105.0,f"垫柱 Φ{PAD_D:g}×{Z_TOP:g} ×2")

# ===== 俯视图 (X-Y, 1:1, 1st-angle 置主视图下方) =====
TXC, TYC = 115.0, 187.0
def pv(x,y): return (TXC+(x-XMID), TYC-(y-XMID))
text(TXC,112.0,"俯视图 (X-Y, 1:1)",size=TXT_L,anchor="middle")
# 毂圆 (臂扇区不画)
HC = pv(0,0)
arc(*HC,HUB_D/2,A_T,90.0-A_T)
arc(*HC,HUB_D/2,90.0+A_T,360.0-A_T)
# +X 臂 + 垫柱
_w(GEOM_W)
pdf.line(*pv(ARM_XT, ARM_W/2),*pv(POST_R, ARM_W/2))
pdf.line(*pv(ARM_XT,-ARM_W/2),*pv(POST_R,-ARM_W/2))
arc(*pv(POST_R,0),PAD_D/2,-90.0,90.0)
# +Y 臂 + 垫柱
pdf.line(*pv( ARM_W/2,ARM_XT),*pv( ARM_W/2,POST_R))
pdf.line(*pv(-ARM_W/2,ARM_XT),*pv(-ARM_W/2,POST_R))
arc(*pv(0,POST_R),PAD_D/2,0.0,180.0)
# 臂下筋 (隐藏)
for sgn in (1.0,-1.0):
    dline(*pv(RIB_R0,sgn*RIB_W/2),*pv(RIB_R1,sgn*RIB_W/2))
    dline(*pv(sgn*RIB_W/2,RIB_R0),*pv(sgn*RIB_W/2,RIB_R1))
dline(*pv(RIB_R0,-RIB_W/2),*pv(RIB_R0,RIB_W/2)); dline(*pv(RIB_R1,-RIB_W/2),*pv(RIB_R1,RIB_W/2))
dline(*pv(-RIB_W/2,RIB_R0),*pv(RIB_W/2,RIB_R0)); dline(*pv(-RIB_W/2,RIB_R1),*pv(RIB_W/2,RIB_R1))
# ang=90 (+Y) 臂筋: 2×Φ3.2 挡光滑片挂孔 (沿 X 贯穿筋, 孔心 z 4, 俯视为隐藏轮廓)
for br in VANE_BOLT_RS:
    dline(*pv(-RIB_W/2,br-M3_TIGHT/2),*pv(RIB_W/2,br-M3_TIGHT/2))
    dline(*pv(-RIB_W/2,br+M3_TIGHT/2),*pv(RIB_W/2,br+M3_TIGHT/2))
    cline(*pv(-RIB_W/2-2,br),*pv(RIB_W/2+2,br))
# 孔系
circ(*HC,BRG_POCKET_D/2); circ(*HC,BRG_SHOULDER_D/2)
dccirc(*HC,BOLT_R)
for k in range(4):
    a=math.radians(45+90*k)
    circ(pv(BOLT_R*math.cos(a),BOLT_R*math.sin(a))[0],pv(BOLT_R*math.cos(a),BOLT_R*math.sin(a))[1],M3_TIGHT/2)
circ(*pv(POST_R,0),M6_CLEAR/2); circ(*pv(0,POST_R),M6_CLEAR/2)
# 中心线
cline(*pv(X0-4,0),*pv(X1+4,0))
cline(*pv(0,X0-4),*pv(0,X1+4))
cross(*pv(POST_R,0),12.0); cross(*pv(0,POST_R),12.0)
# 局部放大 I 标记
_w(0.2); pdf.circle(*HC,25.0,style="D")
text(HC[0]+21.0,HC[1]-19.0,"I",size=TXT_L)
# 尺寸
xg_=pv(X0,0)[0]
vdim(pv(0,X1)[1],pv(0,X0)[1],xg_,xg_-14.0,f"{FOOT:.2f} (足迹)")
yg_=pv(0,X0)[1]
hdim(HC[0],pv(POST_R,0)[0],yg_,yg_+10.0,f"{POST_R:.2f} (POST_R 柱位)")
xa_=pv(-ARM_W/2,0)[0]
vdim(pv(0,0)[1],pv(0,VANE_BOLT_RS[0])[1],xa_,xa_-8.5,f"{VANE_BOLT_RS[0]:g}")
vdim(pv(0,0)[1],pv(0,VANE_BOLT_RS[1])[1],xa_,xa_-16.5,f"{VANE_BOLT_RS[1]:g}")
# 引注
note(*pv(0,X1),100.0,105.0,f"垫柱 Φ{PAD_D:g}×{Z_TOP:g} ×2, Φ{M6_CLEAR:g} M6 通 (M6×30)")
note(*pv(55.0,ARM_W/2),151.0,205.0,f"臂 {ARM_W:g} 宽 × {ARM_T:g} 厚 ×2 (z 8..16)")
note(*pv(70.0,RIB_W/2),161.0,220.0,f"筋 {RIB_W:g}×{RIB_T:g} (臂下, z 0..8, 隐藏)")
note(*pv(RIB_W/2,VANE_BOLT_RS[1]),86.0,166.0,
     f"2×Φ{M3_TIGHT:g} 贯穿筋 (沿X) @r{VANE_BOLT_RS[0]:g}/{VANE_BOLT_RS[1]:g}, 孔心 z{VANE_BOLT_Z:g} (筋高正中, asm294)")
text(87.0,172.6,"M3×20+螺母 ×2 挂挡光滑片 vane_slider_v3 (刀片印长50, 装机剪短调高)",size=TXT_I)
bx,by=pv(BOLT_R*math.cos(math.radians(45)),BOLT_R*math.sin(math.radians(45)))
note(bx,by,106.0,190.0,f"4×Φ{M3_TIGHT:g} @R{BOLT_R:g} (45°+90k°), M3×20+螺母 ×4 对锁 frame_A")
note(HC[0]+(HUB_D/2)*math.cos(math.radians(-45)),HC[1]-(HUB_D/2)*math.sin(math.radians(-45)),
     111.0,255.0,f"毂 Φ{HUB_D:g} (详见 I)")

# ===== 局部放大 I (毂, 俯视, 2.5:1) =====
S3, DX, DY = 2.5, 318.0, 186.0
def dv(x,y): return (DX+x*S3, DY-y*S3)
text(DX,120.0,"局部放大 I (毂, 俯视 2.5:1)",size=TXT_L,anchor="middle")
_w(0.2); pdf.circle(DX,DY,60.0,style="D")                 # 放大界圈
arc(DX,DY,(HUB_D/2)*S3,A_T,90.0-A_T)
arc(DX,DY,(HUB_D/2)*S3,90.0+A_T,360.0-A_T)
BND=60.0
_w(GEOM_W)
bx2=math.sqrt(BND**2-(ARM_W/2*S3)**2)
pdf.line(DX+ARM_XT*S3,DY-ARM_W/2*S3,DX+bx2,DY-ARM_W/2*S3) # +X 臂侧线到界圈
pdf.line(DX+ARM_XT*S3,DY+ARM_W/2*S3,DX+bx2,DY+ARM_W/2*S3)
pdf.line(DX-ARM_W/2*S3,DY-ARM_XT*S3,DX-ARM_W/2*S3,DY-bx2) # +Y 臂侧线到界圈
pdf.line(DX+ARM_W/2*S3,DY-ARM_XT*S3,DX+ARM_W/2*S3,DY-bx2)
circ(DX,DY,BRG_POCKET_D/2*S3); circ(DX,DY,BRG_SHOULDER_D/2*S3)
dccirc(DX,DY,BOLT_R*S3)
for k in range(4):
    a=math.radians(45+90*k)
    circ(DX+BOLT_R*S3*math.cos(a),DY-BOLT_R*S3*math.sin(a),M3_TIGHT/2*S3)
cline(DX-64,DY,DX+64,DY); cline(DX,DY-64,DX,DY+64)
# 尺寸
hdim(DX-HUB_D/2*S3,DX+HUB_D/2*S3,DY+HUB_D/2*S3,DY+HUB_D/2*S3+11.0,f"Φ{HUB_D:g} (毂)")
hdim(DX-BRG_POCKET_D/2*S3,DX+BRG_POCKET_D/2*S3,DY-BRG_POCKET_D/2*S3,150.0,f"Φ{BRG_POCKET_D:g}")
# 引注
note(DX+BRG_POCKET_D/2*S3,DY,395.0,165.0,f"688 压入窝 深 {BRG_POCKET_DEPTH:g} (自顶面 z16)",anchor="end")
note(DX+BRG_SHOULDER_D/2*S3*math.cos(math.radians(-40)),DY+BRG_SHOULDER_D/2*S3*math.sin(math.radians(40)),
     395.0,215.0,f"Φ{BRG_SHOULDER_D:g} 台肩孔 贯通",anchor="end")
b45=BOLT_R*S3*math.cos(math.radians(45))
note(DX+b45+M3_TIGHT/2*S3*0.7,DY-b45-M3_TIGHT/2*S3*0.7,395.0,138.0,
     f"4×Φ{M3_TIGHT:g} @R{BOLT_R:g} (45°+90k°)",anchor="end")

# ===== 标题栏 =====
tb_y=PAGE_H-28; tb_x,tb_w,tb_h=20,PAGE_W-40,18
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+6,"POV 3D v3 结构件 — frame_B_v3 顶轴承架 B (上层, ×1, PLA; 翻转姿态打印零支撑)",size=TXT_L)
text(tb_x+tb_w-4,tb_y+6,"投影 1st-angle / 比例 见各视图",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+14.5,f"毂 Φ{HUB_D:g} (z8..16) / 臂 {ARM_W:g}×{ARM_T:g} ×2 / 筋 {RIB_W:g}×{RIB_T:g} (z0..8, 底平垫柱底) / 垫柱 Φ{PAD_D:g}×{Z_TOP:g} @R{POST_R:.2f} (75·√2, 柱 (±75,±75)) / "
     f"M6 Φ{M6_CLEAR:g} 通 ×2 (M6×30) / 688 窝 Φ{BRG_POCKET_D:g}×{BRG_POCKET_DEPTH:g} + Φ{BRG_SHOULDER_D:g} 通 / 4×Φ{M3_TIGHT:g} @R{BOLT_R:g} (对锁 frame_A) / "
     f"ang90 臂筋 2×Φ{M3_TIGHT:g} 挂孔 @r{VANE_BOLT_RS[0]:g}/{VANE_BOLT_RS[1]:g} z{VANE_BOLT_Z:g} (筋高正中, asm294, M3×20+螺母 挂 vane_slider_v3, 刀片印长50 装机剪短) / "
     f"装配 rot-45° 置柱顶: 垫/筋底 asm290, 毂 298..306, 688 上轴承 301..306 / 总高 {Z_TOP:g} / 足迹 {FOOT:.2f}×{FOOT:.2f} / 单位 mm",size=TXT_I)
text(tb_x+tb_w-4,tb_y+14.5,"2026-07-24  /  POV3D / v3 / top_bearing_v3 / frame_B_v3.stl",size=TXT_I,anchor="end")

out = Path(__file__).with_name("frame_B_v3_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt = Path(__file__).with_name("frame_B_v3_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
