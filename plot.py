import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import numpy as np
import statistics
from io import BytesIO

font_path = os.path.join("fonts", "NotoSansCJKtc-Regular.otf")
font_prop = None

if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    font_name = font_prop.get_name()
    plt.rcParams["font.family"] = font_name
    print(f"use chinese font：{font_name}")
else:
    print("chinese font not found")

plt.rcParams["axes.unicode_minus"] = False


def generate_price_chart(data, plan="Standard", output_path="static/price_chart.png"):
    filtered = [d for d in data if isinstance(d.get("price_twd"), (int, float))]
    if not filtered:
        return

    if os.path.exists(output_path):
        os.remove(output_path)

    sorted_data = sorted(filtered, key=lambda x: x["price_twd"])
    prices = [d["price_twd"] for d in sorted_data]
    countries = [d["country"] for d in sorted_data]


    q1 = np.percentile(prices, 25, method="nearest")
    q2 = np.percentile(prices, 50, method="nearest")
    q3 = np.percentile(prices, 75, method="nearest")

    def find_index(p):
        for i, v in enumerate(prices):
            if v == p:
                return i
        return -1

    markers = {
        "最便宜": (0, prices[0], countries[0]),
        "25% 分位": (find_index(q1), q1, countries[find_index(q1)]),
        "中位數": (find_index(q2), q2, countries[find_index(q2)]),
        "75% 分位": (find_index(q3), q3, countries[find_index(q3)]),
        "最貴": (len(prices) - 1, prices[-1], countries[-1])
    }


    plt.figure(figsize=(max(14, len(countries) * 0.2), 6))  # X 軸動態調整寬度
    plt.plot(range(len(prices)), prices, color="blue", linewidth=2)

    for label, (x, y, cname) in markers.items():
        plt.scatter(x, y, label=f"{label}（{cname}）", s=80)
        plt.text(x, y + 15, f"{label}\n{cname}", ha="center", va="bottom", fontsize=9, fontproperties=font_prop)

    plt.xticks(ticks=range(len(countries)), labels=countries, rotation=90, fontsize=7, fontproperties=font_prop)
    plt.title(f"Netflix {plan} 全球價格分布（含國家名稱）", fontproperties=font_prop)
    plt.xlabel("國家（依價格排序）", fontproperties=font_prop)
    plt.ylabel("價格（TWD）", fontproperties=font_prop)
    plt.grid(True)
    plt.legend(prop=font_prop)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png", dpi=200)
    plt.close()
    buf.seek(0)
    return buf

def compute_stats(data):
    filtered = [d["price_twd"] for d in data if isinstance(d.get("price_twd"), (int, float))]
    if not filtered:
        return None
    return {
        "count": len(filtered),
        "avg": round(statistics.mean(filtered), 2),
        "stdev": round(statistics.stdev(filtered), 2) if len(filtered) >= 2 else 0,
        "min": round(min(filtered), 2),
        "max": round(max(filtered), 2)
    }