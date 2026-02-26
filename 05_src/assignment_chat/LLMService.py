
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def get_LLM_Response(messages: str, TONE: str = "") -> str:
    try:
        client = OpenAI(base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1', 
                api_key='any value',
                default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')})
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"{TONE}"},
                {"role": "user", "content": f"{messages}"}
            ]
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error accessing LLM Service"