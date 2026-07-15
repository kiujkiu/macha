"""
A3 drawing — gantry_v3 门形底座 (v3 双面屏支架两件套之二)。GB first-angle。
**同一件打印 2 次**, 装配对角放 (件2 绕 Z 转 180°), 不再是镜像左右手件。
全部特征均为平面通孔 (贯通螺丝+螺母连接) → 无详图。
基准 = 脚底面 (= 盘顶面)。侧视/正视 1:1, 俯视 (装配位) 1:2。
"""
import math, os
from pathlib import Path
from fpdf import FPDF

# ===== Geometry (与 build_gantry.py 一致) =====
PLATE_HT = 3.0
FIN_X0 = -PLATE_HT                    # -3 塔前面 (= screen_plate_v3 板面)
M3 = 3.2
FOOT_T, FOOT_HX, FOOT_Y0, FOOT_Y1 = 4.0, 36.0, 63.5, 93.0   # 外缘随筋墙外移
DISC_R, RIM_R = 85.0, 77.5
HXF = RIM_R * math.cos(math.radians(67.5))    # 29.658
HYF = RIM_R * math.sin(math.radians(67.5))    # 71.601
TWR_Y0, TWR_Y1, TWR_TOP = 76.0, 88.0, 90.0    # 塔宽 12, 中心 82
TWR_D = 10.0
TWR_XB = FIN_X0 - TWR_D               # -13 直背 (平面, 坐螺母)
WALL_T = 5.0                          # 外侧筋墙 满三角 (外面与脚外缘共面=打印底面)
WALL_PTS = [(-36.0, 4.0), (36.0, 4.0), (-3.0, 90.0), (-13.0, 90.0)]
JY, JZ = 82.0, [28.0, 56.0, 84.0]
S1, S2 = 1.0, 0.5                     # 侧视/正视 1:1, 俯视 1:2

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
text(PAGE_W/2,15,"POV 3D v3 — gantry_v3 门形底座 (支架两件之二, 配 screen_plate_v3)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,
     f"同一件打印 2 次, 对角安装 (件2 绕 Z 转 180°) / 脚 {FOOT_T:g}厚 72×29.5 借盘R{RIM_R:g}环孔 2×Φ{M3:g} / "
     f"塔柱 宽{TWR_Y1-TWR_Y0:g}×深{TWR_D:g} 直背 (前面X=-3贴板面) + 外侧筋墙{WALL_T:g}厚满三角(外面=打印底面, 侧躺零支撑) / "
     f"3×Φ{M3:g} 贯通: M3×18/20 穿 板6+塔{TWR_D:g}, 塔背垫片+螺母 (无嵌件无沉头, 全平面通孔) / "
     f"基准=脚底面(=盘顶)  (GB 1st-angle, 侧视·正视 1:1, 俯视 1:2, mm)",
     size=TXT_I,anchor="middle")

BASE = 190.0     # Z0 (脚底面) 的图纸 y

# ===================== 侧视图 (主视, X→右, Z→上, 1:1) =====================
SV_CX = 95.0
def sv(x,z): return (SV_CX+x*S1, BASE-z*S1)
text(SV_CX,72,"侧视图 (主视, 1:1)",size=TXT_L,anchor="middle")
pl([sv(-FOOT_HX,0),sv(-FOOT_HX,FOOT_T),sv(FOOT_HX,FOOT_T),sv(FOOT_HX,0),sv(-FOOT_HX,0)])       # 脚
pl([sv(TWR_XB,FOOT_T),sv(FIN_X0,FOOT_T),sv(FIN_X0,TWR_TOP),sv(TWR_XB,TWR_TOP),sv(TWR_XB,FOOT_T)])  # 塔柱
pl([sv(*p) for p in WALL_PTS] + [sv(*WALL_PTS[0])])                                             # 外侧筋墙满三角轮廓
# 2 脚孔位置 (中心线示意)
for hx in (HXF, -HXF):
    pdf.set_dash_pattern(dash=1.2,gap=0.6); _w(0.13)
    pdf.line(*sv(hx,-3),*sv(hx,10)); pdf.set_dash_pattern(); _w(GEOM_W)
# 旋转轴中心线
pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.18)
pdf.line(*sv(0,-6),*sv(0,TWR_TOP+6)); pdf.set_dash_pattern(); _w(GEOM_W)
# 3 贯通孔 (隐藏线)
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
for z in JZ:
    for dz in (-M3/2, M3/2):
        pdf.line(*sv(FIN_X0,z+dz),*sv(TWR_XB,z+dz))
