"""
Example of integrating OpenAI GPT models with MedMitra.
Replace the Gemini API code in actions.py with this code.
"""

import os
import openai
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# Configure OpenAI API with your key
# You should store this in an environment variable for security
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your_openai_api_key_here")
openai.api_key = OPENAI_API_KEY

# Helper function to generate response using OpenAI API
def generate_health_response(query, context=None):
    system_instruction = """
    You are MedMitra, a compassionate and knowledgeable health education chatbot designed specifically for rural and semi-urban populations in India. 
    Your purpose is to provide clear, accurate, and culturally relevant health information in a simple, easy-to-understand manner.
    
    Always remember:
    1. Use simple language without medical jargon
    2. Be respectful of local cultural contexts and traditions
    3. Provide both Hindi and English responses when possible
    4. Focus on practical, actionable advice that can be implemented with limited resources
    5. Emphasize the importance of seeking professional medical help for serious conditions
    6. Never diagnose specific medical conditions
    7. Include a disclaimer when appropriate that you are not a substitute for professional medical advice
    8. Be sensitive to the limited healthcare infrastructure in rural areas
    9. Provide information that is evidence-based and medically accurate
    
    Format your responses to be easy to read, with clear sections and bullet points when appropriate.
    """
    
    messages = [{"role": "system", "content": system_instruction}]
    
    if context:
        messages.append({"role": "user", "content": f"Context: {context}"})
    
    messages.append({"role": "user", "content": query})
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" for better results
            messages=messages,
            temperature=0.3,
            max_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm sorry, I'm having trouble providing information right now. Please try again later."

# The rest of the action classes remain the same as in the original actions.py file
# Just replace the generate_health_response function with this one