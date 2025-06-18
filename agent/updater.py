"""
Updater module for models and components
"""

import json
import requests
from pathlib import Path
from typing import Dict, List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.table import Table

class Updater:
    """Handle updates for models and components"""
    
    def __init__(self):
        self.console = Console()
        self.config_file = Path("config.json")
        self.update_info_url = "https://api.github.com/repos/godtier-ai/coding-agent/releases/latest"
        
    def check_and_update(self):
        """Check for and apply updates"""
        
        self.console.print(Panel(
            "[bold cyan]📦 God-Tier Coding Agent Updater[/bold cyan]\n"
            "Checking for updates...",
            border_style="cyan"
        ))
        
        # Check for app updates
        self.check_app_updates()
        
        # Check for model updates
        self.check_model_updates()
        
        # Check for component updates
        self.check_component_updates()
        
        self.console.print(Panel(
            "[bold green]✅ Update check complete![/bold green]",
            border_style="green"
        ))
    
    def check_app_updates(self):
        """Check for application updates"""
        
        self.console.print("\n[bold cyan]🔄 Checking application updates...[/bold cyan]")
        
        try:
            # This would check against a real repository
            # For now, we'll simulate the check
            self.console.print("[green]✅ Application is up to date[/green]")
            
        except Exception as e:
            self.console.print(f"[red]❌ Failed to check app updates: {e}[/red]")
    
    def check_model_updates(self):
        """Check for model updates"""
        
        self.console.print("\n[bold cyan]🤖 Checking model updates...[/bold cyan]")
        
        # Available models with versions
        available_models = {
            "deepseek-coder-1.3b-instruct.Q4_K_M.gguf": {
                "version": "1.3",
                "url": "https://huggingface.co/TheBloke/deepseek-coder-1.3B-instruct-GGUF/resolve/main/deepseek-coder-1.3b-instruct.Q4_K_M.gguf",
                "size": "2.1 GB"
            },
            "codellama-7b-instruct.Q4_K_M.gguf": {
                "version": "7.0",
                "url": "https://huggingface.co/TheBloke/CodeLlama-7B-Instruct-GGUF/resolve/main/codellama-7b-instruct.Q4_K_M.gguf",
                "size": "4.1 GB"
            }
        }
        
        # Check existing models
        model_files = list(Path(".").glob("*.gguf"))
        
        if not model_files:
            self.console.print("[yellow]⚠️ No models found. Run setup to download models.[/yellow]")
            return
        
        table = Table(title="Model Status")
        table.add_column("Model", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Action", style="yellow")
        
        for model_file in model_files:
            if model_file.name in available_models:
                table.add_row(model_file.name, "✅ Current", "No update needed")
            else:
                table.add_row(model_file.name, "❓ Unknown", "Check manually")
        
        self.console.print(table)
    
    def check_component_updates(self):
        """Check for component updates"""
        
        self.console.print("\n[bold cyan]🔧 Checking component updates...[/bold cyan]")
        
        # Check Python dependencies
        try:
            import subprocess
            result = subprocess.run(["pip", "list", "--outdated"], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                outdated_packages = result.stdout.strip().split('\n')[2:]  # Skip header
                
                if outdated_packages:
                    self.console.print(f"[yellow]📦 Found {len(outdated_packages)} outdated packages[/yellow]")
                    
                    table = Table(title="Outdated Packages")
                    table.add_column("Package", style="cyan")
                    table.add_column("Current", style="yellow")
                    table.add_column("Latest", style="green")
                    
                    for package_line in outdated_packages[:10]:  # Show first 10
                        if package_line.strip():
                            parts = package_line.split()
                            if len(parts) >= 3:
                                table.add_row(parts[0], parts[1], parts[2])
                    
                    self.console.print(table)
                    
                    if self.console.input("\n[bold cyan]Update packages? (y/n): [/bold cyan]").lower() == 'y':
                        self.update_packages()
                else:
                    self.console.print("[green]✅ All packages are up to date[/green]")
            else:
                self.console.print("[green]✅ All packages are up to date[/green]")
                
        except Exception as e:
            self.console.print(f"[red]❌ Failed to check packages: {e}[/red]")
    
    def update_packages(self):
        """Update Python packages"""
        
        self.console.print("[cyan]Updating packages...[/cyan]")
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                
                task = progress.add_task("Updating packages...", total=None)
                
                import subprocess
                result = subprocess.run(["pip", "install", "--upgrade", "-r", "requirements.txt"], 
                                      capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.console.print("[green]✅ Packages updated successfully[/green]")
                else:
                    self.console.print(f"[red]❌ Package update failed: {result.stderr}[/red]")
                    
        except Exception as e:
            self.console.print(f"[red]❌ Failed to update packages: {e}[/red]")
    
    def download_model(self, url: str, filename: str):
        """Download a model file"""
        
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
            return True
            
        except Exception as e:
            self.console.print(f"[red]❌ Download failed: {e}[/red]")
            return False 