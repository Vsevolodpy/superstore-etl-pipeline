import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine, text
from config import DB_CONFIG

engine = create_engine(
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

@st.cache_data
def fetch_data(query: str) -> pd.DataFrame:
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

df_sales_year = fetch_data(QUERY_SALES_BY_YEAR)
df_sales_month = fetch_data(QUERY_SALES_BY_MONTH)
df_profit_region = fetch_data(QUERY_PROFIT_BY_REGION)
df_top_categories = fetch_data(QUERY_TOP_CATEGORIES)

st.set_page_config(page_title="Superstore Analytics", layout="wide")
st.title("📊 Анализ продаж Superstore")
st.markdown("Интерактивный дашборд на основе данных о продажах.")

st.subheader("📈 Сумма продаж по годам")
fig1, ax1 = plt.subplots()
sns.barplot(data=df_sales_year, x="year", y="total_sales", hue="year", palette="Blues_d", legend=False)
ax1.set_xlabel("Год")
ax1.set_ylabel("Продажи ($)")
st.pyplot(fig1)

st.subheader("📆 Сезонность продаж")
available_years = sorted(df_sales_month["year"].unique())
selected_years = st.multiselect("Выберите годы для отображения", available_years, default=available_years)
df_filtered = df_sales_month[df_sales_month["year"].isin(selected_years)]

fig2, ax2 = plt.subplots()
sns.lineplot(data=df_filtered, x="month", y="total_sales", hue="year", marker="o")
ax2.set_xlabel("Месяц")
ax2.set_ylabel("Продажи ($)")
ax2.legend(title="Год")
st.pyplot(fig2)

st.subheader("🏆 Прибыль и маржа по регионам")
fig3, ax3 = plt.subplots()
ax3.bar(df_profit_region["Region"], df_profit_region["profit"], color="skyblue", label="Прибыль")
ax3.set_xlabel("Регион")
ax3.set_ylabel("Прибыль ($)", color="blue")
ax3.tick_params(axis="y", labelcolor="blue")

ax4 = ax3.twinx()
ax4.plot(df_profit_region["Region"], df_profit_region["profit_margin_percent"],
         color="red", marker="o", linewidth=2, label="Маржа (%)")
ax4.set_ylabel("Маржа (%)", color="red")
ax4.tick_params(axis="y", labelcolor="red")

lines1, labels1 = ax3.get_legend_handles_labels()
lines2, labels2 = ax4.get_legend_handles_labels()
ax3.legend(lines1 + lines2, labels1 + labels2, loc="upper left")
st.pyplot(fig3)

st.subheader("🏷️ ТОП-5 подкатегорий по выручке")
fig4, ax5 = plt.subplots()
df_sorted = df_top_categories.sort_values("total_sales", ascending=True)
sns.barplot(data=df_sorted, y="Sub-Category", x="total_sales", hue="Sub-Category", palette="Greens_d", legend=False)
ax5.set_xlabel("Продажи ($)")
ax5.set_ylabel("Подкатегория")
st.pyplot(fig4)

if st.button("🔄 Обновить данные из БД"):
    st.cache_data.clear()
    st.success("Данные обновлены! Перезагрузите страницу.")
    st.rerun()

st.sidebar.header("О проекте")
st.sidebar.info(
    "Дашборд построен на основе данных Superstore.\n"
    "Используемые технологии: Python, Pandas, SQLAlchemy, PostgreSQL, Streamlit."
)