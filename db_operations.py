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
    """
    Returns True if a given product_code is located in the donation_history table for a specific date.
    """
    query_result = conn.query(c.CHECK_IF_ITEM_IN_DONATION_HISTORY, params={"product_code": product_code, "date_received": date})
    return not query_result.empty and query_result.iloc[0]['count'] > 0

def get_food_item_by_product_code(conn, product_code, date):
    """Returns a food item from the dataset table given a product_code."""
    return conn.query(c.FIND_DATASET_ITEM_BY_PRODUCT_CODE, params={"product_code": product_code})

def save_donated_item_to_donation_history(conn, donated_item):
    """Saves a donated item to the donation_history table."""
    # Ensure that the SQL command is a text query for execution
    sql_command = text(c.DONATION_HISTORY_INSERT_FOOD_ITEM)

    with conn.session as session:
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
