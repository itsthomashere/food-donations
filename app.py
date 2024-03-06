import os
from datetime import datetime

import openai
import streamlit as st
from dataclasses import asdict
from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Connection
from streamlit_option_menu import option_menu

import constants as c
from models import DatasetItem, DonatedFoodItem, MissingBarcode
from sql_tables import donations_dataset, food_dataset


def get_connection() -> Connection:
    """Establishes and returns a database connection."""
    return st.connection("digitalocean", type="sql", autocommit=True)


def connect_to_table(query: str, conn: Connection) -> None:
    """Executes an SQL query using Streamlit connection object"""
    with conn.session as session:
        session.execute(text(query))


def execute_query(conn: Connection, query: str, query_params: dict = None) -> list:
    """Execute a SQL query with optional parameters on a given connection and return the first result."""
    with conn.session as s:
        return s.execute(text(query), params=query_params).fetchone()


def convert_to_donated_item(dataset_item: DatasetItem, quantity: int = 1) -> DonatedFoodItem:
    """Converts a given DatasetItem to a DonatedFoodItem with specified quantity."""
    date_received = datetime.now().strftime("%Y-%m-%d")
    total_price = dataset_item.price * quantity
    total_weight = dataset_item.weight * quantity
    return DonatedFoodItem(
        date_received=date_received,
        product_code=dataset_item.product_code,
        product_name=dataset_item.product_name,
        category=dataset_item.category,
        price=dataset_item.price,
        weight=dataset_item.weight,
        quantity=quantity,
        total_price=total_price,
        total_weight=total_weight,
    )


def save_donated_food_item(conn: Connection, donated_food_item: DonatedFoodItem) -> None:
    """
    Saves a DonatedFoodItem to the 'donation_history' table.
    """
    product_details = asdict(donated_food_item)

    # Connect to the database and execute the query
    with conn.session as session:
        session.execute(text(c.DONATION_HISTORY_INSERT_FOOD_ITEM), product_details)
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
                try:
                    # Convert the result to a `DatasetItem` object
                    food_item = DatasetItem(*result)
                    # st.write("Query succeeded:", food_item)

                    # st.write("Converting `DatasetItem` to `DonatedFoodItem`")
                    donated_item: DonatedFoodItem = convert_to_donated_item(food_item, quantity=1)
                    # st.write(donated_item)

                    # st.write("`Saving to donation history...`")
                    save_donated_food_item(conn, donated_item)
                    # product_details = DatasetItem(*result)

                except Exception as e:
                    st.error(e)

                finally:
                    st.write(donated_item)
                    st.success(f"Saved {user_input} item to donation log.")
            else:
                st.write("No data found.")

    except Exception as e:
        st.error(e)
    # -------------------------------------------

main()
