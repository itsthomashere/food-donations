from datetime import datetime, date

import streamlit as st
from sqlalchemy import text

import input_parser as ip
import db_operations as dbo
from models import FoodItem, DonatedFoodItem, MissingItem
from layout import set_page_config_and_hide_defaults, display_page_title


def main():
    set_page_config_and_hide_defaults()  # must always be called first
    conn = dbo.get_connection()
    display_page_title("Woolworths Food Donations")

    user_input = st.chat_input("Enter a barcode: ")
    st.write("Missing item: 6009226866340")
    st.write("Dataset item: 6009217484898")

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
                    item = conn.query(
                        "select * from dataset where product_code = :product_code",
                        ttl=3600,
                        params={"product_code": barcode},
                    )
                    if not item.empty:
                        food_item_row = item.iloc[0]
                        food_item = FoodItem(
                            product_code=food_item_row["product_code"],
                            product_name=food_item_row["product_name"],
                            category=food_item_row["category"],
                            price=food_item_row["price"],
                            weight=food_item_row["weight"],
                        )
                        st.write(food_item)
                    else:
                        st.write("Adding MissingItem to barcode_queue...")
                        missing_item = MissingItem(
                            date_added=datetime.now(),
                            product_code=barcode,
                            status="pending",
                        )
                        with conn.session as session:
                            session.execute(text(
                                """
                                                INSERT INTO barcode_queue (date_added, product_code, status)
                                                VALUES (:date_added, :product_code, :status)"""),
                                {
                                    "date_added": missing_item.date_added,
                                    "product_code": missing_item.product_code,
                                    "status": missing_item.status,
                                },
                            )
                            session.commit()
                except Exception as e:
                    st.error(f"Error retrieving item: {e}")

            else:
                st.write("Invalid input or table not found.")

        except Exception as e:
            st.error(e)


main()
