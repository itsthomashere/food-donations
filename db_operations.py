import streamlit as st

from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Connection

def get_connection():
    """Establishes and returns a database connection."""
    return st.connection("digitalocean", type="sql", autocommit=True)

def fetch_all_items(conn, model):
    """Fetches all items using the specified SQLAlchemy model."""
    st.write(f"Fetching all items from {model}")
