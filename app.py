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
                    # query donation_history to first check if product_code is already present
                    # if it is, update the quantity and total_price/total_weight
                    st.write("Checking if item is in donation history...")
                    if dbo.check_if_item_in_donation_history(conn, barcode, date.today()):
                        st.write("Item already in donation history.")
                        # update the quantity and total_price/total_weight
                        updated_item = dbo.update_donation_history_item(conn, barcode, quantity)
                    else:
                        st.write("Item not in donation history.")
                        # retrieve the food item from the dataset

                    item = dbo.get_food_item_by_product_code(conn, barcode, date.today())
                    if not item.empty:
                        food_item_row = item.iloc[0]

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

                        # food_item = FoodItem(
                        #     product_code=food_item_row["product_code"],
                        #     product_name=food_item_row["product_name"],
                        #     category=food_item_row["category"],
                        #     price=food_item_row["price"],
                        #     weight=food_item_row["weight"],
                        # )
                        # st.write(food_item)

                        # Save the item to donation_history
                        # st.write("Converting to DonatedFoodItem...")
                        # donated_item = DonatedFoodItem(
                        #     date_received=datetime.now(),
                        #     product_code=food_item.product_code,
                        #     product_name=food_item.product_name,
                        #     category=food_item.category,
                        #     price=food_item.price,
                        #     weight=food_item.weight,
                        #     quantity=quantity,
                        #     total_price=food_item.price * quantity,
                        #     total_weight=food_item.weight * quantity,
                        # )
                        st.write(donated_item)

                        # save donated item to donation_history
                        st.write("Adding DonatedFoodItem to donation_history...")
                        
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
