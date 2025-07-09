import sys
from dotenv import load_dotenv
load_dotenv()
from src.agent.rag_agent import LangGraphRAGAgent
from langchain_core.messages import HumanMessage, AIMessage

def main():
    agent = LangGraphRAGAgent('src/rag/static_document.txt')
    thread_id = input("Enter a session/thread id (or press Enter for default): ") or "default"
    print("Type your message (type 'quit' or 'exit' to stop):")
    messages = []
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in {"quit", "exit"}:
            print("Exiting chat.")
            break
        messages.append(HumanMessage(content=user_input))
        response, messages = agent.invoke_with_memory(messages, thread_id=thread_id)
        print(f"Agent: {response}")

if __name__ == "__main__":
    main() 