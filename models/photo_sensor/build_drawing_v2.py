"""
A3 drawings — v2 光电件两张: sensor_bracket_v2 (含详图A: Φ4.2 顶沉) + index_vane_v2 (全平面孔)。
基准 = 旋转轴 (X=0) / 盘顶面 (支架) / 洞洞板面 (挡片)。GB first-angle。
"""
import math, os
from pathlib import Path
from fpdf import FPDF

FONT = "/mnt/c/Windows/Fonts/simhei.ttf"
GEOM_W, DIM_W, EXT_W_, HID_W = 0.50, 0.20, 0.20, 0.30
ARR_L, ARR_W, EXT_OV, EXT_GP = 4.2, 1.5, 2.4, 1.0
TXT_D, TXT_L, TXT_T, TXT_I = 4.5, 6.5, 8.0, 4.0
DIM_O1, DIM_O2, DIM_O3 = 12.0, 22.0, 34.0
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

def save(pdf, name):
    out = Path(__file__).with_name(name)
    try:
        pdf.output(str(out)); print(f"wrote {out}")
    except PermissionError:
        alt = Path(__file__).with_name(name.replace(".pdf",".NEW.pdf")); pdf.output(str(alt)); print(f"wrote {alt} (locked)")

# ================= Sheet 1: sensor_bracket_v2 =================
pdf = new_pdf(); h = mk_helpers(pdf)
h['frame']("POV 3D v2 — sensor_bracket_v2 光电支架 (θ=180/-X, 装 mlkpai_carrier_disc)",
     "3厚盘顶板 (6→3, 2026-07-15) X-113..-64×Y±35 (外角45°斜切; R_SLOT 112→98 缩半径 2026-07-07), 借盘R77.5环孔(-71.60,±29.66) Φ3.4 M3上进 / "
     "模块孔(-91,17)/(-105,17) Φ3.2 直通 (顶沉取消, M3×8+螺母) / 3× 贯通避空槽 / 梁(-98,0,盘顶-8) / 基准=旋转轴  (GB 1st-angle, 2:1, mm)")
S=2.0; CX, CY = 130.0, 130.0    # plan: pdf_x = (X+95.5)*S+CX, pdf_y = CY - Y*S (θ=180 件, 轴在图右外侧)
def pv(x,y): return (CX+(x+95.5)*S, CY-y*S)
h['text'](CX,52,"俯视图 (2:1)  基准: X=0 为旋转轴 (在图右外侧)",size=TXT_L,anchor="middle")
h['pl']([pv(-113,-20),pv(-113,20),pv(-98,35),pv(-64,35),pv(-64,-35),pv(-98,-35),pv(-113,-20)])
for (x,y) in [(-71.601,29.658),(-71.601,-29.658)]:
    cx,cy=pv(x,y); pdf.circle(cx,cy,1.7*S,style="D"); h['cross'](cx,cy,4.5)
for (x,y) in [(-91,17),(-105,17)]:
    cx,cy=pv(x,y); pdf.circle(cx,cy,1.6*S,style="D"); h['cross'](cx,cy,4.5)
for (x0,x1,y0,y1) in [(-108,-102,-4.5,4.5),(-94,-88,-4.5,4.5),(-101.85,-94.15,15,21.5)]:
    h['pl']([pv(x0,y0),pv(x1,y0),pv(x1,y1),pv(x0,y1),pv(x0,y0)])   # 贯通槽 → 实线
