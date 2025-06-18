"""
Interactive setup wizard for the God-Tier Coding Agent
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import requests

from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn

class SetupWizard:
    """Interactive setup wizard"""
    
    def __init__(self):
        self.console = Console()
        self.config = {}
        self.config_file = Path("config.json")
        
    def run(self):
        """Run the complete setup wizard"""
        
        self.console.print(Panel(
            "[bold cyan]🛠️ God-Tier Coding Agent Setup Wizard[/bold cyan]\n"
            "Let's configure your ultimate coding assistant!",
            border_style="cyan"
        ))
        
        # Check existing config
        if self.config_file.exists():
            if Confirm.ask("Found existing configuration. Update it?"):
                self.load_config()
        
        # Setup steps
        self.setup_models()
        self.setup_preferences()
        self.setup_integrations()
        self.setup_advanced_features()
        
        # Save configuration
        self.save_config()
        
        # Final setup
        self.finalize_setup()
        
        self.console.print(Panel(
            "[bold green]✅ Setup Complete![/bold green]\n"
            "Your God-Tier Coding Agent is ready to use!\n\n"
            "[bold]Quick Start:[/bold]\n"
            "• Web UI: [cyan]python main.py web[/cyan]\n"
            "• Enhanced CLI: [cyan]python main.py chat[/cyan]\n"
            "• Code Analysis: [cyan]python main.py analyze <file>[/cyan]",
            border_style="green"
        ))
    
    def setup_models(self):
        """Setup AI models"""
        
        self.console.print("\n[bold cyan]🤖 AI Model Configuration[/bold cyan]")
        
        # Check for existing models
        model_files = list(Path(".").glob("*.gguf"))
        
        if model_files:
            self.console.print(f"[green]Found {len(model_files)} model file(s):[/green]")
            for model in model_files:
                size_mb = model.stat().st_size / (1024 * 1024)
                self.console.print(f"  • {model.name} ({size_mb:.1f} MB)")
            
            if Confirm.ask("Use existing model files?"):
                self.config["model_path"] = str(model_files[0])
                return
        
        # Download models
        self.console.print("\n[yellow]No models found. Let's download one![/yellow]")
        
        models = {
            "1": ("DeepSeek Coder 1.3B (Recommended)", "deepseek-coder-1.3b-instruct.Q4_K_M.gguf", 
                  "https://huggingface.co/TheBloke/deepseek-coder-1.3B-instruct-GGUF/resolve/main/deepseek-coder-1.3b-instruct.Q4_K_M.gguf"),
            "2": ("CodeLlama 7B (More Powerful)", "codellama-7b-instruct.Q4_K_M.gguf",
                  "https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF/resolve/main/codellama-7b-instruct.Q4_K_M.gguf"),
            "3": ("Qwen Coder 1.5B (Fast)", "qwen2.5-coder-1.5b-instruct.Q4_K_M.gguf",
                  "https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct.Q4_K_M.gguf")
        }
        
        table = Table(title="Available Models")
        table.add_column("Option", style="bold cyan")
        table.add_column("Model", style="green")
        table.add_column("Description", style="yellow")
        
        for key, (name, filename, url) in models.items():
            table.add_row(key, name, f"File: {filename}")
        
        self.console.print(table)
        
        choice = Prompt.ask("Select model to download", choices=list(models.keys()), default="1")
        
        if choice in models:
            name, filename, url = models[choice]
            self.download_model(url, filename)
            self.config["model_path"] = filename
    
    def download_model(self, url: str, filename: str):
        """Download model with progress bar"""
        
        self.console.print(f"[cyan]Downloading {filename}...[/cyan]")
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                console=self.console
            ) as progress:
                
                task = progress.add_task(f"Downloading {filename}", total=total_size)
                
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        progress.update(task, advance=len(chunk))
            
            self.console.print(f"[green]✅ Downloaded {filename}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Download failed: {e}[/red]")
            self.console.print("[yellow]You can download manually from:[/yellow]")
            self.console.print(f"[blue]{url}[/blue]")
    
    def setup_preferences(self):
        """Setup user preferences"""
        
        self.console.print("\n[bold cyan]⚙️ Preferences Configuration[/bold cyan]")
        
        # Model parameters
        self.config["max_tokens"] = IntPrompt.ask("Maximum tokens per response", default=1024)
        self.config["temperature"] = float(Prompt.ask("Temperature (creativity)", default="0.7"))
        self.config["context_window"] = IntPrompt.ask("Context window size", default=2048)
        
        # UI preferences
        self.config["theme"] = Prompt.ask("Preferred theme", choices=["dark", "light"], default="dark")
        self.config["auto_open_browser"] = Confirm.ask("Auto-open browser for web UI?", default=True)
        
        # Code preferences
        self.config["default_language"] = Prompt.ask("Default programming language", default="python")
        self.config["code_style"] = Prompt.ask("Code style", choices=["compact", "verbose"], default="verbose")
    
    def setup_integrations(self):
        """Setup integrations"""
        
        self.console.print("\n[bold cyan]🔗 Integrations Setup[/bold cyan]")
        
        integrations = {}
        
        # Git integration
        if Confirm.ask("Enable Git integration?", default=True):
            integrations["git"] = {
                "enabled": True,
                "auto_commit": Confirm.ask("Auto-commit generated code?", default=False)
            }
        
        # VS Code integration
        if Confirm.ask("Enable VS Code integration?", default=True):
            integrations["vscode"] = {
                "enabled": True,
                "auto_format": Confirm.ask("Auto-format code?", default=True)
            }
        
        # Database integration
        if Confirm.ask("Enable database integration?", default=False):
            integrations["database"] = {
                "enabled": True,
                "type": Prompt.ask("Database type", choices=["sqlite", "postgresql", "mysql"], default="sqlite")
            }
        
        self.config["integrations"] = integrations
    
    def setup_advanced_features(self):
        """Setup advanced features"""
        
        self.console.print("\n[bold cyan]🚀 Advanced Features[/bold cyan]")
        
        features = {}
        
        # Code analysis
        features["deep_analysis"] = Confirm.ask("Enable deep code analysis?", default=True)
        features["security_scanning"] = Confirm.ask("Enable security scanning?", default=True)
        features["performance_profiling"] = Confirm.ask("Enable performance profiling?", default=False)
        
        # AI features
        features["code_completion"] = Confirm.ask("Enable AI code completion?", default=True)
        features["auto_documentation"] = Confirm.ask("Enable auto-documentation?", default=True)
        features["test_generation"] = Confirm.ask("Enable test generation?", default=True)
        
        # Experimental features
        if Confirm.ask("Enable experimental features?", default=False):
            features["voice_coding"] = Confirm.ask("Enable voice coding?", default=False)
            features["code_visualization"] = Confirm.ask("Enable code visualization?", default=False)
            features["ai_pair_programming"] = Confirm.ask("Enable AI pair programming?", default=False)
        
        self.config["features"] = features
    
    def load_config(self):
        """Load existing configuration"""
        
        try:
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
            self.console.print("[green]✅ Loaded existing configuration[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Failed to load config: {e}[/red]")
    
    def save_config(self):
        """Save configuration to file"""
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            self.console.print(f"[green]✅ Configuration saved to {self.config_file}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Failed to save config: {e}[/red]")
    
    def finalize_setup(self):
        """Finalize the setup"""
        
        self.console.print("\n[bold cyan]🔧 Finalizing Setup[/bold cyan]")
        
        # Create necessary directories
        directories = ["uploads", "logs", "cache", "projects"]
        for dir_name in directories:
            Path(dir_name).mkdir(exist_ok=True)
        
        # Initialize database if needed
        if self.config.get("integrations", {}).get("database", {}).get("enabled"):
            self.setup_database()
        
        # Install additional dependencies if needed
        if Confirm.ask("Install additional Python packages?", default=True):
            self.install_dependencies()
    
    def setup_database(self):
        """Setup database"""
        
        self.console.print("[cyan]Setting up database...[/cyan]")
        
        db_type = self.config["integrations"]["database"]["type"]
        
        if db_type == "sqlite":
            # Create SQLite database
            import sqlite3
            conn = sqlite3.connect("godtier_agent.db")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    user_message TEXT,
                    ai_response TEXT
                )
            """)
            conn.commit()
            conn.close()
            self.console.print("[green]✅ SQLite database created[/green]")
    
    def install_dependencies(self):
        """Install additional dependencies"""
        
        optional_packages = []
        
        # Add packages based on enabled features
        if self.config.get("features", {}).get("voice_coding"):
            optional_packages.extend(["speechrecognition", "pyaudio", "pyttsx3"])
        
        if self.config.get("features", {}).get("code_visualization"):
            optional_packages.extend(["matplotlib", "plotly", "graphviz"])
        
        if self.config.get("integrations", {}).get("database", {}).get("type") == "postgresql":
            optional_packages.append("psycopg2-binary")
        elif self.config.get("integrations", {}).get("database", {}).get("type") == "mysql":
            optional_packages.append("pymysql")
        
        if optional_packages:
            self.console.print(f"[cyan]Installing {len(optional_packages)} additional packages...[/cyan]")
            
            for package in optional_packages:
                try:
                    subprocess.check_call(["pip", "install", package], 
                                        stdout=subprocess.DEVNULL, 
                                        stderr=subprocess.DEVNULL)
                    self.console.print(f"[green]✅ Installed {package}[/green]")
                except subprocess.CalledProcessError:
                    self.console.print(f"[yellow]⚠️ Failed to install {package}[/yellow]") 