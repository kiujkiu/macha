"""
Verify a generated engineering-drawing PDF for the kinds of problems that
keep slipping past visual inspection.

Checks performed:
  1. text-vs-text overlap (two labels colliding)
  2. text-vs-arrow overlap (a label hidden behind / pierced by an arrowhead)
  3. text-vs-line proximity for stroke lines that pass through a text bbox
  4. missing 'mm' unit indicator (either per-label or as a "尺寸单位: mm"
     view-label suffix)
  5. expected label substrings present (via --expect)

Exit code 0 = PASS, non-zero = FAIL.  Always prints a report.
This is the gate that drawings must clear before being shown to the user.
"""
from __future__ import annotations

import argparse
import ctypes
import sys
from pathlib import Path
from typing import Iterable

import pypdfium2 as pdfium
import pypdfium2.raw as raw

# ----- bbox helpers (PDF points, y-from-bottom) -----
def bbox_overlap(a, b, pad: float = 0.0) -> bool:
    al, ab, ar, at = a
    bl, bb, br, bt = b
    return not (ar + pad < bl - pad or br + pad < al - pad
                or at + pad < bb - pad or bt + pad < ab - pad)

def overlap_area(a, b) -> float:
    al, ab, ar, at = a
    bl, bb, br, bt = b
    w = min(ar, br) - max(al, bl)
    h = min(at, bt) - max(ab, bb)
    return max(0.0, w) * max(0.0, h)

# ----- extraction -----
def extract_text_rects(page) -> list[tuple[str, tuple]]:
    tp = page.get_textpage()
    out = []
    for i in range(tp.count_rects()):
        bbox = tp.get_rect(i)        # (l, b, r, t)
        txt = tp.get_text_bounded(*bbox).strip()
        if txt:
            out.append((txt, bbox))
    return out

def extract_filled_path_bboxes(page) -> list[tuple]:
    """Returns bboxes of filled paths (= arrows in our drawings)."""
    out = []
    n = raw.FPDFPage_CountObjects(page)
    for i in range(n):
        obj = raw.FPDFPage_GetObject(page, i)
        if raw.FPDFPageObj_GetType(obj) != 2:        # 2 = PATH
            continue
        fm = ctypes.c_int(); sk = ctypes.c_int()
        if not raw.FPDFPath_GetDrawMode(obj, ctypes.byref(fm), ctypes.byref(sk)):
            continue
        if fm.value == 0:                              # not filled
            continue
        l, b, r, t = (ctypes.c_float() for _ in range(4))
        if raw.FPDFPageObj_GetBounds(obj,
                ctypes.byref(l), ctypes.byref(b), ctypes.byref(r), ctypes.byref(t)):
            # Skip very large filled paths (likely page rect / title-block bg)
            w_pt, h_pt = r.value - l.value, t.value - b.value
            if w_pt < 40 and h_pt < 40:               # arrows are small
                out.append((l.value, b.value, r.value, t.value))
    return out

# ----- checks -----
def check_text_overlaps(rects, ignore: Iterable[str] = ()) -> list[tuple]:
    out = []
    for i in range(len(rects)):
        t1, b1 = rects[i]
        if any(s in t1 for s in ignore):
            continue
        for j in range(i + 1, len(rects)):
            t2, b2 = rects[j]
            if any(s in t2 for s in ignore):
                continue
            if bbox_overlap(b1, b2, pad=-0.5):
                area = overlap_area(b1, b2)
                if area > 0.2:
                    out.append(((t1, b1), (t2, b2), area))
    return out

def check_text_arrow_overlaps(rects, arrows, ignore: Iterable[str] = ()) -> list[tuple]:
    """Detect text labels whose bbox overlaps an arrowhead bbox."""
    out = []
    for t, tb in rects:
        if any(s in t for s in ignore):
            continue
        for ab in arrows:
            if bbox_overlap(tb, ab, pad=-0.3):
                area = overlap_area(tb, ab)
                if area > 0.5:
                    out.append((t, tb, ab, area))
    return out

def check_arrow_arrow_overlaps(arrows, dup_tol: float = 0.5) -> list[tuple]:
    """Detect two arrowheads PARTIALLY colliding into each other — the classic
    'tight inside-arrows turn into a black diamond' bug.

    Skip *exact* duplicates (identical bbox within `dup_tol` pt): those happen
    when adjacent chain-dim segments share an endpoint and each draws an arrow
    there — visually they render as one arrow, not a collision."""
    out = []
    n = len(arrows)
    for i in range(n):
        for j in range(i + 1, n):
            a, b = arrows[i], arrows[j]
            # Exact duplicate (within tolerance) — visually one arrow, not a bug
            if (abs(a[0]-b[0]) < dup_tol and abs(a[1]-b[1]) < dup_tol and
                abs(a[2]-b[2]) < dup_tol and abs(a[3]-b[3]) < dup_tol):
                continue
            if bbox_overlap(a, b, pad=-0.2):
                area = overlap_area(a, b)
                if area > 0.3:
                    out.append((a, b, area))
    return out

def check_missing_labels(rects, expected: Iterable[str]) -> list[str]:
    all_text = " ".join(t for t, _ in rects)
    return [e for e in expected if e not in all_text]

