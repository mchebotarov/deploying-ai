import gradio as gr
from flightAPIService import get_flight_info
from aviationSemanticService import query_aviation
from weatherService import get_weather
from LLMService import get_LLM_Response
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately


TONE = "You are an aviation expert.  Answer questions based on the provided context. Be concise and informative.  Speak like a pilot or aviation engineer would, using natural language but including technical details when relevant.  If the question is about flight mechanics, aerodynamics, aircraft systems, airline economics, safety, or future aviation trends, provide a clear and engaging explanation.  Use examples and analogies when helpful.  Always maintain an expert yet approachable tone."
MAX_TOKENS = 2000  # Max tokens for conversation history


def manage_memory(history):
    if not history:
        return []
    
    # Convert Gradio history to LangChain messages
    messages = []
    for user_msg, bot_msg in history:
        messages.append(HumanMessage(content=user_msg))
        messages.append(AIMessage(content=bot_msg))
    
    # Trim messages using LangGraph's strategy
    trimmed = trim_messages(
        messages,
        strategy="last",  # Keep recent messages
        token_counter=count_tokens_approximately,
        max_tokens=MAX_TOKENS,
        start_on="human", 
        end_on=("human", "ai"),
    )
    
    # Convert back to Gradio format
    trimmed_history = []
    for i in range(0, len(trimmed), 2):
        if i + 1 < len(trimmed):
            trimmed_history.append((trimmed[i].content, trimmed[i+1].content))
    
    return trimmed_history


def check_guardrails(message):

    message_lower = message.lower()
    
    # Check for system prompt access/revelation attempts
    prompt_access_keywords = [
        "system prompt", "system message", "your prompt", "your instructions",
        "show me your", "what are your instructions", "reveal your",
        "what is your system", "display your prompt", "print your instructions",
        "your system message", "initial prompt", "original instructions"
    ]
    
    for keyword in prompt_access_keywords:
        if keyword in message_lower:
            return (True, "I cannot share information about system configuration. I'm here to help you with aviation-related questions. What would you like to know about aviation?")
    
    # Check for system prompt modification attempts
    prompt_modification_keywords = [
        "ignore previous", "ignore all previous", "disregard previous",
        "forget your instructions", "forget previous", "new instructions",
        "you are now", "act as if", "pretend you are", "behave like",
        "override your", "change your instructions", "reprogram",
        "ignore your instructions", "disregard your instructions"
    ]
    
    for keyword in prompt_modification_keywords:
        if keyword in message_lower:
            return (True, "I cannot modify my core functionality or instructions. How can I assist you with aviation topics today?")
    
    # Check for restricted topics
    restricted_topics = {
        "cats": ["cat", "cats", "feline", "kitten", "kitty"],
        "dogs": ["dog", "dogs", "canine", "puppy", "puppies"],
        "horoscopes": ["horoscope", "horoscopes", "zodiac", "astrology", "astrological", 
                      "aries", "taurus", "gemini", "cancer", "leo", "virgo", 
                      "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"],
        "taylor swift": ["taylor swift", "swift", "swiftie", "t swift", "tay tay"]
    }
    
    for topic, keywords in restricted_topics.items():
        for keyword in keywords:
            if keyword in message_lower:
                return (True, f"I am specifically designed to discuss aviation topics only. Is there anything related to aviation I can help you with?")
    
    return (False, None)


def chat_handler(message: str, history: list[dict]) -> str:
    
    # Check guardrails
    is_violation, violation_response = check_guardrails(message)
    if is_violation:
        return violation_response

    # Limit history to 10 exchanges
    MAX_HISTORY = 10

    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]

    # Apply memory management with token-based trimming
    managed_history = manage_memory(history)

    # Detect which service to use based on message content
    message_lower = message.lower()
    
    # Use Flight API Service if user asks about flights
    if "flight" in message_lower:
        return get_flight_info(message, TONE)
    
    # Use Aviation Semantic Service if user asks for aviation, information, or research
    if "research" in message_lower or "find" in message_lower or "aviation" in message_lower or "information" in message_lower or "explain" in message_lower:
        return query_aviation(message, top_n=3, TONE=TONE)
    
    # Use weather Service if user asks for weather
    if "weather" in message_lower:
        return get_weather(message, TONE)
    
    messages = [{"role": "system", "content": TONE}]
    
    for user_msg, bot_msg in managed_history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
    
    messages.append({"role": "user", "content": message})

    # Default fallback - use aviation semantic search
    return get_LLM_Response(messages, TONE=TONE)

gr.ChatInterface(
    fn=chat_handler,
    title="Aviation Assistant",
    description=(
        "Hello! I'm your aviation expert. Ask me about:\n"
        "- Live flight information\n"
        "- Aerodynamics & flight mechanics\n"
        "- Airline network planning & economics\n"
        "- Aircraft systems engineering\n"
        "- Safety & accident investigation\n"
        "- Future aviation & sustainability\n\n"
        "- Current weather conditions at any location\n"
        "\n\n"
        "To ask about live flight information, include the word 'flight' in your question. For general aviation information or research, include words like 'aviation', 'information', 'research', or 'explain'. For weather-related questions, include the word 'weather'.\n\n"
    ),
    examples=[
        "What flights are in the air?",
        "Explain induced drag vs parasitic drag, and how winglets change the trade-off.",
        "What's the weather like in Toronto?"
    ]
).launch()