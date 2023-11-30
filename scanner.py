import datetime

import streamlit as st
from sqlalchemy import create_engine, text

from sql_tables import update_table


def get_formatted_date():
    """Return today's date in 'YYYY-MM-DD' format."""
    today = datetime.date.today()
    return today.strftime('%Y-%m-%d')


def check_existing_entry(table_name: str, product_code: str) -> tuple | None:
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
    user_input = st.text_input("Enter a barcode")

    if user_input:

        if not in_donations_table(user_input, "2023-11-30"):
            st.write("Searching dataset")
            product_details = check_existing_entry("dataset", user_input)
            if product_details is not None:
                st.write(product_details)

#                product_details = {
#                    'date_received': get_formatted_date(),
#                    'product_code': product_details[0],
#                    'product_name': product_details[1],
#                    'category': product_details[2],
#                    'price': product_details[3],
#                    'weight': product_details[4],
#                    'quantity': 1,
#                    'total_price': product_details[3],
#                    'total_weight': product_details[4]
#                }
#
#                st.write(product_details)
                update_table("donation_log", product_details)
                st.success("Saved item to donation log.")

            else:
                st.write("Barcode not in dataset.")
                st.write("`manual_entry()`")
        else:
            st.write("Item already in today's donations. Incrementing quantity.")
            st.write("`increment_quantity()`")

