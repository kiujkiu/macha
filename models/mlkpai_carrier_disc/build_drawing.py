"""
A3 drawing — mlkpai_carrier_disc (Φ170×5 转子承载盘, 重画 2026-07-06 定型版)。
平盘: 16×M3 挂环孔 (R35+R77.5, Φ7×2.5 顶沉) + 7× pi2hub 孔 (Φ3.2 通 +
盘底 Φ4.2×4 铜螺母沉孔)。凸台/支托均已取消。
俯视 1:1 + 详图A (环孔顶沉 6:1) + 详图B (铜螺母沉孔 6:1)。GB first-angle, mm。
"""
import math, os
from pathlib import Path
from fpdf import FPDF

DISC_OD, THICK = 170.0, 5.0
INNER_R, OUTER_R = 35.0, 77.5
ANGLES = [22.5 + k*45.0 for k in range(8)]
M3, CB_D, CB_DEEP = 3.2, 7.0, 2.5
THRU_D, INS_D, INS_DEEP = 3.2, 4.2, 4.0
PCB_XY = [(-54.0,-47.0), (-54.0,0.0), (-54.0,47.0),
          (-35.0,-39.5), (-35.0,39.5), (15.0,-39.5), (15.0,39.5)]

PAGE_W, PAGE_H = 420.0, 297.0
pdf = FPDF(orientation="L", unit="mm", format="A3"); pdf.set_auto_page_break(False); pdf.add_page()
_font = next((f for f in ["/mnt/c/Windows/Fonts/simhei.ttf"] if os.path.exists(f)), None)
if _font is None: raise FileNotFoundError("SimHei not found")
pdf.add_font("SimHei", "", _font)
GEOM_W, DIM_W, EXT_W_, HID_W = 0.50, 0.20, 0.20, 0.30
ARR_L, ARR_W, EXT_OV, EXT_GP = 4.2, 1.5, 2.4, 1.0
TXT_D, TXT_L, TXT_T, TXT_I = 4.5, 6.5, 8.0, 4.0
DIM_O1, DIM_O2 = 12.0, 22.0

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
def cross(cx,cy,r=3.5):
    pdf.set_dash_pattern(dash=1.2,gap=0.6); _w(0.13)
    pdf.line(cx-r,cy,cx+r,cy); pdf.line(cx,cy-r,cx,cy+r); pdf.set_dash_pattern(); _w(GEOM_W)
def pl(pts,w=GEOM_W):
    _w(w)
    for i in range(len(pts)-1): pdf.line(*pts[i],*pts[i+1])
def hatch_pts(p0,p1,spacing=2.0):
    xmin,xmax=min(p0[0],p1[0]),max(p0[0],p1[0]); ymin,ymax=min(p0[1],p1[1]),max(p0[1],p1[1])
    _w(0.13); c=xmin-(ymax-ymin)
    while c<=xmax:
        px0=max(xmin,c); px1=min(xmax,c+(ymax-ymin))
        if px0<px1: pdf.line(px0,ymin+(px0-c),px1,ymin+(px1-c))
        c+=spacing
    _w(GEOM_W)

# ===== header =====
_w(0.3); pdf.rect(5,5,PAGE_W-10,PAGE_H-10,style="D")
text(PAGE_W/2,15,"POV 3D v2 — mlkpai_carrier_disc 转子承载盘 (Φ170×5, 2026-07-06 定型)",size=TXT_T,anchor="middle")
text(PAGE_W/2,21,
     f"平盘 (凸台/支托均取消) / 16×Φ{M3:g} 挂环孔 (R{INNER_R:g}+R{OUTER_R:g}, 22.5°+45k°) + Φ{CB_D:g}×{CB_DEEP:g} 顶沉→详图A / "
     f"7× pi2hub 孔 Φ{THRU_D:g} 通 + 盘底 Φ{INS_D:g}×{INS_DEEP:g} 铜螺母沉→详图B (台肩仅1!) / 基准=盘心  (GB 1st-angle, 1:1, mm)",
     size=TXT_I,anchor="middle")

# ===== 俯视图 1:1 =====
CX, CY = 128.0, 152.0
def tv(x,y): return (CX+x, CY-y)
text(CX,52,"俯视图 (1:1)",size=TXT_L,anchor="middle")
pdf.circle(CX,CY,DISC_OD/2,style="D")
pdf.set_dash_pattern(dash=3.0,gap=1.5); _w(0.18)
pdf.circle(CX,CY,INNER_R,style="D"); pdf.circle(CX,CY,OUTER_R,style="D")
pdf.set_dash_pattern(); _w(GEOM_W)
for R in (INNER_R, OUTER_R):
    for a in ANGLES:
        x,y = R*math.cos(math.radians(a)), R*math.sin(math.radians(a))
        cx,cy = tv(x,y)
        pdf.circle(cx,cy,M3/2,style="D"); pdf.circle(cx,cy,CB_D/2,style="D"); cross(cx,cy)
