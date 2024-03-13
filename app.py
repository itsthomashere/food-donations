from datetime import datetime, date

import streamlit as st

import input_parser as ip
import db_operations as dbo
from models import FoodItem, DonatedFoodItem, MissingItem
from layout import set_page_config_and_hide_defaults, display_page_title


def main():
    conn = dbo.get_connection()
    set_page_config_and_hide_defaults()
    display_page_title("Woolworths Food Donations")


main()
