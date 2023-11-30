import streamlit as st

def receive_barcodes():
    user_input = st.text_input("Enter a barcode")
    if user_input:
        st.write(user_input)