for (x,y) in PCB_XY:
    cx,cy = tv(x,y)
    pdf.circle(cx,cy,THRU_D/2,style="D")
    pdf.set_dash_pattern(dash=1.5,gap=1.0); pdf.circle(cx,cy,INS_D/2,style="D"); pdf.set_dash_pattern()
    cross(cx,cy)
cross(CX,CY,6)
# 详图标记
ax,ay = tv(OUTER_R*math.cos(math.radians(22.5)), OUTER_R*math.sin(math.radians(22.5)))
pdf.circle(ax,ay,6.5,style="D"); text(ax+7,ay-5,"A",size=TXT_L)
bx,by = tv(15.0,-39.5)
pdf.circle(bx,by,6.5,style="D"); text(bx+7,by+8,"B",size=TXT_L)
# dims
hdim(tv(-DISC_OD/2,0)[0],tv(DISC_OD/2,0)[0],tv(0,-DISC_OD/2)[1],tv(0,-DISC_OD/2)[1]+DIM_O1,f"Φ{DISC_OD:g}")
note(*tv(INNER_R*math.cos(math.radians(67.5)),INNER_R*math.sin(math.radians(67.5))),
     tv(0,DISC_OD/2)[0]+32,tv(0,DISC_OD/2)[1]-16,f"8×Φ{M3:g} @ PCD Φ{2*INNER_R:g} (22.5°+45k°)")
note(*tv(OUTER_R*math.cos(math.radians(67.5)),OUTER_R*math.sin(math.radians(67.5))),
     tv(0,DISC_OD/2)[0]+32,tv(0,DISC_OD/2)[1]-8,f"8×Φ{M3:g} @ PCD Φ{2*OUTER_R:g}, 16孔均有Φ{CB_D:g}×{CB_DEEP:g}顶沉")
hdim(tv(-54,0)[0],tv(-35,0)[0],tv(0,47)[1],tv(0,DISC_OD/2)[1]-DIM_O1,"19")
hdim(tv(-35,0)[0],tv(15,0)[0],tv(0,39.5)[1],tv(0,DISC_OD/2)[1]-DIM_O2,"50")
vdim(tv(0,47)[1],tv(0,-47)[1],tv(-54,0)[0],tv(-DISC_OD/2,0)[0]-DIM_O1,"94")
vdim(tv(0,39.5)[1],tv(0,-39.5)[1],tv(15,0)[0],tv(DISC_OD/2,0)[0]+DIM_O1,"79")
note(*tv(-54,-47),98.0,232.0,"7× pi2hub 孔 → 详图B",anchor="end")
text(CX,tv(0,-DISC_OD/2)[1]+DIM_O1+8,
     "pi2hub 孔位 (盘心系): (-54,±47)(-54,0)(-35,±39.5)(15,±39.5)  [X列 -54/-35/15]",size=TXT_I,anchor="middle")

# ===== 详图 A (6:1): 挂环孔顶沉 =====
DS=6.0
DAX,DAY = 300.0, 95.0
text(DAX,58,"详图 A (6:1) — 挂环孔 Φ7 顶沉",size=TXT_L,anchor="middle")
def daz(z,r): return (DAX+r*DS, DAY+(THICK/2-z)*DS)   # z: 0盘底..5盘顶 (上=顶)
for sgn in (1,-1):
    pl([daz(0,sgn*6),daz(0,sgn*1.6)])                        # 底面
    pl([daz(0,sgn*1.6),daz(THICK-CB_DEEP,sgn*1.6)])          # Φ3.2 壁
    pl([daz(THICK-CB_DEEP,sgn*1.6),daz(THICK-CB_DEEP,sgn*3.5)])  # 台肩
    pl([daz(THICK-CB_DEEP,sgn*3.5),daz(THICK,sgn*3.5)])      # Φ7 壁
    pl([daz(THICK,sgn*3.5),daz(THICK,sgn*6)])                # 顶面
    pl([daz(0,sgn*6),daz(THICK,sgn*6)])                      # 断边
    hatch_pts(daz(0,sgn*1.6),daz(THICK-CB_DEEP,sgn*6))
    hatch_pts(daz(THICK-CB_DEEP,sgn*3.5),daz(THICK,sgn*6))
pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.18)
pdf.line(DAX,DAY-22,DAX,DAY+22); pdf.set_dash_pattern(); _w(GEOM_W)
vdim(daz(THICK,0)[1],daz(THICK-CB_DEEP,0)[1],daz(0,6)[0],daz(0,6)[0]+DIM_O1,f"{CB_DEEP:g}")
vdim(daz(THICK,0)[1],daz(0,0)[1],daz(0,-6)[0],daz(0,-6)[0]-DIM_O1,f"{THICK:g}")
hdim(daz(THICK,-3.5)[0],daz(THICK,3.5)[0],daz(THICK,0)[1],daz(THICK,0)[1]-DIM_O1-4,f"Φ{CB_D:g}")
hdim(daz(0,-1.6)[0],daz(0,1.6)[0],daz(0,0)[1],daz(0,0)[1]+DIM_O1+4,f"Φ{M3:g}")
text(DAX,daz(0,0)[1]+DIM_O1+14,"上=盘顶 (M3 头沉入); 装 rim_ring 螺丝",size=TXT_I,anchor="middle")

# ===== 详图 B (6:1): 铜螺母沉孔 (盘底) =====
DBX,DBY = 300.0, 208.0
text(DBX,172,"详图 B (6:1) — pi2hub 孔 铜螺母沉 (盘底)",size=TXT_L,anchor="middle")
def db(z,r): return (DBX+r*DS, DBY+(THICK/2-z)*DS)
for sgn in (1,-1):
    pl([db(THICK,sgn*6),db(THICK,sgn*1.6)])                  # 顶面
    pl([db(THICK,sgn*1.6),db(INS_DEEP,sgn*1.6)])             # Φ3.2 壁
    pl([db(INS_DEEP,sgn*1.6),db(INS_DEEP,sgn*2.1)])          # 台肩 (仅 1 高)
    pl([db(INS_DEEP,sgn*2.1),db(0,sgn*2.1)])                 # Φ4.2 壁
    pl([db(0,sgn*2.1),db(0,sgn*6)])                          # 底面
    pl([db(0,sgn*6),db(THICK,sgn*6)])                        # 断边
    hatch_pts(db(INS_DEEP,sgn*1.6),db(THICK,sgn*6))
    hatch_pts(db(0,sgn*2.1),db(INS_DEEP,sgn*6))
pdf.set_dash_pattern(dash=4.0,gap=1.5,phase=2.0); _w(0.18)
pdf.line(DBX,DBY-22,DBX,DBY+22); pdf.set_dash_pattern(); _w(GEOM_W)
vdim(db(INS_DEEP,0)[1],db(0,0)[1],db(0,6)[0],db(0,6)[0]+DIM_O1,f"{INS_DEEP:g}")
vdim(db(THICK,0)[1],db(INS_DEEP,0)[1],db(0,-6)[0],db(0,-6)[0]-DIM_O1,"1 (台肩)")
hdim(db(0,-2.1)[0],db(0,2.1)[0],db(0,0)[1],db(0,0)[1]+DIM_O1+4,f"Φ{INS_D:g}")
hdim(db(THICK,-1.6)[0],db(THICK,1.6)[0],db(THICK,0)[1],db(THICK,0)[1]-DIM_O1-4,f"Φ{THRU_D:g}")
text(DBX,db(0,0)[1]+DIM_O1+14,"下=盘底: 压入 M3×4×4.5 注塑铜花螺母 (台肩仅1, 勿压过深)",size=TXT_I,anchor="middle")

# ===== Title block =====
tb_y=PAGE_H-28; tb_x,tb_w,tb_h=20,PAGE_W-40,18
_w(0.3); pdf.rect(tb_x,tb_y,tb_w,tb_h,style="D"); pdf.line(tb_x,tb_y+tb_h/2,tb_x+tb_w,tb_y+tb_h/2)
text(tb_x+4,tb_y+6,"POV 3D v2 结构件 — mlkpai_carrier_disc 转子承载盘 (平盘定型版)",size=TXT_L,anchor="start")
text(tb_x+tb_w-4,tb_y+6,"投影 1st-angle / 比例 1:1, 详图 6:1",size=TXT_I,anchor="end")
text(tb_x+4,tb_y+14.5,
     f"Φ{DISC_OD:g}×{THICK:g} / 16×Φ{M3:g}@PCD{2*INNER_R:g}/{2*OUTER_R:g}+Φ{CB_D:g}×{CB_DEEP:g}顶沉 / "
     f"7×pi2hub孔 Φ{THRU_D:g}+盘底Φ{INS_D:g}×{INS_DEEP:g}螺母沉 / 平躺打印 / mm",
     size=TXT_I,anchor="start")
text(tb_x+tb_w-4,tb_y+14.5,"2026-07-06  /  POV3D / models / mlkpai_carrier_disc / mlkpai_carrier_disc.stl",size=TXT_I,anchor="end")

out=Path(__file__).with_name("mlkpai_carrier_disc_drawing.pdf")
try:
    pdf.output(str(out)); print(f"wrote {out}")
except PermissionError:
    alt=Path(__file__).with_name("mlkpai_carrier_disc_drawing.NEW.pdf"); pdf.output(str(alt)); print(f"wrote {alt} (locked)")
