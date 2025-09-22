from __future__ import annotations
import json, time
from datetime import date, timedelta
import requests
from requests.adapters import HTTPAdapter, Retry
from .config import BASE_URL, USER_AGENT, REQUESTS_PER_SEC

def make_session():
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT, "Accept": "application/json,text/plain,*/*"})
    retry = Retry(total=5, backoff_factor=0.5,
                  status_forcelist=(429,500,502,503,504),
                  allowed_methods=frozenset({"GET"}), respect_retry_after_header=True)
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.mount("http://", HTTPAdapter(max_retries=retry))
    return s

def daterange(d1: date, d2: date):
    cur, one = d1, timedelta(days=1)
    while cur <= d2:
        yield cur
        cur += one

def load_json(sess: requests.Session, day: date):
    url = BASE_URL.format(y=day.year, m=day.month, d=day.day)
    resp = sess.get(url, timeout=20)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return json.loads(resp.text)

def extract_rate(payload: dict, code: str):
    v = (payload.get("Valute") or {}).get(code)
    if not v: return None
    value, nominal = float(v["Value"]), int(v.get("Nominal", 1))
    return value/nominal if nominal else value

def polite_delay():
    time.sleep(1.0 / REQUESTS_PER_SEC)
