"""
A3 drawing — gantry_base 门形底座 A/B (v2 支架之二)。GB first-angle, 1:2。
A(+Y)/B(-Y) 互为镜像左右手件, 图示 A 件几何 (B 镜像)。
全部特征均为平面通孔 (贯通螺丝+螺母连接, 2026-07-02 修订) → 无详图。
基准 = 脚底面 (= 盘顶面)。
"""
import math, os
from pathlib import Path
from fpdf import FPDF

# ===== Geometry =====
SCREEN_T, FIN_T = 7.27, 6.0
FIN_X0 = -SCREEN_T - FIN_T            # -13.27 塔前面
M3 = 3.2
FOOT_T, FOOT_HX, FOOT_Y0, FOOT_Y1 = 4.0, 36.0, 63.5, 83.5   # 外缘平直
DISC_R, RIM_R = 85.0, 77.5
HXF = RIM_R * math.cos(math.radians(67.5))    # 29.658
HYF = RIM_R * math.sin(math.radians(67.5))    # 71.601
TWR_Y0, TWR_Y1, TWR_TOP = 63.5, 78.5, 90.0
TWR_D = 10.0
TWR_XB = FIN_X0 - TWR_D               # -23.27 直背 (加强墩已删: 压后脚孔)
WALL_T = 5.0                                # 外侧筋墙 满三角 (外面与脚外缘共面=打印底面)
WALL_PTS = [(-36.0,4.0),(36.0,4.0),(-13.27,90.0),(-23.27,90.0)]
JY, JZ = 71.0, [28.0, 56.0, 84.0]
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
text(PAGE_W/2,15,"POV 3D v2 — gantry_base 门形底座 A/B (支架三件之二三, 配 screen_plate)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,
     f"A(+Y)/B(-Y) 互为镜像左右手件, 本图示 A 件 / 脚 {FOOT_T:g}厚 借盘R{RIM_R:g}环孔 2×Φ{M3:g} / "
     f"塔柱 宽{TWR_Y1-TWR_Y0:g}×深{TWR_D:g} 直背 + 外侧筋墙{WALL_T:g}厚满三角(塔顶90拉到脚两端; 外面=打印底面, 侧躺零支撑) / 3×Φ{M3:g} 贯通: M3×18/20 穿 板6+塔{TWR_D:g}, "
     f"塔背垫片+螺母 (无嵌件无沉头, 全平面通孔) / 基准=脚底面(=盘顶)  (GB 1st-angle, 1:2, mm)",
     size=TXT_I,anchor="middle")

# ===================== 主视图 (塔前面方向, Y→右, Z→上) =====================
FV_CX, FV_Y0 = 100.0, 175.0
def fv(y,z): return (FV_CX+y*S, FV_Y0-z*S)
text(FV_CX,105,"主视图 (1:2, 双件装配位)",size=TXT_L,anchor="middle")
for s in (1,-1):
    pl([fv(s*TWR_Y0,FOOT_T),fv(s*TWR_Y0,TWR_TOP),fv(s*TWR_Y1,TWR_TOP),fv(s*TWR_Y1,FOOT_T)])   # 塔
    pl([fv(s*FOOT_Y0,0),fv(s*FOOT_Y0,FOOT_T),fv(s*FOOT_Y1,FOOT_T),fv(s*FOOT_Y1,0),fv(s*FOOT_Y0,0)])  # 脚
    pl([fv(s*TWR_Y1,FOOT_T),fv(s*TWR_Y1,TWR_TOP),fv(s*FOOT_Y1,TWR_TOP),fv(s*FOOT_Y1,FOOT_T)])   # 外侧筋墙 (满三角, 正视投影到顶)
for z in JZ:
    for s in (1,-1):
        cx,cy=fv(s*JY,z); pdf.circle(cx,cy,M3/2*S,style="D"); cross(cx,cy,3.0)
pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.18)
pdf.line(*fv(0,-6),*fv(0,TWR_TOP+8)); pdf.set_dash_pattern(); _w(GEOM_W)
hdim(fv(-JY,0)[0],fv(JY,0)[0],fv(0,JZ[0])[1],fv(0,0)[1]+DIM_O2,f"{2*JY:g}")
hdim(fv(TWR_Y0,0)[0],fv(TWR_Y1,0)[0],fv(0,TWR_TOP)[1],fv(0,TWR_TOP)[1]-DIM_O1,f"{TWR_Y1-TWR_Y0:g}")
vdim(fv(0,TWR_TOP)[1],fv(0,0)[1],fv(-FOOT_Y1,0)[0],fv(-FOOT_Y1,0)[0]-DIM_O1,f"{TWR_TOP:g}")
vdim(fv(0,JZ[0])[1],fv(0,0)[1],fv(FOOT_Y1,0)[0],fv(FOOT_Y1,0)[0]+DIM_O1,f"{JZ[0]:g}")
vdim(fv(0,JZ[2])[1],fv(0,JZ[0])[1],fv(FOOT_Y1,0)[0],fv(FOOT_Y1,0)[0]+DIM_O2,"56 (2×28)")
hdim(fv(-FOOT_Y1,0)[0],fv(FOOT_Y1,0)[0],fv(0,0)[1],fv(0,0)[1]+DIM_O3,f"{2*FOOT_Y1:g}")
note(*fv(-JY,JZ[2]),fv(-FOOT_Y1,0)[0]-6,fv(0,TWR_TOP+14)[1],f"3×Φ{M3:g}/件 贯通 (M3×18/20+螺母)",anchor="end")
text(FV_CX,fv(0,-14)[1],"左 = A 件 (+Y) · 右 = B 件 (-Y), 镜像",size=TXT_I,anchor="middle")

# ===================== 侧视图 (X→右, Z→上) =====================
SV_CX = 225.0
def sv(x,z): return (SV_CX+x*S, FV_Y0-z*S)
text(SV_CX,105,"侧视图 (1:2)",size=TXT_L,anchor="middle")
pl([sv(-FOOT_HX,0),sv(-FOOT_HX,FOOT_T),sv(FOOT_HX,FOOT_T),sv(FOOT_HX,0),sv(-FOOT_HX,0)])
pl([sv(TWR_XB,FOOT_T),sv(FIN_X0,FOOT_T),sv(FIN_X0,TWR_TOP),sv(TWR_XB,TWR_TOP),sv(TWR_XB,FOOT_T)])
pl([sv(*p) for p in WALL_PTS] + [sv(*WALL_PTS[0])])                               # 外侧筋墙满三角轮廓
# 2 脚孔位置 (中心线示意: 前 +29.66 / 后 -29.66, 后孔上方无遮挡)
for hx in (HXF, -HXF):
    pdf.set_dash_pattern(dash=1.2,gap=0.6); _w(0.13)
    pdf.line(*sv(hx,-3),*sv(hx,10)); pdf.set_dash_pattern(); _w(GEOM_W)
pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.18)
pdf.line(*sv(0,-6),*sv(0,TWR_TOP+8)); pdf.set_dash_pattern(); _w(GEOM_W)
# 贯通孔 (隐藏线)
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(HID_W)
for z in JZ:
    for dz in (-M3/2, M3/2):
        pdf.line(*sv(FIN_X0,z+dz),*sv(TWR_XB,z+dz))
pdf.set_dash_pattern(); _w(GEOM_W)
hdim(sv(-FOOT_HX,0)[0],sv(FOOT_HX,0)[0],sv(0,0)[1],sv(0,0)[1]+DIM_O1,f"{2*FOOT_HX:g}")
hdim(sv(FIN_X0,0)[0],sv(0,0)[0],sv(0,TWR_TOP)[1],sv(0,TWR_TOP)[1]-DIM_O1,"13.27 (前面距轴)")
hdim(sv(TWR_XB,0)[0],sv(FIN_X0,0)[0],sv(0,TWR_TOP)[1],sv(0,TWR_TOP)[1]-DIM_O2,f"{TWR_D:g}")
vdim(sv(0,FOOT_T)[1],sv(0,0)[1],sv(FOOT_HX,0)[0],sv(FOOT_HX,0)[0]+DIM_O1,f"{FOOT_T:g}")
note(*sv(-HXF,5),sv(-FOOT_HX,0)[0]-6,fv(0,26)[1],"后脚孔 -29.66: 上方通畅, M3 从上往下打",anchor="end")
note(*sv(5.0,58.0),sv(FOOT_HX,0)[0]+6,fv(0,120)[1],f"外侧筋墙 {WALL_T:g}厚 满三角 (外面=打印底面)")
note(*sv(TWR_XB,JZ[1]),sv(-FOOT_HX,0)[0]-6,fv(0,64)[1],"直背平面: 垫片+M3螺母座面",anchor="end")

