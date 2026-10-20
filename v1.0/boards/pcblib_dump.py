"""
Altium .PcbLib 封装解析 (只取结构要用的: 焊盘 / 孔 / 走线 / 圆弧, 按层统计), 单位 mm。
用法: ../../.venv/bin/python pcblib_dump.py <file.PcbLib> [封装名子串]
记录格式 (Data 流): 名字块 + 若干 [类型 u8][块...]; 坐标 int32, 单位 1e-4 mil。
"""
import struct
import sys
from collections import defaultdict
import olefile

U = 0.0254e-4                       # 1e-4 mil → mm
LAYER = {1: "Top", 32: "Bottom", 33: "TopOverlay", 34: "BottomOverlay", 74: "Multi"}
for i in range(57, 73):
    LAYER[i] = f"Mech{i-56}"


def blocks(buf, pos, n):
    out = []
    for _ in range(n):
        L = struct.unpack_from("<I", buf, pos)[0]
        out.append(buf[pos + 4:pos + 4 + L])
        pos += 4 + L
    return out, pos


def parse(data):
    L = struct.unpack_from("<I", data, 0)[0]
    pos = 4 + L
    prims = []
    while pos < len(data):
        t = data[pos]
        pos += 1
        if t == 2:                                  # pad: 6 块
            bl, pos = blocks(data, pos, 6)
            b = bl[4]
            name = bl[0][1:1 + bl[0][0]].decode("latin1") if bl[0] else ""
            x, y = struct.unpack_from("<ii", b, 13)
            sx, sy = struct.unpack_from("<ii", b, 21)
            hole = struct.unpack_from("<i", b, 45)[0]
            rot = struct.unpack_from("<d", b, 52)[0]
            prims.append(("pad", b[0], name, x * U, y * U, sx * U, sy * U, hole * U, rot))
        elif t in (1, 3, 4, 5, 6, 11, 12):
            nb = {1: 1, 3: 1, 4: 1, 5: 2, 6: 1, 11: 2, 12: 2}[t]
            bl, pos = blocks(data, pos, nb)
            b = bl[0]
            if t == 4:
                x1, y1, x2, y2, w = struct.unpack_from("<iiiii", b, 13)
                prims.append(("track", b[0], x1 * U, y1 * U, x2 * U, y2 * U, w * U))
            elif t == 1:
                cx, cy, r = struct.unpack_from("<iii", b, 13)
                a0, a1 = struct.unpack_from("<dd", b, 25)
                prims.append(("arc", b[0], cx * U, cy * U, r * U, a0, a1))
            elif t == 12:
                prims.append(("body", b[0], bl[1][:600]))
        else:
            break
    return prims


def main():
    ole = olefile.OleFileIO(sys.argv[1])
    want = sys.argv[2] if len(sys.argv) > 2 else ""
    for entry in ole.listdir():
        if len(entry) == 2 and entry[1] == "Data" and want in entry[0]:
            prims = parse(ole.openstream(entry).read())
            print(f"=== 封装 {entry[0]}: {len(prims)} 图元")
            bylayer = defaultdict(list)
            for p in prims:
                if p[0] == "track":
                    bylayer[p[1]] += [(p[2], p[3]), (p[4], p[5])]
                elif p[0] == "arc":
                    bylayer[p[1]] += [(p[2] - p[4], p[3] - p[4]), (p[2] + p[4], p[3] + p[4])]
            for ly, pts in sorted(bylayer.items()):
                xs, ys = [q[0] for q in pts], [q[1] for q in pts]
                print(f"  线 {LAYER.get(ly, ly)}: X {min(xs):.3f}..{max(xs):.3f}  Y {min(ys):.3f}..{max(ys):.3f}"
                      f"  ({max(xs)-min(xs):.3f} × {max(ys)-min(ys):.3f}), {len(pts)//2} 段")
            pads = [p for p in prims if p[0] == "pad"]
            holes = [p for p in pads if p[7] > 0.01]
            for h in holes:
                print(f"  孔 '{h[2]}' ({h[3]:.3f},{h[4]:.3f}) Φ{h[7]:.3f} 盘 {h[5]:.2f}×{h[6]:.2f} 层 {LAYER.get(h[1], h[1])}")
            smd = [p for p in pads if p[7] <= 0.01]
            groups = defaultdict(list)
            for p in smd:
                groups[round(p[3], 1) if abs(p[3]) > 1 else 0].append(p)
            # 按 X 聚类成排
            xs = sorted(set(round(p[3], 2) for p in smd))
            print(f"  SMD 焊盘 {len(smd)} 个, X 取值: {xs[:12]}{' ...' if len(xs) > 12 else ''}")
            if smd:
                ys = [p[4] for p in smd]
                print(f"    Y {min(ys):.3f}..{max(ys):.3f}; 盘 {smd[0][5]:.3f}×{smd[0][6]:.3f}; 层 {LAYER.get(smd[0][1])}")
                for x in xs:
                    row = sorted(p[4] for p in smd if round(p[3], 2) == x)
                    names = [p[2] for p in smd if round(p[3], 2) == x]
                    print(f"    排 X={x}: {len(row)} 盘, Y {row[0]:.3f}..{row[-1]:.3f}, 名 {names[:2]}..{names[-1:]}")
            for p in prims:
                if p[0] == "body":
                    txt = p[2].decode("latin1", "replace")
                    print("  3D body:", txt[:300].replace("\x00", ""))


if __name__ == "__main__":
    main()
