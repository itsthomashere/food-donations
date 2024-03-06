import datetime

import pandas as pd
import streamlit as st
from sqlalchemy import bindparam, create_engine, text


def display_overall_totals(df: pd.DataFrame) -> None:
    """
    Display the overall total price and total weight using Streamlit.
    """
    total_price = df["total_price"].sum()
    total_weight = df["total_weight"].sum()
    st.write(f"Overall Total Price: {total_price}")
    st.write(f"Overall Total Weight: {total_weight}")


def get_today_data(table_name: str) -> pd.DataFrame:
    """
    Fetch data from the specified table where 'date_received' is today's date,
    and return it as a pandas DataFrame.
    """
    today = datetime.date.today().strftime("%Y-%m-%d")
    conn = st.experimental_connection("digitalocean", type="sql")
    query = f"SELECT * FROM {table_name} WHERE date_received = '{today}'"
    result = conn.query(query)
    return pd.DataFrame(result)


def calculate_totals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the total price and total weight, grouped by categories from the DataFrame.
    """
    grouped_df = (
        df.groupby("category")
        .agg(
            total_price=pd.NamedAgg(column="total_price", aggfunc="sum"),
            total_weight=pd.NamedAgg(column="total_weight", aggfunc="sum"),
        )
        .reset_index()
    )
    return grouped_df


def get_sql_dataframe(table_name: str, order) -> None:
    conn = st.connection("digitalocean", type="sql")
    query = f"select * from {table_name} order by {order}"
    messages = conn.query(query)
    st.dataframe(messages, use_container_width=True, hide_index=True)