# 盘边 R85 参考弧 (θ=180 侧)
pdf.set_dash_pattern(dash=2.0,gap=1.2); pdf.set_line_width(0.18)
arc=[pv(85*math.cos(math.radians(a)),85*math.sin(math.radians(a))) for a in range(154,207,2)]
h['pl'](arc); pdf.set_dash_pattern(); pdf.set_line_width(GEOM_W)
h['hdim'](pv(-113,-35)[0],pv(-64,-35)[0],pv(0,-35)[1],pv(0,-35)[1]+DIM_O1,"49")
h['hdim'](pv(-71.601,-35)[0],pv(-64,-35)[0],pv(0,-35)[1],pv(0,-35)[1]+DIM_O2,"7.6")
h['hdim'](pv(-105,35)[0],pv(-91,35)[0],pv(0,17)[1],pv(0,35)[1]-DIM_O1,"14")
h['vdim'](pv(0,29.658)[1],pv(0,-29.658)[1],pv(-71.601,0)[0],pv(-64,0)[0]+DIM_O1,"59.32")
h['vdim'](pv(0,35)[1],pv(0,-35)[1],pv(-64,0)[0],pv(-64,0)[0]+DIM_O2,"70")
h['vdim'](pv(0,17)[1],pv(0,0)[1],pv(-105,0)[0],pv(-113,0)[0]-DIM_O1,"17")
h['note'](*pv(-71.601,-29.658),pv(-64,0)[0]+8,pv(0,-44)[1],"2×Φ3.4 通 (M3上进 穿板+盘+环)")
h['note'](*pv(-105,17),pv(-113,0)[0]-8,pv(0,30)[1],"2×Φ3.2 通 (M3×12 顶入, 模块下螺母)",anchor="end")
h['note'](*pv(-78.3,33.2),pv(-64,0)[0]+8,66.0,"盘边 R85 (参考)")
h['text'](pv(-88.5,0)[0],236.0,"梁位置 (-98, 0), 距轴 98 / 3 槽贯通 (焊脚避空, 2026-07-14 挖穿) / 外角斜切 (-113,±20)→(-98,±35)",size=TXT_I,anchor="middle")
h['hdim'](pv(-98,20)[0],pv(-64,20)[0],pv(0,17)[1]-14,pv(0,35)[1]-DIM_O2,"34 (梁R98-板内缘64)")
# 侧视 (X→右, Z→上; 板厚)
SVX=300.0
def sv(x,z): return (SVX+(x+95.5)*S, 150.0-(z-48.2)*S)
h['text'](SVX,52,"侧视图 (2:1)",size=TXT_L,anchor="middle")
h['pl']([sv(-113,45.7),sv(-64,45.7),sv(-64,48.7),sv(-113,48.7),sv(-113,45.7)])
pdf.set_dash_pattern(dash=2.0,gap=1.2)
for sx in (-108,-102,-94,-88):   # 两条贯通槽的边 (隐藏线, 全厚)
    h['line'](*sv(sx,45.7),*sv(sx,48.7),HID_W)
pdf.set_dash_pattern()
h['hdim'](sv(-113,0)[0],sv(-64,0)[0],sv(0,45.7)[1],sv(0,45.7)[1]+DIM_O1,"49")
h['vdim'](sv(0,48.7)[1],sv(0,45.7)[1],sv(-64,0)[0],sv(-64,0)[0]+DIM_O1,"3")
h['note'](*sv(-98,45.7),sv(-64,0)[0]+8,sv(0,42)[1]+14,"模块扣板底(槽口朝下), 避空槽贯通")
h['tblock']("POV 3D v2 结构件 — sensor_bracket_v2 光电支架 (θ=180)","投影 1st-angle / 比例 2:1",
       "板 49×70×3 (X-113..-64, 外角斜切) / 借环孔(-71.60,±29.66) Φ3.4 (M3×16) / 模块孔 -91/-105@Y+17 Φ3.2直通(M3×8) / 3避空槽贯通 / 平躺打印 / mm",
       "2026-07-15  /  POV3D / models / photo_sensor / sensor_bracket_v2.stl")
save(pdf, "photo_sensor_bracket_v2_drawing.pdf")

# ================= Sheet 2: index_vane_v2 =================
pdf = new_pdf(); h = mk_helpers(pdf)
h['frame']("POV 3D v2 — index_vane_v2 静止挡光片 (θ=180/-X, 洞洞板 中心锚定 25mm 网格)",
     "脚 5厚 X-108..-92×Y±32, 2×Φ6.5 M6 @ 网格(-100,±25) 切向对 / 挡片 径向4 (X-100..-96=R98居中): "
     "槽下宽10 到Z28, 槽内宽8 到Z39 / 梁(-98,0,37.7) / R_SLOT 112→98 (2026-07-07 缩半径) / 基准=旋转轴+洞洞板面 / 全平面孔无详图  (GB 1st-angle, 3:1, mm)")
