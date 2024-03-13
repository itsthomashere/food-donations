from datetime import datetime, date

import streamlit as st

import input_parser as ip
import db_operations as dbo
from models import FoodItem, DonatedFoodItem, MissingItem
from layout import set_page_config_and_hide_defaults, display_page_title


def main():
    set_page_config_and_hide_defaults() # must always be called first
    conn = dbo.get_connection()
    display_page_title("Woolworths Food Donations")

    user_input = st.chat_input("Enter a barcode: ")
    st.write("Missing item: 6009226866340")
    st.write("Dataset item: 6009233018428")

    if user_input:
        try:
            routes = ip.get_routes()
            action, data = ip.parse_input(user_input)

            if action == "display" and data in routes:
                dbo.fetch_all_items(conn, routes[data])
            
            elif action == "barcode":
                barcode, quantity = data
                st.write(f"Barcode: {barcode}, Quantity: {quantity}")

                # with barcode and quantity in hand, we can now continue to retrieve the item from the database
                try:
                    item = conn.query("select * from dataset where product_code = :product_code", ttl=3600, params={"product_code": barcode})
                    st.dataframe(item)
                except Exception as e:
                    st.error(f"Error retrieving item: {e}")

            else:
                st.write("Invalid input or table not found.")

        except Exception as e:
            st.error(e)

main()
