import streamlit as st
from sqlalchemy import text
import db.constants as c
import datetime


def save_pending_product_codes(conn, date=None):
    """
    Saves pending product codes with a specified date (defaulting to today) to a text file.
    """
    if date is None:
        date = datetime.date.today()

    date_str = date if isinstance(date, str) else date.strftime("%Y-%m-%d")

    try:
        # Adjusting the call to conn.query to match the provided example
        query = c.FETCH_PENDING_PRODUCT_CODES_BY_DATE
        parameters = {"date_added": date_str}

        pending_product_codes = conn.query(query, params=parameters)

        # Assuming pending_product_codes is a DataFrame
        if not pending_product_codes.empty:
            with open(f"pending_product_codes_{date_str}.txt", "w") as file:
                for _, row in pending_product_codes.iterrows():
                    file.write(f'{row["product_code"]}\n')
        else:
            print("No pending product codes found for the specified date.")
    except Exception as e:
        print(f"An error occurred: {e}")
