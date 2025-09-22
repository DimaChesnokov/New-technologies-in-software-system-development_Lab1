import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

def plot_curve(dates, rates, code: str, out_png: Path):
    if not dates: 
        print("Нет данных для графика."); return
    plt.figure(figsize=(12,6))
    plt.plot(dates, rates, marker="o", linewidth=1, markersize=2, label=f"{code}/RUB")
    plt.title(f"Курс {code}/RUB, ЦБ РФ — 2020")
    plt.xlabel("Дата"); plt.ylabel("Курс, ₽"); plt.grid(True)
    ax = plt.gca()
    loc = mdates.AutoDateLocator(); ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))
    plt.legend(); plt.tight_layout(); out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=150); print(f"График сохранён: {out_png.resolve()}"); plt.show()
