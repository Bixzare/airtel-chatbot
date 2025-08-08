"""
Main LangGraph RAG agent implementation.
"""

from src.tools.rag_tool import RAGTool
from src.tools.placeholder_tools import CalculatorTool, SummarizerTool
from src.agent.agent_state import AgentState
from src.memory.checkpointer import Checkpointer
from src.prompts.system_prompt import AIRTEL_NIGER_OPTIMIZED_PROMPT
from langgraph.graph import START, StateGraph
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, trim_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableConfig
import os
import time
import logging
import re
from typing import List, Any, AsyncGenerator, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Maximum number of tokens to keep in conversation history - OPTIMIZED FOR SPEED
MAX_HISTORY_TOKENS = 3000


class LangGraphRAGAgent:
    """LangGraph-based RAG agent with memory, RAG tool, and LLM node."""

    def __init__(self, document_path: str, model_name: str = "gemini-1.5-flash", checkpointer=None, additional_documents: Optional[List[str]] = None):
        """
        Initialize the RAG agent with document path and model.

        Args:
            document_path: Path to the knowledge base document
            model_name: Name of the Google Generative AI model to use
            checkpointer: Optional checkpointer instance for memory persistence
            additional_documents: List of additional document paths to load
        """
        logger.info(f"Initializing RAG agent with document: {document_path}")
        if additional_documents:
            logger.info(
                f"Additional documents to load: {additional_documents}")

        # Initialize LLM for regular (non-streaming) calls - OPTIMIZED FOR SPEED
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.environ.get("GOOGLE_API_KEY"),
            temperature=0.1,  # Lower temperature for faster, more consistent responses
            top_p=0.8,  # Reduced for faster generation
            top_k=20,  # Reduced for faster generation
            # Reduced timeout for faster responses
            timeout=int(os.environ.get("LLM_TIMEOUT", 60))
        )

        # Initialize message trimmer
        self.message_trimmer = trim_messages(
            max_tokens=MAX_HISTORY_TOKENS,
            strategy="last",  # Keep the most recent messages
            token_counter=self.llm,  # Use the LLM to count tokens
            include_system=True,  # Always keep system messages
            allow_partial=False,  # Don't allow partial messages
            start_on="human"  # Start with a human message
        )

        # Initialize tools with multiple documents
        self.rag_tool = RAGTool(
            document_path, additional_documents=additional_documents or [])
        self.calculator_tool = CalculatorTool()
        self.summarizer_tool = SummarizerTool(llm=self.llm)

        # Initialize memory
        self.checkpointer = checkpointer or Checkpointer()

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
                    if isinstance(user_message, list):
                        user_message = " ".join(
                            [str(item) for item in user_message])
                    elif not isinstance(user_message, str):
                        user_message = str(user_message)
                    logger.info(f"Processing query: {user_message}")

                    # Trim messages to prevent context window overflow
                    trimmed_messages = self.message_trimmer.invoke(
                        state["messages"])
                    logger.info(
                        f"Trimmed message history from {len(state['messages'])} to {len(trimmed_messages)} messages")

                    # Detect which tool to use
                    tool_name, tool_input = self._detect_tool_calls(
                        user_message)
                    logger.info(f"Selected tool: {tool_name}")

                    # Call appropriate tool
                    if tool_name == "calculator":
                        tool_result = self.calculator_tool(tool_input)
                        context = f"Calculator result: {tool_result}"
                        logger.info(f"Calculator result: {tool_result}")
                    elif tool_name == "summarizer":
                        tool_result = self.summarizer_tool(tool_input)
                        context = "Summary points:\n" + \
                            "\n".join([f"- {point}" for point in tool_result])
                        logger.info(
                            f"Summarizer result: {len(tool_result)} points")
                    else:  # Default to RAG
                        docs = self.rag_tool(user_message)
                        if docs and docs[0] != "No specific information found in the knowledge base for this query.":
                            logger.info(
                                f"Retrieved {len(docs)} relevant document chunks")
                            context = "\n\n".join(
                                [f"Document chunk {i+1}:\n{doc}" for i, doc in enumerate(docs)])
                        else:
                            logger.warning("No relevant documents found")
                            context = "No specific information found in the knowledge base for this query."
                        tool_result = docs

                    # Prepare system prompt with context
                    system_prompt = AIRTEL_NIGER_OPTIMIZED_PROMPT
                    context_message = SystemMessage(
                        content=f"{system_prompt}\n\nRelevant Information:\n{context}")

                    # Pass trimmed conversation history to LLM
                    llm_messages = [context_message] + trimmed_messages
                    logger.info("Calling LLM for response")
                    response = self.llm.invoke(llm_messages)

                    # Create updated state
                    updated_state: AgentState = {
                        "messages": state["messages"] + [AIMessage(content=response.content)],
                        "retrieved_docs": tool_result if tool_name == "rag" and isinstance(tool_result, list) else state["retrieved_docs"],
                        "current_query": user_message,
                        "tool_calls": state["tool_calls"] + [{"tool": tool_name, "result": tool_result}]
                    }

                    # Get thread_id from config if available
                    thread_id = None
                    try:
                        # This is a bit of a hack to get the thread_id from the context
                        # It assumes the thread_id is passed in the config
                        from inspect import currentframe
                        f = currentframe()
                        while f:
                            if 'config' in f.f_locals and isinstance(f.f_locals['config'], dict) and 'configurable' in f.f_locals['config']:
                                thread_id = f.f_locals['config']['configurable'].get(
                                    'thread_id')
                                break
                            f = f.f_back
                    except Exception as e:
                        logger.warning(
                            f"Could not get thread_id from context: {str(e)}")

                    # Save state to our manual store if thread_id is available
                    if thread_id:
                        self.checkpointer.save_state(
                            dict(updated_state), thread_id)

                    # Return updated state
                    return updated_state

                except Exception as e:
                    logger.error(
                        f"Error in agent node (attempt {attempt+1}/{max_retries}): {str(e)}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.info(f"Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        fallback_response = "I'm experiencing technical difficulties. Please try again in a moment or contact Airtel customer service for immediate assistance."
                        logger.error(
                            "Max retries reached, returning fallback response")
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
        logger.info(
            f"Invoking agent with query: {query} (thread: {thread_id})")
        state: AgentState = {
            "messages": [HumanMessage(content=query)],
            "retrieved_docs": [],
            "current_query": query,
            "tool_calls": []
        }
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
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
        logger.info(
            f"Invoking agent with message history (thread: {thread_id})")
        state: AgentState = {
            "messages": messages,
            "retrieved_docs": [],
            "current_query": query,
            "tool_calls": []
        }
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        result = self.workflow.invoke(state, config)
        updated_messages = result["messages"]
        return result["messages"][-1].content, updated_messages

    async def _process_query_and_get_context(self, query: str, messages: List[HumanMessage]) -> Tuple[str, Any]:
        """
        Process a query and get the context for LLM.

        Args:
            query: User query
            messages: Message history

        Returns:
            Tuple of (context, tool_result)
        """
        # Trim messages to prevent context window overflow
        trimmed_messages = self.message_trimmer.invoke(messages)
        logger.info(
            f"Trimmed message history from {len(messages)} to {len(trimmed_messages)} messages for streaming")

        # Detect which tool to use
        tool_name, tool_input = self._detect_tool_calls(query)
        logger.info(f"Selected tool: {tool_name}")

        # Call appropriate tool
        if tool_name == "calculator":
            tool_result = self.calculator_tool(tool_input)
            context = f"Calculator result: {tool_result}"
            logger.info(f"Calculator result: {tool_result}")
        elif tool_name == "summarizer":
            tool_result = self.summarizer_tool(tool_input)
            context = "Summary points:\n" + \
                "\n".join([f"- {point}" for point in tool_result])
            logger.info(f"Summarizer result: {len(tool_result)} points")
        else:  # Default to RAG
            docs = self.rag_tool(query)
            if docs and docs[0] != "No specific information found in the knowledge base for this query.":
                logger.info(f"Retrieved {len(docs)} relevant document chunks")
                context = "\n\n".join(
                    [f"Document chunk {i+1}:\n{doc}" for i, doc in enumerate(docs)])
            else:
                logger.warning("No relevant documents found")
                context = "No specific information found in the knowledge base for this query."
            tool_result = docs

        return context, tool_result

    async def invoke_with_streaming(self, query: str, thread_id: str = "default") -> AsyncGenerator[str, None]:
        """
        Invoke the agent with streaming response.

        Args:
            query: User query
            thread_id: Thread ID for conversation memory

        Yields:
            Chunks of the response as they are generated
        """
        logger.info(
            f"Invoking agent with streaming for query: {query} (thread: {thread_id})")

        # Get conversation state from memory
        config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
        try:
            state = self.checkpointer.get_memory().get(config)
        except Exception as e:
            logger.warning(f"Could not load from memory: {str(e)}")
            state = None

        # If not found in LangGraph memory, try our manual store
        if state is None:
            state = self.checkpointer.get_state(thread_id)

        # Initialize state if it doesn't exist
        if state is None:
            messages = [HumanMessage(content=query)]
            state = {
                "messages": messages,
                "retrieved_docs": [],
                "current_query": query,
                "tool_calls": []
            }
        else:
            # Add the new message to existing state
            messages = state.get("messages", []) + \
                [HumanMessage(content=query)]
            state = {
                "messages": messages,
                "retrieved_docs": state.get("retrieved_docs", []),
                "current_query": query,
                "tool_calls": state.get("tool_calls", [])
            }

        try:
            # Process query and get context
            context, tool_result = await self._process_query_and_get_context(query, messages)

            # Prepare system prompt with context
            system_prompt = AIRTEL_NIGER_OPTIMIZED_PROMPT
            context_message = SystemMessage(
                content=f"{system_prompt}\n\nRelevant Information:\n{context}")

            # Trim messages to prevent context window overflow
            trimmed_messages = self.message_trimmer.invoke(messages)

            # Pass trimmed conversation history to LLM
            llm_messages = [context_message] + trimmed_messages
            logger.info("Streaming LLM response")

            # Stream the response using the correct approach for Google's Generative AI
            full_response = ""
            async for chunk in self.llm.astream(llm_messages):
                if hasattr(chunk, 'content'):
                    content = chunk.content
                    if content and isinstance(content, str):
                        full_response += content
                        yield content

            # Update state with the complete response
            state["messages"].append(AIMessage(content=full_response))
            state["retrieved_docs"] = tool_result if isinstance(
                tool_result, list) else state["retrieved_docs"]
            state["tool_calls"].append({"tool": "rag", "result": tool_result})

            # Save updated state using our manual method
            self.checkpointer.save_state(state, thread_id)

        except Exception as e:
            logger.error(f"Error in streaming response: {str(e)}")
            fallback_response = "I'm experiencing technical difficulties. Please try again in a moment or contact Airtel customer service for immediate assistance."
            yield fallback_response

            # Update state with fallback response
            state["messages"].append(AIMessage(content=fallback_response))
            self.checkpointer.save_state(state, thread_id)

    async def invoke_with_memory_streaming(self, messages, thread_id: str = "default") -> AsyncGenerator[str, None]:
        """
        Invoke the agent with a full message history and streaming response.

        Args:
            messages: List of message objects
            thread_id: Thread ID for conversation memory

        Yields:
            Chunks of the response as they are generated
        """
        if not messages:
            # Instead of returning a value, just don't yield anything
            return

        query = messages[-1].content
        logger.info(
            f"Invoking agent with streaming and message history (thread: {thread_id})")

        try:
            # Process query and get context
            context, tool_result = await self._process_query_and_get_context(query, messages)

            # Prepare system prompt with context
            system_prompt = AIRTEL_NIGER_OPTIMIZED_PROMPT
            context_message = SystemMessage(
                content=f"{system_prompt}\n\nRelevant Information:\n{context}")

            # Trim messages to prevent context window overflow
            trimmed_messages = self.message_trimmer.invoke(messages)

            # Pass trimmed conversation history to LLM
            llm_messages = [context_message] + trimmed_messages
            logger.info("Streaming LLM response")

            # Stream the response using the correct approach for Google's Generative AI
            full_response = ""
            async for chunk in self.llm.astream(llm_messages):
                if hasattr(chunk, 'content'):
                    content = chunk.content
                    if content and isinstance(content, str):
                        full_response += content
                        yield content

            # Update messages with the complete response
            updated_messages = messages + [AIMessage(content=full_response)]

            # Save state to memory
            state: AgentState = {
                "messages": updated_messages,
                "retrieved_docs": tool_result if isinstance(tool_result, list) else [],
                "current_query": query,
                "tool_calls": [{"tool": "rag", "result": tool_result}]
            }

            # Save updated state using our manual method
            self.checkpointer.save_state(dict(state), thread_id)

        except Exception as e:
            logger.error(f"Error in streaming response with memory: {str(e)}")
            fallback_response = "I'm experiencing technical difficulties. Please try again in a moment or contact Airtel customer service for immediate assistance."
            yield fallback_response
