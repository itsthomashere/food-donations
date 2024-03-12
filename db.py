import streamlit as st
from sqlmodel import create_engine, SQLModel


username = st.secrets["database"]["username"]
password = st.secrets["database"]["password"]
host = st.secrets["database"]["host"]
port = st.secrets["database"]["port"]
database_name = st.secrets["database"]["dialect"]

postgresql_url = f"postgresql://{username}:{password}@{host}:{port}/{database_name}"

engine = create_engine(postgresql_url, echo=False)

