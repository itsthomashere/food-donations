import streamlit as st

from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Connection

def get_connection() -> Connection:
    """Establishes and returns a database connection."""
    return st.connection("digitalocean", type="sql", autocommit=True)
