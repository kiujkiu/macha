"""
V1.0 打印包 (2026-10-20): 把各零件 STL (打印姿态) + A3 图纸收进 v1.0/print/<件>/, 生成总览页,
合并成一本 v1_0_print_sheet.pdf, 再打 pov3d_v1_0_print.zip (zip 已 gitignore)。

前置: 各 models/*/build_stl.py (或 build_frame.py) → models/build_drawings_v1_0.py → assembly_v1_0.py。
之后 print/ 里的 STL/PDF 也可以用 ../tools/sync_print.py 按文件名同步。
"""
import shutil
import sys
import zipfile
from pathlib import Path

import pypdfium2 as pdfium

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "models"))
from drawing_v1_0 import PAGE_H, PAGE_W, Page, read_stl, _iso  # noqa: E402

PRINT = ROOT / "print"
M = ROOT / "models"
V04 = ROOT.parent / "v0.4"

# (文件夹, [(源, 打印包内文件名)], 数量, 打印姿态, 备注)
PARTS = [
    ("hub_disc_v1_0", [M / "hub_disc_v1_0/hub_disc_v1_0.stl", M / "hub_disc_v1_0/hub_disc_v1_0_drawing.pdf"],
     "1", "底面贴床", "转子下盘 Φ175 (外圈孔 R82.5)"),
    ("rim_ring_v1_0", [M / "rim_ring_v1_0/rim_ring_v1_0.stl", M / "rim_ring_v1_0/rim_ring_v1_0_drawing.pdf"],
     "1", "托盘面贴床", "转子承载盘 Φ180 + DR1M90 4 孔"),
    ("screen_foot_v1_0", [M / "screen_foot_v1_0/screen_foot_v1_0_posY.stl",
                          M / "screen_foot_v1_0/screen_foot_v1_0_negY.stl",
                          M / "screen_foot_v1_0/screen_foot_v1_0_drawing.pdf"],
     "posY ×1 + negY ×1", "内侧面贴床", "屏幕底座 (portal_tee 式), 两件互为镜像"),
    ("top_cap_v1_0", [M / "top_cap_v1_0/top_cap_v1_0.stl", M / "top_cap_v1_0/top_cap_v1_0_drawing.pdf"],
     "1", "顶面贴床", "屏幕顶盖 + 光电模块座"),
    ("wifi_plate_v1_0", [M / "wifi_plate_v1_0/wifi_plate_v1_0.stl", M / "wifi_plate_v1_0/wifi_plate_v1_0_drawing.pdf"],
     "1", "平放", "WiFi 托板 (H 形)"),
    ("top_bearing_frame_v1_0", [M / "top_bearing_v1_0/frame_A_v1_0.stl", M / "top_bearing_v1_0/frame_A_v1_0_drawing.pdf",
                                M / "top_bearing_v1_0/frame_B_v1_0.stl", M / "top_bearing_v1_0/frame_B_v1_0_drawing.pdf"],
     "A ×1 + B ×1", "STL 即姿态", "顶轴承架 (柱位 R107.53)"),
    ("vane_slider_v4", [V04 / "models/photo_sensor_v4/vane_slider_v4.stl",
                        V04 / "models/photo_sensor_v4/vane_slider_v4_drawing.pdf"],
     "1", "平躺 (Y2 面贴床)", "挡光滑片 (沿用 V0.4 件, 装机剪到筋底下 14.7)"),
]
REUSE = [
    ("baseplate_collar_v4 / flange_disc_v4 / mounting_flange_v4", "定子三件, V0.4 原件, 不用重打"),
    ("wifi_shell", "V0.4 原件可直接用 (v0.4/print/wifi_shell)"),
]


