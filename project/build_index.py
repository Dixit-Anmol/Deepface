import os
import pickle
import sys
import numpy as np

# Import settings and ingestion modules
try:
    import faiss
    from sentence_transformers import SentenceTransformer
    from config import EMBEDDING_MODEL_NAME, FAISS_INDEX_PATH, METADATA_PATH, VECTORSTORE_DIR
    from ingest import get_chunks
except ImportError as e:
    print(f"Error loading dependencies: {e}")
    sys.exit(1)


def build_or_load_index():
    """
    Checks if a local FAISS index exists.
    If yes, loads it (unless --force is passed). Otherwise, ingests the document,
    generates embeddings, and constructs the FAISS index from scratch.
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Force rebuilding the index")
    args = parser.parse_known_args()[0]

    # Create vectorstore directory if missing
    os.makedirs(VECTORSTORE_DIR, exist_ok=True)
    
    if not args.force and os.path.exists(FAISS_INDEX_PATH) and os.path.exists(METADATA_PATH):
        print(f"Loading existing FAISS index from: {VECTORSTORE_DIR}")
        try:
            index = faiss.read_index(FAISS_INDEX_PATH)
            with open(METADATA_PATH, "rb") as f:
                chunks = pickle.load(f)
            print(f"FAISS index loaded successfully with {index.ntotal} vectors.")
            return index, chunks
        except Exception as e:
            print(f"Failed to load existing index: {e}. Rebuilding index...")
            
    # Rebuild logic
    print("Building new FAISS vector database index...")
    
    # 1. Ingest PDF and generate chunks
    chunks = get_chunks()
    if not chunks:
        print("Error: No text chunks extracted. Index building aborted.")
        sys.exit(1)
        
    # 2. Extract texts to embed
    texts_to_embed = [chunk["text"] for chunk in chunks]
    
    # 3. Generate embeddings
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    try:
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("Generating embeddings (this may take a few seconds)...")
        embeddings = model.encode(texts_to_embed, show_progress_bar=True)
        embeddings = np.array(embeddings).astype("float32")
    except Exception as e:
        print(f"Embedding Generation Failure: {e}")
        sys.exit(1)
        
    # 4. Construct FAISS Index (IndexFlatL2 for L2 distance similarity metrics)
    print("Building FAISS FlatL2 index...")
    try:
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
    except Exception as e:
        print(f"FAISS construction failure: {e}")
        sys.exit(1)
        
    # 5. Serialize and save index + metadata pickle
    try:
        faiss.write_index(index, FAISS_INDEX_PATH)
        with open(METADATA_PATH, "wb") as f:
            pickle.dump(chunks, f)
        print(f"FAISS vector store saved successfully to: {VECTORSTORE_DIR}")
    except Exception as e:
        print(f"Serialization Failure: Failed to write index files: {e}")
        sys.exit(1)
        
    return index, chunks


if __name__ == "__main__":
    build_or_load_index()
