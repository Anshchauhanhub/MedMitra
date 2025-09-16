import os
import warnings
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from operator import add as add_messages
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.tools import tool
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import pickle
import numpy as np

# Suppress warnings
warnings.filterwarnings("ignore")
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Load environment variables from .env file
load_dotenv()

# ===========================
# CONFIG
# ===========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MEDICAL_DOCS_PATH = "data/datasets/"
DISEASE_SYMPTOMS_CSV = "data/datasets/disease_symptoms.csv"
VACCINATION_SCHEDULE_JSON = "data/datasets/vaccination_schedule.json"
HEALTH_CONDITIONS_JSON = "data/datasets/health_conditions.json"
PERSIST_DIRECTORY = "database/medical_knowledge_db"

# Validate required environment variables
if not GROQ_API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in environment variables")

# ===========================
# LOAD MEDICAL KNOWLEDGE BASE
# ===========================
def load_medical_documents():
    """Load and process medical documents from various sources."""
    documents = []
    
    # Load disease-symptom CSV data
    if os.path.exists(DISEASE_SYMPTOMS_CSV):
        csv_loader = CSVLoader(
            file_path=DISEASE_SYMPTOMS_CSV,
            csv_args={"delimiter": ","}
        )
        csv_docs = csv_loader.load()
        documents.extend(csv_docs)
    
    # Load medical PDFs if available
    if os.path.exists(MEDICAL_DOCS_PATH):
        pdf_files = [f for f in os.listdir(MEDICAL_DOCS_PATH) if f.endswith('.pdf')]
        for pdf_file in pdf_files:
            pdf_path = os.path.join(MEDICAL_DOCS_PATH, pdf_file)
            pdf_loader = PyPDFLoader(pdf_path)
            pdf_docs = pdf_loader.load()
            documents.extend(pdf_docs)
    
    return documents

# Silent loading
medical_docs = load_medical_documents()

# ===========================
# CHUNKING
# ===========================
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " ", ""]
)

docs_split = text_splitter.split_documents(medical_docs)

# ===========================
# VECTOR STORE
# ===========================
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

collection_name = "odisha_health_knowledge"

if not os.path.exists(PERSIST_DIRECTORY):
    os.makedirs(PERSIST_DIRECTORY)

# Create vector store silently
vectorstore = Chroma.from_documents(
    documents=docs_split,
    embedding=embeddings,
    persist_directory=PERSIST_DIRECTORY,
    collection_name=collection_name
)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# ===========================
# DISEASE PREDICTION MODEL
# ===========================
class DiseasePredictionModel:
    def __init__(self):
        self.model = None
        self.symptoms_list = []
        self.diseases_list = []
    
    def load_model(self, model_path="ml_models/disease_prediction/disease_model.pkl"):
        """Load pre-trained disease prediction model."""
        try:
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
        except Exception:
            pass
    
    def predict_disease(self, symptoms):
        """Predict disease based on symptoms."""
        if not self.model:
            return "Disease prediction model not available. Please consult the knowledge base."
        return "Predicted disease based on symptoms"

disease_predictor = DiseasePredictionModel()
disease_predictor.load_model()

# ===========================
# TOOL DEFINITIONS
# ===========================
@tool
def search_medical_knowledge(query: str) -> str:
    """Search medical knowledge base for health information, diseases, symptoms, treatments, and prevention."""
    try:
        docs = retriever.invoke(query)
        
        if not docs:
            return "I couldn't find specific information about that in our medical knowledge base. Please try rephrasing your question or ask about common health topics."
        
        # Combine retrieved medical content
        context = "\n\n".join([doc.page_content.strip() for doc in docs])
        return f"Based on our medical knowledge base:\n\n{context}"
    except Exception as e:
        return f"Sorry, I encountered an error while searching medical information: {str(e)}"

@tool
def predict_disease_from_symptoms(symptoms: str) -> str:
    """Predict possible diseases based on reported symptoms. Provide symptoms as comma-separated text."""
    try:
        # Use disease prediction model
        prediction = disease_predictor.predict_disease(symptoms)
        
        # Also search knowledge base for symptom-related information
        symptom_query = f"symptoms {symptoms} disease diagnosis treatment"
        docs = retriever.invoke(symptom_query)
        
        knowledge_context = ""
        if docs:
            knowledge_context = "\n\n".join([doc.page_content.strip() for doc in docs[:3]])
        
        result = f"Disease Prediction Analysis:\n{prediction}\n\nRelated Medical Information:\n{knowledge_context}"
        return result
    except Exception as e:
        return f"Sorry, I encountered an error during disease prediction: {str(e)}"

