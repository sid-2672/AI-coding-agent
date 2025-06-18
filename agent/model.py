"""
Model module for loading and using local LLM.
"""

import os
from pathlib import Path
from typing import Optional, List
from llama_cpp import Llama
from .code_tools import CodeTools

class CodeAssistant:
    """Main assistant class that handles model loading and text generation."""
    
    def __init__(
        self,
        model_path: str,
        max_tokens: int = 512,
        temperature: float = 0.7,
        n_ctx: int = 2048,
        n_threads: Optional[int] = None
    ):
        """
        Initialize the code assistant with a local LLM.
        
        Args:
            model_path: Path to GGUF model file
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            n_ctx: Context window size
            n_threads: Number of CPU threads (None for auto)
        """
        self.model_path = model_path
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.n_ctx = n_ctx
        
        # Auto-detect CPU threads if not specified
        if n_threads is None:
            import multiprocessing
            self.n_threads = multiprocessing.cpu_count()
        else:
            self.n_threads = n_threads
            
        self.model = self._load_model()
        self.code_tools = CodeTools()
        
    def _load_model(self) -> Llama:
        """Load the GGUF model."""
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
        try:
            print(f"Loading model: {self.model_path}")
            print(f"Using {self.n_threads} CPU threads")
            model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                verbose=False
            )
            print("Model loaded successfully!")
            return model
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {e}")
    
    def generate_response(self, prompt: str, context: str = "") -> str:
        """
        Generate a response for a general prompt.
        
        Args:
            prompt: User prompt
            context: Previous conversation context
            
        Returns:
            Generated response
        """
        system_prompt = """You are a helpful coding assistant. Provide clear, concise, and accurate responses.
Focus on practical solutions and best practices. If you're not sure about something, say so."""
        
        full_prompt = self._build_prompt(system_prompt, prompt, context)
        
        try:
            response = self.model(
                full_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stop=["</s>", "Human:", "Assistant:"],
                echo=False
            )
            
            return response['choices'][0]['text'].strip()
        except Exception as e:
            return f"Error generating response: {e}"
    
    def generate_code(self, prompt: str) -> str:
        """
        Generate code from a prompt.
        
        Args:
            prompt: Code generation prompt
            
        Returns:
            Generated code
        """
        system_prompt = """You are a coding assistant. Generate clean, well-documented code.
Always include necessary imports and follow best practices.
If the language isn't specified, assume Python."""
        
        full_prompt = self._build_prompt(system_prompt, prompt)
        
        try:
            response = self.model(
                full_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stop=["</s>", "Human:", "Assistant:"],
                echo=False
            )
            
            return response['choices'][0]['text'].strip()
        except Exception as e:
            return f"Error generating code: {e}"

    def generate_advanced_code(self, prompt: str, language: Optional[str] = None, template: Optional[str] = None) -> str:
        """
        Advanced code generation with language and template support.
        
        Args:
            prompt: Code generation prompt
            language: Target programming language
            template: Code template to use
            
        Returns:
            Generated code
        """
        
        # Build enhanced system prompt
        system_parts = ["You are an expert coding assistant. Generate high-quality, production-ready code."]
        
        if language:
            system_parts.append(f"Generate code in {language}.")
        else:
            system_parts.append("Auto-detect the best programming language for the task.")
        
        system_parts.extend([
            "Follow these principles:",
            "- Write clean, readable, and well-documented code",
            "- Include proper error handling where appropriate", 
            "- Follow language-specific best practices and conventions",
            "- Add helpful comments explaining complex logic",
            "- Include necessary imports and dependencies",
            "- Make the code modular and reusable when possible"
        ])
        
        if template:
            system_parts.append(f"Use this template structure: {template}")
        
        system_prompt = "\n".join(system_parts)
        
        # Enhanced prompt with context
        enhanced_prompt = f"""Code Generation Request:
{prompt}

Requirements:
- Language: {language if language else 'Auto-detect best fit'}
- Style: Production-ready with proper documentation
- Include: Imports, error handling, comments
- Format: Clean and well-structured

Generate the complete code:"""
        
        full_prompt = self._build_prompt(system_prompt, enhanced_prompt)
        
        try:
            response = self.model(
                full_prompt,
                max_tokens=min(self.max_tokens * 2, 2048),  # Allow more tokens for code
                temperature=max(self.temperature - 0.1, 0.1),  # Slightly lower temp for code
                stop=["</s>", "Human:", "Assistant:", "```\n\n"],
                echo=False
            )
            
            generated_code = response['choices'][0]['text'].strip()
            
            # Clean up the response
            if generated_code.startswith("```"):
                # Remove markdown code blocks
                lines = generated_code.split('\n')
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                generated_code = '\n'.join(lines)
            
            return generated_code
            
        except Exception as e:
            return f"Error generating advanced code: {e}"
    
    def explain_code(self, code: str, language: str = "python") -> str:
        """
        Explain code functionality.
        
        Args:
            code: Code to explain
            language: Programming language
            
        Returns:
            Code explanation
        """
        system_prompt = f"""You are a coding assistant. Explain the provided {language} code clearly and concisely.
Focus on what the code does, how it works, and any important patterns or concepts."""
        
        prompt = f"Please explain this {language} code:\n\n```{language}\n{code}\n```"
        full_prompt = self._build_prompt(system_prompt, prompt)
        
        try:
            response = self.model(
                full_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stop=["</s>", "Human:", "Assistant:"],
                echo=False
            )
            
            return response['choices'][0]['text'].strip()
        except Exception as e:
            return f"Error explaining code: {e}"
    
    def debug_code(self, code: str, language: str = "python", error_message: Optional[str] = None) -> str:
        """
        Debug code and provide fixes.
        
        Args:
            code: Code to debug
            language: Programming language
            error_message: Optional error message
            
        Returns:
            Debugging help and fixes
        """
        system_prompt = f"""You are a debugging assistant. Analyze the provided {language} code and identify issues.
Provide specific fixes and explanations. If an error message is provided, focus on that specific issue."""
        
        if error_message:
            prompt = f"Please debug this {language} code. Error: {error_message}\n\n```{language}\n{code}\n```"
        else:
            prompt = f"Please analyze this {language} code for potential issues:\n\n```{language}\n{code}\n```"
            
        full_prompt = self._build_prompt(system_prompt, prompt)
        
        try:
            response = self.model(
                full_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stop=["</s>", "Human:", "Assistant:"],
                echo=False
            )
            
            return response['choices'][0]['text'].strip()
        except Exception as e:
            return f"Error debugging code: {e}"
    
    def _build_prompt(self, system_prompt: str, user_prompt: str, context: str = "") -> str:
        """
        Build the full prompt with system message and context.
        
        Args:
            system_prompt: System instructions
            user_prompt: User input
            context: Previous conversation context
            
        Returns:
            Formatted prompt
        """
        prompt_parts = [f"<|im_start|>system\n{system_prompt}<|im_end|>"]
        
        if context:
            prompt_parts.append(f"<|im_start|>user\n{context}<|im_end|>")
            
        prompt_parts.append(f"<|im_start|>user\n{user_prompt}<|im_end|>")
        prompt_parts.append("<|im_start|>assistant\n")
        
        return "\n".join(prompt_parts) 