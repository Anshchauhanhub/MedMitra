# Standard library imports
import os
import uuid

# LangChain imports
from langchain_chroma import Chroma
from langchain_community.document_loaders import JSONLoader
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Local application imports
from service.config import config
from service.prompts import prompt

# Path for the persistent ChromaDB
CHROMA_PERSIST_DIRECTORY = os.path.join("service", "data", "chroma_db")
COLLECTION_NAME = "disease_symptoms"

chat_prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}")
])

output_parser = StrOutputParser()

def get_or_create_vectorstore():

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
    
    print("Creating new ChromaDB from source data...")
    
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
    vectorstore.persist()
    return vectorstore

vectorstore = get_or_create_vectorstore()

# Chat histories
chat_sessions = {}

def main(query, thread_id=None):
    """ Perform a vector search and return the most relevant document """
    # Generate a new thread_id if none is provided
    if thread_id is None:
        thread_id = str(uuid.uuid4())
    
    # Initialize chat history for new thread
    if thread_id not in chat_sessions:
        chat_sessions[thread_id] = []
    
    # Get the chat history for this thread
    chat_history = chat_sessions[thread_id]
    
    # ChromaDB for retrieval
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
    
    retrieval_chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
            "chat_history": lambda _: chat_history
        }
        | chat_prompt
        | config.llm
        | output_parser
    )
    response = retrieval_chain.invoke(query)
    
    # Update chat history with the new exchange
    chat_history.append(HumanMessage(content=query))
    chat_history.append(AIMessage(content=response))
    
    # Session update
    chat_sessions[thread_id] = chat_history
    
    return response, thread_id


if __name__ == "__main__":

    session_id = str(uuid.uuid4())
    print(f"Test session ID: {session_id}")
    
    query = "I am feeling fever and headache with mild cough and sore throat"
    
    response, session_id = main(query, session_id)
    print(f"Response: {response}")
    
    # Test with a follow-up question
    follow_up = "What should I drink to feel better?"
    print(f"\nFollow-up question: {follow_up}")
    response, session_id = main(follow_up, session_id)
    print(f"Follow-up response: {response}")