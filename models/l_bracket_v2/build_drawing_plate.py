"""
A3 drawing — screen_plate 屏幕板 (v2 支架之一)。GB first-angle。
主视 1:2 + 侧视 1:2。全部特征均为平面直通孔 → 无详图。
2026-07-03 深夜: 屏底沿抬到盘面+50, 板底中央开 120宽×到盘面+50 让位缺口
(中间 12cm 对盘面保 5cm 净空), 两侧翼板下伸连塔柱。
图纸基准 = 翼板底边 (装配时 = 盘顶 +21)。
"""
import math, os
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (板底边 = 0) =====
FIN_T, FIN_HW = 6.0, 78.0   # 宽 162→156 (让位筋墙)
PLATE_H = 192.5                       # 213.5-21
M3 = 3.2
SCREEN_HOLES = [(-52.5, 39.5), (52.5, 39.5), (-49.975, 186.5), (49.975, 186.5)]
PITCH_BOT, PITCH_TOP, VSPAN = 105.0, 99.95, 147.0
WIN_HW, WZ0, WZ1 = 27.0, 72.0, 106.0  # 93-21 / 127-21, 顶 R27 拱
NOTCH_HW, NOTCH_H = 60.0, 29.0        # 底部中央缺口 (顶=盘面+50)
JY, JZ = 71.0, [7.0, 35.0, 63.0]      # 连接孔 (28/56/84 − 21)
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
def hatch_rect(x0,y0,x1,y1,spacing=2.0):
    _w(0.13); xmin,xmax=min(x0,x1),max(x0,x1); ymin,ymax=min(y0,y1),max(y0,y1)
    c=xmin-(ymax-ymin)
    while c<=xmax:
        xa,ya=max(xmin,c),min(ymax,ymin+(max(xmin,c)-c))
        xb,yb=min(xmax,c+(ymax-ymin)),max(ymin,ymin+(min(xmax,c+(ymax-ymin))-c))
        p1=(max(xmin,c),ymin+max(0,xmin-c)); p2=(min(xmax,c+ymax-ymin),ymin+min(ymax-ymin,xmax-c))
        if p1[0]<=p2[0]: pdf.line(p1[0],p1[1],p2[0],p2[1])
        c+=spacing
    _w(GEOM_W)

# ===== header =====
_w(0.3); pdf.rect(5,5,PAGE_W-10,PAGE_H-10,style="D")
text(PAGE_W/2,15,"POV 3D v2 — screen_plate 屏幕板 (支架三件之一, 配 gantry_base A/B)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,
     f"平板 {2*FIN_HW:g}×{PLATE_H:g}×{FIN_T:g}, 平躺打印(前面朝下) / 4×Φ{M3:g} 屏幕孔 (梯形阵 {PITCH_BOT:g}/{PITCH_TOP:g}×{VSPAN:g}) / "
     f"6×连接孔 Φ{M3:g} 直通无沉头 (M3×18/20 贯通板+塔) / 接口窗 {2*WIN_HW:g}×{WZ1-WZ0:g}+顶R{WIN_HW:g}拱 / "
     f"底部中央缺口 {2*NOTCH_HW:g}×{NOTCH_H:g} (顶=盘面+50) / 基准=翼板底边(装配=盘顶+21)  (GB 1st-angle, 1:2, mm)",
     size=TXT_I,anchor="middle")

# ===================== 主视图 (前面, Y→右, 高→上) =====================
FV_CX, FV_Y0 = 105.0, 195.0
def fv(y,z): return (FV_CX+y*S, FV_Y0-z*S)
text(FV_CX,88,"主视图 (前面/贴屏面, 1:2)",size=TXT_L,anchor="middle")
pl([fv(-FIN_HW,0),fv(-NOTCH_HW,0),fv(-NOTCH_HW,NOTCH_H),fv(NOTCH_HW,NOTCH_H),fv(NOTCH_HW,0),
    fv(FIN_HW,0),fv(FIN_HW,PLATE_H),fv(-FIN_HW,PLATE_H),fv(-FIN_HW,0)])
