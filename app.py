import streamlit as st

from config import client
import tools


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

        # Clear previous RAG results
        tools.last_retrieved_reviews.clear()

        chat = client.chats.create(
            model="gemini-3.6-flash",
            config={
                "tools": [
                    tools.get_order_summary,
                    tools.get_order_status_summary,
                    tools.get_category_revenue,
                    tools.get_payment_method_summary,
                    tools.get_revenue_by_state,
                    tools.get_revenue_summary,
                    tools.search_reviews
                ]
            }
        )

        try:
            response = chat.send_message(question)

            st.write(response.text)

        except Exception as e:
            st.error(
                "Sorry, I couldn't process your question right now."
            )

            st.caption(
                "Please try again in a moment."
            )

            print(f"Application error: {e}")
            
        # Show retrieved reviews when RAG was used
        if tools.last_retrieved_reviews:

            with st.expander(
                f"🔎 Retrieved Sources ({len(tools.last_retrieved_reviews)})"
            ):

                for i, review in enumerate(
                    tools.last_retrieved_reviews,
                    start=1
                ):

                    st.markdown(
                        f"**Review {i}** · ⭐ {review['rating']}/5"
                    )

                    st.caption(
                        f"Similarity: {review['similarity']:.4f}"
                    )

                    st.write(review["text"])

                    if i < len(tools.last_retrieved_reviews):
                        st.divider()