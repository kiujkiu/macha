import sys,zipfile,io,struct,numpy as np,pickle
from pathlib import Path; SRC=Path(__file__).resolve().parent.parent/'src'
from m2b import convert_part,vol,BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
z=zipfile.ZipFile('/mnt/d/claude_workspace/pov3d/POV3D_结构交付包_2026-10-28/附录_原始依据/A10_V0.4现役转子/pov3d_v4_print.zip')
for n in 'AB':
    b=z.read(f'print/top_bearing_frame_v4/frame_{n}_v4.stl')
    if b[:5]==b'solid' and b.count(b'facet')>0 and len(b)!=84+50*struct.unpack('<I',b[80:84])[0]:
        raise SystemExit('ascii stl')
    nt=struct.unpack('<I',b[80:84])[0]
    a=np.frombuffer(b[84:84+50*nt],dtype=np.dtype([('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]))
    V=a['v'].reshape(-1,3).astype(float); T=np.arange(len(V)).reshape(-1,3)
    C,st,bad,op=convert_part(V,T)
    print(n,nt,'tris',st,bad,op, V.min(0),V.max(0))
    w=STEPControl_Writer(); w.Transfer(C,STEPControl_AsIs); w.Write(f'{sys.argv[1]}/frame_{n}_v4_raw.step')
