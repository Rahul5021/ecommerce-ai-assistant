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

print("\n--- RAG RESULTS ---\n")
print(result)