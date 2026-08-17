from database import con
from rag import create_rag, search_customer_reviews


rag_documents, index = create_rag(con)

print("Documents:", len(rag_documents))
print("Vectors:", index.ntotal)


question = "What problems are customers complaining about?"

result = search_customer_reviews(
    question,
    rag_documents,
    index,
    top_k=8
)

print("\n--- RAG CONTEXT ---\n")
print(result["context"])

print("\n--- RETRIEVED REVIEWS ---\n")

for i, review in enumerate(result["reviews"], start=1):
    print(f"Review {i}")
    print(f"Review ID: {review['review_id']}")
    print(f"Rating: {review['rating']}/5")
    print(f"Similarity: {review['similarity']:.4f}")
    print(f"Text: {review['text']}")
    print()