S3=3.0; BX, BY = 120.0, 148.0
def bv(x,y): return (BX+(x+100.0)*S3, BY-y*S3)
h['text'](BX,42,"俯视图 (3:1)  (轴在图右外侧)",size=TXT_L,anchor="middle")
h['pl']([bv(-108,-32),bv(-92,-32),bv(-92,32),bv(-108,32),bv(-108,-32)])
for (x,y) in [(-100,25),(-100,-25)]:
    cx,cy=bv(x,y); pdf.circle(cx,cy,3.25*S3,style="D"); h['cross'](cx,cy,12)
h['pl']([bv(-100,-5),bv(-96,-5),bv(-96,5),bv(-100,5),bv(-100,-5)])
h['vdim'](bv(0,25)[1],bv(0,-25)[1],bv(-108,0)[0],bv(-108,0)[0]-DIM_O1,"50 (网格)")
h['vdim'](bv(0,32)[1],bv(0,-32)[1],bv(-92,0)[0],bv(-92,0)[0]+DIM_O1,"64")
h['vdim'](bv(0,5)[1],bv(0,-5)[1],bv(-92,0)[0],bv(-92,0)[0]+DIM_O2,"10 (槽下段)")
h['hdim'](bv(-108,-32)[0],bv(-92,-32)[0],bv(0,-32)[1],bv(0,-32)[1]+DIM_O1,"16")
h['hdim'](bv(-100,-32)[0],bv(-96,-32)[0],bv(0,-5)[1],bv(0,-32)[1]+DIM_O2,"4")
h['note'](*bv(-100,25),bv(-108,0)[0]-14,bv(0,40)[1],"2×Φ6.5 (M6→洞洞板 (-100,±25))",anchor="end")
h['note'](*bv(-98,5),bv(-92,0)[0]+14,bv(0,40)[1],"挡片 X-100..-96 (R98 居中)")
# 正视 (X→右, Z→上)
FVX, FVZ0 = 300.0, 230.0
def fe(x,z): return (FVX+(x+100.0)*S3, FVZ0-z*S3)
h['text'](FVX,58,"正视图 (3:1)",size=TXT_L,anchor="middle")
h['pl']([fe(-108,0),fe(-92,0),fe(-92,5),fe(-108,5),fe(-108,0)])
h['pl']([fe(-100,5),fe(-100,39),fe(-96,39),fe(-96,5)])
pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); pdf.set_line_width(0.18)
pdf.line(*fe(-114,37.7),*fe(-86,37.7)); pdf.set_dash_pattern(); pdf.set_line_width(GEOM_W)
h['text'](fe(-86,37.7)[0]+3,fe(0,37.7)[1]+1.5,"梁 Z37.7",size=TXT_I)
h['vdim'](fe(0,39)[1],fe(0,0)[1],fe(-108,0)[0],fe(-108,0)[0]-DIM_O1,"39")
h['vdim'](fe(0,28)[1],fe(0,0)[1],fe(-108,0)[0],fe(-108,0)[0]-DIM_O2,"28 (槽下沿)")
h['vdim'](fe(0,5)[1],fe(0,0)[1],fe(-92,0)[0],fe(-92,0)[0]+DIM_O1,"5")
h['hdim'](fe(-108,0)[0],fe(-92,0)[0],fe(0,0)[1],fe(0,0)[1]+DIM_O1,"16")
h['note'](*fe(-98,34),fe(-92,0)[0]+10,fe(0,34)[1],"槽内段 宽8 (Z28..39) / 槽下段 宽10")
h['tblock']("POV 3D v2 结构件 — index_vane_v2 静止挡光片 (θ=180)","投影 1st-angle / 比例 3:1 / 全平面通孔",
       "脚 16×64×5, 2×Φ6.5 @ (-100,±25) / 挡片 4径向×(10/8)切向 @R98, 顶39, 槽下沿28, 梁37.7 / 平躺打印 / mm",
       "2026-07-03  /  POV3D / models / photo_sensor / index_vane_v2.stl")
save(pdf, "photo_sensor_vane_v2_drawing.pdf")
