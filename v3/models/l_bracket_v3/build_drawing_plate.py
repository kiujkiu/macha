"""
A3 drawing — screen_plate_v3 中央屏幕板 (v3 双面屏支架两件套之一)。GB first-angle。
主视 1:2 + 侧视 1:2。全部特征均为平面直通孔 → 无详图。平躺打印。
2026-07-10: v2 单面板加宽 (156→176, ±88) + 顶部中央凸舌 (±40, 伸到 Z235 给
top_cap_v3 双腿夹持); 板厚 6 居中到轴平面 (X -3..+3), 两面各贴一块屏。
屏幕孔/接口窗均为两侧屏共用 (对头短螺丝 / 两屏接口相向伸入同一窗)。
图纸基准 = 翼板底边 (盘坐标 Z21 = 盘顶 +21); 括注内 Z 值为盘坐标。
"""
import math, os
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (板底边 = 0; 盘坐标 Z = 局部 + 21) =====
FIN_T, FIN_HW = 6.0, 88.0             # 厚 6 (X -3..+3 居中) / 宽 176 (塔柱外移)
PLATE_H = 214.0                       # 235-21 (含顶舌)
BODY_H  = 192.5                       # 213.5-21 (主体)
TAB_HW, TAB_H = 40.0, 21.5            # 顶部中央凸舌 ±40 × Z 213.5..235
M3 = 3.2
SCREEN_HOLES = [(-52.5, 39.5), (52.5, 39.5), (-49.975, 186.5), (49.975, 186.5)]
PITCH_BOT, PITCH_TOP, VSPAN = 105.0, 99.95, 147.0
WIN_HW, WZ0, WZ1 = 27.0, 72.0, 106.0  # 93-21 / 127-21, 顶 R27 拱 (圆心盘 Z127)
NOTCH_HW, NOTCH_H = 60.0, 29.0        # 底部中央缺口 ±60 (顶 = 盘面+50)
JY, JZ = 82.0, [7.0, 35.0, 63.0]      # 连接孔 (盘 Z 28/56/84 − 21)
CAP_Y, CAP_Z = 22.0, [204.3, 209.8]   # 顶帽夹舌孔 (盘 Z 225.3/230.8 − 21)
S = 0.5

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

# ===== header =====
_w(0.3); pdf.rect(5,5,PAGE_W-10,PAGE_H-10,style="D")
text(PAGE_W/2,15,"POV 3D v3 — screen_plate_v3 中央屏幕板 (双面屏, 支架两件套之一, 配 gantry_v3 + top_cap_v3)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,
     f"平板 {2*FIN_HW:g}×{PLATE_H:g}×{FIN_T:g} 居中轴平面 (X -3..+3), 平躺打印 / 顶舌 {2*TAB_HW:g}×{TAB_H:g} (盘 Z 213.5..235) / "
     f"4×Φ{M3:g} 屏幕孔两侧屏共用 (对头短螺丝) / 6×连接孔 + 4×夹舌孔 Φ{M3:g} 直通无沉头 / 接口窗 {2*WIN_HW:g}×{WZ1-WZ0:g}+顶R{WIN_HW:g}拱 两屏共用 / "
     f"底部中央缺口 {2*NOTCH_HW:g}×{NOTCH_H:g} / 基准=翼板底边(盘 Z21)  (GB 1st-angle, 1:2, mm)",
     size=TXT_I,anchor="middle")

# ===================== 主视图 (YZ 正视, Y→右, Z→上) =====================
FV_CX, FV_Y0 = 105.0, 200.0
def fv(y,z): return (FV_CX+y*S, FV_Y0-z*S)
text(FV_CX,57,"主视图 (YZ 正视, 1:2)",size=TXT_L,anchor="middle")
# 外轮廓: 底(含缺口)→右翼→右肩→舌→左肩→左翼
pl([fv(-FIN_HW,0),fv(-NOTCH_HW,0),fv(-NOTCH_HW,NOTCH_H),fv(NOTCH_HW,NOTCH_H),fv(NOTCH_HW,0),
    fv(FIN_HW,0),fv(FIN_HW,BODY_H),fv(TAB_HW,BODY_H),fv(TAB_HW,PLATE_H),
    fv(-TAB_HW,PLATE_H),fv(-TAB_HW,BODY_H),fv(-FIN_HW,BODY_H),fv(-FIN_HW,0)])
