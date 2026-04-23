import duckdb
import pandas as pd


def model_star_schema(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    conn = duckdb.connect()
    conn.register("raw", df)

    # Dimensões

    dim_customer = conn.execute("""
        SELECT DISTINCT
            customer_id,
            customer_name,
            customer_segment,
            customer_type,
            first_purchase_date,
            last_purchase_date,
            monthly_burn,
            churn_flag
        FROM raw
    """).df()

    dim_product = conn.execute("""
        SELECT DISTINCT
            product_id,
            product_name,
            category,
            sub_category,
            brand
        FROM raw
    """).df()

    # sales_rep 
    dim_sales_rep = conn.execute("""
        SELECT
            ROW_NUMBER() OVER (ORDER BY sales_rep) AS sales_rep_id,
            sales_rep
        FROM (SELECT DISTINCT sales_rep FROM raw)
    """).df()

    # canal = sales_channel + payment_method
    dim_channel = conn.execute("""
        SELECT
            ROW_NUMBER() OVER (ORDER BY sales_channel, payment_method) AS channel_id,
            sales_channel,
            payment_method
        FROM (SELECT DISTINCT sales_channel, payment_method FROM raw)
    """).df()

    dim_region = conn.execute("""
        SELECT
            ROW_NUMBER() OVER (ORDER BY region) AS region_id,
            region
        FROM (SELECT DISTINCT region FROM raw)
    """).df()

    dim_date = conn.execute("""
        SELECT DISTINCT
            CAST(order_date AS DATE)        AS date_id,
            YEAR(order_date)                AS year,
            QUARTER(order_date)             AS quarter,
            MONTH(order_date)               AS month,
            DAY(order_date)                 AS day,
            DAYOFWEEK(order_date)           AS day_of_week,
            DAYNAME(order_date)             AS day_name,
            MONTHNAME(order_date)           AS month_name
        FROM raw
        ORDER BY date_id
    """).df()

    # Fato 

    conn.register("dim_channel",  dim_channel)
    conn.register("dim_sales_rep", dim_sales_rep)
    conn.register("dim_region",   dim_region)

    fact_sales = conn.execute("""
        SELECT
            r.order_id,
            r.customer_id,
            r.product_id,
            dc.channel_id,
            dr.sales_rep_id,
            dre.region_id,
            CAST(r.order_date AS DATE)                          AS date_id,
            r.quantity,
            r.unit_price,
            r.discount_pct,
            ROUND(r.unit_price * r.quantity, 2)                 AS gross_amount,
            ROUND(r.unit_price * r.quantity * (1 - r.discount_pct), 2) AS net_amount,
            r.operating_expenses,
            r.cash_balance,
            r.debt_balance
        FROM raw r
        JOIN dim_channel  dc  ON r.sales_channel  = dc.sales_channel
                              AND r.payment_method = dc.payment_method
        JOIN dim_sales_rep dr  ON r.sales_rep      = dr.sales_rep
        JOIN dim_region   dre  ON r.region         = dre.region
    """).df()

    conn.close()

    return {
        "dim_customer":  dim_customer,
        "dim_product":   dim_product,
        "dim_channel":   dim_channel,
        "dim_sales_rep": dim_sales_rep,
        "dim_region":    dim_region,
        "dim_date":      dim_date,
        "fact_sales":    fact_sales,
    }