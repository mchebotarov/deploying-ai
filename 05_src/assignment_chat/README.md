# Aviation Assistant Chatbot

## Overview
An aviation chatbot that provides expert information about aviation topics through multiple specialized services. The assistant maintains a consistent aviation expert personality and handles conversations with appropriate memory management and safety guardrails.

## Services

### Service 1: Live Flight Information (API Service)
- **API Used:** [Aviationstack API](https://aviationstack.com/)
- **Functionality:** Retrieves real-time flight data and transforms structured API responses into natural, conversational summaries
- **Trigger Keywords:** "flight"
- **Example:** "What flights are in the air?"
- **Implementation Details:** 
  - Fetches current flight data from aviationstack API
  - Limits results to top 10 flights for readability

### Service 2: Aviation Knowledge Base (Semantic Search)
- **Technology:** ChromaDB with persistent file storage
- **Dataset:** 5 custom aviation text documents (created by ChatGPT and stored in the docs folder ) covering:
  1. Aerodynamics & Flight Mechanics
  2. Airline Network Planning & Economics
  3. Aircraft Systems Engineering
  4. Safety & Accident Investigation
  5. Future Aviation & Sustainability
- **Trigger Keywords:** "research", "find", "aviation", "information", "explain"
- **Example:** "Explain induced drag vs parasitic drag"
- **Implementation Details:**
  - Uses OpenAI's `text-embedding-3-small` model for embeddings
  - Documents chunked with RecursiveCharacterTextSplitter (2000 char chunks, 200 overlap)
  - ChromaDB PersistentClient stores embeddings in `./db/` directory
  - Retrieves top 3 most relevant chunks for each query
  - RAG pattern: semantic search → context retrieval → LLM-generated response

### Service 3: Weather Information (Function Calling)
- **Technology:** OpenAI Function Calling with Weatherstack API
- **API Used:** [Weatherstack API](https://weatherstack.com/)
- **Trigger Keywords:** "weather"
- **Example:** "What's the weather in Toronto?"
- **Implementation Details:**
  - LLM determines when to invoke weather function based on user query
  - Fetches current weather data and presents in natural language

## User Interface

### Gradio ChatInterface
- **Framework:** Gradio ChatInterface for web-based chat
- **Personality:** Aviation expert with technical depth but approachable tone
- **Examples Provided:** Flight queries, aerodynamics, systems engineering
- **Launch:** Run `python chat.py` and access via web browser

## Memory Management

The system implements **two layers** of memory management:

1. **Basic History Limiting:** Maintains last 10 conversation exchanges
2. **Token-Based Trimming (Optional Feature):** Uses LangChain's `trim_messages` utility with:
   - Max token limit: 2,000 tokens
   - Strategy: Keep most recent messages ("last" strategy)
   - Ensures conversation stays within context window
   - Prevents token overflow for long conversations

**Decision Rationale:** The dual-layer approach ensures both simplicity and robustness. Basic limiting handles typical use cases, while token-based trimming protects against edge cases with very long messages.

## Guardrails

### System Prompt Protection
Prevents users from:
- Accessing or revealing internal instructions
- Viewing the system prompt
- Keywords blocked: "system prompt", "your instructions", "show me your", etc.

### Restricted Topics
The assistant will **not** respond to questions about:
- Cats or dogs
- Horoscopes or zodiac signs  
- Taylor Swift

**Response:** Politely redirects users back to aviation topics

## Embedding Process

### Dataset Preparation
1. **Source:** 5 custom aviation text files (`.txt` format) in `./docs/` directory
2. **Topics:** Each file covers a distinct aviation domain

### Embedding Generation (`aviationSemanticService_setup.py`)
1. **Text Loading:** Read all `.txt` files from `./docs/` directory
2. **Chunking:** 
   - Tool: LangChain RecursiveCharacterTextSplitter
   - Chunk size: 2,000 characters
   - Overlap: 200 characters (maintains context continuity)
3. **Embedding Model:** OpenAI `text-embedding-3-small` via API Gateway
4. **Storage:** ChromaDB PersistentClient with file persistence at `./db/`
5. **Metadata:** Each chunk tagged with source file and chunk index

### Important Notes
- **One-time setup:** Embeddings are pre-generated; no need to re-run setup
- **Persistent storage:** Embeddings stored in `./db/` directory (included in repository)

### Query Process
1. User query embedded with same `text-embedding-3-small` model
2. ChromaDB performs similarity search
3. Top 3 most relevant chunks retrieved
4. Chunks passed as context to LLM for natural language response

## Implementation Decisions

### Service Routing Logic
- **Keyword-based:** Simple and transparent routing based on message content
- **Default fallback:** Uses LLM service for general queries


### Tone Consistency
- **Global TONE constant:** Ensures all services maintain aviation expert personality
- **Injected into:** System prompts, service calls, and LLM responses


## Setup and Usage

### Prerequisites
- Python environment with course-provided libraries
- API keys for three services (see instructions below)
- `.env` file in the `assignment_chat` folder with all required keys

### Obtaining API Keys

#### 1. Aviationstack API Key (Flight Data - Service 1)
1. Visit [https://aviationstack.com/](https://aviationstack.com/)

#### 2. Weatherstack API Key (Weather Data - Service 3)
1. Visit [https://weatherstack.com/](https://weatherstack.com/)

#### 3. API Gateway Key (OpenAI Access)
- Course evaluators should have a key

### Creating the .env File

Open `.env` file in the `05_src`:

```env
# OpenAI API Gateway 
API_GATEWAY_KEY=your_api_gateway_key_here

# Aviationstack API (sign up at https://aviationstack.com/)
AVIATIONSTACK_API_KEY=your_aviationstack_key_here

# Weatherstack API (sign up at https://weatherstack.com/)
WEATHERSTACK_API_KEY=your_weatherstack_key_here
```


### Running the Application
```bash
cd 05_src/assignment_chat
python chat.py
```

The Gradio interface will launch in your browser automatically or use the url given when running the `chat.py` file.

### Example Queries
- **Flights:** "What flights are currently in the air?"
- **Aviation Knowledge:** "Explain how winglets improve fuel efficiency"
- **Weather:** "What's the weather in Los Angeles?"