warch=[(WIN_HW*math.cos(math.radians(a)), WZ1+WIN_HW*math.sin(math.radians(a))) for a in range(0,181,6)]
pl([fv(*p) for p in ([(WIN_HW,WZ0)]+warch+[(-WIN_HW,WZ0),(WIN_HW,WZ0)])])
pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.18)
pdf.line(*fv(0,-6),*fv(0,PLATE_H+6)); pdf.set_dash_pattern(); _w(GEOM_W)
for (hy,hz) in SCREEN_HOLES:
    cx,cy=fv(hy,hz); pdf.circle(cx,cy,M3/2*S,style="D"); cross(cx,cy,3.5)
for z in JZ:
    for sy in (1,-1):
        cx,cy=fv(sy*JY,z); pdf.circle(cx,cy,M3/2*S,style="D"); cross(cx,cy,3.5)
for z in CAP_Z:
    for sy in (1,-1):
        cx,cy=fv(sy*CAP_Y,z); pdf.circle(cx,cy,M3/2*S,style="D"); cross(cx,cy,2.2)
# --- 底部横向尺寸 ---
hdim(fv(-PITCH_BOT/2,0)[0],fv(PITCH_BOT/2,0)[0],fv(0,SCREEN_HOLES[0][1])[1],fv(0,0)[1]+DIM_O1,f"{PITCH_BOT:g}")
hdim(fv(-FIN_HW,0)[0],fv(FIN_HW,0)[0],fv(0,0)[1],fv(0,0)[1]+DIM_O2,f"{2*FIN_HW:g}")
hdim(fv(-JY,0)[0],fv(JY,0)[0],fv(0,JZ[0])[1],fv(0,0)[1]+DIM_O3,f"{2*JY:g}")
# --- 顶部横向尺寸 (夹舌孔距 / 舌宽 / 屏孔上排距) ---
hdim(fv(-CAP_Y,0)[0],fv(CAP_Y,0)[0],fv(0,CAP_Z[1])[1],86.0,f"{2*CAP_Y:g}")
hdim(fv(-TAB_HW,0)[0],fv(TAB_HW,0)[0],fv(0,PLATE_H)[1],77.0,f"{2*TAB_HW:g}")
hdim(fv(-PITCH_TOP/2,0)[0],fv(PITCH_TOP/2,0)[0],fv(0,SCREEN_HOLES[2][1])[1],68.0,f"{PITCH_TOP:g}")
# --- 左侧竖向尺寸 ---
vdim(fv(0,SCREEN_HOLES[0][1])[1],fv(0,0)[1],fv(-FIN_HW,0)[0],fv(-FIN_HW,0)[0]-DIM_O1,f"{SCREEN_HOLES[0][1]:g}")
vdim(fv(0,BODY_H)[1],fv(0,0)[1],fv(-FIN_HW,0)[0],fv(-FIN_HW,0)[0]-DIM_O2,f"{BODY_H:g}")
vdim(fv(0,PLATE_H)[1],fv(0,0)[1],fv(-FIN_HW,0)[0],fv(-FIN_HW,0)[0]-DIM_O3,f"{PLATE_H:g}")
line(fv(-TAB_HW,PLATE_H)[0]-1.0,fv(0,PLATE_H)[1],fv(-FIN_HW,0)[0]-EXT_GP,fv(0,PLATE_H)[1],EXT_W_)  # 214 顶端延长线接舌角
# --- 右侧竖向尺寸 ---
vdim(fv(0,SCREEN_HOLES[2][1])[1],fv(0,SCREEN_HOLES[0][1])[1],fv(FIN_HW,0)[0],fv(FIN_HW,0)[0]+DIM_O1,f"{VSPAN:g}")
vdim(fv(0,JZ[0])[1],fv(0,0)[1],fv(FIN_HW,0)[0],fv(FIN_HW,0)[0]+DIM_O2,f"{JZ[0]:g}")
vdim(fv(0,JZ[2])[1],fv(0,JZ[0])[1],fv(FIN_HW,0)[0],fv(FIN_HW,0)[0]+DIM_O3,"56 (2×28)")
# --- 顶舌竖向 (右肩侧); 夹舌孔行距 5.5 见注释坐标 ---
vdim(fv(0,PLATE_H)[1],fv(0,BODY_H)[1],fv(TAB_HW,0)[0],fv(TAB_HW,0)[0]+16.0,f"{TAB_H:g}")
# --- 窗 / 缺口 ---
hdim(fv(-WIN_HW,0)[0],fv(WIN_HW,0)[0],fv(0,WZ0)[1],fv(0,WZ0)[1]+5.5,f"{2*WIN_HW:g}")
hdim(fv(-NOTCH_HW,0)[0],fv(NOTCH_HW,0)[0],fv(0,NOTCH_H)[1],fv(0,NOTCH_H)[1]-7.0,f"{2*NOTCH_HW:g}")
vdim(fv(0,NOTCH_H)[1],fv(0,0)[1],fv(-NOTCH_HW,0)[0],fv(-NOTCH_HW,0)[0]+DIM_O1,f"{NOTCH_H:g}")
text(fv(0,10)[0],fv(0,10)[1],"缺口顶 = 盘 Z50 (盘面+50 = 屏底沿)",size=TXT_I,anchor="middle",halo=True)
# --- 注释 (括注为盘坐标 Z) ---
note(*fv(-WIN_HW*0.7071,WZ1+WIN_HW*0.7071),fv(-FIN_HW,0)[0]-6,fv(0,150)[1],
     f"接口窗 {2*WIN_HW:g}×{WZ1-WZ0:g}+顶R{WIN_HW:g}拱 (盘 Z 93..127) 两屏共用",anchor="end")
