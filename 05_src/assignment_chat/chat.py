import gradio as gr
from flightAPIService import get_flight_info
from aviationSemanticService import query_aviation
from weatherService import get_weather
from LLMService import get_LLM_Response


TONE = "You are an aviation expert.  Answer questions based on the provided context. Be concise and informative.  Speak like a pilot or aviation engineer would, using natural language but including technical details when relevant.  If the question is about flight mechanics, aerodynamics, aircraft systems, airline economics, safety, or future aviation trends, provide a clear and engaging explanation.  Use examples and analogies when helpful.  Always maintain an expert yet approachable tone."


def chat_handler(message, history):

   
    
    # Detect which service to use based on message content
    message_lower = message.lower()
    
    # Use Flight API Service if user asks about flights
    if "flight" in message_lower:
        return get_flight_info(message, TONE)
    
    # Use Aviation Semantic Service if user asks for aviation, information, or research
    if "find" in message_lower or "aviation" in message_lower or "information" in message_lower:
        return query_aviation(message, top_n=3, TONE=TONE)
    
    # Use weather Service if user asks for weather
    if "weather" in message_lower:
        return get_weather(message, TONE)
    
    messages = [{"role": "system", "content": TONE}]
    
    for user_msg, bot_msg in history:
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
        "Tip: Ask 'compare', 'explain', 'trade-offs', or 'what are the risks/mitigations' for best results."
    ),
    examples=[
        "What flights are in the air?",
        "Explain induced drag vs parasitic drag, and how winglets change the trade-off.",
       "How do aircraft electrical buses and redundancy typically work, and what happens after a generator loss?"
    ]
).launch()