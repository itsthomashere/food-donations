import os

import openai
import streamlit as st
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Connection
import constants as c
from models import DonatedFoodItem, MissingBarcode, DatasetItem

from sql_tables import food_dataset, donations_dataset
# from scanner import receive_barcodes

def connect_to_table(query: str, conn: Connection) -> None:
    """
    Executes an SQL query using Streamlit connection object
    """
    with conn.session as session:
        session.execute(text(query))
        # session.commit()

def check_existing_entry(table_name: str, product_code: str) -> tuple | None:
    conn = st.connection("digitalocean", type="sql", autocommit=True)
    with conn.session as s:
        query = text(f"""
            SELECT product_code, product_name, category, price, weight FROM {table_name} WHERE product_code = :product_code
        """)
        result = s.execute(query, {"product_code": product_code}).fetchone()
    return result




def get_connection() -> Connection:
    """
    Establishes and returns a database connection.
    
    Returns:
        Connection object
    """
    return st.connection("digitalocean", type="sql")


def execute_query(conn: Connection, query: str, query_params: dict = None) -> list:
    with conn.session as s:
        # return conn.execute(text(query), query_params).fetchone()
        result = s.execute(text(query), params=query_params).fetchone()
        # session.commit()
        return result
        # df = conn.query("select * from pet_owners where owner = :owner", ttl=3600, params={"owner":"barbara"})
    # with conn.session as session:
    #     session.execute("INSERT INTO numbers (val) VALUES (:n);", {"n": n})
        # session.commit()
# ---------------------------------

def main() -> None:

    st.set_page_config(
        page_title="Barcode Scanner",
        page_icon="📊",
        layout="wide"
        )

    st.markdown("""
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """,
                unsafe_allow_html=True)

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

        # Setting this up as a global variable. 
        conn: Connection = get_connection()
        # Establish connection to Donation History table
        connect_to_table(c.DONATION_HISTORY_TABLE, conn)

        # Establish connection to Missing Barcodes table
        connect_to_table(c.MISSING_BARCODES_TABLE, conn)

    except Exception as e:
        st.error(e)
    # -------------------------------------------

def receive_barcodes() -> None:
    # Step 2: Receive barcodes
    try:
        conn: Connection = get_connection()

        user_input = st.chat_input("Enter a barcode")

        if user_input:
            result = execute_query(conn,
                                   c.FIND_DATASET_ITEM_BY_PRODUCT_CODE,
                                   {"product_code": user_input}
                                   )
            if result:
                st.write("Query succeeded:", result)
                food_item = DatasetItem(*result)
                # format the results into DonatedFoodItem object
                try:
                    st.write("Converting DatasetItem to DonatedFoodItem")
                    # product_details = DatasetItem(*result)

                except Exception as e:
                    st.error(e)

                update_table("donation_log", product_details)
                st.success(f"Saved {user_input} item to donation log.")
            else:
                st.write("No data found.")
    except Exception as e:
        st.error(e)
    # -------------------------------------------

main()
