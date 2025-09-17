from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os

class Config:
    def __init__(self):
        load_dotenv()
        
        # Configure LLM
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            model_kwargs={
                "max_output_tokens": 128,  # Limit output tokens
                "temperature": 0.1,        # Lower temperature for more deterministic responses
            }
        )

        # Configure embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001"
        )

config = Config()

if __name__ == "__main__":
    t = config.llm.invoke("Hello, world!")
    print(t)