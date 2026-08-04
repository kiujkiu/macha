"""
A3 drawing — frame_A_v4 (v4 顶轴承架 A, 下层架, PLA ×1)。
参数 import 自 build_frame.py (单一数据源; import 会幂等重建两个 frame STL)。
GB 1st-angle: 主视图 (X-Z, 2:1) 上, 俯视图 (X-Y, 1:1) 下, 毂局部放大 I (2.5:1) 右。

A 与 B 由同一个 frame_piece() 生成, **只差 Z 分层**:
  · A (本图): 毂/臂/垫柱 z0..8, 筋 z8..16 (**在臂之上**), 688 窝 z3..8 **朝上开口**,
             垫柱高 8 → M6×16; **正立姿态打印** (STL 即打印姿态)
  · B       : 毂/臂 z8..16, 筋 z0..8 (在臂之下), 688 窝 z11..16, 垫柱高 16 → M6×30;
             翻转姿态打印; 且 B 的 ang=90 臂筋上多 2×Φ3.2 挡光滑片挂孔 (A 没有)
装配: A 先坐柱顶 (asm 290..306, 毂 290..298, 688#1 293..298), B 叠在 A 上 (毂 298..306),
      两毂用 4× M3×20+螺母 @R14 对锁。
2026-08-04 补出 (v3 起就一直只有 frame_B 的图)。
"""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from fpdf import FPDF

