import os
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# Paths
# --------------------------------------------------

EMBEDDINGS_FILE = os.path.join(
    "embeddings",
    "local_review_embeddings.npy"
)


# --------------------------------------------------
# Load embedding model
# --------------------------------------------------

embedding_model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


# --------------------------------------------------
# Load review data
# --------------------------------------------------

# We will load the review data from DuckDB through
# database.py rather than keeping another copy of it.


# --------------------------------------------------
# Build RAG documents
# --------------------------------------------------

def prepare_rag_documents(con):
    """
    Load customer reviews from DuckDB and prepare
    them for semantic search.
    """

    reviews = con.execute("""
        SELECT
            review_id,
            order_id,
            review_score,
            review_comment_message,
            review_creation_date
        FROM reviews
        WHERE review_comment_message IS NOT NULL
          AND TRIM(review_comment_message) <> ''
    """).df()

    rag_documents = (
        reviews[
            reviews["review_comment_message"].notna()
            & reviews["review_comment_message"].str.strip().ne("")
        ][
            [
                "review_id",
                "order_id",
                "review_score",
                "review_comment_message",
                "review_creation_date"
            ]
        ]
        .copy()
    )

    rag_documents = rag_documents.rename(
        columns={
            "review_comment_message": "review_text"
        }
    )

    rag_documents = rag_documents[
        rag_documents["review_text"].str.strip().ne("")
    ].copy()

    rag_documents = rag_documents.drop_duplicates(
        subset="review_id"
    ).reset_index(drop=True)

    return rag_documents


# --------------------------------------------------
# Load embeddings
# --------------------------------------------------


def load_embeddings():
    """
    Load the locally generated review embeddings.
    """

    embeddings = np.load(
        EMBEDDINGS_FILE
    ).astype(np.float32)

    return embeddings


# --------------------------------------------------
# Build FAISS index
# --------------------------------------------------


def build_index(embeddings):
    """
    Create a FAISS cosine-similarity index.
    """

    dimension = embeddings.shape[1]

    faiss.normalize_L2(embeddings)

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    return index


# --------------------------------------------------
# Create RAG system
# --------------------------------------------------

def create_rag(con):
    """
    Prepare review documents, embeddings,
    and FAISS index.
    """

    rag_documents = prepare_rag_documents(con)

    embeddings = load_embeddings()

    if len(rag_documents) != len(embeddings):
        raise ValueError(
            f"Mismatch between review documents "
            f"({len(rag_documents)}) and embeddings "
            f"({len(embeddings)})."
        )

    index = build_index(embeddings)

    return rag_documents, index


# --------------------------------------------------
# Search customer reviews
# --------------------------------------------------

def search_customer_reviews(
    question: str,
    rag_documents,
    index,
    top_k: int = 8
):
    """
    Search customer reviews using semantic retrieval
    with Maximal Marginal Relevance (MMR) to improve
    diversity among retrieved reviews.

    Returns:
        A dictionary containing:
        - context: formatted review context for Gemini
        - reviews: structured retrieved reviews for the UI
    """

    query_embedding = embedding_model.encode(
        [question],
        normalize_embeddings=True
    )

    query_vector = np.asarray(
        query_embedding,
        dtype=np.float32
    )

    # Retrieve a larger candidate pool first.
    candidate_k = min(
        max(top_k * 5, 50),
        index.ntotal
    )

    scores, indices = index.search(
        query_vector,
        candidate_k
    )

    candidates = []

    for score, idx in zip(scores[0], indices[0]):

        if idx < 0:
            continue

        review = rag_documents.iloc[idx]

        candidates.append({
            "index": int(idx),
            "review_id": review["review_id"],
            "rating": int(review["review_score"]),
            "text": review["review_text"],
            "similarity": float(score)
        })

    # --------------------------------------------------
    # MMR selection
    # --------------------------------------------------

    selected = []

    lambda_param = 0.7

    while candidates and len(selected) < top_k:

        best_candidate = None
        best_score = -float("inf")

        for candidate in candidates:

            relevance = candidate["similarity"]

            if not selected:
                mmr_score = relevance

            else:
                candidate_vector = index.reconstruct(
                    candidate["index"]
                )

                max_similarity = max(
                    float(
                        np.dot(
                            candidate_vector,
                            index.reconstruct(
                                selected_item["index"]
                            )
                        )
                    )
                    for selected_item in selected
                )

                mmr_score = (
                    lambda_param * relevance
                    - (1 - lambda_param) * max_similarity
                )

            if mmr_score > best_score:
                best_score = mmr_score
                best_candidate = candidate

        selected.append(best_candidate)

        candidates.remove(best_candidate)

    retrieved = [
        {
            "review_id": review["review_id"],
            "rating": review["rating"],
            "text": review["text"],
            "similarity": review["similarity"]
        }
        for review in selected
    ]

    context = "\n\n".join(
        f"""Review {i + 1}
        Rating: {r['rating']}/5
        Similarity: {r['similarity']:.4f}
        Text: {r['text']}"""
        for i, r in enumerate(retrieved)
    )

    return {
        "context": context,
        "reviews": retrieved
    }