pdf.set_dash_pattern(); _w(GEOM_W)
hdim(sv(-FOOT_HX,0)[0],sv(FOOT_HX,0)[0],BASE,BASE+DIM_O1,f"{2*FOOT_HX:g}")
hdim(sv(TWR_XB,0)[0],sv(FIN_X0,0)[0],sv(0,TWR_TOP)[1],sv(0,TWR_TOP)[1]-DIM_O1,f"{TWR_D:g}")
hdim(sv(TWR_XB,0)[0],sv(0,0)[0],sv(0,TWR_TOP)[1],sv(0,TWR_TOP)[1]-DIM_O2,f"{-TWR_XB:g} (背面距轴)")
vdim(sv(0,JZ[0])[1],BASE,sv(FOOT_HX,0)[0],sv(FOOT_HX,0)[0]+DIM_O1,f"{JZ[0]:g}")
vdim(sv(0,JZ[2])[1],sv(0,JZ[0])[1],sv(FOOT_HX,0)[0],sv(FOOT_HX,0)[0]+DIM_O2,"56 (2×28)")
vdim(sv(0,TWR_TOP)[1],BASE,sv(FOOT_HX,0)[0],sv(FOOT_HX,0)[0]+DIM_O3,f"{TWR_TOP:g}")
note(*sv(FIN_X0,60),sv(FIN_X0,0)[0]+8,96.0-1.2,"前面 X=-3 贴 screen_plate_v3 板面")
note(*sv(-24.5,47),50.0,110.0-1.2,f"筋墙 {WALL_T:g}厚 满三角 (外面=打印底面)",anchor="end")
note(*sv(TWR_XB,45),56.0,170.0-1.2,"直背 X=-13: 垫片+M3螺母座面",anchor="end")

# ===================== 正视图 (Y→右, Z→上, 1:1) =====================
EV_X0 = 175.0    # y=63.5 的图纸 x
def ev(y,z): return (EV_X0+(y-FOOT_Y0)*S1, BASE-z*S1)
EV_CX = ev((FOOT_Y0+FOOT_Y1)/2,0)[0]
text(EV_CX,72,"正视图 (1:1)",size=TXT_L,anchor="middle")
pl([ev(FOOT_Y0,0),ev(FOOT_Y0,FOOT_T),ev(FOOT_Y1,FOOT_T),ev(FOOT_Y1,0),ev(FOOT_Y0,0)])          # 脚
pl([ev(TWR_Y0,FOOT_T),ev(TWR_Y0,TWR_TOP),ev(TWR_Y1,TWR_TOP),ev(TWR_Y1,FOOT_T)])                # 塔柱
pl([ev(TWR_Y1,TWR_TOP),ev(FOOT_Y1,TWR_TOP),ev(FOOT_Y1,FOOT_T)])                                # 筋墙 (投影矩形)
# 3 连接孔 + 孔线 (Y=82 = 塔中心)
pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.18)
pdf.line(*ev(JY,-6),*ev(JY,TWR_TOP+2)); pdf.set_dash_pattern(); _w(GEOM_W)
for z in JZ:
    cx,cy=ev(JY,z); pdf.circle(cx,cy,M3/2*S1,style="D"); cross(cx,cy,3.0)
hdim(ev(TWR_Y0,0)[0],ev(TWR_Y1,0)[0],ev(0,TWR_TOP)[1],ev(0,TWR_TOP)[1]-DIM_O1,f"{TWR_Y1-TWR_Y0:g}")
hdim(ev(TWR_Y1,0)[0],ev(FOOT_Y1,0)[0],ev(0,TWR_TOP)[1],ev(0,TWR_TOP)[1]-DIM_O2,f"{WALL_T:g}")
hdim(ev(FOOT_Y0,0)[0],ev(FOOT_Y1,0)[0],BASE,BASE+DIM_O1,f"{FOOT_Y1-FOOT_Y0:g}")
hdim(ev(JY,0)[0],ev(FOOT_Y1,0)[0],BASE,BASE+DIM_O2,f"{FOOT_Y1-JY:g}")
vdim(ev(0,FOOT_T)[1],BASE,ev(FOOT_Y1,0)[0],ev(FOOT_Y1,0)[0]+DIM_O1,f"{FOOT_T:g}")
vdim(ev(0,JZ[2])[1],BASE,ev(FOOT_Y1,0)[0],ev(FOOT_Y1,0)[0]+DIM_O2,f"{JZ[2]:g}")
note(ev(JY,JZ[2])[0]+1.1,ev(JY,JZ[2])[1]-1.1,ev(FOOT_Y1,0)[0]+8.5,95.0-1.2,
     f"3×Φ{M3:g} 贯通 (M3×18/20+垫片+螺母)")

