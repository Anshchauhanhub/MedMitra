import os
import requests
import json
from typing import Any, Dict, List, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# For Gemini API
import google.generativeai as genai

# Configure the Gemini API with your key
# You should store this in an environment variable for security
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "your_gemini_api_key_here")
# Configure API key
genai.configure(api_key=GEMINI_API_KEY)

# Configure the model
generation_config = {
    "temperature": 0.3,
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 1024,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(
    model_name="gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)

# Helper function to generate response using Gemini API
def generate_health_response(query, context=None):
    prompt_parts = []
    
    # Add system instructions
    system_instruction = """
    You are MedMitra, a compassionate and knowledgeable health education chatbot designed specifically for rural and semi-urban populations in India. 
    Your purpose is to provide clear, accurate, and culturally relevant health information in a simple, easy-to-understand manner.
    
    Always remember:
    1. Use simple language without medical jargon
    2. Be respectful of local cultural contexts and traditions
    3. Provide responses in three languages: Hindi, English, and Odia (the language of Odisha, India)
    4. Focus on practical, actionable advice that can be implemented with limited resources
    5. Emphasize the importance of seeking professional medical help for serious conditions
    6. Never diagnose specific medical conditions
    7. Include a disclaimer when appropriate that you are not a substitute for professional medical advice
    8. Be sensitive to the limited healthcare infrastructure in rural areas
    9. Provide information that is evidence-based and medically accurate
    
    For Odia language responses, follow these guidelines:
    1. Start with Odia text, followed by Hindi, then English
    2. Keep Odia sentences simple and direct, using common vocabulary
    3. Ensure accurate transliteration of medical terms in Odia
    4. Be culturally sensitive to Odisha-specific health practices
    
    Format your responses to be easy to read, with clear sections and bullet points when appropriate.
    Format multilingual responses with clear separation:
    
    ଓଡ଼ିଆ (Odia):
    [Odia response here]
    
    हिंदी (Hindi):
    [Hindi response here]
    
    English:
    [English response here]
    """
    prompt_parts.append(system_instruction)
    
    # Add context if provided
    if context:
        prompt_parts.append(f"Context: {context}")
    
    # Add user query
    prompt_parts.append(f"User question: {query}")
    
    try:
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm sorry, I'm having trouble providing information right now. Please try again later."

class ActionProvidePreventiveHealthcare(Action):
    def name(self) -> Text:
        return "action_provide_preventive_healthcare"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Get any entity values that might be relevant
        disease = tracker.get_slot("disease")
        health_condition = tracker.get_slot("health_condition")
        
        user_message = tracker.latest_message.get("text")
        
        context = "The user is asking about preventive healthcare measures. "
        if disease:
            context += f"They mentioned {disease}. "
        if health_condition:
            context += f"They have a health condition: {health_condition}. "
            
        response = generate_health_response(user_message, context)
        dispatcher.utter_message(text=response)
        
        return []

class ActionProvideDiseaseSymptoms(Action):
    def name(self) -> Text:
        return "action_provide_disease_symptoms"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disease = tracker.get_slot("disease")
        symptom = tracker.get_slot("symptom")
        
        user_message = tracker.latest_message.get("text")
        
        context = "The user is asking about disease symptoms. "
        if disease:
            context += f"They mentioned {disease}. "
        if symptom:
            context += f"They mentioned a symptom: {symptom}. "
            
        response = generate_health_response(user_message, context)
        dispatcher.utter_message(text=response)
        
        return []

class ActionProvideVaccinationSchedule(Action):
    def name(self) -> Text:
        return "action_provide_vaccination_schedule"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        vaccine = tracker.get_slot("vaccine")
        age_group = tracker.get_slot("age_group")
        
        user_message = tracker.latest_message.get("text")
        
        context = "The user is asking about vaccination schedules. "
        if vaccine:
            context += f"They mentioned {vaccine} vaccine. "
        if age_group:
            context += f"They mentioned age group: {age_group}. "
            
        response = generate_health_response(user_message, context)
        dispatcher.utter_message(text=response)
        
        return []

class ActionProvideHealthTips(Action):
    def name(self) -> Text:
        return "action_provide_health_tips"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get("text")
        
        context = "The user is asking for general health tips and advice. "
            
        response = generate_health_response(user_message, context)
        dispatcher.utter_message(text=response)
        
        return []

class ActionProvideCommonIllnesses(Action):
    def name(self) -> Text:
        return "action_provide_common_illnesses"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disease = tracker.get_slot("disease")
        
        user_message = tracker.latest_message.get("text")
        
        context = "The user is asking about common illnesses in their area or during specific seasons. "
        if disease:
            context += f"They mentioned {disease}. "
            
        response = generate_health_response(user_message, context)
        dispatcher.utter_message(text=response)
        
        return []

class ActionProvideMedicationInfo(Action):
    def name(self) -> Text:
        return "action_provide_medication_info"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        medication = tracker.get_slot("medication")
        symptom = tracker.get_slot("symptom")
        
        user_message = tracker.latest_message.get("text")
        
        context = "The user is asking about medication information. "
        if medication:
            context += f"They mentioned {medication}. "
        if symptom:
            context += f"They mentioned a symptom: {symptom}. "
            
        response = generate_health_response(user_message, context)
        dispatcher.utter_message(text=response)
        
        # Add a medical disclaimer
        disclaimer = "Disclaimer: This information is for educational purposes only and not a substitute for professional medical advice. Please consult a healthcare provider before taking any medication."
        dispatcher.utter_message(text=disclaimer)
        
        return []

class ActionProvideEmergencySymptoms(Action):
    def name(self) -> Text:
        return "action_provide_emergency_symptoms"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        disease = tracker.get_slot("disease")
        
        user_message = tracker.latest_message.get("text")
        
        context = "The user is asking about emergency symptoms that require immediate medical attention. "
        if disease:
            context += f"They mentioned {disease}. "
            
        response = generate_health_response(user_message, context)
        dispatcher.utter_message(text=response)
        
        # Add an emergency disclaimer
        disclaimer = "Important: If you or someone is experiencing a medical emergency, seek immediate medical help or call emergency services."
        dispatcher.utter_message(text=disclaimer)
        
        return []

class ActionProvideMaternalHealth(Action):
    def name(self) -> Text:
        return "action_provide_maternal_health"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get("text")
        
        context = "The user is asking about maternal health, pregnancy care, or postnatal care. "
            
        response = generate_health_response(user_message, context)
        dispatcher.utter_message(text=response)
        
        return []

class ActionProvideChildHealth(Action):
    def name(self) -> Text:
        return "action_provide_child_health"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get("text")
        
        context = "The user is asking about child health, development, or pediatric care. "
            
        response = generate_health_response(user_message, context)
        dispatcher.utter_message(text=response)
        
        return []

class ActionProvideElderlyCare(Action):
    def name(self) -> Text:
        return "action_provide_elderly_care"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get("text")
        
        context = "The user is asking about elderly care and health issues related to older people. "
            
        response = generate_health_response(user_message, context)
        dispatcher.utter_message(text=response)
        
        return []

class ActionProvideNutrition(Action):
    def name(self) -> Text:
        return "action_provide_nutrition"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        nutrition_type = tracker.get_slot("nutrition_type")
        
        user_message = tracker.latest_message.get("text")
        
        context = "The user is asking about nutrition, diet, or specific nutrients. "
        if nutrition_type:
            context += f"They mentioned {nutrition_type}. "
            
        response = generate_health_response(user_message, context)
        dispatcher.utter_message(text=response)
        
        return []

class ActionProvideMentalHealth(Action):
    def name(self) -> Text:
        return "action_provide_mental_health"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get("text")
        
        context = "The user is asking about mental health, stress management, or emotional wellbeing. "
            
        response = generate_health_response(user_message, context)
        dispatcher.utter_message(text=response)
        
        return []

class ActionProvideGeneralHealthcare(Action):
    def name(self) -> Text:
        return "action_provide_general_healthcare"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get("text")
        
        context = "The user is asking about general healthcare topics. "
            
        response = generate_health_response(user_message, context)
        dispatcher.utter_message(text=response)
        
        return []