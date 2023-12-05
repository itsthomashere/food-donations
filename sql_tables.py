import streamlit as st
from sqlalchemy import create_engine, text, bindparam
import datetime

def get_sql_dataframe(table_name: str, order) -> None:
    conn = st.connection("digitalocean", type="sql")
    query = f'select * from {table_name} order by {order}'
    messages = conn.query(query)
    st.dataframe(messages, use_container_width=True, hide_index=True)

def update_table(table_name: str, product_details: dict) -> None:
    """
    Updates the specified table with product details.
    """

    query = f"""
    INSERT INTO {table_name} (date_received, product_code, product_name, category, price, weight, quantity, total_price, total_weight)
    VALUES (:date_received, :product_code, :product_name, :category, :price, :weight, :quantity, :total_price, :total_weight)
    ON CONFLICT (product_code)
    DO UPDATE SET
    quantity = {table_name}.quantity + EXCLUDED.quantity,
    total_price = {table_name}.price * ({table_name}.quantity + EXCLUDED.quantity),
    total_weight = {table_name}.weight * ({table_name}.quantity + EXCLUDED.quantity);
    """

    # Connect to the database and execute the query
    conn = st.connection("digitalocean", type="sql")
    with conn.session as s:
        s.execute(text(query), product_details)
        s.commit()

def parse_input(user_input):
    """
    Parse the input string from the user to extract product details.
    """
    details = user_input.split('|')
    product_name, category, price, weight, product_code = [detail.strip() for detail in details]

    # Converting price and weight to float
    price = float(price) if price else 0.0
    weight = float(weight) if weight else 0.0

    return {
        'product_name': product_name,
        'category': category,
        'price': price,
        'weight': weight,
        'product_code': product_code
    }


def create_product_dictionary(details):
    """
    Create a dictionary with product details and default values for quantity and totals.
    """
    return {
        'date_received': datetime.now().strftime('%Y-%m-%d'),
        'product_code': details['product_code'],
        'product_name': details['product_name'],
        'category': details['category'],
        'price': details['price'],
        'weight': details['weight'],
        'quantity': 1,
        'total_price': details['price'],
        'total_weight': details['weight']
    }

def donations_dataset():
    st.title("Manual Entry")
    
    user_input = st.text_input("Enter food item details (Format: Name | Category | Price | Weight | Code):")

    if user_input:
        details = parse_input(user_input)
        product_details = create_product_dictionary(details)
        st.write("Product Details:")
        st.json(product_details)
    

def food_dataset():
    get_sql_dataframe('dataset', 'category')