warch=[(WIN_HW*math.cos(math.radians(a)), WZ1+WIN_HW*math.sin(math.radians(a))) for a in range(0,181,6)]
pl([fv(*p) for p in ([(WIN_HW,WZ0)]+warch+[(-WIN_HW,WZ0),(WIN_HW,WZ0)])])
pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.18)
pdf.line(*fv(0,-6),*fv(0,PLATE_H+6)); pdf.set_dash_pattern(); _w(GEOM_W)
for (hy,hz) in SCREEN_HOLES:
    cx,cy=fv(hy,hz); pdf.circle(cx,cy,M3/2*S,style="D"); cross(cx,cy,3.5)
for z in JZ:
    for sy in (1,-1):
        cx,cy=fv(sy*JY,z); pdf.circle(cx,cy,M3/2*S,style="D"); cross(cx,cy,3.5)
# dims
hdim(fv(-FIN_HW,0)[0],fv(FIN_HW,0)[0],fv(0,0)[1],fv(0,0)[1]+DIM_O2,f"{2*FIN_HW:g}")
hdim(fv(-PITCH_BOT/2,0)[0],fv(PITCH_BOT/2,0)[0],fv(0,SCREEN_HOLES[0][1])[1],fv(0,0)[1]+DIM_O1,f"{PITCH_BOT:g}")
hdim(fv(-PITCH_TOP/2,0)[0],fv(PITCH_TOP/2,0)[0],fv(0,SCREEN_HOLES[2][1])[1],97.0,f"{PITCH_TOP:g}")
hdim(fv(-JY,0)[0],fv(JY,0)[0],fv(0,JZ[0])[1],fv(0,0)[1]+DIM_O3,f"{2*JY:g}")
vdim(fv(0,PLATE_H)[1],fv(0,0)[1],fv(-FIN_HW,0)[0],fv(-FIN_HW,0)[0]-DIM_O2,f"{PLATE_H:g}")
vdim(fv(0,SCREEN_HOLES[0][1])[1],fv(0,0)[1],fv(-FIN_HW,0)[0],fv(-FIN_HW,0)[0]-DIM_O1,f"{SCREEN_HOLES[0][1]:g}")
vdim(fv(0,SCREEN_HOLES[2][1])[1],fv(0,SCREEN_HOLES[0][1])[1],fv(FIN_HW,0)[0],fv(FIN_HW,0)[0]+DIM_O1,f"{VSPAN:g}")
vdim(fv(0,JZ[0])[1],fv(0,0)[1],fv(FIN_HW,0)[0],fv(FIN_HW,0)[0]+DIM_O2,f"{JZ[0]:g}")
vdim(fv(0,JZ[2])[1],fv(0,JZ[0])[1],fv(FIN_HW,0)[0],fv(FIN_HW,0)[0]+DIM_O3,"56 (2×28)")
hdim(fv(-WIN_HW,0)[0],fv(WIN_HW,0)[0],fv(0,WZ0)[1],fv(0,WZ0)[1]+5.5,f"{2*WIN_HW:g}")
hdim(fv(-NOTCH_HW,0)[0],fv(NOTCH_HW,0)[0],fv(0,NOTCH_H)[1],fv(0,NOTCH_H)[1]-7.0,f"{2*NOTCH_HW:g}")
vdim(fv(0,NOTCH_H)[1],fv(0,0)[1],fv(-NOTCH_HW,0)[0],fv(-NOTCH_HW,0)[0]+DIM_O1,f"{NOTCH_H:g}")
text(fv(0,14)[0],fv(0,14)[1],"缺口顶 = 盘面+50 (= 屏幕底沿)",size=TXT_I,anchor="middle",halo=True)
note(*fv(-WIN_HW*0.7071,WZ1+WIN_HW*0.7071),fv(-FIN_HW,0)[0]-8,fv(0,150)[1],
     f"接口窗 {2*WIN_HW:g}×{WZ1-WZ0:g}+顶R{WIN_HW:g}拱 (窗底 {WZ0:g})",anchor="end")