note(*fv(-PITCH_TOP/2,SCREEN_HOLES[2][1]),fv(-FIN_HW,0)[0]-6,fv(0,176)[1],
     f"4×Φ{M3:g} 屏幕孔 两侧屏共用 (盘 Z 60.5 / 207.5)",anchor="end")
note(*fv(-JY,JZ[2]),fv(-FIN_HW,0)[0]-6,fv(0,120)[1],
     f"6×Φ{M3:g} 直通 (±{JY:g}, 盘 Z 28/56/84)",anchor="end")
note(*fv(-CAP_Y,CAP_Z[1]),fv(-FIN_HW,0)[0]-6,88.0,
     f"4×Φ{M3:g} 夹舌孔 (±{CAP_Y:g}, 盘 Z 225.3/230.8)",anchor="end")

# ===================== 侧视图 (X→右, 厚度 6 居中) =====================
SV_CX = 213.0
def sv(x,z): return (SV_CX+x*S, FV_Y0-z*S)
text(SV_CX,57,"侧视图 (1:2)",size=TXT_L,anchor="middle")
pl([sv(-3,0),sv(-3,PLATE_H),sv(3,PLATE_H),sv(3,0),sv(-3,0)])
line(*sv(-3,BODY_H),*sv(3,BODY_H),GEOM_W)                       # 肩线 (舌根 213.5)
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
for z in JZ+[h[1] for h in SCREEN_HOLES[::2]]+CAP_Z:
    pdf.line(*sv(-3,z),*sv(3,z))
