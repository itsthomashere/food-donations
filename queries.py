from sqlalchemy import text
import streamlit as st  

def check_existing_entry(product_code):
    conn = st.experimental_connection("digitalocean", type="sql")
    with conn.session as s:
        query = text("""
            SELECT quantity, price, weight FROM donation_history WHERE product_code = :product_code
        """)
        result = s.execute(query, {"product_code": product_code}).fetchone()
    return result

def update_existing_entry(product_code, new_quantity, new_total_price, new_total_weight):
    conn = st.experimental_connection("digitalocean", type="sql")
    with conn.session as s:
        update_query = text("""
            UPDATE donation_history
            SET quantity = :quantity, total_price = :total_price, total_weight = :total_weight
            WHERE product_code = :product_code
        """)
        s.execute(update_query, {
            "quantity": new_quantity,
            "total_price": new_total_price,
            "total_weight": new_total_weight,
            "product_code": product_code
        })
        s.commit()

def insert_new_entry(product_info):
    conn = st.experimental_connection("digitalocean", type="sql")
    with conn.session as s:
        insert_query = text("""
            INSERT INTO donation_history (product_code, product_name, category, price, weight, quantity, total_price, total_weight)
            VALUES (:product_code, :product_name, :category, :price, :weight, :quantity, :total_price, :total_weight)
        """)
        s.execute(insert_query, {
            "product_code": product_info['product code'],
            "product_name": product_info['product name'],
            "category": product_info['category'],
            "price": product_info['price'],
            "weight": product_info['weight'],
            "quantity": product_info['quantity'],
            "total_price": product_info['total price'],
            "total_weight": product_info['total weight']
        })
        s.commit()


def save_to_table(product_info: dict) -> None:
    # Time Complexity: O(1) - Both check_existing_entry and update/insert operations are O(1)
    # Space Complexity: O(1) - No additional space used aside from the input dictionary
    existing_entry = check_existing_entry(product_info['product code'])

    if existing_entry:
        new_quantity = existing_entry['quantity'] + 1
        new_total_price = existing_entry['price'] * new_quantity
        new_total_weight = existing_entry['weight'] * new_quantity
        update_existing_entry(product_info['product code'], new_quantity, new_total_price, new_total_weight)
    else:
        insert_new_entry(product_info)

