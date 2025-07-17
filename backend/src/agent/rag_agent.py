"""
Main LangGraph RAG agent implementation.
"""

from src.tools.rag_tool import RAGTool
from src.tools.placeholder_tools import CalculatorTool, SummarizerTool
from src.agent.agent_state import AgentState
from src.memory.checkpointer import Checkpointer
from src.prompts.system_prompt import AIRTEL_NIGER_SYSTEM_PROMPT
from langgraph.graph import START, StateGraph
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import time
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LangGraphRAGAgent:
    """LangGraph-based RAG agent with memory, RAG tool, and LLM node."""
    def __init__(self, document_path: str, model_name: str = "gemini-1.5-flash"):
        """
        Initialize the RAG agent with document path and model.
        
        Args:
            document_path: Path to the knowledge base document
            model_name: Name of the Google Generative AI model to use
        """
        logger.info(f"Initializing RAG agent with document: {document_path}")
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.environ.get("GOOGLE_API_KEY"),
            temperature=0.2,  # Lower temperature for more factual responses
            top_p=0.9,
            top_k=40,
            timeout=30  # 30 second timeout
        )
        
        # Initialize tools
        self.rag_tool = RAGTool(document_path)
        self.calculator_tool = CalculatorTool()
        self.summarizer_tool = SummarizerTool(llm=self.llm)
        
        # Initialize memory
        self.checkpointer = Checkpointer()
        
        # Build workflow
        self.workflow = self._build_workflow()
        logger.info("RAG agent initialized successfully")

    def _detect_tool_calls(self, query: str):
        """
        Detect which tool to use based on the query.
        
        Args:
            query: User query
            
        Returns:
            Tuple of (tool_name, tool_input)
        """
        # Check for calculation requests
        calc_patterns = [
            r'calculate\s+([\d\+\-\*\/\(\)\.\s]+)',
            r'compute\s+([\d\+\-\*\/\(\)\.\s]+)',
            r'what is\s+([\d\+\-\*\/\(\)\.\s]+)',
            r'([\d]+\s*[\+\-\*\/]\s*[\d]+)'
        ]
        
        for pattern in calc_patterns:
            match = re.search(pattern, query.lower())
            if match:
                return "calculator", match.group(1)
        
        # Check for summarization requests
        if any(keyword in query.lower() for keyword in ["summarize", "summary", "summarization", "key points"]):
            # Extract text to summarize - assume it's the rest of the query after the keyword
            for keyword in ["summarize", "summary", "summarization", "key points"]:
                if keyword in query.lower():
                    parts = query.lower().split(keyword, 1)
                    if len(parts) > 1:
                        return "summarizer", parts[1].strip()
        
        # Default to RAG tool
        return "rag", query

    def _build_workflow(self):
        """Build the LangGraph workflow."""
        workflow = StateGraph(state_schema=AgentState)

        def agent_node(state: AgentState):
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Get the latest user message
                    user_message = state["messages"][-1].content
                    logger.info(f"Processing query: {user_message}")
                    
                    # Detect which tool to use
                    tool_name, tool_input = self._detect_tool_calls(user_message)
                    logger.info(f"Selected tool: {tool_name}")
                    
                    # Call appropriate tool
                    if tool_name == "calculator":
                        tool_result = self.calculator_tool(tool_input)
                        context = f"Calculator result: {tool_result}"
                        logger.info(f"Calculator result: {tool_result}")
                    elif tool_name == "summarizer":
                        tool_result = self.summarizer_tool(tool_input)
                        context = f"Summary points:\n" + "\n".join([f"- {point}" for point in tool_result])
                        logger.info(f"Summarizer result: {len(tool_result)} points")
                    else:  # Default to RAG
                        docs = self.rag_tool(user_message)
                        if docs and docs[0] != "No specific information found in the knowledge base for this query.":
                            logger.info(f"Retrieved {len(docs)} relevant document chunks")
                            context = "\n\n".join([f"Document chunk {i+1}:\n{doc}" for i, doc in enumerate(docs)])
                        else:
                            logger.warning("No relevant documents found")
                            context = "No specific information found in the knowledge base for this query."
                        tool_result = docs
                    
                    # Prepare system prompt with context
                    system_prompt = AIRTEL_NIGER_SYSTEM_PROMPT
                    context_message = SystemMessage(content=f"{system_prompt}\n\nRelevant Information:\n{context}")
                    
                    # Pass full conversation history to LLM
                    llm_messages = [context_message] + state["messages"]
                    logger.info("Calling LLM for response")
                    response = self.llm.invoke(llm_messages)
                    
                    # Update state
                    return {
                        "messages": state["messages"] + [AIMessage(content=response.content)],
                        "retrieved_docs": tool_result if tool_name == "rag" else state["retrieved_docs"],
                        "current_query": user_message,
                        "tool_calls": state["tool_calls"] + [{"tool": tool_name, "result": tool_result}]
                    }
                except Exception as e:
                    logger.error(f"Error in agent node (attempt {attempt+1}/{max_retries}): {str(e)}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        fallback_response = "I'm experiencing technical difficulties. Please try again in a moment or contact Airtel customer service for immediate assistance."
                        logger.error(f"Max retries reached, returning fallback response")
                        return {
                            "messages": state["messages"] + [AIMessage(content=fallback_response)],
                            "retrieved_docs": state["retrieved_docs"],
                            "current_query": state["current_query"],
                            "tool_calls": state["tool_calls"]
                        }

        # Add node and edge
        workflow.add_node("agent", agent_node)
        workflow.add_edge(START, "agent")
        
        # Compile workflow with checkpointer
        return workflow.compile(checkpointer=self.checkpointer.get_memory())

    def invoke(self, query: str, thread_id: str = "default"):
        """
        Invoke the agent with a single query.
        
        Args:
            query: User query
            thread_id: Thread ID for conversation memory
            
        Returns:
            Agent response text
        """
        logger.info(f"Invoking agent with query: {query} (thread: {thread_id})")
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
        """
        Invoke the agent with a full message history.
        
        Args:
            messages: List of message objects
            thread_id: Thread ID for conversation memory
            
        Returns:
            Tuple of (response text, updated messages)
        """
        query = messages[-1].content if messages else ""
        logger.info(f"Invoking agent with message history (thread: {thread_id})")
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