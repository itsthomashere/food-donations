import os

import openai
import streamlit as st
from sqlalchemy import create_engine, text
#from streamlit_option_menu import option_menu

import constants as c

product_info = {
    'product code': 6009178236888,
    'product name': 'Pork Bacon & Cheese Bangers 500 g',
    'category': 'Mixed Groceries',
    'price': 64.99,
    'weight': 0.5,
    'quantity': 1,
    'total price': 64.99,
    'total weight': 0.5,
}

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

def create_chat_completion(model: str, messages: list[dict[str, str]]) -> None:
    """Generate and display chat completion using OpenAI and Streamlit."""
    with st.chat_message(name="assistant", avatar="./icons/assistant.png"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model=model,
            messages=messages,
            stream=True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

        #check_keywords(full_response)
    return full_response

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


def check_existing_entry(table_name, product_code):
    conn = st.experimental_connection("digitalocean", type="sql")
    with conn.session as s:
        query = text(f"""
            SELECT quantity, price, weight FROM {table_name} WHERE product_code = :product_code
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

# --- CONFIGURE API KEY ---
openai.api_key = st.secrets["OPENAI_API_KEY"]


customize_streamlit_ui()

create_tables()

st.title("Food Donations")
st.write(product_info)

# --- USER INTERACTION ---
user_message = st.chat_input("Enter a barcode")
if user_message:
    # --- DISPLAY MESSAGE TO STREAMLIT UI, UPDATE SQL, UPDATE SESSION STATE ---
    display_message(role="user", content=user_message)
    with st.spinner("Searching dataset."):
        result = check_existing_entry('dataset', user_message)
        if result is not None:
            st.success(result)
        else:
            st.write("Not in there.")

    st.write(result)

    # --- PASS THE ENTIRETY OF SESSION STATE MESSAGES TO OPENAI ---
    try:
        response = create_chat_completion(
            model="gpt-4", 
            messages=st.session_state["messages"]
        ) # create_chat_completion already displays message to streamlit UI
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)
        pass


