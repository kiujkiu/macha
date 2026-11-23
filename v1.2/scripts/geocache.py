"""几何运算结果缓存 (11-20, 用户「改一个单一的件太慢了, 彻底解决」)。

原理: build_v1_2 的 cyl / gbox / op(cut/fuse/common) / clean / xf / one 都经过这里。每个形体带一个"配方键":
  - 基本体 (cyl / gbox / 读 STEP): 键 = 参数 (读 STEP 用 路径 + 大小 + mtime)
  - 运算结果: 键 = hash(运算名, 各输入的键, 参数)
  - 不是从这里出来的形体 (别处直接 BRepPrimAPI / MakePrism / TopExp 拆出来的): 按几何指纹算键
    (顶点坐标 + 每条边/每个面上几个采样点 + 朝向), 几何不同键就不同。
运算前先查键: 磁盘有就直接读 (BinTools 二进制), 没有才算; 算得慢 (≥ MIN_SAVE_S) 的结果写盘。
改一个常量 ⇒ 只有用到它的那串运算键变了要重算, 其余全命中。

环境变量:
  GEO_CACHE=0       关掉 (全部现算, 与原来完全一样)
  GEO_CACHE=verify  命中时也现算一遍, 比体积/包围盒, 不一致就报错 (查缓存正确性用)
  GEO_CACHE_DIR     缓存目录 (默认 ~/.cache/macha_geo; 放 Linux 盘, /mnt/d 小文件读写慢)
  GEO_CACHE_STATS=1 进程结束打印命中统计
清缓存: rm -rf ~/.cache/macha_geo (随时可删, 只影响速度)
"""
import os, sys, time, hashlib, atexit
from pathlib import Path

VERSION = 'g1'                                   # 改了键的算法就加 1, 旧缓存自动作废
MODE = os.environ.get('GEO_CACHE', '1').lower()
ON = MODE not in ('0', 'off', 'no', 'false')
VERIFY = MODE == 'verify'
DIR = Path(os.environ.get('GEO_CACHE_DIR', Path.home() / '.cache' / 'macha_geo')) / VERSION
MIN_SAVE_S = 0.01                                # 算得比这快的不写盘 (读文件也要 ~1 ms)
if ON: DIR.mkdir(parents=True, exist_ok=True)

_REG = {}                                        # id(shape) → (key, shape); 持有引用防 id 复用
ST = dict(hit=0, miss=0, saved=0, fp=0, fp_s=0.0, run_s=0.0, load_s=0.0, saved_s=0.0)


def _h(*parts):
    return hashlib.sha1(repr(parts).encode()).hexdigest()


def _r(v):                                       # 浮点统一到 1e-9, 免得 -0.0 / 末位噪声
    v = round(float(v), 9)
    return 0.0 if v == 0 else v


def tag(shape, *parts):
    """给基本体挂键 (参数决定几何, 不用算指纹)。"""
    if ON: _REG[id(shape)] = (_h(VERSION, *parts), shape)
    return shape


def fingerprint(s):
    """几何指纹: 顶点 + 边采样点 + 面采样点 + 朝向。"""
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_VERTEX, TopAbs_EDGE, TopAbs_FACE
    from OCP.TopoDS import TopoDS
    from OCP.BRep import BRep_Tool
    from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
    from OCP.BRepTools import BRepTools
    t0 = time.perf_counter()
    m = hashlib.sha1(); m.update(f'{s.ShapeType()}|{s.Orientation()}|'.encode())
    e = TopExp_Explorer(s, TopAbs_VERTEX)
    while e.More():
        p = BRep_Tool.Pnt_s(TopoDS.Vertex(e.Current())); m.update(f'v{_r(p.X())},{_r(p.Y())},{_r(p.Z())}'.encode()); e.Next()
    e = TopExp_Explorer(s, TopAbs_EDGE)
    while e.More():
        ed = TopoDS.Edge(e.Current())
        if BRep_Tool.Degenerated_s(ed): m.update(b'dg')
        else:
            c = BRepAdaptor_Curve(ed); a, b = c.FirstParameter(), c.LastParameter()
            for f in (0.37, 0.71):
                p = c.Value(a + (b - a) * f); m.update(f'e{_r(p.X())},{_r(p.Y())},{_r(p.Z())}'.encode())
        e.Next()
    e = TopExp_Explorer(s, TopAbs_FACE)
    while e.More():
        fc = TopoDS.Face(e.Current()); u0, u1, v0, v1 = BRepTools.UVBounds_s(fc); sf = BRepAdaptor_Surface(fc)
        m.update(f'f{int(fc.Orientation())}t{int(sf.GetType())}'.encode())
        for fu, fv in ((0.29, 0.43), (0.61, 0.77)):
            p = sf.Value(u0 + (u1 - u0) * fu, v0 + (v1 - v0) * fv); m.update(f'{_r(p.X())},{_r(p.Y())},{_r(p.Z())}'.encode())
        e.Next()
    ST['fp'] += 1; ST['fp_s'] += time.perf_counter() - t0
    if os.environ.get('GEO_CACHE_DEBUG') and time.perf_counter() - t0 > 0.05:
        import traceback; fr = [x for x in traceback.extract_stack()[:-1] if 'geocache' not in x.filename][-1]
        print(f'[geocache] 指纹慢 {time.perf_counter() - t0:.2f}s  {Path(fr.filename).name}:{fr.lineno} {fr.line[:90]}', file=sys.stderr)
    return 'fp' + m.hexdigest()


