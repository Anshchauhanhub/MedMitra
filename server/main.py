from service.main import main
from fastapi import Request
from server import app

@app.post("/chatbot")
async def health_chat_post(request: Request):
    
    try:
        data = await request.json()
        user_input = data.get("message", "").strip()
        
        if not user_input:
            return {"error": "Health query cannot be empty"}
        
        response = main(user_input)
        
        return {
            "result": response,
        }
    
    except Exception as e:
        return {"error": f"Sorry, I encountered an error while processing your health query: {str(e)}"}
    

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "AarogyaX is running!",
        "service": "AI-Driven Public Health Chatbot",
    }