# ===================== 俯视图 (Y→右, X→下) =====================
TV_CX, TV_CY = 330.0, 160.0
def tv(y,x): return (TV_CX+y*S, TV_CY+x*S)
text(TV_CX,105,"俯视图 (1:2, 双件装配位)",size=TXT_L,anchor="middle")
pdf.set_dash_pattern(dash=2.0,gap=1.2); _w(0.18)
pdf.circle(TV_CX,TV_CY,DISC_R*S,style="D"); pdf.set_dash_pattern(); _w(GEOM_W)
for s in (1,-1):
    pl([tv(s*FOOT_Y0,-FOOT_HX),tv(s*FOOT_Y0,FOOT_HX),tv(s*FOOT_Y1,FOOT_HX),
        tv(s*FOOT_Y1,-FOOT_HX),tv(s*FOOT_Y0,-FOOT_HX)])                     # 脚 (矩形, 外缘平直)
    pl([tv(s*TWR_Y1,-FOOT_HX),tv(s*TWR_Y1,FOOT_HX)])                        # 外侧筋墙内缘
    pl([tv(s*TWR_Y0,FIN_X0),tv(s*TWR_Y1,FIN_X0),tv(s*TWR_Y1,TWR_XB),tv(s*TWR_Y0,TWR_XB),tv(s*TWR_Y0,FIN_X0)])  # 塔顶截面
for (hx,hy) in [(HXF,HYF),(-HXF,HYF),(HXF,-HYF),(-HXF,-HYF)]:
    cx,cy=tv(hy,hx); pdf.circle(cx,cy,M3/2*S,style="D"); cross(cx,cy,3.5)
cross(TV_CX,TV_CY,6); text(TV_CX+7,TV_CY-2,"旋转轴",size=TXT_I,anchor="start",halo=True)
hdim(tv(-HYF,0)[0],tv(HYF,0)[0],tv(0,HXF)[1],TV_CY+FOOT_HX*S+DIM_O1,f"{2*HYF:.1f}")
vdim(tv(0,-HXF)[1],tv(0,HXF)[1],tv(HYF,0)[0],TV_CX+DISC_R*S+DIM_O1,f"{2*HXF:.2f}")
hdim(tv(-FOOT_Y0,0)[0],tv(FOOT_Y0,0)[0],tv(0,-FOOT_HX)[1],TV_CY-FOOT_HX*S-DIM_O2,f"{2*FOOT_Y0:g}")
hdim(tv(-FOOT_Y1,0)[0],tv(FOOT_Y1,0)[0],tv(0,FOOT_HX)[1],TV_CY+FOOT_HX*S+DIM_O2,f"{2*FOOT_Y1:g}")
note(*tv(HYF,-HXF),tv(HYF,0)[0]+16,TV_CY-FOOT_HX*S-DIM_O1-8,f"4×Φ{M3:g} 借盘R{RIM_R:g}环孔")
note(*tv(-DISC_R*0.7071,-DISC_R*0.7071),tv(-DISC_R,0)[0]-2,TV_CY-FOOT_HX*S-DIM_O3-6,
     f"盘边 R{DISC_R:g} (参考)",anchor="end")

# ===== Title block =====
tb_y=PAGE_H-28; tb_x,tb_w,tb_h=20,PAGE_W-40,18
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+6,"POV 3D v2 结构件 — gantry_base A/B 门形底座 (镜像左右手件)",size=TXT_L,anchor="start")
text(tb_x+tb_w-4,tb_y+6,"投影 1st-angle / 比例 1:2 / 全部 Φ3.2 平面通孔",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+14.5,
     f"脚 4厚 X±{FOOT_HX:g} Y±({FOOT_Y0:g}..{FOOT_Y1:g}) 外缘平直, 孔(±{HXF:.2f},±{HYF:.2f}) / "
     f"塔 15×{TWR_D:g} 直背 Z4..{TWR_TOP:g} + 外侧筋墙{WALL_T:g}满三角 / 连接孔 ±{JY:g}×高{{28,56,84}} 贯通 M3×18/20+螺母 / 侧躺打印(外侧面为底)零支撑 / mm",
     size=TXT_I,anchor="start")
text(tb_x+tb_w-4,tb_y+14.5,"2026-07-03  /  POV3D / models / l_bracket_v2 / gantry_base_A/B.stl",size=TXT_I,anchor="end")

out=Path(__file__).with_name("gantry_base_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt=Path(__file__).with_name("gantry_base_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
