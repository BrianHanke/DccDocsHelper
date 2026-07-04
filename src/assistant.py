import os
import chromadb
from chromadb.utils import embedding_functions
import ollama
from rich.console import Console
from rich.markdown import Markdown
import time

DB_DIR = "../db"
COLLECTION_NAME = "gaffer_docs"
MODEL = 'granite4.1:8b'
TOPIC = "Gaffer"

console = Console()

def query_assistant():
    if not os.path.exists(DB_DIR):
        print(f"Error: database not found at {DB_DIR}.")
        return

    chroma_client = chromadb.PersistentClient(path=DB_DIR)
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    collection = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=default_ef)

    print(f"{TOPIC} Documentation Assistant\n")
    print(f"Using {MODEL}.")
    print("Type 'q' to quit.\n")

    while True:
        user_query = input("Ask a question: ")
        if user_query.strip().lower() in ['q']:
            break

        if not user_query.strip():
            continue

        # Extract the top 3 relevant documentation snippets
        db_results = collection.query(
            query_texts=[user_query],
            n_results=3
        )

        # Flatten the retrieved context and track sources
        context_blocks = []
        sources = set()

        for doc, meta in zip(db_results['documents'][0], db_results['metadatas'][0]):
            context_blocks.append(doc)
            sources.add(f"{meta['title']} ({meta['source']})")

        combined_context = "\n\n---\n\n".join(context_blocks)

        # Construct the prompt
        system_prompt = (
			"### SYSTEM CONTEXT\n"
			"You are an expert in 3D and computer graphics.\n\n"

			"### DATA GROUNDING RULES\n"
			f"- You are provided with {TOPIC} documentation below.\n"
			"- Answer the user's question by summarizing the information in this documentation.\n"
			"- If the documentation does not contain the answer, do not guess, "
			f"do not use general web knowledge, do not offer to help further. Stop there. Instead, say: 'I could not find that topic in the {TOPIC} documentation.'\n\n"

			"### STYLE AND TEXT FORMATTING\n"
			"- Use bold text and markdown to highlight key words.\n"
            "- Use friendly and casual style, but not use emojis or make jokes.\n\n"

			f"INJECTED {TOPIC.upper()} DOCUMENTATION\n"
            f"{combined_context}"
		)

        start_time = time.perf_counter()

        print("\nThinking...\n")

        # Prompt the model with Temperature 0.0 (no hallucinations)
        try:
            # with console.status("Thinking...", spinner="pong"):
            response = ollama.chat(
                model=MODEL,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_query}
                ],
                options={'temperature': 0.0}
            )

            markdown_rendered = Markdown(response['message']['content'])

            end_time = time.perf_counter()
            elapsed_seconds = end_time - start_time

            # Print the response
            console.print(markdown_rendered)
            console.print(f"(Response generated in {elapsed_seconds:.2f} seconds.)", highlight=False)

            # Print citations
            if "I could not find that topic" not in response['message']['content']:
                print("\nSource:")
                for source in sources:
                    print(f" {source}")

            print("")

        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    query_assistant()