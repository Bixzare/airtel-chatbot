"""
Additional tools: calculator and summarizer.
"""

from .base_tool import BaseTool
import re
import math
from typing import List, Dict, Any, Union, Optional

class CalculatorTool(BaseTool):
    """Tool for performing basic arithmetic calculations."""
    name = "calculator"
    description = "Calculate arithmetic expressions (add, subtract, multiply, divide)."
    
    def __call__(self, expression: str) -> str:
        """
        Evaluate a mathematical expression.
        
        Args:
            expression: The mathematical expression to evaluate
            
        Returns:
            String result of the calculation or error message
        """
        try:
            # Clean the expression
            clean_expr = self._clean_expression(expression)
            
            # Check for safety
            if not self._is_safe_expression(clean_expr):
                return "Sorry, I can only perform basic arithmetic operations."
            
            # Evaluate the expression
            result = eval(clean_expr, {"__builtins__": None}, 
                         {"abs": abs, "round": round, "max": max, "min": min, 
                          "pow": pow, "sqrt": math.sqrt})
            
            # Format the result
            if isinstance(result, int) or result.is_integer():
                return str(int(result))
            else:
                return f"{result:.2f}"
                
        except Exception as e:
            return f"Error calculating result: {str(e)}"
    
    def _clean_expression(self, expression: str) -> str:
        """Clean and prepare the expression for evaluation."""
        # Remove any text that isn't part of a math expression
        math_expr = re.sub(r'[^0-9+\-*/().^\s]', '', expression)
        # Replace ^ with ** for exponentiation
        math_expr = math_expr.replace('^', '**')
        return math_expr
    
    def _is_safe_expression(self, expression: str) -> bool:
        """Check if the expression is safe to evaluate."""
        # Only allow basic arithmetic operations and a few math functions
        allowed_pattern = r'^[0-9+\-*/().\s\*\*]+$'
        return bool(re.match(allowed_pattern, expression))


class SummarizerTool(BaseTool):
    """Tool for summarizing text."""
    name = "summarizer"
    description = "Summarize long text into key points."
    
    def __init__(self, llm=None):
        """
        Initialize the summarizer tool.
        
        Args:
            llm: Optional language model to use for summarization
        """
        self.llm = llm
    
    def __call__(self, text: str, max_points: int = 3) -> List[str]:
        """
        Summarize text into key points.
        
        Args:
            text: The text to summarize
            max_points: Maximum number of key points to return
            
        Returns:
            List of key points from the text
        """
        if not text or len(text) < 50:
            return ["Text too short to summarize."]
        
        if self.llm:
            # If we have an LLM, use it for summarization
            try:
                prompt = f"Summarize the following text into {max_points} key points:\n\n{text}"
                response = self.llm.invoke(prompt)
                
                # Extract bullet points
                points = re.findall(r'•\s*(.*?)(?=\n•|\n\n|$)', response.content, re.DOTALL)
                if not points:
                    points = response.content.split('\n')
                    points = [p.strip() for p in points if p.strip()]
                
                return points[:max_points]
            except Exception as e:
                return [f"Error summarizing text: {str(e)}"]
        else:
            # Simple fallback summarization
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            
            if len(sentences) <= max_points:
                return sentences
            
            # Very basic summarization - just take first few sentences
            return sentences[:max_points] 