import streamlit as st
from sqlalchemy import create_engine, text, bindparam

def get_sql_dataframe(table_name: str, order) -> None:
    conn = st.connection("digitalocean", type="sql")
    query = f'select * from {table_name} order by {order}'
    messages = conn.query(query)
    st.dataframe(messages, use_container_width=True, hide_index=True)


def update_table(table_name, donation_data):
    """Update a SQL table with donation data."""
    # Define the SQL query with placeholders
    query = text(f"""
    INSERT INTO {table_name} (date_received, product_code, product_name, category, price, weight, quantity, total_price, total_weight)
    VALUES (:date_received, :product_code, :product_name, :category, :price, :weight, :quantity, :total_price, :total_weight)
    ON CONFLICT (product_code)
    DO UPDATE SET
        quantity = {table_name}.quantity + EXCLUDED.quantity,
        total_price = {table_name}.price * ({table_name}.quantity + EXCLUDED.quantity),
        total_weight = {table_name}.weight * ({table_name}.quantity + EXCLUDED.quantity);
    """)

    # Explicitly bind parameters
    for key, value in donation_data.items():
        query = query.bindparams(bindparam(key, value))

    # Connect to the database
    conn = st.connection("digitalocean", type="sql")

    # Execute the query using the donation data
    with conn.session as s:
        s.execute(query)
        s.commit()


def donations_dataset():
    product_details = {
        'date_received': '2023-11-30',
        'product_code': '20000370',
        'product_name': 'Pork Bangers 500 g',
        'category': 'Mixed Groceries',
        'price': 59.99,
        'weight': 0.5,
        'quantity': 1,
        'total_price': 59.99,
        'total_weight': 0.5
    }

    get_sql_dataframe('donation_log', 'date_received')
    dummy_data = st.button("Send dummy data...")
    if dummy_data:
        update_table('donation_log', product_details)


def food_dataset():
    get_sql_dataframe('dataset', 'category')

