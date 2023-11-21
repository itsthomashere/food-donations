import streamlit as st
from sqlalchemy import create_engine, text
#from streamlit_option_menu import option_menu

import constants as c

product_info = (6009178236888, 20011697)

def customize_streamlit_ui() -> None:
    st.set_page_config(
        page_title="→ 🤖 → 🕸️ IdeaVault!",
        page_icon="💡",
        layout="centered"
        )

    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_st_style, unsafe_allow_html=True)

def create_tables() -> None:
    conn = st.experimental_connection("digitalocean", type="sql")
    with conn.session as s:
        # Create the 'donation_history' table with specified columns
        s.execute(text("""
                    CREATE TABLE IF NOT EXISTS donation_history (
                    product_code VARCHAR(13),
                    product_name VARCHAR(255),
                    category VARCHAR(255),
                    price NUMERIC(10, 2),
                    weight NUMERIC(10, 2),
                    quantity INT,
                    total_price NUMERIC(10, 2),
                    total_weight NUMERIC(10, 2));"""))
        s.commit()


def item_exists(table_name: str, product_code: str) -> bool:
    conn = st.experimental_connection("digitalocean", type="sql")
    with conn.session as s:
        query = text(f"""
            SELECT product_code FROM {table_name} WHERE product_code = :product_code
        """)
        result = s.execute(query, {"product_code": product_code}).fetchone()
    return result is not None


def check_existing_entry(table_name: str, product_code: str) -> tuple | None:
    conn = st.experimental_connection("digitalocean", type="sql")
    with conn.session as s:
        query = text(f"""
            SELECT product_code, product_name, category, price, weight FROM {table_name} WHERE product_code = :product_code
        """)
        result = s.execute(query, {"product_code": product_code}).fetchone()
    return result


def save_to_sql(user_id: str, role: str, content: str) -> None:
    conn = st.experimental_connection("digitalocean", type="sql")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conn.session as s:
        # Insert user_id and timestamp into 'users' table if it doesn't already exist
        s.execute(
            text('INSERT INTO users (uuid, timestamp) VALUES (:uuid, :timestamp) ON CONFLICT (uuid) DO NOTHING;'),
            params=dict(uuid=user_id, timestamp=timestamp)
        )
        
        # Insert into 'submissions' table
        s.execute(
            text('INSERT INTO submissions (uuid, timestamp, role, content) VALUES (:uuid, :timestamp, :role, :content);'),
            params=dict(uuid=user_id, timestamp=timestamp, role=role, content=content)
        )
        s.commit()

def get_sql_dataframe(table_name: str, uuid: str) -> None:
    conn = st.experimental_connection("digitalocean", type="sql")
    query = f'select * from {table_name} where uuid = :uuid order by timestamp'
    messages = conn.query(query, ttl=timedelta(minutes=1), params={"uuid": uuid})
    st.dataframe(messages)


def display_message(role: str, content: str) -> None:
    with st.chat_message(name=role):
        st.write(content)


customize_streamlit_ui()

create_tables()

st.title("Food Donations")
st.write(product_info)

# --- USER INTERACTION ---
user_input = st.text_input("Enter a barcode")
if user_input:

    st.divider()
    st.header("Is it already in today's donated goods?")
    donations = check_existing_entry('donation_history', user_input)
    if donations is not None:
        st.success("Incrementing quantity.")
        st.write("`product_details = get_product_info(donations, product_code)`")
        st.write("`increment_quantity(product_details)`")
        st.write("`add_new_product(donations, product_code)`")
    else:
        st.write("Negative. Moving on...")
        st.divider()

    st.header("Is it in my 6,000 item dataset?")
    if item_exists('dataset', user_input):
    #result = check_existing_entry('dataset', user_input)
    #if result is not None:
        st.success("Item located in dataset.")
        st.write("Extracting product details associated with product code...")
        st.write("`product_details = extract_product_details('dataset', barcode)`")
        result = check_existing_entry('dataset', user_input)
        st.write("Adding columns 'quantity', 'total price' and 'total weight'...")
        st.write("`product_details.extend(additional_columns)`")
        additional_columns = [1, result[3], result[4]]
        product_details = list(result) + list(additional_columns)
        st.write(result)
        st.write("Appending new row to today's donated items.")
        st.write("`add_new_product('donations', product_details)`")
        st.divider()
    else:
        st.write("Negative. Moving on...")
        st.divider()
        st.header("Product code not found in dataset.")
        col1, col2 = st.columns(2)
        with col1:
            manual_entry = st.button("Enter manually")
        with col2:
            webscrape = st.button("Try webscraping")
        st.divider()

        if manual_entry:
            st.text_input("Enter product details")

            with st.form("my_form"):
                st.write("Enter product details")
                product_name = st.text_input("Enter product_name:")
                price = st.text_input("Enter price:")
                category = st.text_input("Enter category:")
                weight = st.text_input("Enter weight:")
                product_code = st.text_input("Enter product code", user_input)

                # Every form must have a submit button.
                submitted = st.form_submit_button("Submit")
                if submitted:

                    product_details = {
                        'product_code': product_code,
                        'product_name': product_name,
                        'category': category,
                        'price': price,
                        'weight': weight,
                        'quantity': 1,
                        'total_price': price,
                        'total_weight': weight
                    }

                    st.write(product_details)
                    st.write("Updating both databases with newly logged item")
                    st.write("`add_new_product('dataset', product_details)`")
                    st.write("`add_new_product('donation_history', product_details)`")
