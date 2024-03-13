"""Module for parsing and handling user input."""
import streamlit as st
from models import FoodItem, DonatedFoodItem, MissingItem


def get_routes():
    return {
            "donation_history": DonatedFoodItem,
            "dataset": FoodItem,
            "barcode_queue": MissingItem
        }

def parse_input(user_input):
    """Parse the user input to determine action."""
    if user_input.startswith("display "):
        return "display", user_input.split(maxsplit=1)[1]
    else:
        return "barcode", handle_barcode_input(user_input)

def handle_barcode_input(user_input):
    """Process barcode input, extracting barcode and quantity."""
    try:
        input_tuple = tuple(user_input.split()) if " " in user_input else (user_input,)
        barcode = input_tuple[-1]
        quantity = int(str(input_tuple[0]).strip("x")) if len(input_tuple) > 1 else 1
        return barcode, quantity
    except Exception as e:
        st.error(f"Error processing barcode input: {e}")
        return None, None