def overview_page(path):
    pg = Page()
    pg.rect(5, 5, PAGE_W - 5, PAGE_H - 5, lw=0.5)
    pg.text(PAGE_W / 2, PAGE_H - 14, "POV3D V1.0 打印清单 (验证板结构, 2026-10-20)", size=6.0, ha="center")
    pg.text(PAGE_W / 2, PAGE_H - 21, "PLA / 单位 mm / STL 均为打印姿态 (屏幕底座、顶盖已摆好), 每件一张 A3 图纸附后",
            size=3.2, ha="center")
    # 缩略图 + 表
    x0, y_top, cw, ch = 14.0, PAGE_H - 30, 56.0, 62.0
    k = 0
    for folder, files, qty, orient, desc in PARTS:
        for f in files:
            if f.suffix != ".stl":
                continue
            col, row = k % 7, k // 7
            bx, by = x0 + col * cw, y_top - (row + 1) * ch
            pg.rect(bx, by, bx + cw - 3, by + ch - 3, lw=0.2)
            tris = read_stl(f)
            _iso(pg, _P(tris), (bx + 2, by + 18, bx + cw - 5, by + ch - 6))
            pg.text(bx + 2, by + 13, f.stem, size=2.7)
            pg.text(bx + 2, by + 8.5, desc if len(desc) < 22 else desc[:21] + "…", size=2.3)
            pg.text(bx + 2, by + 4.2, f"打 1 件 / {orient}", size=2.2)
            k += 1
    y = y_top - 2 * ch - 8
    pg.text(14, y, "沿用 (不用打)", size=3.6)
    y -= 5.5
    for nm, why in REUSE:
        pg.text(18, y, f"· {nm}: {why}", size=2.9)
        y -= 4.5
    y -= 3
    pg.text(14, y, "五金 (V1.0 新增/变化部分, 详见 print/README.md)", size=3.6)
    y -= 5.5
    for ln in HARDWARE:
        pg.text(18, y, "· " + ln, size=2.8)
        y -= 4.3
    pg.save(path)


class _P:
    def __init__(self, tris):
        self.tris = tris


HARDWARE = [
    "M3 通孔六角铜螺母 对边 4.6 × 长 4.0 ×12 —— 焊在两块灯板背面, 每板 6 颗 (每侧 3 组, A 焊上颗 / B 焊下颗)",
    "屏幕锁紧 M3 (头 Φ7×1.5): 上 M3×16 ×2 (顶盖往下) / 下 M3×120 ×2 (底座往上, 非标, 可用 M3 牙条 + 螺母)",
    "屏幕底座 → hub_disc: M3×14 ×4, 拧进 hub_disc 底面铜螺母 (D 组 67.5/112.5/247.5/292.5°)",
    "DR1M90 底板: M3×5 尼龙垫柱 ×4 + 螺丝, rim_ring E 组压铜螺母 ×4",
    "WiFi 托板: M3×25 尼龙螺柱 (公母) ×4 + M3 螺丝 ×4; 罩沿 M3×10 ×4 (从托板底往上) + 螺母 ×4",
    "顶部: M6×20 平头 ×1 + Φ8×45 螺柱 ×1 + 688 轴承 ×2; 立柱 Φ8 × 360 ×4 (V0.4 是 290, 要换长柱)",
    "轴承架: M6×16 ×2 (A) + M6×30 ×2 (B) + M3×20+螺母 ×4; 挡光滑片 M3×20+螺母 ×2",
    "光电模块: M3×10 + 螺母 ×2 (螺丝从顶盖底面往上, 头沉 Φ7.5×2.5 窝)",
    "铜螺母 M3 (Φ4.2 孔): hub_disc / rim_ring 按图纸孔表压, 至少 hub D 组 4 + rim E 组 4",
]


def main():
    PRINT.mkdir(exist_ok=True)
    for folder, files, *_ in PARTS:
        d = PRINT / folder
        d.mkdir(exist_ok=True)
        for f in files:
            assert f.exists(), f
            shutil.copy2(f, d / f.name)
    a = PRINT / "assembly"
    a.mkdir(exist_ok=True)
    for f in ("assembly_v1_0.3mf", "assembly_v1_0_preview.png"):
        shutil.copy2(ROOT / f, a / f)
    ov = PRINT / "_overview.pdf"
    overview_page(ov)
    book = pdfium.PdfDocument.new()
    for src in [ov] + [f for _, files, *_ in PARTS for f in files if f.suffix == ".pdf"]:
        doc = pdfium.PdfDocument(str(src))
        book.import_pages(doc)
    out = PRINT / "v1_0_print_sheet.pdf"
    book.save(str(out))
    ov.unlink()
    (PRINT / "_overview_preview.png").replace(PRINT / "v1_0_print_sheet_preview.png")
    print(f"wrote {out} ({len(book)} 页)")
    z = PRINT / "pov3d_v1_0_print.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(PRINT.rglob("*")):
            if p.is_file() and p != z:
                zf.write(p, p.relative_to(PRINT))
    print(f"wrote {z} ({z.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
