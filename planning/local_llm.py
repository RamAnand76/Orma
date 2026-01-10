import os
import sys
import config
from rich.console import Console

console = Console()

class LocalLLM:
    """
    Adapter for running local GGUF models via llama-cpp-python.
    Supports Lazy Loading to save RAM until needed.
    """
    def __init__(self):
        self.model = None
        self.path = config.LOCAL_MODEL_PATH
        self.params = config.LOCAL_MODEL_PARAMS
        
    def _load_model(self):
        """Loads the model into memory. This is heavy."""
        try:
            from llama_cpp import Llama
        except ImportError:
            console.print("[bold red]❌ Error: `llama-cpp-python` not installed.[/bold red]")
            console.print("Run: `pip install llama-cpp-python`")
            return False

        if not os.path.exists(self.path):
            console.print(f"[bold red]❌ Error: Model not found at {self.path}[/bold red]")
            return False

        console.print(f"[bold yellow]🧠 Loading Local Brain ({os.path.basename(self.path)})...[/bold yellow]")
        # Force flush to ensure user sees message before freeze
        sys.stdout.flush() 
        try:
            self.model = Llama(
                model_path=self.path,
                n_ctx=self.params["n_ctx"],
                n_gpu_layers=self.params["n_gpu_layers"],
                verbose=self.params["verbose"]
            )
            console.print("[bold green]✅ Local Brain Loaded.[/bold green]")
            return True
        except Exception as e:
            console.print(f"[bold red]❌ Failed to load model: {e}[/bold red]")
            return False

    def generate(self, system_prompt, user_input):
        """
        Generates text using the local model.
        Handles auto-loading and Qwen3 formatting.
        """
        if self.model is None:
            success = self._load_model()
            if not success:
                return "Error: Local Brain failed to load."

        # Qwen3 uses ChatML format
        full_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{user_input}<|im_end|>\n<|im_start|>assistant\n"
        
        try:
            output = self.model(
                full_prompt,
                max_tokens=1024,
                stop=["<|im_end|>", "User:", "<|im_start|>"],
                echo=False,
                temperature=config.GENERATION_TEMPERATURE
            )
            return output['choices'][0]['text'].strip()
        except Exception as e:
            return f"Error Generating Local Response: {e}"
