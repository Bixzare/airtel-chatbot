"""
Test script for the RAG agent.
"""

from src.agent.rag_agent import LangGraphRAGAgent
import os
import sys
from dotenv import load_dotenv


def main():
    """Run test queries against the RAG agent."""
    # Load environment variables
    load_dotenv()

    # Check for Google API key
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable not set.")
        print("Please set it in a .env file or export it in your shell.")
        sys.exit(1)

    # Initialize the agent
    print("Initializing RAG agent...")
    document_path = os.environ.get(
        "DOCUMENT_PATH", "src/rag/static_document.txt")
    agent = LangGraphRAGAgent(document_path)
    print("Agent initialized successfully.")

    # Test queries
    test_queries = [
        # RAG queries
        "What data plans does Airtel offer?",
        "How much does the monthly data plan cost?",
        "What is Airtel's customer service number?",
        "I'm using Moov currently, why should I switch to Airtel?",

        # Calculator queries
        "Calculate 125 + 75",
        "What is 2500 / 5?",

        # Summarization queries
        "Summarize this text: Airtel Niger provides comprehensive mobile telecommunications services including voice calls, SMS, and data services. Our network covers major cities and towns across Niger. We offer various data plans including daily, weekly and monthly options at competitive rates. Our customer service is available 24/7 to assist with any issues.",

        # Unknown information
        "What is Airtel's 5G rollout plan?"
    ]

    # Run tests
    session_id = "test_session"
    messages = []

    print("\n" + "="*50)
    print("Starting test queries...")
    print("="*50)

    for i, query in enumerate(test_queries):
        print(f"\nTest {i+1}: {query}")
        print("-" * 50)

        # Add user message to history
        from langchain_core.messages import HumanMessage
        messages.append(HumanMessage(content=query))

        # Get response
        try:
            response, messages = agent.invoke_with_memory(
                messages, thread_id=session_id)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")

        print("-" * 50)

    print("\nAll tests completed.")


if __name__ == "__main__":
    main()
