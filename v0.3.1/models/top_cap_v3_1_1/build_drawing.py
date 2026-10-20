"""
A3 drawing — top_cap_v3_1_1 薄压条 (v3 双面屏顶部, 2026-07-24 六改: 不加宽,
光电模块绕两孔连线中点 M(0,-45) 旋转 22.19° → 光轴过圆心)。
参数 import 自 build_stl.py (单一数据源)。GB 1st-angle。
"""
import math
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))
from fpdf import FPDF

from build_stl import (BLK_X, BLK_Y, BAR_Z0, BAR_Z1, AXIS_BORE, SCR_ECC,
                       SCREW_XS, CW_ENABLE, CW_D, CW_X, CW_YS,
                       HEAD_D, HEAD_T, SCREW_YS, SCREW_D,
                       SEN_TH, SEN_M, SEN_HOLES, SEN_CB_D, SEN_CB_T,
                       SEN_SLOT_L, SEN_SLOT_W, SEN_SLOT_C, SEN_SLOT_ANG)

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
text(PAGE_W/2,15,"POV 3D v3 — top_cap_v3_1_1 双面屏顶部薄压条 (光电斜置, 光轴过圆心)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,f"扁条 {2*BLK_X:g}×{2*BLK_Y:g}×{H:g} (装配 {BAR_Z0:g}..{BAR_Z1:g}, 底面压双面屏顶) / "
     f"轴: Φ{AXIS_BORE:g} 通孔 + Φ{HEAD_D:g}×{HEAD_T:g} 底面头窝 (M6×20 平头, 先装 M6 再压屏) / "
     f"{len(SCREW_XS)}×2 Φ{SCREW_D:g} @ X{tuple(round(v,1) for v in SCREW_XS)}/Y±64 (居中/偏心可切换)",
     size=TXT_I,anchor="middle")
text(PAGE_W/2,26,f"光电模块绕两孔连线中点 M({SEN_M[0]:g},{SEN_M[1]:g}) 旋转 {SEN_TH:.2f}° (sin = 17/45): "
     f"2×Φ3.2 平通 @ ({SEN_HOLES[0][0]:.2f},{SEN_HOLES[0][1]:.2f})/({SEN_HOLES[1][0]:.2f},{SEN_HOLES[1][1]:.2f}) + "
     f"底面 Φ{SEN_CB_D:g}×{SEN_CB_T:g} 头窝 (M3×12 先装后压屏, 螺母锁 PCB 上); "
     f"排针尾避空槽 {SEN_SLOT_L:g}×{SEN_SLOT_W:g} 斜置随转 (中心 ({SEN_SLOT_C[0]:.2f},{SEN_SLOT_C[1]:.2f}), 穿透); 对射管焊脚落条外悬空",
     size=TXT_I,anchor="middle")
text(PAGE_W/2,31,"光轴 (对射连线) 过圆心 — 叉臂扫掠为同心环, 挡光片净通道 r36.78..46.66, 刀片 r40.2..43.2 双侧余量 ~3.4 / "
     "配套: M6×20 平头 + Φ8×30 单头内丝螺柱 + M3×12×4 / 平躺打印零支撑 (GB 1st-angle, 主视 2:1, mm)",
     size=TXT_I,anchor="middle")

S = 2.0
def zr(z): return z - BAR_Z0
_th = math.radians(SEN_TH)
_d = (math.sin(_th), -math.cos(_th))       # 孔线方向
_n = (math.cos(_th),  math.sin(_th))       # 光轴偏距方向
# ===== 俯视图 (2:1, 长边横放: 图X=件Y, 图Y=件X) =====
TX, TYC = 210.0, 90.0
def pv(x,y): return (TX+y*S, TYC-x*S)
text(TX,44.0,"俯视图 (2:1) — 长边横放",size=TXT_L,anchor="middle")
rect(*pv(BLK_X,-BLK_Y),*pv(-BLK_X,BLK_Y))
for sy in SCREW_YS:                                   # v3.1: 3×2 离散屏孔
    for sx in SCREW_XS:
        cx,cy = pv(sx,sy); pdf.circle(cx,cy,SCREW_D/2*S,style="D"); cross(cx,cy)
if CW_ENABLE:                                         # 配重孔一排
    for cy2 in CW_YS:
        cx,cy = pv(CW_X,cy2); pdf.circle(cx,cy,CW_D/2*S,style="D"); cross(cx,cy)
