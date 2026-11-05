import math,cmath,sys
sys.path.insert(0,'.')
import numpy as np, solve_single_plane as M
D='/mnt/d/claude_workspace/mtr/APL+LDR_V1.1/tools/_cap/hss/bal/'
ch=['ax','ay','az','gx','gy','gz']
fs=['bal_b1','bal_b2','bal_t1','bal_c1','bal_t2','bal_t3','bal_v7']
NS=[2,3,4,5,6]
P={}
for f in fs:
    ms,agl,rpm,d,_=M.load(D+f+'.csv','hfi_agl',ch)
    i0=M.anchor(rpm,ms); th,e0=M.mech_angle(agl,i0,7); t=(ms[i0:]-ms[i0])/1e3
    m=(abs(abs(rpm[i0:])-300)<30)&(t>4); q=th[m]
    cols=[np.ones_like(q),t[m]-t[m].mean()]
    for n in [1]+NS: cols+= [np.cos(n*q),np.sin(n*q)]
    A=np.column_stack(cols)
    for c in ch+['rpm']:
        y=(rpm[i0:] if c=='rpm' else d[c][i0:])[m]
        x=np.linalg.lstsq(A,y,rcond=None)[0]; res=(y-A@x).std()
        for j,n in enumerate([1]+NS): P[f,c,n]=complex(x[2+2*j],-x[3+2*j])
        P[f,c,'res']=res
# 列出幅值足够的 (通道,谐波)
sel=[]
for c in ch+['rpm']:
    for n in NS+[1] if c=='rpm' else NS:
        a=[abs(P[f,c,n]) for f in fs]
        if min(a)>0.3*max(a) and np.mean(a)>6*P['bal_b1',c,'res']/math.sqrt(30*20/2): sel.append((c,n))
print('通道谐波:',sel)
print('相对 b1 的相位差 (度), 以及按 k 解释: n·k·51.43')
for f in fs[1:]:
    best=[]
    for k in range(-3,4):
        e=0;w=0
        for c,n in sel:
            r=P[f,c,n]/P['bal_b1',c,n]; wt=abs(P['bal_b1',c,n])/P['bal_b1',c,'res']
            e+=wt*abs(r/abs(r)-cmath.exp(1j*math.radians(n*k*360/7)))**2; w+=wt
        best.append((e/w,k))
    best.sort(); print(f"{f}: 最佳 k={best[0][1]:+d} (err {best[0][0]:.3f}), 次 k={best[1][1]:+d} (err {best[1][0]:.3f})  | "+' '.join(f"{c}{n}:{math.degrees(cmath.phase(P[f,c,n]/P['bal_b1',c,n])):.0f}" for c,n in sel[:9]))

print('\n=== 连续零点偏移 δ (机械角) ===')
R=82.5
dl={}
g=np.arange(-180,180,0.1)
for f in fs:
    sc=np.zeros_like(g)
    for c,n in sel:
        r=P[f,c,n]/P['bal_b1',c,n]; wt=abs(P['bal_b1',c,n])/P['bal_b1',c,'res']
        sc+=wt*np.real(r/abs(r)*np.exp(-1j*np.radians(n*g)))
    i=sc.argmax(); dl[f]=g[i]
    tot=sum(abs(P['bal_b1',c,n])/P['bal_b1',c,'res'] for c,n in sel)
    # 残余散布
    rs=[math.degrees(cmath.phase(P[f,c,n]/P['bal_b1',c,n]*cmath.exp(-1j*math.radians(n*g[i])))) for c,n in sel]
    print(f"{f}: δ={g[i]:+.1f}°  相干度 {sc[i]/tot:.2f}  谐波残差中位 {np.median(np.abs(rs)):.0f}°")
V={f:{c:P[f,c,1]*cmath.exp(-1j*math.radians(dl[f])) for c in ch} for f in fs}
print('\n校正后 1× (raw):')
for f in fs: print(f"{f:8s}",' '.join(f"{c}={abs(V[f][c]):6.1f}∠{math.degrees(cmath.phase(V[f][c])):4.0f}" for c in ch))
T={'bal_t1':cmath.rect(2.2*R,math.radians(22.5)),'bal_t2':cmath.rect(4.8*R,math.radians(22.5)),'bal_t3':cmath.rect(4.8*R,math.radians(22.5)),
   'bal_v7':cmath.rect(4.8*R,math.radians(292.5)),
   'bal_c1':cmath.rect(1.09*R,math.radians(67.5))+cmath.rect(1.44*R,math.radians(112.5)),'bal_b1':0,'bal_b2':0}
print('\n检查 (V7-Vb)/(Vt-Vb), 期望 1∠-90:')
for c in ch:
    vb=(V['bal_b1'][c]+V['bal_b2'][c])/2; vt=(V['bal_t2'][c]+V['bal_t3'][c])/2
    x=(V['bal_v7'][c]-vb)/(vt-vb); y=(V['bal_t1'][c]-vb)/(vt-vb); z=(V['bal_c1'][c]-vb)/(vt-vb)
    w=T['bal_c1']/T['bal_t2']
    print(f" {c}: v7 {abs(x):.2f}∠{math.degrees(cmath.phase(x)):.0f} | t1 {abs(y):.2f}∠{math.degrees(cmath.phase(y)):.0f} (期望 .46∠0) | c1 {abs(z):.2f}∠{math.degrees(cmath.phase(z)):.0f} (期望 {abs(w):.2f}∠{math.degrees(cmath.phase(w)):.0f})")
num=den=0
print('\n全状态拟合 V=V0+H·T:')
for c in ch:
    A=np.array([[1,T[f]] for f in fs],complex); y=np.array([V[f][c] for f in fs]); x=np.linalg.lstsq(A,y,rcond=None)[0]
    s=abs(x[0]); W=-x[0]/x[1]
    print(f" {c}: 配重 {abs(W):.0f} g·mm ∠{math.degrees(cmath.phase(W))%360:.0f}  拟合残差最大 {abs(y-A@x).max()/s*100:.0f}%")
    num+=(x[1]/s).conjugate()*(x[0]/s); den+=abs(x[1]/s)**2
W=-num/den; print(f"LS {abs(W):.0f} g·mm ∠{math.degrees(cmath.phase(W))%360:.0f} = {abs(W)/R:.2f} g", M.split(abs(W),math.degrees(cmath.phase(W))%360))
