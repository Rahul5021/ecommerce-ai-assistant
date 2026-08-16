import streamlit as st

from config import client
from tools import *


st.set_page_config(
    page_title="E-Commerce AI Assistant",
    page_icon="🛒",
    layout="wide"
)


st.title("🛒 E-Commerce AI Assistant")

st.write(
    "Your AI-powered business analytics assistant."
)


question = st.chat_input(
    "Ask a question about your business..."
)


if question:

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):

        chat = client.chats.create(
            model="gemini-3.6-flash",
            config={
                "tools": [
                    get_order_summary,
                    get_order_status_summary,
                    get_category_revenue,
                    get_payment_method_summary,
                    get_revenue_by_state,
                    get_revenue_summary
                ]
            }
        )

        response = chat.send_message(question)

        st.write(response.text)