from build_frame import (ARM_W, ARM_T, RIB_W, RIB_T, HUB_D, BOLT_R,
                         BRG_POCKET_D, BRG_POCKET_DEPTH, BRG_SHOULDER_D,
                         PAD_D, POST_R, POST_A0, POST_GRID, RIB_R0, RIB_R1, M3_TIGHT, M6_CLEAR,
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
# ===== A 的 Z 分层 =====
ARM_Z0, ARM_Z1 = 0.0, ARM_T          # 毂/臂/垫柱 z0..8
RIB_Z0, RIB_Z1 = ARM_T, ARM_T + RIB_T  # 筋 z8..16 (在臂之上)
Z_TOP   = RIB_Z1                     # 件总高 16
PK_Z0   = ARM_Z1 - BRG_POCKET_DEPTH  # 688 窝 z3..8 (朝上开口)
PAD_H_A = 8.0                        # A 的垫柱高 (B 是 16)
X0      = -HUB_D/2
X1      = POST_R + PAD_D/2
XMID    = (X0 + X1)/2
FOOT    = X1 - X0
ARM_XT  = math.sqrt((HUB_D/2)**2 - (ARM_W/2)**2)
A_T     = math.degrees(math.asin((ARM_W/2)/(HUB_D/2)))   # 24.16°

_w(0.3); pdf.rect(5,5,PAGE_W-10,PAGE_H-10,style="D")
text(PAGE_W/2,15,"POV 3D v4 — frame_A_v4 顶轴承架 A (下层架, ×1)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,f"毂 Φ{HUB_D:g} / 臂 {ARM_W:g} 宽 × {ARM_T:g} 厚 ×2 (0°/90° L 形) / 臂**上**筋 {RIB_W:g}×{RIB_T:g} (z{RIB_Z0:g}..{RIB_Z1:g}) / 垫柱 Φ{PAD_D:g}×{PAD_H_A:g} @POST_R {POST_R:.2f} / "
     f"688 压入窝 Φ{BRG_POCKET_D:g}×{BRG_POCKET_DEPTH:g} (z{PK_Z0:g}..{ARM_Z1:g}, **朝上开口**) + Φ{BRG_SHOULDER_D:g} 台肩通孔 / 4×Φ{M3_TIGHT:g} @R{BOLT_R:g} 45°+90k° 对锁 frame_B / "
     f"柱位 网格 M6 螺纹孔 ({POST_GRID[0]:g},{POST_GRID[1]:g}) 族, 角向 {POST_A0:.3f}°+90k / **正立姿态打印零支撑** (STL 即打印姿态) / PLA  (GB 1st-angle, 主视 2:1 / 俯视 1:1 / 放大 2.5:1, mm)",
     size=TXT_I,anchor="middle")

# ===== 主视图 (X-Z, 从 -Y 视向, 2:1) =====
S2, FX, FZ0 = 2.0, 200.0, 92.0
def fv(x,z): return (FX+(x-XMID)*S2, FZ0-z*S2)
text(FX,46.0,"主视图 (从 -Y 视向, 2:1)",size=TXT_L,anchor="middle")
_w(GEOM_W)
pdf.line(*fv(X0,ARM_Z0),*fv(X1,ARM_Z0))                   # 底 z0 (毂/臂/垫柱共面)
pdf.line(*fv(X0,ARM_Z0),*fv(X0,ARM_Z1))                   # 毂左缘
pdf.line(*fv(X0,ARM_Z1),*fv(X1,ARM_Z1))                   # 顶 z8 (毂/臂/垫柱共面)
pdf.line(*fv(X1,ARM_Z0),*fv(X1,ARM_Z1))                   # 垫柱右缘
pdf.line(*fv(ARM_XT,ARM_Z1),*fv(ARM_XT,ARM_Z0))           # +X 臂前侧面与毂圆交线
# +X 臂上的筋 (z8..16, 在臂之上 → 可见)
pdf.line(*fv(RIB_R0,RIB_Z0),*fv(RIB_R0,RIB_Z1))
pdf.line(*fv(RIB_R1,RIB_Z0),*fv(RIB_R1,RIB_Z1))
pdf.line(*fv(RIB_R0,RIB_Z1),*fv(RIB_R1,RIB_Z1))           # 筋顶 z16
# 90° 臂的筋 (投影 x -2..2, z8..16) + 垫柱 (投影 x -9..9, z0..8, 藏在毂后)
pdf.line(*fv(-RIB_W/2,RIB_Z0),*fv(-RIB_W/2,RIB_Z1))
pdf.line(*fv( RIB_W/2,RIB_Z0),*fv( RIB_W/2,RIB_Z1))
pdf.line(*fv(-RIB_W/2,RIB_Z1),*fv( RIB_W/2,RIB_Z1))
dline(*fv(-ARM_W/2,ARM_Z0),*fv(-ARM_W/2,ARM_Z1))          # 远端垫柱 (隐藏于毂后)
dline(*fv( ARM_W/2,ARM_Z0),*fv( ARM_W/2,ARM_Z1))
# 隐藏: 688 窝 Φ15.8 (z3..8, 朝上) + Φ13 台肩 (z0..3)
dline(*fv(-BRG_POCKET_D/2,PK_Z0),*fv(-BRG_POCKET_D/2,ARM_Z1))
dline(*fv( BRG_POCKET_D/2,PK_Z0),*fv( BRG_POCKET_D/2,ARM_Z1))
dline(*fv(-BRG_SHOULDER_D/2,ARM_Z0),*fv(-BRG_SHOULDER_D/2,PK_Z0))
dline(*fv( BRG_SHOULDER_D/2,ARM_Z0),*fv( BRG_SHOULDER_D/2,PK_Z0))
dline(*fv(-BRG_POCKET_D/2,PK_Z0),*fv(-BRG_SHOULDER_D/2,PK_Z0))
dline(*fv( BRG_SHOULDER_D/2,PK_Z0),*fv( BRG_POCKET_D/2,PK_Z0))
# 隐藏: +X 垫柱 M6 Φ6.5 通孔
dline(*fv(POST_R-M6_CLEAR/2,ARM_Z0),*fv(POST_R-M6_CLEAR/2,ARM_Z1))
dline(*fv(POST_R+M6_CLEAR/2,ARM_Z0),*fv(POST_R+M6_CLEAR/2,ARM_Z1))
# 中心线
cline(*fv(0,-2),*fv(0,Z_TOP+2))
cline(*fv(POST_R,-2),*fv(POST_R,ARM_Z1+2))
# 尺寸
xr_=fv(X1,0)[0]
vdim(fv(0,Z_TOP)[1],fv(0,ARM_Z0)[1],xr_,xr_+15.0,f"{Z_TOP:g} (总高)")
xl_=fv(X0,0)[0]
vdim(fv(0,ARM_Z1)[1],fv(0,ARM_Z0)[1],xl_,xl_-15.0,f"{ARM_T:g} (臂/垫柱)")
vdim(fv(0,RIB_Z1)[1],fv(0,RIB_Z0)[1],xl_,xl_-15.0,f"{RIB_T:g} (筋, 在臂上)")
yb_=fv(0,ARM_Z0)[1]
hdim(fv(RIB_R0,0)[0],fv(RIB_R1,0)[0],fv(0,ARM_Z0)[1],yb_+DIM_O1,f"{RIB_R1-RIB_R0:.2f} (筋 R{RIB_R0:g}..R{RIB_R1:.2f})")
# 引注
note(*fv(-BRG_POCKET_D/2,PK_Z0+2.5),70.0,44.0,f"688 窝 Φ{BRG_POCKET_D:g}×{BRG_POCKET_DEPTH:g} 朝上 + Φ{BRG_SHOULDER_D:g} 通 (隐藏)")
note(*fv(POST_R+M6_CLEAR/2,5.0),362.0,44.0,f"Φ{M6_CLEAR:g} M6 通 ×2 (**M6×16**, B 那边是 M6×30)")
note(*fv(61.5,RIB_Z1),255.0,116.0,f"筋 {RIB_W:g}×{RIB_T:g} ×2 (z {RIB_Z0:g}..{RIB_Z1:g}, **在臂之上** — 与 B 相反)")
note(*fv(X1,4.0),365.0,105.0,f"垫柱 Φ{PAD_D:g}×{PAD_H_A:g} ×2 (B 是 ×16)")

# ===== 俯视图 (X-Y, 1:1) =====
TXC, TYC = 115.0, 187.0
def pv(x,y): return (TXC+(x-XMID), TYC-(y-XMID))
text(TXC,112.0,"俯视图 (X-Y, 1:1)",size=TXT_L,anchor="middle")
HC = pv(0,0)
_w(GEOM_W)
arc(*HC,HUB_D/2,A_T,90-A_T); arc(*HC,HUB_D/2,90+A_T,360-A_T)
pdf.line(*pv(ARM_XT, ARM_W/2),*pv(POST_R, ARM_W/2))
pdf.line(*pv(ARM_XT,-ARM_W/2),*pv(POST_R,-ARM_W/2))
arc(*pv(POST_R,0),PAD_D/2,-90.0,90.0)
pdf.line(*pv( ARM_W/2,ARM_XT),*pv( ARM_W/2,POST_R))
pdf.line(*pv(-ARM_W/2,ARM_XT),*pv(-ARM_W/2,POST_R))
arc(*pv(0,POST_R),PAD_D/2,0.0,180.0)
# 臂上筋 (可见, 因为在臂之上)
for sgn in (1.0,-1.0):
    pdf.line(*pv(RIB_R0,sgn*RIB_W/2),*pv(RIB_R1,sgn*RIB_W/2))
    pdf.line(*pv(sgn*RIB_W/2,RIB_R0),*pv(sgn*RIB_W/2,RIB_R1))
pdf.line(*pv(RIB_R0,-RIB_W/2),*pv(RIB_R0,RIB_W/2)); pdf.line(*pv(RIB_R1,-RIB_W/2),*pv(RIB_R1,RIB_W/2))
pdf.line(*pv(-RIB_W/2,RIB_R0),*pv(RIB_W/2,RIB_R0)); pdf.line(*pv(-RIB_W/2,RIB_R1),*pv(RIB_W/2,RIB_R1))
# 孔系
circ(*HC,BRG_POCKET_D/2); circ(*HC,BRG_SHOULDER_D/2)
dccirc(*HC,BOLT_R)
for k in range(4):
    a=math.radians(45+90*k)
    circ(*pv(BOLT_R*math.cos(a),BOLT_R*math.sin(a)),M3_TIGHT/2)
circ(*pv(POST_R,0),M6_CLEAR/2); circ(*pv(0,POST_R),M6_CLEAR/2)
cline(*pv(X0-4,0),*pv(X1+4,0)); cline(*pv(0,X0-4),*pv(0,X1+4))
cross(*pv(POST_R,0),12.0); cross(*pv(0,POST_R),12.0)
_w(0.2); pdf.circle(*HC,25.0,style="D")
text(HC[0]+21.0,HC[1]-19.0,"I",size=TXT_L)
# 尺寸
xg_=pv(X0,0)[0]
vdim(pv(0,X1)[1],pv(0,X0)[1],xg_,xg_-14.0,f"{FOOT:.2f} (足迹)")
yg_=pv(0,X0)[1]
hdim(HC[0],pv(POST_R,0)[0],yg_,yg_+10.0,f"{POST_R:.2f} (POST_R 柱位)")
bx,by=pv(BOLT_R*math.cos(math.radians(45)),BOLT_R*math.sin(math.radians(45)))
note(bx,by,106.0,190.0,f"4×Φ{M3_TIGHT:g} @R{BOLT_R:g} (45°+90k°), M3×20+螺母 ×4 对锁 frame_B")
note(*pv(RIB_R1,RIB_W/2),86.0,166.0,f"筋在臂**上**面 (z {RIB_Z0:g}..{RIB_Z1:g}) — A 无挡光滑片挂孔 (那是 B 的)")
note(HC[0]+(HUB_D/2)*math.cos(math.radians(-45)),HC[1]-(HUB_D/2)*math.sin(math.radians(-45)),
     111.0,255.0,f"毂 Φ{HUB_D:g} (详见 I)")

# ===== 局部放大 I (毂, 俯视, 2.5:1) =====
S3, DX, DY = 2.5, 318.0, 186.0
def dv(x,y): return (DX+x*S3, DY-y*S3)
text(DX,112.0,"局部放大 I (毂, 俯视, 2.5:1)",size=TXT_L,anchor="middle")
_w(GEOM_W)
BND = HUB_D/2
arc(DX,DY,BND*S3,A_T,90-A_T); arc(DX,DY,BND*S3,90+A_T,360-A_T)
bx2=math.sqrt(BND**2-(ARM_W/2*1.0)**2)
for (ax,ay,bx3,by3) in ((bx2,ARM_W/2,BND+6,ARM_W/2),(bx2,-ARM_W/2,BND+6,-ARM_W/2),
                        (ARM_W/2,bx2,ARM_W/2,BND+6),(-ARM_W/2,bx2,-ARM_W/2,BND+6)):
    pdf.line(*dv(ax,ay),*dv(bx3,by3))
circ(DX,DY,BRG_POCKET_D/2*S3); circ(DX,DY,BRG_SHOULDER_D/2*S3)
dccirc(DX,DY,BOLT_R*S3)
for k in range(4):
    a=math.radians(45+90*k)
    circ(*dv(BOLT_R*math.cos(a),BOLT_R*math.sin(a)),M3_TIGHT/2*S3)
cline(*dv(-BND-8,0),*dv(BND+8,0)); cline(*dv(0,-BND-8),*dv(0,BND+8))
hdim(dv(-BRG_POCKET_D/2,0)[0],dv(BRG_POCKET_D/2,0)[0],DY,DY-18.0,f"Φ{BRG_POCKET_D:g}")
hdim(dv(-HUB_D/2,0)[0],dv(HUB_D/2,0)[0],dv(0,-BND)[1],dv(0,-BND)[1]+18.0,f"Φ{HUB_D:g} (毂)")
b45=BOLT_R*S3*math.cos(math.radians(45))
note(DX+b45+M3_TIGHT/2*S3*0.7,DY-b45-M3_TIGHT/2*S3*0.7,395.0,138.0,
     f"4×Φ{M3_TIGHT:g} @R{BOLT_R:g} (45°+90k°)",anchor="end")
note(DX+BRG_SHOULDER_D/2*S3,DY+6.0,395.0,150.0,f"Φ{BRG_SHOULDER_D:g} 台肩孔 贯通")

# ===== 标题栏 =====
tb_y = PAGE_H-28; tb_x, tb_w, tb_h = 20, PAGE_W-40, 18
_w(0.3); pdf.rect(tb_x, tb_y, tb_w, tb_h, style="D")
pdf.line(tb_x, tb_y+tb_h/2, tb_x+tb_w, tb_y+tb_h/2)
text(tb_x+4,tb_y+6,"POV 3D v4 结构件 — frame_A_v4 顶轴承架 A (下层, ×1, PLA; 正立姿态打印零支撑)",size=TXT_L)
text(tb_x+tb_w-4,tb_y+6,"投影 1st-angle / 比例 1:1 (主视 2:1 / 放大 2.5:1)",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+14.5,f"毂 Φ{HUB_D:g} (z{ARM_Z0:g}..{ARM_Z1:g}) / 臂 {ARM_W:g}×{ARM_T:g} ×2 / 筋 {RIB_W:g}×{RIB_T:g} (z{RIB_Z0:g}..{RIB_Z1:g}, **在臂上**) / 垫柱 Φ{PAD_D:g}×{PAD_H_A:g} @R{POST_R:.2f} (12.5·√58, 柱落网格螺纹孔 ({POST_GRID[0]:g},{POST_GRID[1]:g}) 族) / "
     f"BOM: 688 ×1, M6×16 ×2, M3×20+螺母 ×4 (与 B 共用) / 装配 rot{POST_A0+90:.3f}° 置柱顶: 垫/毂底 asm290, 688 下轴承 293..298 / 总高 {Z_TOP:g} / 足迹 {FOOT:.2f}×{FOOT:.2f} / 单位 mm",size=TXT_I)
text(tb_x+tb_w-4,tb_y+14.5,"2026-08-04  /  POV3D / v4 / top_bearing_v4 / frame_A_v4.stl",size=TXT_I,anchor="end")

out = Path(__file__).with_name("frame_A_v4_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except Exception:
    alt = Path(__file__).with_name("frame_A_v4_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
