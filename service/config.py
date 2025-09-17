from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os

class Config:
    def __init__(self):
        load_dotenv()
        
        # Configure LLM with optimized settings
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            max_output_tokens=128,
        )

        # Configure embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
        )

config = Config()

if __name__ == "__main__":
    t = config.llm.invoke("Hello, world!")
    print(t)