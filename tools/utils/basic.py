import time
import ast
import operator
from ..base import BaseTool

class TimeTool(BaseTool):
    name = "get_time"
    description = "Returns current local time. Use when asked about time/date."
    
    def execute(self, *args) -> str:
        return time.strftime("%Y-%m-%d %H:%M:%S")

class CalculatorTool(BaseTool):
    name = "calculate"
    description = "Evaluates math expressions. Use for arithmetic. Input: string expression."
    
    def execute(self, expression: str) -> str:
        # Safe evaluation using ast.literal_eval is too limited (no operators).
        # We'll use a safer approach than eval().
        allowed_operators = {
            ast.Add: operator.add, ast.Sub: operator.sub, 
            ast.Mult: operator.mul, ast.Div: operator.truediv, 
            ast.Pow: operator.pow, ast.USub: operator.neg 
        }
        
        def eval_expr(node):
            if isinstance(node, ast.Num):
                return node.n
            elif isinstance(node, ast.BinOp):
                return allowed_operators[type(node.op)](eval_expr(node.left), eval_expr(node.right))
            elif isinstance(node, ast.UnaryOp):
                return allowed_operators[type(node.op)](eval_expr(node.operand))
            else:
                raise TypeError(node)
                
        try:
            # Clean string
            expression = expression.strip().replace('^', '**')
            return str(eval_expr(ast.parse(expression, mode='eval').body))
        except Exception as e:
            return f"Error calculating: {e}"
