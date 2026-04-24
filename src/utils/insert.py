import os
from sqlalchemy import create_engine, Engine, text
from dotenv import load_dotenv
import pandas as pd
from loguru import logger

load_dotenv() 

def connect_to_db() -> Engine:
    """Estabelece conexão com o banco de dados PostgreSQL usando SQLAlchemy."""
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT")
    db_name = os.getenv("POSTGRES_DB")

    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    logger.info("Conectando ao banco de dados PostgreSQL...")
    engine = create_engine(connection_string)
    
    return engine


def insert_star_schema(star_schema: dict[str, pd.DataFrame], engine: Engine) -> None:
    insert_order = [
        "dim_customer", "dim_product", "dim_channel",
        "dim_sales_rep", "dim_region", "dim_date", "fact_sales",
    ]


    with engine.begin() as conn:
        for table_name in reversed(insert_order):
            logger.info(f"Truncando {table_name}...")
            conn.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))

    try:
        with engine.begin() as conn:
            for table_name in insert_order:
                df = star_schema[table_name]
                logger.info(f"Inserindo dados na tabela {table_name}...")
                df.to_sql(name=table_name, con=conn, if_exists="append", index=False)
                logger.info(f"{table_name}: {len(df)} linhas inseridas.")

    except Exception as e:
        logger.error(f"Erro ao inserir dados: {e}")
        raise




