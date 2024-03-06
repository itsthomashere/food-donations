import os

import openai
import streamlit as st
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Connection
from constants as c
from models import DonatedFoodItem, MissingBarcode, DatasetItem

from sql_tables import food_dataset, donations_dataset
from scanner import receive_barcodes


# def create_tables() -> None:
#     conn = st.connection("digitalocean", type="sql")
#     with conn.session as s:
#         # Create the 'donation_log' table with specified columns
#         s.execute(text("""
#                     CREATE TABLE IF NOT EXISTS donation_log (
#                     date_received DATE,
#                     product_code VARCHAR(13),
#                     product_name VARCHAR(255),
#                     category VARCHAR(255),
#                     price NUMERIC(10, 2),
#                     weight NUMERIC(10, 2),
#                     quantity INT,
#                     total_price NUMERIC(10, 2),
#                     total_weight NUMERIC(10, 2));"""))
#         # s.commit()

def connect_to_table(query: str, conn: Connection) -> None:
    """
    Executes an SQL query using Streamlit connection object
    """
    with conn.session as session:
        session.execute(text(query))
        session.commit()

def check_existing_entry(table_name: str, product_code: str) -> tuple | None:
    conn = st.connection("digitalocean", type="sql")
    with conn.session as s:
        query = text(f"""
            SELECT product_code, product_name, category, price, weight FROM {table_name} WHERE product_code = :product_code
        """)
        result = s.execute(query, {"product_code": product_code}).fetchone()
    return result


def customize_streamlit_ui() -> None:
    st.set_page_config(
        page_title="Barcode Scanner",
        page_icon="📊",
        layout="wide"
        )

    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)


def get_connection() -> Connection:
    """
    Establishes and returns a database connection.
    
    Returns:
        Connection object
    """
    return st.connection("digitalocean", type="sql")

# ---------------------------------

def main() -> None:

    customize_streamlit_ui()

    title = "Woolworths Food Donations"
    title = st.markdown(
        f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True
    )

    options = option_menu(None, 
                          ["Manual", "Barcode Scanner", "Totals"], 
                          icons=['clipboard-data', 'upc-scan', "database-add"], 
                          menu_icon="cast", 
                          default_index=1, 
                          orientation="horizontal"
                          )

    pages = {
        'Manual': donations_dataset,
        'Barcode Scanner': receive_barcodes,
        'Totals': food_dataset
    }
    pages[options]()

    # --- Step 1: Connect to database tables --- 
    try:
        conn: Connection = get_connection()

        # Establish connection to Donation History table
        connect_to_table(c.DONATION_HISTORY_TABLE, conn)

        # Establish connection to Missing Barcodes table
        connect_to_table(c.MISSING_BARCODES_TABLE, conn)

    except Exception as e:
        st.error(e)
    # -------------------------------------------

    # Step 2: Receive barcodes
    try:
        
        user_input = st.chat_input("Enter a barcode")

        if user_input:
            # product_details: dict = find_product("dataset", user_input)
            pass
            if product_details is not None:
                update_table("donation_log", product_details)
                st.success(f"Saved {user_input} item to donation log.")
            else:
                st.write("Barcode not in dataset.")
    # -------------------------------------------


main()
