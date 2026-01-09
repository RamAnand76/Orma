"""
Phase 12: Code Autonomy - The Sandbox
A secure Python execution environment for Orma.
"""
import sys
import io
import traceback
from contextlib import redirect_stdout, redirect_stderr

# Restricted builtins - remove dangerous functions
SAFE_BUILTINS = {
    'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool,
    'chr': chr, 'dict': dict, 'divmod': divmod, 'enumerate': enumerate,
    'filter': filter, 'float': float, 'format': format, 'frozenset': frozenset,
    'getattr': getattr, 'hasattr': hasattr, 'hash': hash, 'hex': hex,
    'int': int, 'isinstance': isinstance, 'issubclass': issubclass,
    'iter': iter, 'len': len, 'list': list, 'map': map, 'max': max,
    'min': min, 'next': next, 'oct': oct, 'ord': ord, 'pow': pow,
    'print': print, 'range': range, 'repr': repr, 'reversed': reversed,
    'round': round, 'set': set, 'slice': slice, 'sorted': sorted,
    'str': str, 'sum': sum, 'tuple': tuple, 'type': type, 'zip': zip,
    # Math essentials
    'True': True, 'False': False, 'None': None,
}

# Safe modules that can be imported
ALLOWED_MODULES = {'math', 'random', 'datetime', 'json', 're', 'statistics', 'itertools', 'functools', 'collections'}

class CodeSandbox:
    """
    Executes Python code in a restricted environment.
    Prevents file I/O, network access, and dangerous operations.
    """
    def __init__(self, timeout_seconds=5):
        self.timeout = timeout_seconds
        
    def execute(self, code: str) -> str:
        """
        Execute Python code safely and return the output.
        """
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Create restricted globals
        restricted_globals = {
            '__builtins__': SAFE_BUILTINS,
            '__name__': '__main__',
        }
        
        # Pre-import allowed modules
        for mod_name in ALLOWED_MODULES:
            try:
                restricted_globals[mod_name] = __import__(mod_name)
            except ImportError:
                pass
        
        try:
            # Redirect stdout/stderr
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, restricted_globals, {})
            
            output = stdout_capture.getvalue()
            errors = stderr_capture.getvalue()
            
            if errors:
                return f"Output:\n{output}\n\nWarnings:\n{errors}"
            return output if output else "[Code executed successfully, no output]"
            
        except Exception as e:
            return f"Error: {type(e).__name__}: {str(e)}"
        
# Tool wrapper for the registry
class PythonTool:
    name = "run_python"
    description = "Execute Python code to solve math problems, analyze data, or perform calculations. Input: valid Python code as a string."
    
    def __init__(self):
        self.sandbox = CodeSandbox()
    
    def execute(self, code: str) -> str:
        """Execute Python code and return the result."""
        # Clean input
        code = code.strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        code = code.strip()
        
        return self.sandbox.execute(code)
