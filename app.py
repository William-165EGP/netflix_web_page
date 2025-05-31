from flask import Flask, render_template, request, send_file
from fetch_data import get_netflix_price_data
from currency import get_twd_exchange_rate
from plot import generate_price_chart, compute_stats
import csv
import io

app = Flask(__name__)

@app.route("/")
def index():
    plan = request.args.get("plan", "Standard")
    selected_country = request.args.get("country")  # pick the country
    search = request.args.get("search", "").strip().lower()  # search keyword

    data = get_netflix_price_data(plan)
    twd_rates = get_twd_exchange_rate()

    for item in data:
        cur = item["currency"].lower()
        rate = twd_rates.get(cur)
        if rate:
            item["price_twd"] = round(item["price"] / rate, 2)
        else:
            item["price_twd"] = None

    # search filter (according to keyword)
    if search:
        def match(item):
            keyword = search
            price = item.get("price_twd")

            try:
                if keyword.startswith(">="):
                    return price is not None and price >= float(keyword[2:])
                elif keyword.startswith("<="):
                    return price is not None and price <= float(keyword[2:])
                elif keyword.startswith(">"):
                    return price is not None and price > float(keyword[1:])
                elif keyword.startswith("<"):
                    return price is not None and price < float(keyword[1:])
                elif keyword.startswith("="):
                    return price is not None and price == float(keyword[1:])
                elif keyword.replace(".", "", 1).isdigit():
                    return price is not None and price == float(keyword)
            except ValueError:
                pass

            return (
                    keyword in item["country"].lower()
                    or keyword in item["currency"].lower()
            )


        data = list(filter(match, data))


    data.sort(key=lambda x: (x["price_twd"] is None, x["price_twd"]))


    generate_price_chart(data, plan)


    country_list = sorted({d["country"] for d in data})


    selected_info = None
    if selected_country:
        for idx, item in enumerate(data):
            if item["country"] == selected_country and item["price_twd"]:
                rank = idx + 1
                percent = round(rank / len(data) * 100, 2)
                selected_info = {
                    "country": item["country"],
                    "price": item["price"],
                    "currency": item["currency"],
                    "price_twd": item["price_twd"],
                    "rank": rank,
                    "total": len(data),
                    "percentile": percent
                }
                break

    stats = compute_stats(data)

    return render_template("index.html",
                           stats = stats,
                           countries=data,
                           selected_plan=plan,
                           country_list=country_list,
                           selected_country=selected_country,
                           selected_info=selected_info,
                           search=search)


@app.route("/download/chart")
def download_chart():
    chart_path = "static/price_chart.png"
    return send_file(chart_path, as_attachment=True, download_name="netflix_price_chart.png")

@app.route("/download/csv")
def download_csv():
    plan = request.args.get("plan", "Standard")
    search = request.args.get("search", "").strip().lower()

    data = get_netflix_price_data(plan)
    twd_rates = get_twd_exchange_rate()

    for item in data:
        cur = item["currency"].lower()
        rate = twd_rates.get(cur)
        if rate:
            item["price_twd"] = round(item["price"] / rate, 2)
        else:
            item["price_twd"] = None


    if search:
        def match(item):
            keyword = search
            price = item.get("price_twd")
            try:
                if keyword.startswith(">="):
                    return price is not None and price >= float(keyword[2:])
                elif keyword.startswith("<="):
                    return price is not None and price <= float(keyword[2:])
                elif keyword.startswith(">"):
                    return price is not None and price > float(keyword[1:])
                elif keyword.startswith("<"):
                    return price is not None and price < float(keyword[1:])
                elif keyword.startswith("="):
                    return price is not None and price == float(keyword[1:])
                elif keyword.replace('.', '', 1).isdigit():
                    return price is not None and price == float(keyword)
            except ValueError:
                pass
            return keyword in item["country"].lower() or keyword in item["currency"].lower()

        data = list(filter(match, data))


    data.sort(key=lambda x: (x["price_twd"] is None, x["price_twd"]))


    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["國家", "幣別", "原幣價格", "台幣價格"])

    for item in data:
        writer.writerow([
            item["country"],
            item["currency"],
            item["price"],
            item["price_twd"] if item["price_twd"] is not None else "N/A"
        ])

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode("utf-8-sig")),
                     mimetype="text/csv",
                     as_attachment=True,
                     download_name=f"netflix_prices_{plan}.csv")


if __name__ == "__main__":
    app.run(port=5002, host="0.0.0.0", debug=False)
