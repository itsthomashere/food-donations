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

def get_food_item_by_product_code(conn, product_code):
    """
    Retrieves a FoodItem from the database based on the given product_code.
    """
    retrieved_item = conn.query("select * from dataset where product_code = :product_code", ttl=3600, params={"product_code": product_code}).iloc[0]
    if not retrieved_item.empty:
        result = retrieved_item.iloc[0]
    return result
