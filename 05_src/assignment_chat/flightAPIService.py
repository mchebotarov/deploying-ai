import requests
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def get_flight_info(query: str = "What flights are currently in the air?") -> str:
    try:
        params = {
            'access_key': os.getenv('AVIATIONSTACK_API_KEY')
        }
        
        api_result = requests.get('https://api.aviationstack.com/v1/flights', params)
        api_response = api_result.json()
        
        # Extract flight data
        flights = api_response.get('data', [])
        
        if not flights:
            return "No flight data available at this time."
        
        # Format the raw data into readable text
        flights_text = "Current flights:\n"
        for f in flights[:10]:  # Limit to first 10 
            flights_text += f"\n- {f['airline']['name']} flight {f['flight']['iata']}: {f['departure']['airport']} ({f['departure']['iata']}) to {f['arrival']['airport']} ({f['arrival']['iata']})"
        
        # Summarize input to natural language
        client = OpenAI(base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1', 
                api_key='any value',
                default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')})
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Transform flight information into a natural, conversational and engaging summary."},
                {"role": "user", "content": f"{flights_text}\n\nUser question: {query}"}
            ]
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error retrieving flight information: {str(e)}"
