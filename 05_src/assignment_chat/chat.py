import gradio as gr
from flightAPIService import get_flight_info
from aviationSemanticService import query_aviation
from weatherService import get_weather

def chat_handler(message, history):
    # Detect which service to use based on message content
    message_lower = message.lower()
    
    # Use Flight API Service if user asks about flights
    if "flight" in message_lower:
        return get_flight_info(message)
    
    # Use Aviation Semantic Service if user asks for aviation, information, or research
    if "find" in message_lower or "aviation" in message_lower or "information" in message_lower:
        return query_aviation(message, top_n=3)
    
    # Use weather Service if user asks for weather
    if "weather" in message_lower:
        return get_weather(message)

    # Default fallback - use aviation semantic search
    return query_aviation(message, top_n=3)

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