from __future__ import annotations
import csv
import json
import time
from datetime import date, timedelta
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter, Retry

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


OUT_CSV = Path("dataset.csv")
START_DATE = date(2020, 1, 1)
END_DATE   = date(2020, 12, 31)
REQUESTS_PER_SEC = 4  # не больше 5/сек
BASE = "https://www.cbr-xml-daily.ru/archive/{y:04d}/{m:02d}/{d:02d}/daily_json.js"


def daterange(d1: date, d2: date):
    cur = d1
    one = timedelta(days=1)
    while cur <= d2:
        yield cur
        cur = cur + one

def extract_usd_rate(payload: dict):
    valute = payload.get("Valute") or {}
    usd = valute.get("USD")
    if not usd:
        return None
    value = float(usd["Value"])
    nominal = int(usd.get("Nominal", 1))
    return value / nominal if nominal else value

def make_session():
    sess = requests.Session()
    sess.headers.update(
        {
            "User-Agent": "LabScraper/1.0 (+https://example.edu)",
            "Accept": "application/json,text/plain,*/*",
        }
    )
    retry = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        respect_retry_after_header=True,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    sess.mount("https://", adapter)
    sess.mount("http://", adapter)
    return sess

def load_json(sess: requests.Session, day: date):
    url = BASE.format(y=day.year, m=day.month, d=day.day)
    resp = sess.get(url, timeout=20)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return json.loads(resp.text)

def read_existing_last_date(csv_path: Path):
    if not csv_path.exists():
        return None
    last = None
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        next(r, None)
        for row in r:
            if not row:
                continue
            last = row[0]
    if last:
        y, m, d = map(int, last.split("-"))
        return date(y, m, d) + timedelta(days=1)
    return None

def ensure_header(csv_path: Path):
    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["date", "rate"])

def append_row(csv_path: Path, day: date, rate: float):
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([day.isoformat(), f"{rate:.6f}"])

#для графика
def load_series(csv_path: Path):
    dates, rates = [], []
    if not csv_path.exists():
        return dates, rates
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        next(r, None)
        for row in r:
            if len(row) < 2:
                continue
            try:
                d = date.fromisoformat(row[0])
                v = float(row[1])
            except Exception:
                continue
            dates.append(d)
            rates.append(v)
    return dates, rates

def plot_usd_curve(csv_path: Path, png_path: Path = Path("Nazvanie.png")):
    dates, rates = load_series(csv_path)
    if not dates:
        print("Нет данных для графика.")
        return
    plt.figure(figsize=(12, 6))
    plt.plot(dates, rates, marker="o", linewidth=1, markersize=2, label="USD/RUB")
    plt.title("Курс доллара (USD/RUB), ЦБ РФ — 2020")
    plt.xlabel("Дата")
    plt.ylabel("Курс, ₽")
    plt.grid(True)
    ax = plt.gca()
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    plt.legend()
    plt.tight_layout()
    plt.savefig(png_path, dpi=150)
    print(f"График сохранён: {png_path.resolve()}")
    plt.show()


def main():
    ensure_header(OUT_CSV)
    start = read_existing_last_date(OUT_CSV) or START_DATE

   
    sess = make_session()
    delay = 1.0 / REQUESTS_PER_SEC

    saved, missing = 0, 0
    for day in daterange(start, END_DATE):
        try:
            payload = load_json(sess, day)
        except requests.RequestException as exc:
            print(f"{day.isoformat()}: ошибка сети: {exc}")
            time.sleep(delay)
            continue

        if not payload:
            missing += 1
            time.sleep(delay)
            continue

        rate = extract_usd_rate(payload)
        if rate is None:
            missing += 1
            time.sleep(delay)
            continue

        append_row(OUT_CSV, day, rate)
        saved += 1
        if saved % 50 == 0:
            print(f"сохранено {saved} строк, пропусков {missing}…")

        time.sleep(delay)

    print(f"Готово: сохранено {saved} строк, пропущено {missing}. Файл: {OUT_CSV.resolve()}")

    plot_usd_curve(OUT_CSV)

if __name__ == "__main__":
    main()
