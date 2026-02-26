import os
from pathlib import Path
from dotenv import load_dotenv
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from langchain_text_splitters  import RecursiveCharacterTextSplitter

load_dotenv()

# Configuration
DOCS_DIR = "./docs"  # Aviation data text files directory
CHROMA_PATH = "./db"  # DB location
COLLECTION_NAME = "aviation"


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 2000, 
    chunk_overlap=200, 
    length_function = len, 
    add_start_index = True
)

def load_text_files(docs_dir: str) -> dict:
    docs = {}
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        print(f"Error: {docs_dir} does not exist")
        return docs
    
    for txt_file in docs_path.glob("*.txt"):
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
                docs[txt_file.stem] = content
                print(f"Added {txt_file.name} ")
        except Exception as e:
            print(f"Error loading {txt_file.name}: {e}")
    
    return docs


def create_embeddings(docs: dict):
    # Initialize persistent Chroma client
    chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # Delete collection if it exists (fresh start)
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
        print(f"Deleted existing collection: {COLLECTION_NAME}")
    except:
        pass
    
    # Create collection with embedding function
    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=OpenAIEmbeddingFunction(
            api_key='any value',
            model_name="text-embedding-3-small",
            api_base='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1',
            default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')}
        )
    )

    doc_id = 0
    for filename, content in docs.items():
        # Chunk the text
        chunks = text_splitter.split_text(content)
        print(f'Split {len(content)} characters from {filename} into {len(chunks)} chunks.' )
        
        for chunk_idx, chunk in enumerate(chunks):
            doc_id += 1
            chunk_id = f"{filename}_chunk_{chunk_idx}"
            
            # Add to collection (embeddings created via embedding_fuction)
            collection.add(
                ids=[chunk_id],
                documents=[chunk],
                metadatas=[{"source": filename, "chunk": chunk_idx}]
            )
            
           
    print(f"\n Created {doc_id} document chunks in ChromaDB")
    return collection

    
# Load documents
docs = load_text_files(DOCS_DIR)

if not docs:
    print("No files found in 'docs' directory.")
    exit(1)

# Create embeddings
collection = create_embeddings(docs)
print("\n ChromaDB & Embeddings are complete.")