# 斜置排针尾槽 (旋转矩形)
_hl, _hw = SEN_SLOT_L/2, SEN_SLOT_W/2
_sa = math.radians(SEN_SLOT_ANG)
_ld = (math.cos(_sa), math.sin(_sa)); _lw = (-math.sin(_sa), math.cos(_sa))
corners = [(SEN_SLOT_C[0]+sx*_hl*_ld[0]+sw*_hw*_lw[0], SEN_SLOT_C[1]+sx*_hl*_ld[1]+sw*_hw*_lw[1])
           for (sx,sw) in ((1,1),(-1,1),(-1,-1),(1,-1))]
dp = [pv(x,y) for (x,y) in corners]
_w(GEOM_W)
for i in range(4):
    a=dp[i]; b=dp[(i+1)%4]; pdf.line(a[0],a[1],b[0],b[1])
# 光电孔 + Φ7.5 底头窝 (隐藏)
for (sx,sy) in SEN_HOLES:
    cx2,cy2 = pv(sx,sy)
    pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
    pdf.circle(cx2,cy2,SEN_CB_D/2*S,style="D")
    pdf.set_dash_pattern(); _w(GEOM_W)
    pdf.circle(cx2,cy2,3.2/2*S,style="D"); cross(cx2,cy2)
# 孔线中心线 (斜点划) + 光轴线 (过圆心, 点划)
pdf.set_dash_pattern(dash=1.2,gap=0.6); _w(0.13)
p1 = pv(SEN_HOLES[0][0]+10*_d[0], SEN_HOLES[0][1]+10*_d[1])
p2 = pv(SEN_HOLES[1][0]-10*_d[0], SEN_HOLES[1][1]-10*_d[1])
pdf.line(p1[0],p1[1],p2[0],p2[1])
_B = (SEN_M[0]+17*_n[0], SEN_M[1]+17*_n[1])
q1 = pv(0.0, 0.0); q2 = pv(_B[0]+8*_d[0], _B[1]+8*_d[1])
pdf.line(q1[0],q1[1],q2[0],q2[1])
pdf.set_dash_pattern(); _w(GEOM_W)
cx,cy = pv(0.0,0.0)
pdf.circle(cx,cy,AXIS_BORE/2*S,style="D")
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
pdf.circle(cx,cy,HEAD_D/2*S,style="D")
pdf.set_dash_pattern(); _w(GEOM_W); cross(cx,cy,6.5)

# --- 尺寸 ---
xL,  xR  = pv(0,-BLK_Y)[0],  pv(0,BLK_Y)[0]
ybar = pv(-BLK_X,0)[1]
hdim(pv(0,SCREW_YS[1])[0],pv(0,SCREW_YS[0])[0],TYC,ybar+34,f"{SCREW_YS[0]-SCREW_YS[1]:g} (孔距)")
hdim(xL,xR,ybar,ybar+23,f"{2*BLK_Y:g}")
hdim(pv(0,SEN_M[1])[0],pv(0,0)[0],TYC,ybar+12,f"{-SEN_M[1]:g} (M 距轴心)")
vdim(pv(BLK_X,0)[1],pv(-BLK_X,0)[1],xL,xL-DIM_O1,f"{2*BLK_X:g}")
# --- 引注 ---
note(*pv(*SEN_HOLES[0]),126,150,
     f"2×Φ3.2 平通 @ ({SEN_HOLES[0][0]:.2f},{SEN_HOLES[0][1]:.2f})/({SEN_HOLES[1][0]:.2f},{SEN_HOLES[1][1]:.2f}), "
     f"孔距 14, 绕 M({SEN_M[0]:g},{SEN_M[1]:g}) 转 {SEN_TH:.4f}°",anchor="end")
note(*pv(SEN_HOLES[1][0],SEN_HOLES[1][1]),120,50,
     f"底面 Φ{SEN_CB_D:g}×{SEN_CB_T:g} 头窝 ×2 (隐藏; M3×12 自下, 螺母锁 PCB 上)",anchor="end")
note(*pv(SEN_SLOT_C[0]-1.0,SEN_SLOT_C[1]),88,160,
     f"排针尾避空槽 {SEN_SLOT_L:g}×{SEN_SLOT_W:g} 斜置 (中心 ({SEN_SLOT_C[0]:.2f},{SEN_SLOT_C[1]:.2f}), 长轴沿孔线, 穿透)",anchor="end")
note(*pv(_B[0],_B[1]),160,58,
     f"光轴 (点划): 平行孔线偏 17, **过圆心**; 挡光片半径带 42.20..45.18",anchor="start")
