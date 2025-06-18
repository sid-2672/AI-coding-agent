#!/usr/bin/env python3
"""
God-Tier Offline Coding Agent - The Ultimate Local AI Developer Assistant
"""

import typer
import uvicorn
import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from typing import Optional

from agent.model import CodeAssistant
from agent.memory import ConversationMemory
from agent.web_server import create_app
from agent.cli_interface import CLIInterface

app = typer.Typer(
    help="🚀 God-Tier Offline Coding Agent - The Ultimate AI Developer Assistant",
    rich_markup_mode="rich"
)
console = Console()

@app.command()
def web(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    model_path: str = typer.Option(
        "deepseek-coder-1.3b-instruct.Q4_K_M.gguf",
        "--model", "-m",
        help="Path to GGUF model file"
    ),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload for development"),
    open_browser: bool = typer.Option(True, "--open-browser", help="Open browser automatically")
):
    """🌐 Launch the beautiful web interface"""
    
    console.print(Panel.fit(
        "[bold cyan]🚀 God-Tier Coding Agent - Web Interface[/bold cyan]\n"
        f"🌐 Server: http://{host}:{port}\n"
        f"🤖 Model: {Path(model_path).name}\n"
        f"🔄 Auto-reload: {'✅' if reload else '❌'}\n"
        "\n[bold green]Features:[/bold green]\n"
        "• 🎨 Beautiful Modern UI\n"
        "• 💬 Real-time Chat Interface\n"
        "• 📝 Advanced Code Editor\n"
        "• 🗂️ File Management\n"
        "• 🔧 Developer Tools Integration\n"
        "• 🎯 AI Pair Programming\n"
        "• 📊 Code Analysis & Visualization",
        border_style="cyan"
    ))
    
    # Create FastAPI app with the model
    fastapi_app = create_app(model_path)
    
    if open_browser:
        import webbrowser
        webbrowser.open(f"http://{host}:{port}")
    
    # Run the server
    uvicorn.run(
        fastapi_app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

@app.command()
def chat(
    model_path: str = typer.Option(
        "deepseek-coder-1.3b-instruct.Q4_K_M.gguf",
        "--model", "-m",
        help="Path to GGUF model file"
    ),
    max_tokens: int = typer.Option(
        1024,
        "--max-tokens", "-t",
        help="Maximum tokens to generate"
    ),
    temperature: float = typer.Option(
        0.7,
        "--temperature", "-temp",
        help="Sampling temperature (0.0-1.0)"
    ),
    enhanced_mode: bool = typer.Option(
        True,
        "--enhanced/--basic",
        help="Enable enhanced CLI mode with advanced features"
    )
):
    """💬 Enhanced interactive chat with the coding assistant"""
    
    if enhanced_mode:
        cli = CLIInterface(model_path, max_tokens, temperature)
        cli.run_enhanced_chat()
    else:
        # Legacy basic chat mode
        try:
            if not Path(model_path).exists():
                console.print(f"[red]❌ Model file not found: {model_path}[/red]")
                raise typer.Exit(1)
            
            assistant = CodeAssistant(model_path, max_tokens, temperature)
            memory = ConversationMemory()
            
            console.print(Panel.fit(
                "[bold green]🤖 Basic Chat Mode[/bold green]\n"
                f"Model: {Path(model_path).name}\n"
                "Type 'quit' to exit",
                border_style="blue"
            ))
            
            while True:
                try:
                    prompt = typer.prompt("\nYou")
                    if prompt.lower() in ['quit', 'exit', 'q']:
                        break
                    
                    console.print("\n🤖 Assistant:")
                    with console.status("[bold green]Thinking..."):
                        response = assistant.generate_response(prompt, memory.get_context())
                        memory.add_exchange(prompt, response)
                        console.print(response)
                        
                except KeyboardInterrupt:
                    console.print("\n[yellow]Use 'quit' to exit[/yellow]")
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                    
        except Exception as e:
            console.print(f"[red]Failed to initialize assistant: {e}[/red]")
            raise typer.Exit(1)

@app.command()
def code(
    prompt: str = typer.Argument(..., help="Code generation prompt"),
    model_path: str = typer.Option(
        "deepseek-coder-1.3b-instruct.Q4_K_M.gguf",
        "--model", "-m",
        help="Path to GGUF model file"
    ),
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="Programming language"),
    output_file: Optional[str] = typer.Option(None, "--output", "-o", help="Save to file"),
    template: Optional[str] = typer.Option(None, "--template", "-t", help="Use code template")
):
    """⚡ Advanced code generation with templates and language detection"""
    
    try:
        assistant = CodeAssistant(model_path)
        
        console.print(f"[bold cyan]Generating code:[/bold cyan] {prompt}")
        if language:
            console.print(f"[blue]Language:[/blue] {language}")
        
        with console.status("[bold green]🧠 AI is crafting your code..."):
            response = assistant.generate_advanced_code(
                prompt, 
                language=language, 
                template=template
            )
        
        console.print("\n[bold green]✨ Generated Code:[/bold green]")
        console.print(response)
        
        if output_file:
            Path(output_file).write_text(response)
            console.print(f"\n[green]💾 Saved to: {output_file}[/green]")
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command() 
def analyze(
    path: str = typer.Argument(..., help="File or directory to analyze"),
    model_path: str = typer.Option(
        "deepseek-coder-1.3b-instruct.Q4_K_M.gguf",
        "--model", "-m",
        help="Path to GGUF model file"
    ),
    deep_analysis: bool = typer.Option(False, "--deep", help="Enable deep AI analysis"),
    generate_docs: bool = typer.Option(False, "--docs", help="Generate documentation"),
    security_scan: bool = typer.Option(False, "--security", help="Run security analysis")
):
    """🔍 Advanced code analysis and insights"""
    
    try:
        from agent.analyzer import CodeAnalyzer
        
        analyzer = CodeAnalyzer(model_path)
        target_path = Path(path)
        
        if not target_path.exists():
            console.print(f"[red]❌ Path not found: {path}[/red]")
            raise typer.Exit(1)
        
        console.print(f"[bold cyan]🔍 Analyzing:[/bold cyan] {path}")
        
        with console.status("[bold green]🧠 AI is analyzing your code..."):
            results = analyzer.analyze_code(
                target_path,
                deep_analysis=deep_analysis,
                generate_docs=generate_docs,
                security_scan=security_scan
            )
        
        analyzer.display_results(results)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command()
def setup():
    """🛠️ Interactive setup and configuration"""
    
    console.print(Panel.fit(
        "[bold cyan]🛠️ God-Tier Coding Agent Setup[/bold cyan]\n"
        "Let's configure your ultimate coding assistant!",
        border_style="cyan"
    ))
    
    from agent.setup_wizard import SetupWizard
    wizard = SetupWizard()
    wizard.run()

@app.command()
def update():
    """📦 Update models and components"""
    
    console.print("[bold cyan]📦 Checking for updates...[/bold cyan]")
    from agent.updater import Updater
    updater = Updater()
    updater.check_and_update()

@app.command()
def benchmark(
    model_path: str = typer.Option(
        "deepseek-coder-1.3b-instruct.Q4_K_M.gguf",
        "--model", "-m",
        help="Path to GGUF model file"
    )
):
    """⚡ Benchmark model performance"""
    
    console.print("[bold cyan]⚡ Running performance benchmark...[/bold cyan]")
    from agent.benchmark import ModelBenchmark
    
    benchmark = ModelBenchmark(model_path)
    results = benchmark.run_comprehensive_benchmark()
    benchmark.display_results(results)

if __name__ == "__main__":
    app() 