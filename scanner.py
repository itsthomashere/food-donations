import datetime

import streamlit as st
from sqlalchemy import create_engine, text

from sql_tables import update_table


def construct_product_details(product_code, product_name, category, price, weight):
    """
    Construct a dictionary of product details.
    """
    return {
        'date_received': datetime.date.today(),
        'product_code': product_code,
        'product_name': product_name,
        'category': category,
        'price': price,
        'weight': weight,
        'quantity': 1,
        'total_price': price,
        'total_weight': weight
    }

def display_form():
    """Display the form for entering product details and return the details."""
    with st.form("product_details_form"):
        st.write("Enter Product Details")
        
        # Use session_state values as default values
        product_code = st.text_input("Product Code", value=st.session_state['product_code'])
        product_name = st.text_input("Product Name", value=st.session_state['product_name'])
        category = st.text_input("Category", value=st.session_state['category'])
        price = st.number_input("Price", min_value=0.0, format="%.2f", value=st.session_state['price'])
        weight = st.number_input("Weight", min_value=0.0, format="%.2f", value=st.session_state['weight'])
        
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            st.write(product_code, product_name, category, price, weight)
            # Return the values entered in the form
            return product_code, product_name, category, price, weight

    return None


def get_formatted_date():
    """Return today's date in 'YYYY-MM-DD' format."""
    today = datetime.date.today()
    return today.strftime('%Y-%m-%d')


def find_product(table_name: str, product_code: str) -> tuple | None:
    conn = st.connection("digitalocean", type="sql")
    with conn.session as s:
        query = text(f"""
            SELECT product_code, product_name, category, price, weight FROM {table_name} WHERE product_code = :product_code
        """)
        result = s.execute(query, {"product_code": product_code}).fetchone()
    return result


def in_donations_table(product_code, date):
    """Checks to see if an item already exists in the dataset"""
    query = text(f"""
    SELECT COUNT(*)
    FROM donation_log
    WHERE product_code = :product_code AND date_received = :date_received;
    """)
    conn = st.connection("digitalocean", type="sql")
    with conn.session as s:
        #result = s.execute(query)
        result = s.execute(query, {"product_code": product_code, "date_received": date}).fetchone()
    try:
        return bool(result[0])
    except Exception as e:
        return result[0] if isinstance(result, tuple) else result


def receive_barcodes():

    # Initialize session state for form values
    if 'product_code' not in st.session_state:
        st.session_state['product_code'] = ''

    if 'product_name' not in st.session_state:
        st.session_state['product_name'] = ''

    if 'category' not in st.session_state:
        st.session_state['category'] = ''

    if 'price' not in st.session_state:
        st.session_state['price'] = 0.0

    if 'weight' not in st.session_state:
        st.session_state['weight'] = 0.0

    user_input = st.chat_input("Enter a barcode")

    if user_input:
        product_details: tuple = find_product("dataset", user_input)
        if product_details is not None:
            product_code, product_name, category, price, weight = product_details

            
            product_details = {
                    'date_received': datetime.date.today(),
                    'product_code': product_code,
                    'product_name': product_name,
                    'category': category,
                    'price': price,
                    'weight': weight,
                    'quantity': 1,
                    'total_price': price,
                    'total_weight': weight
                }

            update_table("donation_log", product_details)
            st.success("Saved item to donation log.")
        else:
            st.write("Barcode not in dataset.")
            product_details = None

            product_info = display_form()
            if product_info:
                # Update session state with form values
                st.session_state['product_code'], st.session_state['product_name'], \
                st.session_state['category'], st.session_state['price'], \
                st.session_state['weight'] = product_info
        
                # Retrieve values from session state
                product_code = st.session_state['product_code']
                product_name = st.session_state['product_name']
                category = st.session_state['category']
                price = st.session_state['price']
                weight = st.session_state['weight']

                # Construct product details and update table
                product_details = construct_product_details(product_code, product_name, category, price, weight)
                st.write("Product Details:")
                update_table("donation_log", product_details)
                st.success("Saved to donations.")