note(*pv(0,SCREW_YS[0]),300,60,
     f"2×Φ{SCREW_D:g} 通 @ (0,±64), 盘头 M3×12 锁屏顶",anchor="start")
note(*pv(1.5,1.5),245,64,
     f"轴 Φ{AXIS_BORE:g} 通 + Φ{HEAD_D:g}×{HEAD_T:g} 底面头窝 (隐藏)",anchor="start")

# ===== 正视图 (件 Y-Z, 2:1) =====
EX, EYB = 210.0, 224.0
def ev(y,z): return (EX+y*S, EYB-zr(z)*S)
text(EX,196.0,"正视图 (2:1)",size=TXT_L,anchor="middle")
rect(*ev(-BLK_Y,BAR_Z1),*ev(BLK_Y,BAR_Z0))
drect(*ev(-AXIS_BORE/2,BAR_Z1),*ev(AXIS_BORE/2,BAR_Z0))
drect(*ev(-HEAD_D/2,BAR_Z0+HEAD_T),*ev(HEAD_D/2,BAR_Z0))
for sy in SCREW_YS:
    drect(*ev(sy-SCREW_D/2,BAR_Z1),*ev(sy+SCREW_D/2,BAR_Z0))
# 斜槽件Y向投影半宽: L/2·|dy| + W/2·|wy|
_hy = SEN_SLOT_L/2*abs(_ld[1]) + SEN_SLOT_W/2*abs(_lw[1])
drect(*ev(SEN_SLOT_C[1]-_hy,BAR_Z1),*ev(SEN_SLOT_C[1]+_hy,BAR_Z0))
for (sx,sy) in SEN_HOLES:
    drect(*ev(sy-1.6,BAR_Z1),*ev(sy+1.6,BAR_Z0))
hdim(ev(-HEAD_D/2,BAR_Z0)[0],ev(HEAD_D/2,BAR_Z0)[0],EYB,EYB+DIM_O1,f"Φ{HEAD_D:g} 头窝")
xr2 = ev(BLK_Y,BAR_Z0)[0]
vdim(ev(0,BAR_Z0+HEAD_T)[1],EYB,xr2,xr2+DIM_O2,f"{HEAD_T:g} (头窝深)")
vdim(ev(0,BAR_Z1)[1],EYB,xr2,xr2+DIM_O1,f"{H:g}")

# ===== 侧视图 (件 X-Z, 2:1) =====
SX2, SYB2 = 52.0, 224.0
def sv2(x,z): return (SX2+x*S, SYB2-zr(z)*S)
text(SX2,196.0,"侧视图 (2:1)",size=TXT_L,anchor="middle")
rect(*sv2(-BLK_X,BAR_Z1),*sv2(BLK_X,BAR_Z0))
drect(*sv2(-AXIS_BORE/2,BAR_Z1),*sv2(AXIS_BORE/2,BAR_Z0))
drect(*sv2(-HEAD_D/2,BAR_Z0+HEAD_T),*sv2(HEAD_D/2,BAR_Z0))
hdim(sv2(-BLK_X,BAR_Z0)[0],sv2(BLK_X,BAR_Z0)[0],SYB2,SYB2+DIM_O1,f"{2*BLK_X:g}")

tb_y=PAGE_H-28; tb_x,tb_w,tb_h=20,PAGE_W-40,18
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+6,"POV 3D v3 结构件 — top_cap_v3_1_1 薄压条 (光电斜置, 底面 = 屏顶压面 260.95)",size=TXT_L)
text(tb_x+tb_w-4,tb_y+6,"投影 1st-angle / 比例 2:1",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+14.5,f"{2*BLK_X:g}×{2*BLK_Y:g}×{H:g} / 轴 Φ{AXIS_BORE:g}+Φ{HEAD_D:g}×{HEAD_T:g} 底头窝 / 2×Φ{SCREW_D:g}@±64 / "
     f"光电 2×Φ3.2 绕 M({SEN_M[0]:g},{SEN_M[1]:g}) 转 {SEN_TH:.4f}° + Φ{SEN_CB_D:g} 头窝 / BOM: M6×20 平头 + Φ8×30 螺柱 + M3×12×4 / 平躺打印 / 单位 mm",size=TXT_I)
text(tb_x+tb_w-4,tb_y+14.5,"2026-07-24  /  POV3D / v3 / top_cap_v3_1_1 / top_cap_v3_1_1.stl",size=TXT_I,anchor="end")

out = Path(__file__).with_name("top_cap_v3_1_1_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt = Path(__file__).with_name("top_cap_v3_1_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
