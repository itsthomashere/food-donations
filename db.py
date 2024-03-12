import streamlit as st
from sqlmodel import create_engine, SQLModel


username = st.secrets["connections.digitalocean"]["username"]
password = st.secrets["connections.digitalocean"]["password"]
host = st.secrets["connections.digitalocean"]["host"]
port = st.secrets["connections.digitalocean"]["port"]
database_name = st.secrets["connections.digitalocean"]["dialect"]

postgresql_url = f"postgresql://{username}:{password}@{host}:{port}/{database_name}"

engine = create_engine(postgresql_url, echo=False)

