import datetime

import streamlit as st
from sqlalchemy import create_engine, text

from sql_tables import update_table


def get_formatted_date():
    """Return today's date in 'YYYY-MM-DD' format."""
    today = datetime.date.today()
    return today.strftime('%Y-%m-%d')


def find_product(table_name: str, product_code: str) -> tuple | None:
    conn = st.connection("digitalocean", type="sql")
    with conn.session as s:
        query = text(f"""
            SELECT product_code, product_name, category, price, weight FROM {table_name} WHERE product_code = :product_code
        """)
        result = s.execute(query, {"product_code": product_code}).fetchone()
    return result


def in_donations_table(product_code, date):
    """Checks to see if an item already exists in the dataset"""
    query = text(f"""
    SELECT COUNT(*)
    FROM donation_log
    WHERE product_code = :product_code AND date_received = :date_received;
    """)
    conn = st.connection("digitalocean", type="sql")
    with conn.session as s:
        #result = s.execute(query)
        result = s.execute(query, {"product_code": product_code, "date_received": date}).fetchone()
    try:
        return bool(result[0])
    except Exception as e:
        return result[0] if isinstance(result, tuple) else result


def receive_barcodes():
    if "text" not in st.session_state:
        st.session_state["text"] = ""

    input = st.chat_input(name='user')
    if input:
        st.write(input)
    user_input = st.text_input("Enter a barcode", key="text")

    if user_input:
        product_details = find_product("dataset", user_input)
        if product_details is not None:
            st.write(product_details, len(product_details))
            update_table("donation_log", product_details)
            st.success("Saved item to donation log.")
            user_input = None
        else:
            st.write("Barcode not in dataset.")
            st.write("`manual_entry()`")

