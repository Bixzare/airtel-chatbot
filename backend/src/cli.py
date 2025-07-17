
from langchain_core.messages import HumanMessage
from src.agent.rag_agent import LangGraphRAGAgent
from dotenv import load_dotenv
load_dotenv()


def main():
    agent = LangGraphRAGAgent('src/rag/static_document.txt')
    thread_id = input(
        "Enter a session/thread id (or press Enter for default): ") or "default"
    print("Type your message (type 'quit' or 'exit' to stop):")
    messages = []
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in {"quit", "exit"}:
            print("Exiting chat.")
            break
        messages.append(HumanMessage(content=user_input))
        response, messages = agent.invoke_with_memory(
            messages, thread_id=thread_id)
        print(f"Agent: {response}")

"""
CLI for testing the RAG agent locally.
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from src.agent.rag_agent import LangGraphRAGAgent
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run the RAG agent from the command line."""
    # Load environment variables
    load_dotenv()
    
    # Check for Google API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable not set.")
        print("Please set it in a .env file or export it in your shell.")
        sys.exit(1)
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Test the RAG agent from the command line.")
    parser.add_argument("--document", "-d", default="src/rag/static_document.txt",
                        help="Path to the document file (default: src/rag/static_document.txt)")
    parser.add_argument("--model", "-m", default="gemini-1.5-flash",
                        help="Model name (default: gemini-1.5-flash)")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Run in interactive mode")
    parser.add_argument("query", nargs="?", default=None,
                        help="Query to send to the agent (not needed in interactive mode)")
    
    args = parser.parse_args()
    
    try:
        # Initialize the agent
        print(f"Initializing RAG agent with document: {args.document}")
        agent = LangGraphRAGAgent(args.document, args.model)
        print("Agent initialized successfully.")
        
        if args.interactive:
            # Interactive mode
            session_id = "cli-session"
            messages = []
            
            print("\nRAG Agent Interactive Mode")
            print("Type 'exit' or 'quit' to end the session.")
            print("Type 'clear' to clear the conversation history.")
            print("-" * 50)
            
            while True:
                query = input("\nYou: ")
                
                if query.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break
                
                if query.lower() == "clear":
                    messages = []
                    print("Conversation history cleared.")
                    continue
                
                if not query.strip():
                    continue
                
                # Add user message to history
                from langchain_core.messages import HumanMessage
                messages.append(HumanMessage(content=query))
                
                # Get response
                print("\nAirtel Agent: ", end="", flush=True)
                
                try:
                    response, messages = agent.invoke_with_memory(messages, thread_id=session_id)
                    print(response)
                except Exception as e:
                    print(f"Error: {str(e)}")
        
        elif args.query:
            # Single query mode
            response = agent.invoke(args.query)
            print(f"\nQuery: {args.query}")
            print(f"Response: {response}")
        
        else:
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)



if __name__ == "__main__":
    main()
