#!/usr/bin/env bash
# POV3D V1.2 按键板: 原理图 + PCB 生成 → 铺铜 → ERC/DRC(含原理图一致性) → 出厂文件 / 预览
#   bash scripts/build_all.sh        (在 key_board_v1_2/ 下或任意目录)
set -euo pipefail
D="$(cd "$(dirname "$0")/.." && pwd)"; cd "$D"
N=key_board_v1_2
VENV=../../../.venv/bin/python
python3 scripts/gen_sch.py
python3 scripts/gen_pcb.py 2>&1 | grep -v 'property.h' || true
# 原生铺铜 + DRC (含 schematic parity) 并存板
kicad-cli pcb drc --refill-zones --save-board --severity-all -o review/drc.rpt $N.kicad_pcb >/dev/null
# 铺铜碎块补缝合孔 (有补就再铺一次)
python3 scripts/stitch_islands.py $N.kicad_pcb 2>&1 | grep -v 'property.h' || true
kicad-cli pcb drc --refill-zones --save-board --schematic-parity --severity-all -o review/drc.rpt $N.kicad_pcb >/dev/null
kicad-cli sch erc --severity-all -o review/erc.rpt $N.kicad_sch >/dev/null
grep -E 'Found|ERC messages' review/drc.rpt review/erc.rpt
# 出厂 (JLC): gerber + 钻孔 → zip
rm -rf fab && mkdir -p fab/gerber
kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,Edge.Cuts \
  --no-x2 --use-drill-file-origin -o fab/gerber/ $N.kicad_pcb >/dev/null
kicad-cli pcb export drill --format excellon --excellon-separate-th --generate-map --map-format gerberx2 -o fab/gerber/ $N.kicad_pcb >/dev/null
python3 -c "import zipfile,glob,os; z=zipfile.ZipFile('fab/${N}_gerber_JLC.zip','w',zipfile.ZIP_DEFLATED); [z.write(f, os.path.basename(f)) for f in sorted(glob.glob('fab/gerber/*'))]; z.close()"
# BOM (按值+封装+LCSC 合并) / CPL
kicad-cli sch export bom --fields 'Value,Reference,Footprint,LCSC,MPN,${QUANTITY}' \
  --labels 'Comment,Designator,Footprint,LCSC Part #,MPN,Qty' --group-by 'Value,Footprint,LCSC' --ref-range-delimiter '' \
  -o fab/${N}_BOM_JLC.csv $N.kicad_sch >/dev/null
kicad-cli pcb export pos --format csv --units mm --side both --exclude-dnp -o fab/${N}_pos_raw.csv $N.kicad_pcb >/dev/null
python3 - "$D/fab/${N}_pos_raw.csv" "$D/fab/${N}_CPL_JLC.csv" <<'E'
import csv, sys
rows = list(csv.DictReader(open(sys.argv[1])))
with open(sys.argv[2], 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['Designator', 'Mid X', 'Mid Y', 'Layer', 'Rotation'])
    for r in rows:
        if r['Ref'].startswith('H'):
            continue
        w.writerow([r['Ref'], r['PosX'] + 'mm', r['PosY'] + 'mm', 'Top' if r['Side'] == 'top' else 'Bottom', r['Rot']])
E
rm -f fab/${N}_pos_raw.csv
# 原理图 PDF / 渲染
kicad-cli sch export pdf -o $N.pdf $N.kicad_sch >/dev/null
mkdir -p preview
kicad-cli pcb render --side top -w 1800 -h 1100 --quality high --background opaque -o preview/${N}_top.png $N.kicad_pcb >/dev/null
kicad-cli pcb render --side bottom -w 1800 -h 1100 --quality high --background opaque -o preview/${N}_bottom.png $N.kicad_pcb >/dev/null
python3 scripts/dump_geom.py review/_geom.json 2>&1 | grep -v 'property.h' || true
$VENV scripts/plot_layers.py review/_geom.json preview/${N}_copper.png && rm -f review/_geom.json
ls -la fab preview $N.pdf
