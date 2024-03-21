"""A Streamlit app for managing Woolworths Food Donations."""

from datetime import datetime, date
import streamlit as st
from sqlalchemy import text
import src.input_parser as ip
import db.operations as dbo
from src.models import DonatedFoodItem, MissingItem
from src.layout import set_page_config_and_hide_defaults, display_page_title
import db.constants as c
import services.inventory_updater as iu

def process_user_input(conn, user_input):
    """Process user input and handle the database operations accordingly."""
    try:
        action, data = ip.parse_input(user_input)
    except Exception as e:
        st.error(e)
        return  # Early return if parsing fails

    if action == "display":
        handle_display_action(conn, data)
    elif action == "barcode":
        handle_barcode_action(conn, data)
    else:
        st.write("Invalid input or table not found.")

def handle_display_action(conn, data):
    """Handle the display action for the given data."""
    routes = ip.get_routes()
    if data in routes:
        dbo.fetch_all_items(conn, routes[data])
    else:
        st.write("Invalid route for display action.")

def handle_barcode_action(conn, data):
    """Handle the barcode action for the given data."""
    barcode, quantity = data
    try:
        process_donated_food_item(conn, barcode, quantity)
    except Exception as e:
        st.error(f"Error processing barcode action: {e}")

def process_donated_food_item(conn, barcode, quantity):
    """Process a donated food item, adding it to the database or handling it as missing."""
    item = dbo.get_food_item_by_product_code(conn, barcode, date.today())
    if not item.empty:
        save_donated_item(conn, barcode, item.iloc[0], quantity)
    else:
        handle_missing_item(conn, barcode)

def save_donated_item(conn, barcode, food_item_row, quantity):
    """Save a donated item to the donation history."""
    col1, col2, col3 = st.columns(3)
    with col2:
        st.write(food_item_row)
    donated_item = DonatedFoodItem(
        date_received=datetime.now(),
        product_code=food_item_row["product_code"],
        product_name=food_item_row["product_name"],
        category=food_item_row["category"],
        price=food_item_row["price"],
        weight=food_item_row["weight"],
        quantity=quantity,
        total_price=food_item_row["price"] * quantity,
        total_weight=food_item_row["weight"] * quantity,
    )
    try:
        dbo.save_donated_item_to_donation_history(conn, donated_item)
        current_quantity = dbo.get_current_quantity(conn, barcode)
        st.success(f"Item added. Current quantity of {barcode}: {current_quantity.iloc[0]['quantity']}")
    except Exception as e:
        st.error(e)
    
def handle_missing_item(conn, barcode):
    """Handle a missing item by adding it to the barcode queue."""
    missing_item = MissingItem(
        date_added=datetime.now(),
        product_code=barcode,
        status="pending",
    )
    dbo.add_missing_item_to_queue(conn, missing_item)

def main():
    """Main function to run the Streamlit app."""
    set_page_config_and_hide_defaults()  # Setup Streamlit page config
    conn = dbo.get_connection()  # Establish database connection
    display_page_title("Woolworths Food Donations")  # Display page title
    user_input = st.chat_input("Enter a barcode: ")  # Get user input

    if user_input:
        if user_input.startswith("{"):
            try:
                dbo.save_donated_item_to_donation_history_dict(conn, user_input)
                st.stop()
                return
            except Exception as e:
                st.error(e)
        process_user_input(conn, user_input)  # Process the input

# main()
