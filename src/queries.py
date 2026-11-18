from sqlalchemy import create_engine, text
from config import DB_CONFIG

engine = create_engine(
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)


def execute_and_print(query: str, prefix: str = "") -> None:
    """
    Выполняет SQL-запрос и выводит результат в консоль.
    Каждая строка ожидается в формате: (год, значение).
    """
    try:
        with engine.connect() as conn:
            rows = list(conn.execute(text(query)))
            if not rows:
                print("⚠️ Нет данных для отображения")
                return
            for row in rows:
                print(f"📅 {int(row[0])}: {prefix} {row[1]}")
    except Exception as e:
        print(f"❌ Ошибка выполнения запроса: {e}")


QUERY_SALES_BY_YEAR = """
    SELECT
        EXTRACT(YEAR FROM "Order Date") AS year,
        ROUND(SUM("Sales")::numeric, 2) AS total_sales
    FROM sales
    GROUP BY year
    ORDER BY year;
"""

QUERY_COUNT_BY_YEAR = """
    SELECT
        EXTRACT(YEAR FROM "Order Date") AS year,
        COUNT("Sales") AS count_sales
    FROM sales
    GROUP BY year
    ORDER BY year;
"""

QUERY_AVG_BY_YEAR = """
    SELECT
        EXTRACT(YEAR FROM "Order Date") AS year,
        ROUND(AVG("Sales")::numeric, 2) AS avg_sales
    FROM sales
    GROUP BY year
    ORDER BY year;
"""


if __name__ == "__main__":
    print("📊 Сумма продаж по годам:")
    print("-" * 30)
    execute_and_print(QUERY_SALES_BY_YEAR, "$")

    print("\n📊 Количество продаж по годам:")
    print("-" * 30)
    execute_and_print(QUERY_COUNT_BY_YEAR)

    print("\n📊 Средняя цена продажи по годам:")
    print("-" * 30)
    execute_and_print(QUERY_AVG_BY_YEAR, "$")