from sqlalchemy import MetaData, Table, Column, Integer, String, Float, Date, ForeignKey
from loguru import logger

metadata = MetaData()

table_dim_customer = Table(
    "dim_customer", metadata,
    Column("customer_id", String, primary_key=True),
    Column("customer_name", String),
    Column("customer_segment", String),
    Column("first_purchase_date", Date),
    Column("last_purchase_date", Date),
    Column("monthly_burn", Float),
    Column("churn_flag", Integer) 
)

table_dim_product = Table(
    "dim_product", metadata,
    Column("product_id", String, primary_key=True),
    Column("product_name", String),
    Column("category", String),
    Column("sub_category", String),
    Column("brand", String)
)

table_dim_sales_rep = Table(
    "dim_sales_rep", metadata,
    Column("sales_rep_id", Integer, primary_key=True),
    Column("sales_rep", String)
)

table_dim_channel = Table(
    "dim_channel", metadata,
    Column("channel_id", Integer, primary_key=True),
    Column("sales_channel", String),
    Column("payment_method", String)
)

table_dim_region = Table(
    "dim_region", metadata,
    Column("region_id", Integer, primary_key=True),
    Column("region", String)
)

table_dim_date = Table(
    "dim_date", metadata,
    Column("date_id", Date, primary_key=True),
    Column("year", Integer),
    Column("quarter", Integer),
    Column("month", Integer),
    Column("day", Integer),
    Column("day_of_week", Integer),
    Column("day_name", String),
    Column("month_name", String)
)

table_fact_sales = Table(
    "fact_sales", metadata,
    Column("order_id", String, primary_key=True),
    Column("customer_id", String, ForeignKey("dim_customer.customer_id")),
    Column("product_id", String, ForeignKey("dim_product.product_id")),
    Column("channel_id", Integer, ForeignKey("dim_channel.channel_id")),
    Column("sales_rep_id", Integer, ForeignKey("dim_sales_rep.sales_rep_id")),
    Column("region_id", Integer, ForeignKey("dim_region.region_id")),
    Column("date_id", Date, ForeignKey("dim_date.date_id")),
    Column("quantity", Integer),
    Column("unit_price", Float),
    Column("discount_pct", Float),
    Column("gross_amount", Float),
    Column("net_amount", Float),
    Column("operating_expenses", Float),
    Column("cash_balance", Float),
    Column("debt_balance", Float),
    Column("customer_type", String)
)


def create_tables(engine):
    """Cria as tabelas no banco de dados usando SQLAlchemy."""
    try:
        metadata.create_all(engine)
        logger.info("Tabelas criadas com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
