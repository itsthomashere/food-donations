import os
from datetime import datetime, date

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


def convert_to_donated_item(dataset_item: DatasetItem, date: date, quantity: int = 1) -> DonatedFoodItem:
    """Converts a given DatasetItem to a DonatedFoodItem with specified quantity."""
    total_price = dataset_item.price * quantity
    total_weight = dataset_item.weight * quantity
    return DonatedFoodItem(
        date_received=date,
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
    """Saves a DonatedFoodItem to the 'donation_history' table."""
    product_details = asdict(donated_food_item)

    # Connect to the database and execute the query
    with conn.session as session:
        session.execute(text(c.DONATION_HISTORY_INSERT_FOOD_ITEM), product_details)
# ---------------------------------

def in_donations_table(conn: Connection, product_code: str | int, date: date) -> bool:
    """Checks to see if an item already exists in the dataset"""

    query = text(f"""
    SELECT COUNT(*)
    FROM donation_log
    WHERE product_code = :product_code AND date_received = :date_received;
    """)

    with conn.session as s:
        result = s.execute(query, {"product_code": product_code, "date_received": date}).fetchone()
    try:
        return bool(result[0])
    except Exception as e:
        return result[0] if isinstance(result, tuple) else result


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
        # connect_to_table(c.DONATION_HISTORY_TABLE, conn)
        execute_query(conn, c.DONATION_HISTORY_TABLE, return_rows=False)

        # Establish connection to Missing Barcodes table
        # connect_to_table(c.MISSING_BARCODES_TABLE, conn)
        execute_query(conn, c.MISSING_BARCODES_TABLE, return_rows=False)


        # connect_to_table(drop_table_query, conn)

        # connect_to_table(constraint, conn)
        # connect_to_table(find_duplicates_query, conn)

    except Exception as e:
        st.error(e)
    # -------------------------------------------

def receive_barcodes() -> None:
    # Step 2: Receive barcodes
    date = datetime.now().strftime("%Y-%m-%d")

    try:
        conn: Connection = get_connection()

        user_input = st.chat_input("Enter a barcode")

        if user_input:
            result = execute_query(conn,
                                          c.CHECK_IF_ITEM_IN_DONATION_HISTORY,
                                          {"product_code": user_input, "date_received": date}
                                          )
            try:
                result = bool(result[0])
            except Exception as e:
                result = result[0] if isinstance(result, tuple) else result

            st.write(result)
                

            # st.write(item_in_table)
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
                    donated_item: DonatedFoodItem = convert_to_donated_item(food_item, date=date, quantity = 1)
                    # st.write(donated_item)

                    # st.write("`Saving to donation history...`")
                    # check to see if the item is already an the donation history

                    # save_donated_food_item(conn, donated_item)
                    # product_details = DatasetItem(*result)

                except Exception as e:
                    st.error(e)

                finally:
                    st.write(donated_item)
                    # st.success(f"Saved {user_input} item to donation log.")
            else:
                st.write("No data found.")

    except Exception as e:
        st.error(e)
    # -------------------------------------------

main()
