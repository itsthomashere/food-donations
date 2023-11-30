import streamlit as st
from sqlalchemy import create_engine, text, bindparam

def get_sql_dataframe(table_name: str, order) -> None:
    conn = st.connection("digitalocean", type="sql")
    query = f'select * from {table_name} order by {order}'
    messages = conn.query(query)
    st.dataframe(messages, use_container_width=True, hide_index=True)


def update_table(table_name: str, donation_data: tuple[str | float]) -> None:
    st.write(donation_data)
    for i in donation_data:
        st.write(i)
    if not isinstance(donation_data, tuple) or len(donation_data) != 5:
        raise ValueError("donation_data must be a tuple with exactly 5 elements.")

    product_code, product_name, category, price, weight = donation_data
    product_code = str(product_code)  # Convert product_code to string

    # Construct the SQL query with named parameters
    query = f"""
    INSERT INTO {table_name} (product_code, product_name, category, price, weight)
    VALUES (:product_code, :product_name, :category, :price, :weight)
    ON CONFLICT (product_code) DO UPDATE SET
        product_name = EXCLUDED.product_name,
        category = EXCLUDED.category,
        price = EXCLUDED.price,
        weight = EXCLUDED.weight;
    """

    # Connect to the database and execute the query
    conn = st.connection("digitalocean", type="sql")
    with conn.session as s:
        s.execute(query, {
            'product_code': product_code, 
            'product_name': product_name, 
            'category': category, 
            'price': price, 
            'weight': weight
        })
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

