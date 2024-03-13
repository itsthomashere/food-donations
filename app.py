import os
from datetime import datetime, date

import openai
import streamlit as st
from dataclasses import asdict
from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Connection
from streamlit_option_menu import option_menu
from sqlmodel import Field, SQLModel, select

import constants as c
from db import engine
# from models import DatasetItem, DonatedFoodItem, MissingBarcode
# from models import Dataset, DonatedFoodItem, MissingBarcode
from sql_tables import donations_dataset, food_dataset

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    st.success("Connected to database.")

# -----------------------------------------------------------------------------

def get_connection() -> Connection:
    """Establishes and returns a database connection."""
    return st.connection("digitalocean", type="sql", autocommit=True)


def execute_query(conn: Connection, query: str, query_params: dict = None, return_rows: bool = True) -> list:
    """Execute a SQL query with optional parameters on a given connection.

    If return_rows is True, return the first result row.
    If return_rows is False, execute the query without expecting a return row, suitable for DDL operations.
    """
    with conn.session as session:
        result = session.execute(text(query), params=query_params)
        if return_rows:
            return result.fetchone()
        return None


# def convert_to_donated_item(dataset_item: DatasetItem, date: date, quantity: int = 1) -> DonatedFoodItem:
#     """Converts a given DatasetItem to a DonatedFoodItem with specified quantity."""
#     total_price = dataset_item.price * quantity
#     total_weight = dataset_item.weight * quantity
#     return DonatedFoodItem(
#         date_received=date,
#         product_code=dataset_item.product_code,
#         product_name=dataset_item.product_name,
#         category=dataset_item.category,
#         price=dataset_item.price,
#         weight=dataset_item.weight,
#         quantity=quantity,
#         total_price=total_price,
#         total_weight=total_weight,
#     )


# def save_donated_food_item(conn: Connection, donated_food_item: DonatedFoodItem) -> None:
#     """Saves a DonatedFoodItem to the 'donation_history' table."""
#     product_details = asdict(donated_food_item)
#
#     # Connect to the database and execute the query
#     with conn.session as session:
#         session.execute(text(c.DONATION_HISTORY_INSERT_FOOD_ITEM), product_details)
# ---------------------------------

# def in_donations_table(conn: Connection, product_code: str | int, date: date) -> bool:
#     """Checks to see if an item already exists in the dataset"""
#
#     query = text(f"""
#     SELECT COUNT(*)
#     FROM donation_log
#     WHERE product_code = :product_code AND date_received = :date_received;
#     """)
#
#     with conn.session as s:
#         result = s.execute(query, {"product_code": product_code, "date_received": date}).fetchone()
#     try:
#         return bool(result[0])
#     except Exception as e:
#         return result[0] if isinstance(result, tuple) else result


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

    # options = option_menu(None, 
    #                       ["Manual", "Barcode Scanner", "Totals"], 
    #                       icons=['clipboard-data', 'upc-scan', "database-add"], 
    #                       menu_icon="cast", 
    #                       default_index=1, 
    #                       orientation="horizontal"
    #                       )

    # pages = {
    #     'Manual': donations_dataset,
    #     'Barcode Scanner': receive_barcodes,
    #     'Totals': food_dataset
    # }
    # pages[options]()

    # --- Step 1: Connect to database tables --- 
    try:
        pass

        # Setting this up as a global variable. 
        # conn: Connection = get_connection()
        # Establish connection to Donation History table
        # connect_to_table(c.DONATION_HISTORY_TABLE, conn)
        # execute_query(conn, c.DONATION_HISTORY_TABLE, return_rows=False)

        # Establish connection to Missing Barcodes table
        # connect_to_table(c.MISSING_BARCODES_TABLE, conn)
        # execute_query(conn, c.MISSING_BARCODES_TABLE, return_rows=False)


        # connect_to_table(drop_table_query, conn)

        # connect_to_table(constraint, conn)
        # connect_to_table(find_duplicates_query, conn)

    except Exception as e:
        st.error(e)
    # -------------------------------------------

def receive_barcodes() -> None:
    # Step 2: Receive barcodes
    # date = datetime.now().strftime("%Y-%m-%d")
    # conn: Connection = get_connection()
    st.write(f"Barcode in dataset: \n2576260000008")
    st.write(f"Barcode not in dataset: \n6009226866340")

    try:
        # create_db_and_tables()

        input_str = st.chat_input("Enter a barcode")

        # 1: Is this a barcode?

        # 1.2 Does the user input contain a spacebar?

        # 2: Is the barcode already in today's donation history?
        # routes = {
        #     True: increment_quantity,
        #     False: add_product_to_donation_history
        # }

        if input_str:
            try:
                input_tuple = tuple(input_str.split()) if " " in input_str else (input_str,)
                barcode = input_tuple[0]
                quantity  = int(str(input_tuple[-1]).strip("x")) if len(input_tuple) > 1 else 1
                st.write(f"Barcode: {barcode} | Quantity: {quantity}")
            except Exception as e:
                st.error(e)

            # Search in our dataset for product information matching the barcode
            # result = execute_query(conn,
            #                        c.FIND_DATASET_ITEM_BY_PRODUCT_CODE,
            #                        {"product_code": barcode}
            #                        )

    except Exception as e:
        st.error(e)
    # -------------------------------------------

main()
