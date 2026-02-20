import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from openai import OpenAI

load_dotenv()

CHROMA_PATH = "./db"  
COLLECTION_NAME = "aviation"

def query_aviation(query: str, top_n: int = 3) -> str:

    try:
        # Connect ChromaDB
        chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
        
        collection = chroma_client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=OpenAIEmbeddingFunction(
                api_key='any value',
                model_name="text-embedding-3-small",
                api_base='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1',
                default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')}
            )
        )
        
        results = collection.query(
            query_texts=[query],
            n_results=top_n
        )
        
        if not results['documents'] or not results['documents'][0]:
            return "No relevant aviation data found."
        
        # Build context from retrieved documents
        context = "\n\n".join(results['documents'][0])
        
        # Generate natural response based on context
        client = OpenAI(
            api_key='any value',
            base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1',
            default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')}
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an aviation expert. Answer questions based on the provided context. Be concise and informative."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer based on the context above:"}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error: Cannot find aviation information"