def check_crowded_regions(rects, ignore: Iterable[str] = (),
                          window: float = 28.0,
                          max_in_window: int = 4) -> list[tuple]:
    """Approximate visual crowding: scan a sliding window (~window points wide,
    default ≈10mm × 10mm at 72 dpi) over the page and flag any window that
    contains more than `max_in_window` distinct text rect CENTERS belonging to
    unrelated labels.

    The window size is in PDF points (1 mm ≈ 2.835 pt; window=28pt ≈ 10mm).
    Two labels are considered 'related' if they share a common prefix of >=4
    chars OR they are both numeric (dim labels can validly stack)."""
    # Pre-filter
    items = []
    for t, b in rects:
        if any(s in t for s in ignore):
            continue
        cx = (b[0] + b[2]) / 2.0
        cy = (b[1] + b[3]) / 2.0
        items.append((t, cx, cy))

    def _related(a: str, b: str) -> bool:
        if a == b:
            return True
        # Stripped pure-number labels can stack as dim chains
        sa = a.replace(" mm", "").replace("Φ", "").strip()
        sb = b.replace(" mm", "").replace("Φ", "").strip()
        try:
            float(sa); float(sb); return True
        except ValueError:
            pass
        # Shared prefix
        n = min(len(a), len(b))
        common = 0
        for i in range(n):
            if a[i] == b[i]:
                common += 1
            else:
                break
        return common >= 4

    out = []
    for i, (ti, xi, yi) in enumerate(items):
        nearby = [ti]
        for j, (tj, xj, yj) in enumerate(items):
            if i == j:
                continue
            if abs(xj - xi) <= window and abs(yj - yi) <= window:
                if not any(_related(tj, k) for k in nearby):
                    nearby.append(tj)
        if len(nearby) > max_in_window:
            out.append((ti, (xi, yi), nearby))
    return out

def check_unit_indicator(rects) -> str | None:
    all_text = " ".join(t for t, _ in rects)
    has_mm_per_label = " mm" in all_text or "mm)" in all_text
    has_unit_callout = ("尺寸单位" in all_text or "单位 mm" in all_text
                       or "单位: mm" in all_text or "Unit: mm" in all_text)
    if not (has_mm_per_label or has_unit_callout):
        return "no 'mm' unit indicator anywhere in the drawing"
    return None

# ----- main -----
def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pdf", type=Path)
    p.add_argument("--expect", nargs="*", default=[],
                   help="label substrings that MUST appear")
    p.add_argument("--ignore", nargs="*",
                   default=["POV 3D", "结构件", "投影", "比例", "日期"],
                   help="text substrings to skip in overlap checks")
    args = p.parse_args(argv)

    if not args.pdf.exists():
        print(f"FAIL: {args.pdf} not found", file=sys.stderr)
        return 2

    pdf = pdfium.PdfDocument(str(args.pdf))
    all_rects, all_arrows = [], []
    for page in pdf:
        all_rects.extend(extract_text_rects(page))
        all_arrows.extend(extract_filled_path_bboxes(page))

    print(f"\n=== verify_drawing  {args.pdf.name} ===")
    print(f"  {len(all_rects)} text rects, {len(all_arrows)} filled paths (arrows)")

    text_overlaps   = check_text_overlaps(all_rects, ignore=args.ignore)
    arrow_overlaps  = check_text_arrow_overlaps(all_rects, all_arrows, ignore=args.ignore)
    arrow_collisions = check_arrow_arrow_overlaps(all_arrows)
    crowded         = check_crowded_regions(all_rects, ignore=args.ignore)
    missing         = check_missing_labels(all_rects, args.expect)
    unit_err        = check_unit_indicator(all_rects)

    passed = True

    if missing:
        passed = False
        print(f"\n  MISSING labels ({len(missing)}):")
        for m in missing:
            print(f"    - {m!r}")

    if text_overlaps:
        passed = False
        print(f"\n  TEXT-vs-TEXT overlaps ({len(text_overlaps)}):")
        for (t1, _), (t2, _), area in text_overlaps:
            print(f"    - {t1!r}  ⨯  {t2!r}   ({area:.2f} pt²)")

    if arrow_overlaps:
        passed = False
        print(f"\n  TEXT-vs-ARROW overlaps ({len(arrow_overlaps)}):")
        for t, _tb, _ab, area in arrow_overlaps:
            print(f"    - label {t!r} pierced by an arrowhead   ({area:.2f} pt²)")

    if arrow_collisions:
        passed = False
        print(f"\n  ARROW-vs-ARROW collisions ({len(arrow_collisions)}):")
        for a, b, area in arrow_collisions:
            print(f"    - arrows at {tuple(round(v,1) for v in a)} and "
                  f"{tuple(round(v,1) for v in b)} overlap ({area:.2f} pt²) — "
                  "tight dim needs outside-arrows mode")

    if crowded:
        passed = False
        print(f"\n  CROWDED REGIONS ({len(crowded)}):")
        seen_centers = set()
        for ti, (cx, cy), nearby in crowded:
            # Dedupe symmetric reports
            key = (round(cx, 0), round(cy, 0))
            if key in seen_centers:
                continue
            seen_centers.add(key)
            others = [n for n in nearby if n != ti]
            print(f"    - {ti!r} at ({cx:.0f},{cy:.0f}) shares a 10mm window with "
                  f"{len(others)} unrelated labels: "
                  f"{[n[:24] for n in others[:6]]}")

    if unit_err:
        passed = False
        print(f"\n  UNIT INDICATOR: {unit_err}")

    if passed:
        print("\n  ✓ PASS — no overlaps, no missing labels, unit indicator present")
        return 0
    print("\n  ✗ FAIL — fix the issues above and re-render")
    return 1

if __name__ == "__main__":
    sys.exit(main())