# ===================== 俯视图 (装配位, Y→右, X→下, 1:2) =====================
TV_CX, TV_CY = 330.0, 150.0
def tv(y,x): return (TV_CX+y*S2, TV_CY+x*S2)
text(TV_CX,72,"俯视图 (1:2, 双件装配位)",size=TXT_L,anchor="middle")
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(0.18)
pdf.circle(TV_CX,TV_CY,DISC_R*S2,style="D"); pdf.set_dash_pattern(); _w(GEOM_W)
for s in (1,-1):   # s=+1 件1 (脚+Y) / s=-1 件2 (绕Z转180°)
    pl([tv(s*FOOT_Y0,-FOOT_HX),tv(s*FOOT_Y0,FOOT_HX),tv(s*FOOT_Y1,FOOT_HX),
        tv(s*FOOT_Y1,-FOOT_HX),tv(s*FOOT_Y0,-FOOT_HX)])                          # 脚
    pl([tv(s*TWR_Y1,-FOOT_HX),tv(s*TWR_Y1,FOOT_HX)])                             # 筋墙内缘
    pl([tv(s*TWR_Y0,s*FIN_X0),tv(s*TWR_Y1,s*FIN_X0),tv(s*TWR_Y1,s*TWR_XB),
        tv(s*TWR_Y0,s*TWR_XB),tv(s*TWR_Y0,s*FIN_X0)])                            # 塔顶截面
    pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.18)                   # 连接孔线 Y=±82
    pdf.line(*tv(s*JY,s*(TWR_XB-4)),*tv(s*JY,s*(FIN_X0+4))); pdf.set_dash_pattern(); _w(GEOM_W)
for (hx,hy) in [(HXF,HYF),(-HXF,HYF),(-HXF,-HYF),(HXF,-HYF)]:
    cx,cy=tv(hy,hx); pdf.circle(cx,cy,M3/2*S2,style="D"); cross(cx,cy,3.5)
cross(TV_CX,TV_CY,6); text(TV_CX+7,TV_CY-2,"旋转轴",size=TXT_I,anchor="start",halo=True)
hdim(tv(-HYF,0)[0],tv(HYF,0)[0],tv(0,HXF)[1],TV_CY+FOOT_HX*S2+DIM_O1,f"{2*HYF:.1f} (2×{HYF:.3f})")
hdim(tv(-FOOT_Y1,0)[0],tv(FOOT_Y1,0)[0],TV_CY+FOOT_HX*S2,TV_CY+FOOT_HX*S2+DIM_O2,f"{2*FOOT_Y1:g}")
hdim(tv(-FOOT_Y0,0)[0],tv(FOOT_Y0,0)[0],TV_CY-FOOT_HX*S2,TV_CY-FOOT_HX*S2-DIM_O1,f"{2*FOOT_Y0:g}")
hdim(TV_CX,tv(JY,0)[0],TV_CY-10.0,104.0,f"{JY:g} (至轴)")
vdim(tv(0,-HXF)[1],tv(0,HXF)[1],tv(FOOT_Y1,0)[0],TV_CX+DISC_R*S2+DIM_O1,f"{2*HXF:.2f} (2×{HXF:.3f})")
note(*tv(-HYF,-HXF),288.0,112.0-1.2,f"4×Φ{M3:g} 借盘R{RIM_R:g}环孔 (45°阵列)",anchor="end")
note(TV_CX-DISC_R*S2*0.5,TV_CY-DISC_R*S2*0.866,295.0,102.0-1.2,f"盘边 R{DISC_R:g} (参考)",anchor="end")
note(tv(FOOT_Y1,-FOOT_HX)[0],tv(FOOT_Y1,-FOOT_HX)[1]+1,394.0,124.0-1.2,"件1 (脚+Y, 塔-X侧)")
note(tv(-FOOT_Y1,-FOOT_HX)[0],tv(-FOOT_Y1,-FOOT_HX)[1]+1,266.0,124.0-1.2,"件2 = 件1 绕Z转180°",anchor="end")

text(210.0,250.0,"同一件打印 2 次, 对角安装 (件2 绕 Z 转 180°) · 侧躺打印: 外侧面 (Y=93 面) 贴床, 零支撑",
     size=TXT_I,anchor="middle")

# ===== Title block =====
tb_y=PAGE_H-28; tb_x,tb_w,tb_h=20,PAGE_W-40,18
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+6,"POV 3D v3 结构件 — gantry_v3 门形底座 (同一件打印 2 次, 对角安装: 件2 绕 Z 转 180°)",size=TXT_L,anchor="start")
text(tb_x+tb_w-4,tb_y+6,"投影 1st-angle / 比例 侧视·正视 1:1, 俯视 1:2 / 全部 Φ3.2 平面通孔",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+14.5,
     f"脚 {FOOT_T:g}厚 X±{FOOT_HX:g} Y{FOOT_Y0:g}..{FOOT_Y1:g}, 孔(±{HXF:.3f},{HYF:.3f}) / "
     f"塔 {TWR_Y1-TWR_Y0:g}×{TWR_D:g} 直背 X-13..-3 Y{TWR_Y0:g}..{TWR_Y1:g} Z{FOOT_T:g}..{TWR_TOP:g} + 筋墙{WALL_T:g}满三角 / "
     f"连接孔 Y{JY:g}×Z{{28,56,84}} 贯通 M3×18/20+螺母 / 侧躺打印(Y=93面为底)零支撑 / mm",
     size=TXT_I,anchor="start")
text(tb_x+tb_w-4,tb_y+14.5,"日期 2026-07-10  /  POV3D / v3 / models / l_bracket_v3 / gantry_v3.stl ×2",size=TXT_I,anchor="end")

out=Path(__file__).with_name("gantry_v3_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt=Path(__file__).with_name("gantry_v3_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
