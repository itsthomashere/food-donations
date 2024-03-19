import streamlit as st

from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm import Session
# from models import FoodItem, DonatedFoodItem, MissingItem
import constants as c


def get_connection():
    """Establishes and returns a database connection."""
    return st.connection("digitalocean", type="sql", autocommit=True)

def fetch_all_items(conn, table):
    """Fetches all items using the specified SQLAlchemy model."""
    df = conn.query(f"select * from {table}", ttl=3600)
    st.dataframe(df)

def check_if_item_in_donation_history(conn, product_code, date):
    """Returns True if a given product_code is located in donation_history table."""
    item = conn.query(c.CHECK_IF_ITEM_IN_DONATION_HISTORY, params={"product_code": product_code, "date_received": date}).first()
    st.write(item)
    return True if item else False
                    
def get_food_item_by_product_code(conn, product_code):
    """
    Retrieves a FoodItem from the database based on the given product_code.
    """
    item = conn.query(c.CHECK_IF_ITEM_IN_DONATION_HISTORY, params={"product_code": product_code, "date_received": date}).first()
    return item

def update_donation_history_item(conn, product_code, quantity):
    """Updates the quantity and total_price/total_weight of a given product_code in donation_history."""
    st.write("Updating donation history item...")
    pass
    # with conn.session as session:
    #     session.execute(c.DONATION_HISTORY_INSERT_FOOD_ITEM, 
    #                     {"product_code": product_code,
    #                      }
    #                     )
    #     session.commit()
