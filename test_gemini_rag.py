from config import client, SYSTEM_INSTRUCTION
import tools


chat = client.chats.create(
    model="gemini-3.6-flash",
    config={
        "system_instruction": SYSTEM_INSTRUCTION,
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


question = "What are customers complaining about?"


response = chat.send_message(question)


print("\n--- QUESTION ---")
print(question)

print("\n--- RESPONSE ---")
print(response.text)