@tool
def get_vaccination_info(query: str) -> str:
    """Get information about vaccination schedules, vaccine availability, and immunization programs."""
    try:
        vaccination_query = f"vaccination vaccine immunization schedule {query}"
        docs = retriever.invoke(vaccination_query)
        
        if not docs:
            return "I couldn't find specific vaccination information. Please ask about common vaccines, vaccination schedules, or immunization programs."
        
        context = "\n\n".join([doc.page_content.strip() for doc in docs])
        return f"Vaccination Information:\n\n{context}"
    except Exception as e:
        return f"Sorry, I encountered an error while retrieving vaccination information: {str(e)}"

@tool
def get_health_alerts(query: str) -> str:
    """Get information about disease outbreaks, health advisories, and public health alerts."""
    try:
        alert_query = f"outbreak alert advisory epidemic pandemic {query}"
        docs = retriever.invoke(alert_query)
        
        if not docs:
            return "No specific health alerts found. Please check official health department websites for the latest updates."
        
        context = "\n\n".join([doc.page_content.strip() for doc in docs])
        return f"Health Alerts and Advisories:\n\n{context}"
    except Exception as e:
        return f"Sorry, I encountered an error while retrieving health alerts: {str(e)}"

# ===========================
# LLM SETUP
# ===========================
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    api_key=GROQ_API_KEY
)

tools = [search_medical_knowledge, predict_disease_from_symptoms, get_vaccination_info, get_health_alerts]
llm_with_tools = llm.bind_tools(tools)

# ===========================
# AGENT STATE
# ===========================
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# ===========================
# AGENT FUNCTIONS
# ===========================
def should_continue(state: AgentState):
    """Check if the last message has tool calls that need to be executed."""
    if not state['messages']:
        return False
    
    last_message = state['messages'][-1]
    has_tool_calls = hasattr(last_message, 'tool_calls') and last_message.tool_calls
    return bool(has_tool_calls)

# Enhanced system prompt for medical chatbot
system_prompt = """You are an AI health assistant for the Government of Odisha's Public Health Chatbot. Your mission is to provide accurate, helpful health information to rural and semi-urban populations.

IMPORTANT MEDICAL GUIDELINES:
- talk as Real dosctor or as human 
- Always use data that you have to provide the best possible answer if you have not information give output i have no information
- ALWAYS use appropriate tools to search for medical information before responding
- Provide evidence-based health information from reliable medical sources
- For symptom queries, use the disease prediction tool and medical knowledge search
- For vaccination questions, use the vaccination information tool
- For outbreak concerns, use the health alerts tool
- Support multiple languages (Hindi, Odia, English) based on user preference
- Be culturally sensitive and appropriate for rural/semi-urban populations

SAFETY PROTOCOLS:
- Always recommend consulting healthcare professionals for serious symptoms
- Never provide definitive medical diagnoses - only educational information
- Emphasize the importance of professional medical care
- Provide preventive health guidance and awareness

CONVERSATION STYLE:
- Be warm, empathetic, and easy to understand
- Use simple language suitable for diverse education levels
- Provide actionable health advice and preventive measures
- Include information about nearby health centers when relevant

Remember: You are an educational health assistant, not a replacement for professional medical care. Always encourage users to seek proper medical attention for health concerns."""

def call_llm(state: AgentState) -> AgentState:
    """Call the LLM with medical context."""
    try:
        messages = [SystemMessage(content=system_prompt)] + list(state['messages'])
        response = llm_with_tools.invoke(messages)
        return {'messages': [response]}
    except Exception as e:
        error_response = HumanMessage(content=f"Sorry, I encountered a technical error. Please try again or contact support: {str(e)}")
        return {'messages': [error_response]}

