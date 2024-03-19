import streamlit as st

from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm import Session
# from models import FoodItem, DonatedFoodItem, MissingItem
import constants as c


@st.cache_data
def get_connection():
    """Establishes and returns a database connection."""
    return st.connection("digitalocean", type="sql", autocommit=True)

@st.cache_data
def fetch_all_items(_conn, table):
    """Fetches all items using the specified SQLAlchemy model."""
    df = _conn.query(f"select * from {table}", ttl=3600)
    st.dataframe(df)

@st.cache_data
def check_if_item_in_donation_history(_conn, product_code, date):
    """
    Returns True if a given product_code is located in the donation_history table for a specific date.
    """
    query_result = _conn.query(c.CHECK_IF_ITEM_IN_DONATION_HISTORY, params={"product_code": product_code, "date_received": date})
    
    # Assuming query_result is a DataFrame and the SQL query returns a column named 'item_count'
    return not query_result.empty and query_result.iloc[0]['item_count'] > 0

@st.cache_data
def get_current_quantity(_conn, product_code):
    """Returns the current quantity of a given product_code in the donation_history table."""
    return _conn.query(c.GET_CURRENT_QUANTITY, params={"product_code": product_code})


@st.cache_data
def get_food_item_by_product_code(_conn, product_code, date):
    """Returns a food item from the dataset table given a product_code."""
    return _conn.query(c.FIND_DATASET_ITEM_BY_PRODUCT_CODE, params={"product_code": product_code})

@st.cache_data
def save_donated_item_to_donation_history(_conn, donated_item):
    """Saves a donated item to the donation_history table."""
    # Ensure that the SQL command is a text query for execution
    sql_command = text(c.DONATION_HISTORY_INSERT_FOOD_ITEM)

    with _conn.session as session:
        session.execute(sql_command, 
                        {"date_received": donated_item.date_received,
                         "product_code": int(donated_item.product_code),
                         "product_name": donated_item.product_name,
                         "category": donated_item.category,
                         "price": float(donated_item.price),
                         "weight": float(donated_item.weight),
                         "quantity": int(donated_item.quantity),
                         "total_price": float(donated_item.total_price),
                         "total_weight": float(donated_item.total_weight)
                         }
                        )
        session.commit()
                    

@st.cache_data
def add_missing_item_to_queue(_conn, missing_item):
    """Adds a missing item to the missing_items table."""
    st.write("Missing item added to queue...")
    with _conn.session as session:
        session.execute(text(c.MISSING_ITEM_INSERT_PRODUCT_CODE),
                        {
                            "date_added": missing_item.date_added,
                            "product_code": missing_item.product_code,
                            "status": missing_item.status,
                            })
        session.commit()
