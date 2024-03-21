from datetime import datetime
import db.constants as c

def save_pending_product_codes(conn):
    """
    Fetches pending product codes and saves them with today's date to a text file.
    """
    # Fetch pending product codes using a predefined SQL query
    pending_product_codes = conn.query(c.FETCH_PENDING_PRODUCT_CODES)

    # Prepare the filename with today's date
    today_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"pending_product_codes_{today_date}.txt"

    # Check if pending_product_codes is not empty and proceed to save to file
    if not pending_product_codes.empty:
        with open(filename, "w") as file:
            for index, row in pending_product_codes.iterrows():
                file.write(f"{row['product_code']}, {today_date}\n")
        print(f"Pending product codes saved to {filename}")
    else:
        print("No pending product codes to save.")
