import pandas as pd
from sqlalchemy import create_engine, Float, Date
from config import DB_CONFIG


def load_data(csv_path: str, table_name: str) -> None:
    """
    Загружает данные из CSV-файла в таблицу PostgreSQL.
    Выполняет преобразование типов (дата, числа с запятыми).
    """
    engine = create_engine(
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
        f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )

    df = pd.read_csv(
        csv_path,
        encoding='latin-1',
        parse_dates=['Order Date'],
        dtype={'Sales': float},
        thousands=','
    )

    df.to_sql(
        table_name,
        engine,
        if_exists='replace',
        index=False,
        dtype={'Order Date': Date, 'Sales': Float}
    )

    print(f"✅ Данные загружены в таблицу {table_name}")


if __name__ == "__main__":
    load_data('data/sample_superstore.csv', 'sales')