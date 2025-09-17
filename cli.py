from service.main import main
from colorama import Fore
import uuid

def run_medical_chatbot():

    print(Fore.BLUE + "Ask me about health conditions, symptoms, vaccinations, or disease prevention." + Fore.RESET)
    
    # Create a unique session ID for this conversation
    session_id = str(uuid.uuid4())
    
    while True:
        try:
            user_input = input("You: ")
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print(Fore.BLUE + "\nAI: Stay healthy! Take care! 👋" + Fore.RESET)
                break
            
            if not user_input:
                print(Fore.BLUE + "AI: Please ask me about your health concerns!" + Fore.RESET)
                continue

            response, session_id = main(user_input, session_id)

            print(Fore.CYAN + f"AI: {response}\n" + Fore.RESET)

        except Exception as e:
            print(Fore.RED + f"❌ Error: {str(e)}\n" + Fore.RESET)


if __name__ == "__main__":
    run_medical_chatbot()