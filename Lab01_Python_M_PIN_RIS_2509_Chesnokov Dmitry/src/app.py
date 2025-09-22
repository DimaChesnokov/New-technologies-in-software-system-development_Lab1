from datetime import date
from .config import START_DATE, END_DATE, OUT_CSV, OUT_PNG, CURRENCY
from .cbr_client import make_session, daterange, load_json, extract_rate, polite_delay
from .rates_io import ensure_header, read_next_date, append_row, load_series
from .plotting import plot_curve

def main():
    ensure_header(OUT_CSV)
    start = read_next_date(OUT_CSV) or START_DATE
    sess = make_session()

    saved = missing = 0
    for day in daterange(start, END_DATE):
        try:
            payload = load_json(sess, day)
        except Exception as e:
            print(f"{day}: сеть: {e}"); polite_delay(); continue
        if not payload:
            missing += 1; polite_delay(); continue
        rate = extract_rate(payload, CURRENCY)
        if rate is None:
            missing += 1; polite_delay(); continue
        append_row(OUT_CSV, day, rate); saved += 1
        if saved % 50 == 0:
            print(f"сохранено {saved}, пропусков {missing}…")
        polite_delay()

    print(f"Готово: {saved} строк. CSV: {OUT_CSV}")
    dates, rates = load_series(OUT_CSV)
    plot_curve(dates, rates, CURRENCY, OUT_PNG)

if __name__ == "__main__":
    main()
