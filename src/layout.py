import streamlit as st

def set_page_config_and_hide_defaults():
    """Set Streamlit page configuration and hide default UI components."""
    # Set page configuration
    st.set_page_config(
        page_title="Barcode Scanner",
        page_icon="📊",
        layout="wide"
    )

    # Hide Streamlit's default menu, footer, and header
    hide_streamlit_defaults = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_defaults, unsafe_allow_html=True)

def display_page_title(title):
    """Display a given title as a centered markdown header in Streamlit."""
    formatted_title = f"<h1 style='text-align: center;'>{title}</h1>"
    st.markdown(formatted_title, unsafe_allow_html=True)
