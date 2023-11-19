import os
import streamlit as st
import openai
import constants as c
from sqlalchemy import create_engine, text


import uuid
from datetime import datetime, timedelta
from openai import api_requestor

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
        # Create the 'users' table with a timestamp column
        s.execute(text("""
                    CREATE TABLE IF NOT EXISTS users (
                    ID SERIAL PRIMARY KEY,
                    uuid VARCHAR(36) UNIQUE,
                    timestamp TIMESTAMPTZ);"""))
        
        # Create the 'submissions' table with a foreign key relation to 'users'
        s.execute(text("""
                    CREATE TABLE IF NOT EXISTS submissions (
                    ID SERIAL PRIMARY KEY,
                    uuid VARCHAR(36),
                    timestamp TIMESTAMPTZ,
                    role VARCHAR(9) CHECK (LENGTH(role) >= 4),
                    content TEXT,
                    FOREIGN KEY (uuid) REFERENCES users(uuid));"""))
        s.commit()

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
    with st.chat_message(
        name=role, 
        avatar=determine_image(role=role, content=content)):
        st.write(content)

# --- CONFIGURE API KEY ---
openai.api_key = st.secrets["OPENAI_API_KEY"]


customize_streamlit_ui()
try:
    create_tables()
except Exception:
    pass

# --- USER INTERACTION ---
user_message = st.chat_input("Present an idea")
if user_message:
    # --- DISPLAY MESSAGE TO STREAMLIT UI, UPDATE SQL, UPDATE SESSION STATE ---
    display_message(role="user", content=user_message)
    try:
        save_to_sql(user_id=st.session_state["uuid"], role="user", content=user_message)
    except Exception:
        pass

    # --- PASS THE ENTIRETY OF SESSION STATE MESSAGES TO OPENAI ---
    try:
        response = create_chat_completion(
            model="gpt-4", 
            messages=st.session_state["messages"]
        ) # create_chat_completion already displays message to streamlit UI

    except openai.error.Timeout as e:
        # Handle timeout error, e.g. retry or log
        print(f"OpenAI API request timed out: {e}")
        pass
    except openai.error.APIError as e:
        # Handle API error, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")
        pass
    except openai.error.APIConnectionError as e:
        # Handle connection error, e.g. check network or log
        print(f"OpenAI API request failed to connect: {e}")
        pass
    except openai.error.InvalidRequestError as e:
        # Handle invalid request error, e.g. validate parameters or log
        print(f"OpenAI API request was invalid: {e}")
        pass
    except openai.error.AuthenticationError as e:
        # Handle authentication error, e.g. check credentials or log
        print(f"OpenAI API request was not authorized: {e}")
        pass
    except openai.error.PermissionError as e:
        # Handle permission error, e.g. check scope or log
        print(f"OpenAI API request was not permitted: {e}")
        pass
    except openai.error.RateLimitError as e:
        # Handle rate limit error, e.g. wait or log
        print(f"OpenAI API request exceeded rate limit: {e}")
        pass
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)
        #self.status_update(False, error_message)
        # CustomApplication.processEvents()
        pass

    # --- DISPLAY MESSAGE TO STREAMLIT UI, UPDATE SQL, UPDATE SESSION STATE ---
    try:
        save_to_sql(user_id=st.session_state["uuid"], role="assistant", content=response)
    except Exception:
        pass