def use_tools(state: AgentState) -> AgentState:
    """Execute medical tools and return results."""
    try:
        last_message = state['messages'][-1]
        tool_calls = getattr(last_message, 'tool_calls', [])
        
        if not tool_calls:
            return {'messages': []}
        
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("name") if isinstance(tool_call, dict) else tool_call.name
            tool_args = tool_call.get("args") if isinstance(tool_call, dict) else tool_call.args
            tool_id = tool_call.get("id") if isinstance(tool_call, dict) else tool_call.id
            
            # Execute appropriate medical tool
            if tool_name == "search_medical_knowledge":
                result = search_medical_knowledge.invoke(tool_args)
            elif tool_name == "predict_disease_from_symptoms":
                result = predict_disease_from_symptoms.invoke(tool_args)
            elif tool_name == "get_vaccination_info":
                result = get_vaccination_info.invoke(tool_args)
            elif tool_name == "get_health_alerts":
                result = get_health_alerts.invoke(tool_args)
            else:
                result = f"Unknown medical tool: {tool_name}"
            
            tool_message = ToolMessage(
                tool_call_id=tool_id,
                name=tool_name,
                content=str(result)
            )
            results.append(tool_message)
        
        return {'messages': results}
    
    except Exception as e:
        error_message = ToolMessage(
            tool_call_id="error",
            name="error",
            content=f"Medical tool error: {str(e)}"
        )
        return {'messages': [error_message]}

# ===========================
# BUILD GRAPH
# ===========================
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("llm", call_llm)
workflow.add_node("tools", use_tools)

# Add conditional edges
workflow.add_conditional_edges(
    "llm",
    should_continue,
    {
        True: "tools",
        False: END
    }
)

workflow.add_edge("tools", "llm")
workflow.set_entry_point("llm")

# Compile the medical chatbot graph
medical_chatbot = workflow.compile()

# ===========================
# FASTAPI WEB SERVER
# ===========================
app = FastAPI(
    title="Odisha Health AI Assistant",
    description="AI-Driven Public Health Chatbot for Disease Awareness - Government of Odisha"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/health-chat")
async def health_chat(request: Request):
    """Handle health-related chat requests."""
    try:
        data = await request.json()
        message = data.get("message", "").strip()
        language = data.get("language", "english").lower()
        
        if not message:
            return {"error": "Health query cannot be empty"}
        
        # Add language context to message if not English
        if language in ["hindi", "odia"]:
            message = f"[Language: {language}] {message}"
        
        # Invoke the medical chatbot
        result = medical_chatbot.invoke({"messages": [HumanMessage(content=message)]})
        
        # Get the final medical response
        final_message = result['messages'][-1]
        response_content = final_message.content if hasattr(final_message, 'content') else str(final_message)
        
        return {
            "result": response_content,
            "language": language,
            "disclaimer": "This information is for educational purposes only. Please consult a healthcare professional for medical advice."
        }
    
    except Exception as e:
        return {"error": f"Sorry, I encountered an error while processing your health query: {str(e)}"}

@app.post("/whatsapp-webhook")
async def whatsapp_webhook(request: Request):
    """Handle WhatsApp webhook for message processing."""
    try:
        data = await request.json()
        # Process WhatsApp message format
        # Implementation depends on WhatsApp Business API structure
        return {"status": "processed"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Odisha Health AI Assistant is running!",
        "service": "AI-Driven Public Health Chatbot",
        "department": "Government of Odisha - Electronics & IT Department"
    }

# ===========================
# CLI Runner for Testing
# ===========================
def run_medical_chatbot():
    """Run the medical chatbot in CLI mode for testing."""
    print("\n🏥 नमस्ते! I'm your AI Health Assistant for Odisha!")
    print("Ask me about health conditions, symptoms, vaccinations, or disease prevention.")
    print("मैं हिंदी में भी जवाब दे सकता हूं। Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ["exit", "quit", "bye", "बाई"]:
                print("\nAI: Stay healthy! Take care! 🏥👋")
                break
            
            if not user_input:
                print("AI: Please ask me about your health concerns!")
                continue
            
            # Invoke the medical chatbot
            result = medical_chatbot.invoke({"messages": [HumanMessage(content=user_input)]})
            
            # Get the final response
            final_message = result['messages'][-1]
            response = final_message.content if hasattr(final_message, 'content') else str(final_message)
            
            print(f"AI: {response}\n")
            print("⚠️ Disclaimer: This is for educational purposes only. Please consult a doctor for medical advice.\n")
        
        except KeyboardInterrupt:
            print("\n\nAI: Stay healthy! Goodbye! 🏥👋")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}\n")

# ===========================
# MAIN EXECUTION
# ===========================
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        # Run as FastAPI server
        import uvicorn
        print("🚀 Starting Odisha Health AI Assistant server...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # Run as CLI for testing
        run_medical_chatbot()