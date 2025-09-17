from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_chroma import Chroma
from service.prompts import prompt
from service.config import config
from langchain_community.document_loaders import JSONLoader
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import hashlib

# Path for the persistent ChromaDB
CHROMA_PERSIST_DIRECTORY = os.path.join("service", "data", "chroma_db")
COLLECTION_NAME = "disease_symptoms"

chat_prompt = ChatPromptTemplate.from_template(prompt)
output_parser = StrOutputParser()

# Load or create ChromaDB instance (only if it doesn't already exist)
def get_or_create_vectorstore():
    """Get existing ChromaDB or create a new one if needed"""
    try:
        # Try to load existing database first
        vectorstore = Chroma(
            persist_directory=CHROMA_PERSIST_DIRECTORY,
            embedding_function=config.embeddings,
            collection_name=COLLECTION_NAME
        )
        
        # Check if the database has documents
        if vectorstore._collection.count() > 0:
            print(f"Loaded existing ChromaDB with {vectorstore._collection.count()} documents")
            return vectorstore
    except Exception as e:
        print(f"Error loading ChromaDB: {e}")
    
    # If we get here, we need to create a new database
    print("Creating new ChromaDB from source data...")
    
    # Load JSON data
    loader = JSONLoader(
        file_path="service/data/disease_symptoms.json",
        jq_schema=".records[]",
        text_content=False,
    )

    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    
    # Initialize or load ChromaDB
    vectorstore = Chroma.from_documents(
        documents=texts,
        embedding=config.embeddings,
        persist_directory=CHROMA_PERSIST_DIRECTORY,
        collection_name=COLLECTION_NAME,
    )
    # Persist data to disk
    vectorstore.persist()
    return vectorstore

# Initialize the vectorstore
vectorstore = get_or_create_vectorstore()

def main(query):
    """ Perform a vector search and return the most relevant document """
    # Use the persisted ChromaDB for retrieval
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
    
    retrieval_chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
        }
        | chat_prompt
        | config.llm
        | StrOutputParser()
    )
    return retrieval_chain.invoke(query)

def add_document(disease_data):
    """
    Add a new document to the ChromaDB vectorstore
    
    :param disease_data: A dictionary with Disease and Symptoms keys
    :return: True if successful, False otherwise
    """
    try:
        from langchain_core.documents import Document
        
        # Convert to Document format with proper text formatting for better matching
        symptoms_text = ", ".join(disease_data.get("Symptoms", []))
        content = f"Disease: {disease_data.get('Disease', '')}\nSymptoms: {symptoms_text}"
        
        doc = Document(
            page_content=content,
            metadata=disease_data
        )
        
        # Generate a unique ID based on the content
        doc_id = f"doc_{hashlib.md5(content.encode()).hexdigest()}"
        
        # Add to the vectorstore with explicit ID
        vectorstore.add_documents([doc], ids=[doc_id])
        
        # Persist data to disk
        vectorstore.persist()
        return True
    except Exception as e:
        print(f"Error adding document to ChromaDB: {e}")
        return False

if __name__ == "__main__":
    query = "I am feeling fever and headache with mild cough and sore throat"
    response = main(query)
    print(response)