def key(s):
    k = _REG.get(id(s))
    if k is not None and k[1] is s: return k[0]
    k = _h(VERSION, 'fp', fingerprint(s))
    _REG[id(s)] = (k, s)
    return k


def _bbox(s):
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    b = Bnd_Box(); BRepBndLib.Add_s(s, b, False); p, q = b.CornerMin(), b.CornerMax()
    return (p.X(), p.Y(), p.Z(), q.X(), q.Y(), q.Z())


def _vol(s):
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import BRepGProp
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()


def run(parts, fn):
    """parts: 键的组成 (运算名, 输入键..., 参数...); fn: 现算函数。返回带键的形体。"""
    if not ON: return fn()
    from OCP.BinTools import BinTools, BinTools_FormatVersion
    from OCP.TopoDS import TopoDS_Shape
    k = _h(VERSION, *parts); f = DIR / k[:2] / f'{k}.bin'
    if f.exists():
        t0 = time.perf_counter(); sh = TopoDS_Shape()
        try:
            BinTools.Read_s(sh, str(f)); ok = not sh.IsNull()
        except Exception:
            ok = False
        if ok:
            ST['hit'] += 1; ST['load_s'] += time.perf_counter() - t0
            if VERIFY:
                ref = fn(); a, b = _vol(sh), _vol(ref)
                if abs(a - b) > 1e-6 * max(1.0, abs(b)) or max(abs(x - y) for x, y in zip(_bbox(sh), _bbox(ref))) > 1e-6:
                    raise AssertionError(f'geocache 校验失败 {parts[0]} {k}: 缓存体积 {a} ≠ 现算 {b}')
            _REG[id(sh)] = (k, sh)
            return sh
    t0 = time.perf_counter(); sh = fn(); dt = time.perf_counter() - t0
    ST['miss'] += 1; ST['run_s'] += dt
    if dt >= MIN_SAVE_S and not sh.IsNull():
        try:
            f.parent.mkdir(exist_ok=True); tmp = f.with_suffix(f'.{os.getpid()}.tmp')
            BinTools.Write_s(sh, str(tmp), False, False, BinTools_FormatVersion.BinTools_FormatVersion_CURRENT)   # 不带三角网格
            os.replace(tmp, f); ST['saved'] += 1; ST['saved_s'] += dt
        except Exception as ex:
            print(f'[geocache] 写缓存失败 (不影响结果): {ex!r}', file=sys.stderr)
    _REG[id(sh)] = (k, sh)
    return sh


def trsf_parts(t):
    return tuple(_r(t.Value(i, j)) for i in (1, 2, 3) for j in (1, 2, 3, 4))


def stats():
    return (f"[geocache] 命中 {ST['hit']} (读盘 {ST['load_s']:.1f}s) / 现算 {ST['miss']} ({ST['run_s']:.1f}s, 写盘 {ST['saved']}) / "
            f"指纹 {ST['fp']} ({ST['fp_s']:.1f}s)")


if ON and os.environ.get('GEO_CACHE_STATS'):
    atexit.register(lambda: print(stats(), file=sys.stderr))
