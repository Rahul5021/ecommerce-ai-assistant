from config import client
from tools import search_reviews


chat = client.chats.create(
    model="gemini-3.6-flash",
    config={
        "tools": [
            search_reviews
        ]
    }
)


response = chat.send_message(
    "What are customers complaining about?"
)


print("\n--- RESPONSE OBJECT ---")
print(response)

print("\n--- RESPONSE TEXT ---")
print(response.text)

print("\n--- RESPONSE CANDIDATES ---")
print(response.candidates)