pdf.set_dash_pattern(); _w(GEOM_W)
hdim(sv(-3,0)[0],sv(3,0)[0],sv(0,PLATE_H)[1],85.0,f"{FIN_T:g}")
text(SV_CX,fv(0,0)[1]+DIM_O1,"板厚居中: X -3..+3 (轴平面)",size=TXT_I,anchor="middle")
rot_text(SV_CX-7.0,150.0,"-X 前屏面",90,size=TXT_I)
rot_text(SV_CX+8.5,150.0,"+X 后屏面",90,size=TXT_I)

# ===================== 双面屏共用说明 =====================
NX = 330.0
text(NX,57,"双面屏共用说明",size=TXT_L,anchor="middle")
text(NX,70,"1. 板两面各贴一块屏 (前屏 X-3 面, 后屏 X+3 面),",size=TXT_D,anchor="middle")
text(NX,77,"   4×Φ3.2 屏幕孔两侧屏共用: 每孔两颗 M3 对头",size=TXT_D,anchor="middle")
text(NX,84,"   拧入各自屏幕自带螺母, 螺杆入板各 ≤2.5 (合计<6)",size=TXT_D,anchor="middle")
text(NX,91,"   互不相碰 → 按屏螺母高度选短螺丝 (M3×6/8)。",size=TXT_D,anchor="middle")
text(NX,101,"2. 接口窗两屏共用: 两屏接口相向伸入同一窗;",size=TXT_D,anchor="middle")
text(NX,108,"   若实测凸出 >3, 两侧加尼龙垫柱增大屏-板间隙。",size=TXT_D,anchor="middle")
text(NX,118,"3. 顶舌由 top_cap_v3 双腿夹持: 4×M3×18 贯通",size=TXT_D,anchor="middle")
text(NX,125,"   腿(4)+板(6)+腿(4) 锁死 (孔位 ±22, 盘 Z 225.3/230.8)。",size=TXT_D,anchor="middle")
text(NX,135,"4. 6×连接孔: M3×18/20 贯通 板(6)+塔柱, 塔背",size=TXT_D,anchor="middle")
text(NX,142,"   垫片+螺母锁死 (gantry_v3 塔柱中心 ±82)。",size=TXT_D,anchor="middle")
text(NX,152,"5. 全部 Φ3.2 普通直通孔, 无沉头/嵌件; 平躺打印",size=TXT_D,anchor="middle")
text(NX,159,"   (任一面朝下), 竖直通孔免支撑。",size=TXT_D,anchor="middle")

# ===== Title block =====
tb_y=PAGE_H-28; tb_x,tb_w,tb_h=20,PAGE_W-40,18
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+6,"POV 3D v3 结构件 — screen_plate_v3 中央屏幕板 (双面屏: 屏幕孔/接口窗两侧屏共用, 对头短螺丝)",size=TXT_L,anchor="start")
text(tb_x+tb_w-4,tb_y+6,"投影 1st-angle / 比例 1:2 / 全部 Φ3.2 平面直通孔",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+14.5,
     f"板 {2*FIN_HW:g}×{PLATE_H:g}×{FIN_T:g} (盘 Z 21..235, X -3..+3) / 顶舌 ±{TAB_HW:g}×盘 Z 213.5..235 / "
     f"屏孔 (±52.5, 盘 Z60.5)+(±49.975, 盘 Z207.5) / 连接孔 (±{JY:g}, 盘 Z{{28,56,84}}) / 夹舌孔 (±{CAP_Y:g}, 盘 Z{{225.3,230.8}}) / "
     f"窗 ±{WIN_HW:g}×盘 Z 93..127+R{WIN_HW:g}拱 / 底缺口 ±{NOTCH_HW:g}×至盘 Z50 / mm",
     size=TXT_I,anchor="start")
text(tb_x+tb_w-4,tb_y+14.5,"2026-07-10  /  POV3D / v3 / models / l_bracket_v3 / screen_plate_v3.stl",size=TXT_I,anchor="end")

out=Path(__file__).with_name("screen_plate_v3_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt=Path(__file__).with_name("screen_plate_v3_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
