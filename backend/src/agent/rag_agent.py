"""
Main LangGraph RAG agent implementation.
"""

from src.tools.rag_tool import RAGTool
from src.agent.agent_state import AgentState
from src.memory.checkpointer import Checkpointer
from src.prompts.system_prompt import AIRTEL_NIGER_SYSTEM_PROMPT
from langgraph.graph import START, StateGraph
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import time

class LangGraphRAGAgent:
    """LangGraph-based RAG agent with memory, RAG tool, and LLM node."""
    def __init__(self, document_path: str):
        with open(document_path, 'r', encoding='utf-8') as f:
            doc = f.read()
        self.rag_tool = RAGTool(doc)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.environ["GOOGLE_API_KEY"],
            timeout=30  # 30 second timeout
        )
        self.checkpointer = Checkpointer()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        workflow = StateGraph(state_schema=AgentState)

        def agent_node(state: AgentState):
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Get the latest user message
                    user_message = state["messages"][-1].content
                    
                    # Call RAG tool
                    docs = self.rag_tool(user_message)
                    context = "\n".join(docs) or "No specific information found in the knowledge base for this query."
                    
                    # Prepare system prompt with context
                    system_prompt = AIRTEL_NIGER_SYSTEM_PROMPT
                    context_message = SystemMessage(content=f"{system_prompt}\n\nRelevant Documentation:\n{context}")
                    
                    # Pass full conversation history to LLM
                    llm_messages = [context_message] + state["messages"]
                    response = self.llm.invoke(llm_messages)
                    
                    return {
                        "messages": state["messages"] + [AIMessage(content=response.content)],
                        "retrieved_docs": docs,
                        "current_query": user_message,
                        "tool_calls": state["tool_calls"] + [{"tool": "rag_search", "result": docs}]
                    }
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        time.sleep(wait_time)
                        continue
                    else:
                        fallback_response = "I'm experiencing technical difficulties. Please try again in a moment or contact Airtel customer service for immediate assistance."
                        return {
                            "messages": state["messages"] + [AIMessage(content=fallback_response)],
                            "retrieved_docs": state["retrieved_docs"],
                            "current_query": state["current_query"],
                            "tool_calls": state["tool_calls"]
                        }

        workflow.add_node("agent", agent_node)
        workflow.add_edge(START, "agent")
        return workflow.compile(checkpointer=self.checkpointer.get_memory())

    def invoke(self, query: str, thread_id: str = "default"):
        state = {
            "messages": [HumanMessage(content=query)],
            "retrieved_docs": [],
            "current_query": query,
            "tool_calls": []
        }
        config = {"configurable": {"thread_id": thread_id}}
        result = self.workflow.invoke(state, config)
        return result["messages"][-1].content

    def invoke_with_memory(self, messages, thread_id: str = "default"):
        """Invoke the agent with a full message history, returning the response and updated messages."""
        query = messages[-1].content if messages else ""
        state = {
            "messages": messages,
            "retrieved_docs": [],
            "current_query": query,
            "tool_calls": []
        }
        config = {"configurable": {"thread_id": thread_id}}
        result = self.workflow.invoke(state, config)
        updated_messages = result["messages"]
        return result["messages"][-1].content, updated_messages

# Example usage:
# agent = LangGraphRAGAgent('src/rag/static_document.txt')
# print(agent.invoke('remote work')) 