note(*fv(PITCH_TOP/2,SCREEN_HOLES[2][1]),fv(FIN_HW,0)[0]+10,fv(0,PLATE_H-14)[1],f"4×Φ{M3:g} (M3→屏幕螺母)")
note(*fv(-JY,JZ[2]),fv(-FIN_HW,0)[0]-8,fv(0,132.0)[1],f"6× Φ{M3:g} 直通 (M3×18/20+塔背螺母)",anchor="end")

# ===================== 侧视图 (X→右) =====================
SV_CX = 208.0
def sv(x,z): return (SV_CX+(x+10.27)*S, FV_Y0-z*S)
text(SV_CX,88,"侧视图 (1:2)",size=TXT_L,anchor="middle")
pl([sv(-13.27,0),sv(-13.27,PLATE_H),sv(-7.27,PLATE_H),sv(-7.27,0),sv(-13.27,0)])
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
for z in JZ+[h[1] for h in SCREEN_HOLES[::2]]:
    pdf.line(*sv(-13.27,z),*sv(-7.27,z))
pdf.set_dash_pattern(); _w(GEOM_W)
hdim(sv(-13.27,0)[0],sv(-7.27,0)[0],sv(-10,PLATE_H)[1],97.0,f"{FIN_T:g}")
text(sv(-10,0)[0],fv(0,0)[1]+DIM_O1,"前面→",size=TXT_I,anchor="middle")

# ===================== 连接说明 (2026-07-03: 沉头取消, 全部直通) =====================
NX = 315.0
text(NX,88,"连接方式说明",size=TXT_L,anchor="middle")
text(NX,100,"6× 连接孔 Φ3.2 普通直通孔 (无沉头):",size=TXT_D,anchor="middle")
text(NX,108,"M3×18/20 从板前面穿过 板(6)+塔柱(10),",size=TXT_D,anchor="middle")
text(NX,116,"gantry_base 塔背面套垫片 + M3 螺母锁死。",size=TXT_D,anchor="middle")
text(NX,126,"注: 螺丝头凸出板前面 ~2mm;",size=TXT_I,anchor="middle")
text(NX,132,"屏幕背面由其自带螺母垫起, 不与螺丝头干涉。",size=TXT_I,anchor="middle")

# ===== Title block =====
tb_y=PAGE_H-28; tb_x,tb_w,tb_h=20,PAGE_W-40,18
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+6,"POV 3D v2 结构件 — screen_plate 屏幕板 (支架三件之一)",size=TXT_L,anchor="start")
text(tb_x+tb_w-4,tb_y+6,"投影 1st-angle / 比例 1:2 / 全部 Φ3.2 平面直通孔",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+14.5,
     f"板 {2*FIN_HW:g}×{PLATE_H:g}×{FIN_T:g} / 屏孔 {PITCH_BOT:g}/{PITCH_TOP:g}×{VSPAN:g} @高{SCREEN_HOLES[0][1]:g} / "
     f"连接孔 ±{JY:g}×高{{7,35,63}} Φ{M3:g} 直通 / 窗±{WIN_HW:g}×{WZ0:g}..{WZ1:g}+R{WIN_HW:g}拱 / 底缺口{2*NOTCH_HW:g}×{NOTCH_H:g} / 平躺打印 / mm",
     size=TXT_I,anchor="start")
text(tb_x+tb_w-4,tb_y+14.5,"2026-07-03  /  POV3D / models / l_bracket_v2 / screen_plate.stl",size=TXT_I,anchor="end")

out=Path(__file__).with_name("screen_plate_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt=Path(__file__).with_name("screen_plate_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
