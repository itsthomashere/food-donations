import datetime

import pandas as pd
import streamlit as st
from sqlalchemy import bindparam, create_engine, text

from weight_extractor import (extract_weight, extract_weight_type,
                              standardise_weight)

category_mapping = {
    "Bakery": "Mixed Bakery",
    "Bread_Bakery_Deserts": "Mixed Bakery",
    "Flowers Plants": "Non-Food Groceries",
    "Kids Food Toiletries": "Non-Food Groceries",
    "High Tea": "Non-Food Groceries",
    "Fruit_Veg": "Mixed Veg",
    "Fruit Vegetables Salads": "Mixed Veg",
    "Meat_poultry_fish": "Mixed Groceries",
    "Meat Poultry Fish": "Mixed Groceries",
    "Easter Feast": "Mixed Groceries",
    "Milk_Dairy_Eggs": "Mixed Groceries",
    "Milk Dairy Eggs": "Mixed Groceries",
    "Beverages & Juices": "Mixed Groceries",
    "Eid Feast": "Mixed Groceries",
    "Pantry": "Non-Food Groceries",
    "Ready Meals": "Mixed Deli",
    "Food To Go": "Mixed Deli",
    "Deli_Entertaining": "Mixed Deli",
    "Recipes": "Mixed Deli",
    "Promotions": "Mixed Deli",
    "Summer Wellbeing": "Mixed Fruit",
    "Food Basket": "Mixed Fruit",
    "Buy Any 2 Save 15 on Berries": "Mixed Fruit",
    "Plant Based Shop": "Mixed Groceries",
    "Ready_meals": "Mixed Deli",
    "Deli Entertaining": "Mixed Deli",
    "Soup Shop": "Mixed Groceries",
}


def extract_product_code(url_segments: list[str]) -> str:
    pc = url_segments.pop()[2:]
    if pc.endswith("?isFromPLP=true"):
        pc = pc.replace("?isFromPLP=true", "")
    return pc


def extract_product_details(
    prod_url: str, prod_price: float, quantity=1
) -> dict[str, str | float]:
    """Extracts product attributes from the item's url and price, both passed in as arguments."""
    pc = pn = c = p = w = ""  # Initialize long form variable names

    pd = {}
    pdetails = prod_url.split("/")
    pc = extract_product_code(pdetails)
    pn = pdetails.pop(-2).replace("-", " ")
    c = category_mapping.get(
        pdetails[5].replace("-", " "), pdetails[5].replace("-", " ")
    )
    p = prod_price
    w = standardise_weight((extract_weight(pn), extract_weight_type(pn)))
    q = quantity

    product_dict = {
        "product_code": pc,
        "product_name": pn,
        "category": c,
        "price": p,
        "weight": w,
        "quantity": quantity,
        "total_price": p * quantity,
        "total_weight": w * quantity,
    }

    return product_dict


def display_overall_totals(df: pd.DataFrame) -> None:
    """
    Display the overall total price and total weight using Streamlit.
    """
    total_price = df["total_price"].sum()
    total_weight = df["total_weight"].sum()
    st.write(f"Overall Total Price: {total_price}")
    st.write(f"Overall Total Weight: {total_weight}")


def get_today_data(table_name: str) -> pd.DataFrame:
    """
    Fetch data from the specified table where 'date_received' is today's date,
    and return it as a pandas DataFrame.
    """
    today = datetime.date.today().strftime("%Y-%m-%d")
    conn = st.experimental_connection("digitalocean", type="sql")
    query = f"SELECT * FROM {table_name} WHERE date_received = '{today}'"
    result = conn.query(query)
    return pd.DataFrame(result)


def calculate_totals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the total price and total weight, grouped by categories from the DataFrame.
    """
    grouped_df = (
        df.groupby("category")
        .agg(
            total_price=pd.NamedAgg(column="total_price", aggfunc="sum"),
            total_weight=pd.NamedAgg(column="total_weight", aggfunc="sum"),
        )
        .reset_index()
    )
    return grouped_df


def get_sql_dataframe(table_name: str, order) -> None:
    conn = st.connection("digitalocean", type="sql")
    query = f"select * from {table_name} order by {order}"
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
    details = user_input.split("|")
    product_name, category, price, weight, product_code = [
        detail.strip() for detail in details
    ]

    # Converting price and weight to float
    price = float(price) if price else 0.0
    weight = float(weight) if weight else 0.0

    return {
        "product_name": product_name,
        "category": category,
        "price": price,
        "weight": weight,
        "product_code": product_code,
    }


def create_product_dictionary(details):
    """
    Create a dictionary with product details and default values for quantity and totals.
    """
    return {
        "date_received": datetime.date.today().strftime("%Y-%m-%d"),
        "product_code": details["product_code"],
        "product_name": details["product_name"],
        "category": details["category"],
        "price": details["price"],
        "weight": details["weight"],
        "quantity": 1,
        "total_price": details["price"],
        "total_weight": details["weight"],
    }


def donations_dataset():
    st.title("Manual Entry")

    user_input = st.text_input(
        "Enter the URL, price and quantity, separated by spacebars: "
    )

    if user_input.startswith("http") and url.contains(" "):
        # split url and price and turn price into float, include try except block
        try:
            prod_url, prod_price, quantity = user_input.split()
            prod_price = float(prod_price)
            quantity = int(quantity)
        except ValueError:
            st.error("Invalid input. Please try again.")
            return
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return
        product_details = extract_product_details(prod_url, prod_price, quantity)

        if product_details is not None and st.button("Submit"):
            st.write("Product Details:")
            st.json(product_details)
            update_table("donation_log", product_details)
            st.success("Saved to donation log.")


def food_dataset():
    # get_sql_dataframe('dataset', 'category')
    table_name = "donation_log"  # Replace with your actual table name
    df = get_today_data(table_name)
    totals_df = calculate_totals(df)
    st.dataframe(totals_df, use_container_width=True, hide_index=True)
    display_overall_totals(totals_df)
