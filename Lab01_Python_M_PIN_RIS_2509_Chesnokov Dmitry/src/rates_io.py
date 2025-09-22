from __future__ import annotations
import csv
from datetime import date, timedelta
from pathlib import Path

def ensure_header(csv_path: Path):
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["date", "rate"])

def read_next_date(csv_path: Path):
    if not csv_path.exists(): return None
    last = None
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        r = csv.reader(f); next(r, None)
        for row in r:
            if row: last = row[0]
    if last:
        y, m, d = map(int, last.split("-"))
        return date(y, m, d) + timedelta(days=1)
    return None

def append_row(csv_path: Path, day: date, rate: float):
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([day.isoformat(), f"{rate:.6f}"])

def load_series(csv_path: Path):
    dates, rates = [], []
    if not csv_path.exists(): return dates, rates
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        r = csv.reader(f); next(r, None)
        for dt, val, *rest in r:
            try:
                dates.append(date.fromisoformat(dt))
                rates.append(float(val))
            except: pass
    return dates, rates
