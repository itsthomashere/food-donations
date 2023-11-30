import streamlit as st
from sqlalchemy import create_engine, text


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
    return result


def receive_barcodes():
    user_input = st.text_input("Enter a barcode")
    if user_input:
        result = in_donations_table(user_input, '2023-11-30')
        st.write(result)

