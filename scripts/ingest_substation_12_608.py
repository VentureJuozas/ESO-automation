"""Copy the 12-608 substation datasets into data/substation_12-608/ and build a redacted TS history.

Raw files (customer locations, meter serials) go to data/substation_12-608/raw/ which is git-ignored.
The redacted TS history (no addresses, meter/client/object numbers) is safe to commit.

Usage: python scripts/ingest_substation_12_608.py [source_dir]   (default: ~/Downloads)
"""
import csv
import re
import shutil
import sys
from pathlib import Path

import openpyxl

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Downloads"
ROOT = Path(__file__).resolve().parent.parent / "data" / "substation_12-608"
RAW = ROOT / "raw"
RAW.mkdir(parents=True, exist_ok=True)

CSV_FILES = [
    "pastotes_load_kas15min.csv",
    "meter_min_max_avg_load.csv",
    "min_itampa.csv",
    "Substations_info.csv",
    "Objects_network_power.csv",
]
for name in CSV_FILES:
    shutil.copy2(SRC / name, RAW / name)
shutil.copy2(SRC / "TS_istorija.xlsx", RAW / "TS_istorija.xlsx")

# --- redacted TS history -------------------------------------------------------------------
PII_PATTERNS = [
    r"\(?\s*(?:Kliento|kliento)?\s*(?:skaitiklio|Skaitiklio|sk\.|Sk\.)?\s*(?:Nr\.?|numeris)[^)]*\)",  # "(Kliento skaitiklio Nr..., obj. Nr...)"
    r"\((?:sk|Sk|Kliento|kliento|elektros)[^)]*(?:Nr|Obj|obj)[^)]*\)",
]


def redact(text: str) -> str:
    if not text:
        return ""
    for p in PII_PATTERNS:
        text = re.sub(p, "(...)", text)
    return text.strip()


wb = openpyxl.load_workbook(RAW / "TS_istorija.xlsx", data_only=True)
ws = wb.worksheets[0]
rows = list(ws.iter_rows(values_only=True))
header = list(rows[0])
drop = {"Objekto adresas", "Objektas"}  # customer address / object name
keep_idx = [i for i, h in enumerate(header) if h not in drop]
with open(ROOT / "ts_history_redacted.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow([header[i] for i in keep_idx])
    for r in rows[1:]:
        out = []
        for i in keep_idx:
            v = r[i]
            if header[i] == "TS tekstas":
                v = redact(v or "")
            out.append("" if v is None else v)
        w.writerow(out)
print("ok", ROOT)
