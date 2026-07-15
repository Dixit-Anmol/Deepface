import os
import pickle
import re
import sys
import numpy as np

# Import configuration
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    from config import EMBEDDING_MODEL_NAME, FAISS_INDEX_PATH, METADATA_PATH, TOP_K
except ImportError as e:
    print(f"Error loading dependencies in retriever: {e}")
    sys.exit(1)


class GitaRetriever:
    def __init__(self):
        # Cache instances
        self.model = None
        self.index = None
        self.chunks = None
        self.load_resources()

    def load_resources(self):
        """Loads FAISS index, metadata, and embedding model."""
        if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(METADATA_PATH):
            raise FileNotFoundError(
                "FAISS vector store files not found. Please run build_index.py first."
            )
            
        print("Loading retriever resources...")
        try:
            self.index = faiss.read_index(FAISS_INDEX_PATH)
            with open(METADATA_PATH, "rb") as f:
                self.chunks = pickle.load(f)
            self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        except Exception as e:
            print(f"Retriever Resource Loading Failure: {e}")
            sys.exit(1)

    def retrieve(self, query: str, top_k: int = TOP_K) -> list[dict]:
        """
        Retrieves top_k relevant text chunks based on semantic similarity search or specific bonus routers.
        
        Parameters:
            query (str): The search query.
            top_k (int): Number of top documents to retrieve.
            
        Returns:
            list[dict]: List of matched chunks with texts, scores, and metadata.
        """
        # --- Router 1: Specific Verse Search (Bonus Feature 1) ---
        verse_match = re.search(r'\bverse\s+(\d+)\b', query, re.IGNORECASE)
        shloka_match = re.search(r'\b(श्लोक|मंत्र)\s+(\d+)\b', query)
        verse_num = None
        if verse_match:
            verse_num = int(verse_match.group(1))
        elif shloka_match:
            verse_num = int(shloka_match.group(2))
            
        if verse_num is not None:
            # Look up chunks containing this specific verse in metadata
            matched_chunks = []
            for chunk in self.chunks:
                # Some shlokas are grouped, e.g., verses 1-3. We check boundaries.
                v_meta = chunk["metadata"].get("verse")
                if v_meta == verse_num or (v_meta is not None and isinstance(v_meta, int) and v_meta >= verse_num - 2 and v_meta <= verse_num):
                    matched_chunks.append({
                        "text": chunk["text"],
                        "metadata": chunk["metadata"],
                        "score": 0.0 # perfect metadata match
                    })
            if matched_chunks:
                print(f"[Router] Direct Metadata match found for Verse {verse_num}.")
                return matched_chunks

        # --- Router 2: Specific Keywords Boosting (Bonus Features 3 & 4) ---
        # If querying for Daivi Sampad or Asuri Qualities, we boost relevant chunks.
        is_daivi_query = any(w in query.lower() for w in ["daivi", "divine qualities", "दैवी", "दैवी संपदा"])
        is_asuri_query = any(w in query.lower() for w in ["asuri", "demoniac", "आसुरी", "आसुरी संपदा"])

        # --- Semantic Similarity Search ---
        # Generate query embedding vector
        query_str = str(query).strip()
        query_vector = self.model.encode([query_str])
        query_vector = np.array(query_vector).astype("float32")
        
        # Search the FAISS L2 index (smaller L2 distance means higher similarity)
        # We search a larger pool (e.g. 10) to apply category boosting or filtering
        search_k = min(len(self.chunks), top_k * 2)
        distances, indices = self.index.search(query_vector, search_k)
        
        retrieved = []
        for i in range(search_k):
            idx = indices[0][i]
            dist = distances[0][i]
            # Convert L2 distance to a raw score representation
            score = float(dist)
            
            chunk = self.chunks[idx]
            text = chunk["text"]
            meta = chunk["metadata"]
            
            # Category boosting score adjustment
            boost = 0.0
            if is_daivi_query and ("daivi" in text.lower() or "divine" in text.lower() or "दैवी" in text):
                boost = 1.5
            elif is_asuri_query and ("asuri" in text.lower() or "demoniac" in text.lower() or "आसुरी" in text):
                boost = 1.5
                
            retrieved.append({
                "text": text,
                "metadata": meta,
                "score": score - boost, # lower score is better (L2 distance)
                "raw_l2": score
            })
            
        # Re-sort based on boosted score
        retrieved = sorted(retrieved, key=lambda x: x["score"])
        
        # Return only requested top_k results
        return retrieved[:top_k]


if __name__ == "__main__":
    retriever = GitaRetriever()
    # Test query
    results = retriever.retrieve("What are the divine qualities?")
    print(f"\nRetrieved {len(results)} chunks for test query:")
    for idx, res in enumerate(results):
        print(f"\n--- Chunk {idx+1} (Page {res['metadata']['page']}, Score: {res['score']:.4f}) ---")
        print(res['text'][:200] + "...")
