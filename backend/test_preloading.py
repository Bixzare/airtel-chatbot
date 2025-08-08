#!/usr/bin/env python3
"""
Test script to verify document preloading functionality.
"""

from src.agent.rag_agent import LangGraphRAGAgent
from src.memory.checkpointer import Checkpointer
from src.config.settings import Settings
import os
import sys
import time


def test_preloading():
    """Test the document preloading functionality."""
    print("🧪 Testing document preloading functionality...")

    # Load settings
    settings = Settings()

    # Initialize checkpointer
    checkpointer = Checkpointer(db_path=settings.checkpoint_db_path)

    # Document path
    document_path = "src/rag/static_document.txt"

    # Check if document exists
    if os.path.exists(document_path):
        print(f"✅ Found document: {document_path}")
    else:
        print(f"❌ Document not found: {document_path}")
        print("❌ No document found to test!")
        return False

    try:
        # Test initialization with single document
        print("\n🚀 Initializing RAG agent with static_document.txt...")
        start_time = time.time()

        agent = LangGraphRAGAgent(
            document_path=document_path,
            model_name="gemini-1.5-flash",
            checkpointer=checkpointer
        )

        init_time = time.time() - start_time
        print(f"✅ RAG Agent initialized in {init_time:.2f} seconds")
        print(f"📊 Total chunks loaded: {agent.rag_tool.num_chunks}")
        print(f"💾 Cache enabled: {agent.rag_tool.cache is not None}")

        # Test query to warm up the system
        print("\n🔥 Testing query to warm up embeddings and cache...")
        test_start = time.time()

        test_query = "Airtel Niger services"
        test_results = agent.rag_tool(test_query)

        test_time = time.time() - test_start
        print(f"✅ Test query completed in {test_time:.2f} seconds")
        print(f"📝 Retrieved {len(test_results)} document chunks")

        # Test cache functionality
        if agent.rag_tool.cache:
            print("\n💾 Testing cache functionality...")
            cache_start = time.time()

            # Same query should hit cache
            cached_results = agent.rag_tool.cache.get(test_query)
            cache_time = time.time() - cache_start

            if cached_results:
                print(f"✅ Cache hit in {cache_time:.4f} seconds")
                print(f"📊 Cache stats: {agent.rag_tool.cache.get_stats()}")
            else:
                print("❌ Cache miss")

        # Test performance with multiple queries
        print("\n⚡ Testing performance with multiple queries...")
        queries = [
            "Airtel Money services",
            "Internet plans",
            "Voice plans",
            "Zamani services",
            "Moov services"
        ]

        total_query_time = 0
        for i, query in enumerate(queries, 1):
            query_start = time.time()
            results = agent.rag_tool(query)
            query_time = time.time() - query_start
            total_query_time += query_time

            print(
                f"  Query {i}: '{query}' - {query_time:.3f}s - {len(results)} chunks")

        avg_query_time = total_query_time / len(queries)
        print(f"📊 Average query time: {avg_query_time:.3f} seconds")

        print("\n🎉 Preloading test completed successfully!")
        print("📈 Performance summary:")
        print(f"  - Initialization: {init_time:.2f}s")
        print(f"  - Test query: {test_time:.2f}s")
        print(f"  - Average query: {avg_query_time:.3f}s")
        print(f"  - Total chunks: {agent.rag_tool.num_chunks}")

        return True

    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_preloading()
    sys.exit(0 if success else 1)
