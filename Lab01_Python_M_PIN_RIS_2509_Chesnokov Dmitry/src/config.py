from datetime import date
from pathlib import Path

CURRENCY = "KZT"                    
START_DATE = date(2020, 1, 1)
END_DATE   = date(2020, 12, 31)
REQUESTS_PER_SEC = 4
OUT_CSV = Path("data") / f"dataset_{CURRENCY}.csv"
OUT_PNG = Path("data") / f"{CURRENCY}_rub_2020.png"

BASE_URL = "https://www.cbr-xml-daily.ru/archive/{y:04d}/{m:02d}/{d:02d}/daily_json.js"
USER_AGENT = "LabScraper/1.0 (+https://example.edu)"
