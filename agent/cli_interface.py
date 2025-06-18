"""
Enhanced CLI interface for the God-Tier Coding Agent
"""

from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn

from .model import CodeAssistant
from .memory import ConversationMemory
from .analyzer import CodeAnalyzer

class CLIInterface:
    """Enhanced CLI interface with advanced features"""
    
    def __init__(self, model_path: str, max_tokens: int = 1024, temperature: float = 0.7):
        self.console = Console()
        self.assistant = CodeAssistant(model_path, max_tokens, temperature)
        self.memory = ConversationMemory()
        self.analyzer = CodeAnalyzer(model_path)
        
    def run_enhanced_chat(self):
        """Run the enhanced chat interface"""
        self.show_welcome_screen()
        
        while True:
            try:
                command = Prompt.ask("\n[bold cyan]You[/bold cyan]", console=self.console)
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command.startswith('/'):
                    self.handle_command(command)
                else:
                    self.handle_chat_message(command)
                    
            except KeyboardInterrupt:
                if Confirm.ask("\n[yellow]Do you want to exit?[/yellow]"):
                    break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
    
    def show_welcome_screen(self):
        """Show enhanced welcome screen"""
        welcome_text = """[bold cyan]🚀 God-Tier Coding Agent - Enhanced CLI[/bold cyan]

[bold green]Commands:[/bold green]
• /help - Show help    • /analyze <file> - Analyze code
• /generate <prompt> - Generate code    • /stats - Statistics
• /files - File browser    • /save - Save conversation"""
        
        self.console.print(Panel(welcome_text, title="Welcome", border_style="cyan"))
    
    def handle_command(self, command: str):
        """Handle special commands"""
        parts = command[1:].split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        if cmd == "help":
            self.show_help()
        elif cmd == "analyze":
            self.analyze_file(args[0] if args else None)
        elif cmd == "generate":
            self.generate_code(" ".join(args))
        elif cmd == "files":
            self.file_browser()
        elif cmd == "stats":
            self.show_statistics()
        elif cmd == "save":
            self.save_conversation()
        else:
            self.console.print(f"[red]Unknown command: {cmd}[/red]")
    
    def handle_chat_message(self, message: str):
        """Handle regular chat messages"""
        with self.console.status("[bold green]🤖 AI is thinking..."):
            response = self.assistant.generate_response(message, self.memory.get_context())
            self.memory.add_exchange(message, response)
        
        self.display_ai_response(response)
    
    def display_ai_response(self, response: str):
        """Display AI response with formatting"""
        if "```" in response:
            parts = response.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 0 and part.strip():
                    self.console.print(Markdown(part))
                elif i % 2 == 1 and part.strip():
                    lines = part.split('\n')
                    language = lines[0].strip() if lines else "python"
                    code = '\n'.join(lines[1:]) if len(lines) > 1 else part
                    if code.strip():
                        syntax = Syntax(code, language, theme="monokai")
                        self.console.print(Panel(syntax, title=f"Code ({language})", border_style="green"))
        else:
            self.console.print(Panel(Markdown(response), title="🤖 AI Assistant", border_style="blue"))
    
    def analyze_file(self, file_path: Optional[str]):
        """Analyze a code file"""
        if not file_path:
            file_path = Prompt.ask("Enter file path to analyze")
        
        if not Path(file_path).exists():
            self.console.print(f"[red]File not found: {file_path}[/red]")
            return
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=self.console) as progress:
            progress.add_task("Analyzing code...", total=None)
            try:
                results = self.analyzer.analyze_code(Path(file_path))
                self.display_analysis_results(results, file_path)
            except Exception as e:
                self.console.print(f"[red]Analysis failed: {e}[/red]")
    
    def display_analysis_results(self, results: dict, file_path: str):
        """Display analysis results"""
        table = Table(title=f"📊 Analysis: {file_path}")
        table.add_column("Metric", style="bold cyan")
        table.add_column("Value", style="green")
        
        if "complexity" in results:
            comp = results["complexity"]
            table.add_row("Lines of Code", str(comp.get("code_lines", 0)))
            table.add_row("Functions", str(comp.get("function_count", 0)))
            table.add_row("Comment Ratio", f"{comp.get('comment_ratio', 0):.2%}")
        
        self.console.print(table)
        
        if "ai_insights" in results:
            self.console.print(Panel(Markdown(results["ai_insights"]), title="🧠 AI Insights", border_style="purple"))
    
    def generate_code(self, prompt: str):
        """Generate code from prompt"""
        if not prompt:
            prompt = Prompt.ask("What code would you like me to generate?")
        
        with self.console.status("[bold green]🧠 AI is crafting code..."):
            try:
                response = self.assistant.generate_advanced_code(prompt)
                syntax = Syntax(response, "python", theme="monokai", line_numbers=True)
                self.console.print(Panel(syntax, title="✨ Generated Code", border_style="green"))
                
                if Confirm.ask("Save this code to a file?"):
                    filename = Prompt.ask("Enter filename", default="generated_code.py")
                    Path(filename).write_text(response)
                    self.console.print(f"[green]✅ Saved to {filename}[/green]")
            except Exception as e:
                self.console.print(f"[red]Generation failed: {e}[/red]")
    
    def file_browser(self):
        """Simple file browser"""
        current_dir = Path.cwd()
        files = list(current_dir.iterdir())
        
        table = Table(title=f"📁 Files in {current_dir.name}")
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Size", style="yellow")
        
        for item in sorted(files)[:20]:  # Limit to 20 items
            if item.is_dir():
                table.add_row(f"📁 {item.name}", "Directory", "-")
            else:
                size = item.stat().st_size
                table.add_row(f"📄 {item.name}", "File", f"{size:,} bytes")
        
        self.console.print(table)
    
    def show_statistics(self):
        """Show statistics"""
        stats = self.memory.get_statistics()
        
        table = Table(title="📊 Statistics")
        table.add_column("Metric", style="bold cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Messages", str(stats['total_exchanges']))
        table.add_row("User Characters", f"{stats['total_user_chars']:,}")
        table.add_row("AI Characters", f"{stats['total_assistant_chars']:,}")
        
        self.console.print(table)
    
    def show_help(self):
        """Show help"""
        help_text = """[bold cyan]Command Reference[/bold cyan]

[bold green]Chat Commands:[/bold green]
• /help - Show this help
• /save - Save conversation
• /stats - Show statistics

[bold green]Code Commands:[/bold green]
• /analyze <file> - Analyze code
• /generate <prompt> - Generate code
• /files - Browse files"""
        
        self.console.print(Panel(help_text, border_style="cyan"))
    
    def save_conversation(self):
        """Save conversation"""
        filename = Prompt.ask("Enter filename", default="conversation.json")
        self.memory.save_conversation(filename)
        self.console.print(f"[green]✅ Saved to {filename}[/green]") 