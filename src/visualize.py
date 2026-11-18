import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, text
from config import DB_CONFIG

engine = create_engine(
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

def fetch_data(query: str) -> pd.DataFrame:
    """Выполняет SQL-запрос и возвращает DataFrame."""
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)

QUERY_SALES_BY_YEAR = """
    SELECT 
        EXTRACT(YEAR FROM "Order Date") AS year,
        ROUND(SUM("Sales")::numeric, 2) AS total_sales
    FROM sales
    GROUP BY year
    ORDER BY year;
"""

QUERY_SALES_BY_MONTH = """
    SELECT 
        EXTRACT(YEAR FROM "Order Date") AS year,
        EXTRACT(MONTH FROM "Order Date") AS month,
        ROUND(SUM("Sales")::numeric, 2) AS total_sales
    FROM sales
    GROUP BY year, month
    ORDER BY year, month;
"""

QUERY_PROFIT_BY_REGION = """
    SELECT 
        "Region",
        ROUND(SUM("Sales")::numeric, 2) AS revenue,
        ROUND(SUM("Profit")::numeric, 2) AS profit,
        ROUND(
            (SUM("Profit")::numeric / NULLIF(SUM("Sales")::numeric, 0) * 100),
            2
        ) AS profit_margin_percent
    FROM sales
    GROUP BY "Region"
    ORDER BY profit DESC;
"""

QUERY_TOP_CATEGORIES = """
    SELECT 
        "Sub-Category",
        ROUND(SUM("Sales")::numeric, 2) AS total_sales
    FROM sales
    GROUP BY "Sub-Category"
    ORDER BY total_sales DESC
    LIMIT 5;
"""

print("📥 Загрузка данных...")
df_sales_year = fetch_data(QUERY_SALES_BY_YEAR)
df_sales_month = fetch_data(QUERY_SALES_BY_MONTH)
df_profit_region = fetch_data(QUERY_PROFIT_BY_REGION)
df_top_categories = fetch_data(QUERY_TOP_CATEGORIES)

os.makedirs("reports", exist_ok=True)

sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (10, 6)

# График 1: Продажи по годам
plt.figure()
sns.barplot(data=df_sales_year, x="year", y="total_sales", palette="Blues_d")
plt.title("Сумма продаж по годам", fontsize=14)
plt.xlabel("Год")
plt.ylabel("Продажи ($)")
plt.tight_layout()
plt.savefig("reports/sales_by_year.png", dpi=150)
plt.close()

# График 2: Сезонность
plt.figure()
sns.lineplot(data=df_sales_month, x="month", y="total_sales", hue="year", marker="o")
plt.title("Сезонность продаж (по годам)", fontsize=14)
plt.xlabel("Месяц")
plt.ylabel("Продажи ($)")
plt.legend(title="Год")
plt.tight_layout()
plt.savefig("reports/sales_seasonality.png", dpi=150)
plt.close()

# График 3: Прибыль и маржа по регионам
fig, ax1 = plt.subplots()
ax1.set_title("Прибыль и маржа по регионам", fontsize=14)
ax1.bar(df_profit_region["Region"], df_profit_region["profit"], color="skyblue", label="Прибыль")
ax1.set_xlabel("Регион")
ax1.set_ylabel("Прибыль ($)", color="blue")
ax1.tick_params(axis="y", labelcolor="blue")

ax2 = ax1.twinx()
ax2.plot(df_profit_region["Region"], df_profit_region["profit_margin_percent"],
         color="red", marker="o", linewidth=2, label="Маржа (%)")
ax2.set_ylabel("Маржа (%)", color="red")
ax2.tick_params(axis="y", labelcolor="red")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

plt.tight_layout()
plt.savefig("reports/profit_by_region.png", dpi=150)
plt.close()

# График 4: ТОП-5 подкатегорий
plt.figure()
sns.barplot(
    data=df_top_categories.sort_values("total_sales", ascending=True),
    y="Sub-Category",
    x="total_sales",
    palette="Greens_d"
)
plt.title("ТОП-5 подкатегорий по выручке", fontsize=14)
plt.xlabel("Продажи ($)")
plt.ylabel("Подкатегория")
plt.tight_layout()
plt.savefig("reports/top_categories.png", dpi=150)
plt.close()

print("✅ Визуализация завершена!")
print("📁 Графики сохранены в папке reports/")