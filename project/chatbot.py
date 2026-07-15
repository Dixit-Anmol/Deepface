# ==============================================================================
# Bhagavad Gita Chatbot CLI Interface with Groq Integration
# ==============================================================================

import os
import sys
import time

try:
    from groq import Groq
    from config import GROQ_API_KEY, GROQ_MODEL
    from retriever import GitaRetriever
except ImportError as e:
    print(f"Error loading dependencies in chatbot: {e}")
    sys.exit(1)

# Configure console streams to use UTF-8 on Windows to correctly render Devanagari characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def safe_print(text: str):
    """Prints text safely to standard output handling console encoding mismatches on Windows."""
    print(text)


def build_prompt(context: str, question: str, source_name: str) -> str:
    """Constructs the system prompt enforcing RAG constraints dynamically based on source metadata."""
    prompt = f"""You are a Bhagavad Gita assistant.
Use ONLY the retrieved context to answer the question.
Never use your own knowledge or speculate outside the context.
If the answer is not available in the retrieved context, say:
"I could not find this information in {source_name}."
Do not hallucinate.

Language Rules:
- If the user asks in English: Answer in English.
- If the user asks in Hindi: Answer in Hindi.
- If the user asks in Hinglish (mixed Hindi-English script): Answer in Hinglish.

Always quote the relevant Sanskrit verse or Hindi translation if available in the context.

Context:
{context}

Question:
{question}

Answer:"""
    return prompt


def query_groq(client: Groq, model_name: str, prompt: str) -> str:
    """Sends prompt request to Groq API and retrieves completion output."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model_name,
            temperature=0.2,  # Low temperature for deterministic factual extraction
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"\nError communicating with Groq API: {e}"


def main():
    print("=========================================================")
    print("  Bhagavad Gita Adhyay 16 - Q&A Chatbot (Groq Engine)")
    print("  Initializing RAG resources, please wait...")
    print("=========================================================")

    # Initialize retriever
    try:
        retriever = GitaRetriever()
    except FileNotFoundError:
        print("\nError: Vector database index not found.")
        print("Please run build_index.py to parse and index the PDF first.")
        sys.exit(1)

    # Initialize Groq client
    if not GROQ_API_KEY or GROQ_API_KEY.startswith("your_"):
        print("\nError: GROQ_API_KEY is not set correctly in config.py.")
        sys.exit(1)
        
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print(f"\nError initializing Groq client: {e}")
        sys.exit(1)

    # Dynamic title extraction
    source_name = "Bhagavad Gita"
    if retriever.chunks:
        source_name = retriever.chunks[0]["metadata"].get("source", "Bhagavad Gita")

    print(f"\nChatbot is ready! Ask your questions about: {source_name}")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            question = input("\nAsk Question:\n>> ")
            if not question.strip():
                continue
                
            if question.lower().strip() == 'exit':
                print("Exiting chatbot. Pranam!")
                break
                
            print("\nRetrieving relevant passages...")
            results = retriever.retrieve(question)
            
            # Extract source_name from the active chunk context dynamically
            active_source = results[0]["metadata"].get("source", source_name) if results else source_name
            
            if not results:
                print(f"I could not find this information in {active_source}.")
                continue
                
            # Display retrieved chunks (Step 8: debug print before generation)
            print("\n================ RETRIEVED CONTEXT CHUNKS ================")
            sources = set()
            context_texts = []
            
            for idx, res in enumerate(results):
                page = res["metadata"]["page"]
                sources.add(page)
                context_texts.append(res["text"])
                
                print(f"\nRetrieved Chunk {idx + 1}")
                print(f"Page:             {page}")
                print(f"Similarity Score: {res['score']:.4f}")
                print("-" * 40)
                safe_print(res["text"])
                print("-" * 40)
            print("==========================================================\n")

            # Augment prompt and run Groq inference
            context_str = "\n\n".join(context_texts)
            prompt = build_prompt(context_str, question, active_source)
            
            print("Generating answer via Groq...")
            start_time = time.time()
            answer = query_groq(client, GROQ_MODEL, prompt)
            end_time = time.time()
            
            print("\nAnswer:")
            safe_print(answer)
            print(f"\n[Response Time: {end_time - start_time:.2f}s]")
            
            # Display source pages used (Bonus Feature 5)
            print("\nSources:")
            for s in sorted(sources):
                print(f"Page {s}")
                
        except KeyboardInterrupt:
            print("\nExiting gracefully. Pranam!")
            break


if __name__ == "__main__":
    main()
