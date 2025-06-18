"""
Benchmark module for performance testing
"""

import time
import psutil
import json
from pathlib import Path
from typing import Dict, List, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from .model import CodeAssistant

class ModelBenchmark:
    """Benchmark model performance"""
    
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.console = Console()
        self.results = {}
        
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive benchmark suite"""
        
        self.console.print(Panel(
            "[bold cyan]⚡ God-Tier Coding Agent Benchmark Suite[/bold cyan]\n"
            f"Model: {Path(self.model_path).name}",
            border_style="cyan"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            
            # Benchmark tasks
            tasks = [
                ("Loading Model", self.benchmark_model_loading),
                ("Text Generation", self.benchmark_text_generation),
                ("Code Generation", self.benchmark_code_generation),
                ("Memory Usage", self.benchmark_memory_usage),
                ("CPU Performance", self.benchmark_cpu_performance),
                ("Response Quality", self.benchmark_response_quality)
            ]
            
            main_task = progress.add_task("Running benchmarks...", total=len(tasks))
            
            for task_name, task_func in tasks:
                progress.update(main_task, description=f"Running {task_name}...")
                self.results[task_name.lower().replace(' ', '_')] = task_func()
                progress.advance(main_task)
        
        return self.results
    
    def benchmark_model_loading(self) -> Dict[str, Any]:
        """Benchmark model loading time"""
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        try:
            assistant = CodeAssistant(self.model_path)
            load_time = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            return {
                "load_time": load_time,
                "memory_increase": end_memory - start_memory,
                "success": True
            }
        except Exception as e:
            return {
                "load_time": time.time() - start_time,
                "error": str(e),
                "success": False
            }
    
    def benchmark_text_generation(self) -> Dict[str, Any]:
        """Benchmark text generation performance"""
        
        test_prompts = [
            "Explain how Python functions work",
            "What is machine learning?",
            "Describe the benefits of using Git for version control",
            "How do you optimize database queries?",
            "What are the principles of clean code?"
        ]
        
        try:
            assistant = CodeAssistant(self.model_path, max_tokens=100)
            
            times = []
            token_counts = []
            
            for prompt in test_prompts:
                start_time = time.time()
                response = assistant.generate_response(prompt)
                generation_time = time.time() - start_time
                
                times.append(generation_time)
                token_counts.append(len(response.split()))
            
            return {
                "avg_time": sum(times) / len(times),
                "min_time": min(times),
                "max_time": max(times),
                "avg_tokens": sum(token_counts) / len(token_counts),
                "tokens_per_second": sum(token_counts) / sum(times),
                "success": True
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def benchmark_code_generation(self) -> Dict[str, Any]:
        """Benchmark code generation performance"""
        
        code_prompts = [
            "Create a Python function to calculate fibonacci numbers",
            "Write a JavaScript function to sort an array",
            "Generate a SQL query to find top 10 customers",
            "Create a Python class for a simple calculator",
            "Write a function to validate email addresses"
        ]
        
        try:
            assistant = CodeAssistant(self.model_path, max_tokens=300)
            
            times = []
            code_lengths = []
            
            for prompt in code_prompts:
                start_time = time.time()
                response = assistant.generate_code(prompt)
                generation_time = time.time() - start_time
                
                times.append(generation_time)
                code_lengths.append(len(response))
            
            return {
                "avg_time": sum(times) / len(times),
                "avg_code_length": sum(code_lengths) / len(code_lengths),
                "chars_per_second": sum(code_lengths) / sum(times),
                "success": True
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def benchmark_memory_usage(self) -> Dict[str, Any]:
        """Benchmark memory usage during operation"""
        
        try:
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            assistant = CodeAssistant(self.model_path)
            
            # Memory after loading
            loaded_memory = process.memory_info().rss / 1024 / 1024
            
            # Generate some responses to test memory usage
            test_prompts = [
                "Generate a Python function for sorting",
                "Explain object-oriented programming",
                "Create a web scraping script",
                "Write a database connection function",
                "Generate unit tests for a calculator"
            ]
            
            memory_samples = []
            
            for prompt in test_prompts:
                assistant.generate_response(prompt)
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)
            
            return {
                "initial_memory": initial_memory,
                "loaded_memory": loaded_memory,
                "peak_memory": max(memory_samples),
                "avg_memory": sum(memory_samples) / len(memory_samples),
                "memory_increase": loaded_memory - initial_memory,
                "success": True
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def benchmark_cpu_performance(self) -> Dict[str, Any]:
        """Benchmark CPU performance"""
        
        try:
            assistant = CodeAssistant(self.model_path)
            
            # Monitor CPU usage during generation
            cpu_samples = []
            
            def monitor_cpu():
                for _ in range(10):  # Sample for 10 seconds
                    cpu_samples.append(psutil.cpu_percent(interval=1))
            
            import threading
            
            # Start CPU monitoring
            cpu_thread = threading.Thread(target=monitor_cpu)
            cpu_thread.start()
            
            # Generate responses while monitoring
            start_time = time.time()
            for i in range(5):
                assistant.generate_response(f"Generate code example {i+1}")
            
            cpu_thread.join()
            total_time = time.time() - start_time
            
            return {
                "avg_cpu_usage": sum(cpu_samples) / len(cpu_samples),
                "peak_cpu_usage": max(cpu_samples),
                "total_time": total_time,
                "cpu_cores": psutil.cpu_count(),
                "cpu_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                "success": True
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def benchmark_response_quality(self) -> Dict[str, Any]:
        """Benchmark response quality (basic metrics)"""
        
        quality_prompts = [
            ("Explain Python functions", "function", "def"),
            ("Create a sorting algorithm", "sort", "algorithm"),
            ("Describe machine learning", "learning", "data"),
            ("Write a web scraper", "scrape", "request"),
            ("Generate unit tests", "test", "assert")
        ]
        
        try:
            assistant = CodeAssistant(self.model_path)
            
            quality_scores = []
            
            for prompt, keyword1, keyword2 in quality_prompts:
                response = assistant.generate_response(prompt)
                
                # Simple quality metrics
                score = 0
                
                # Check if response contains relevant keywords
                if keyword1.lower() in response.lower():
                    score += 1
                if keyword2.lower() in response.lower():
                    score += 1
                
                # Check response length (not too short, not too long)
                if 50 < len(response) < 1000:
                    score += 1
                
                # Check if response is coherent (basic check)
                if len(response.split()) > 10:
                    score += 1
                
                quality_scores.append(score / 4)  # Normalize to 0-1
            
            return {
                "avg_quality_score": sum(quality_scores) / len(quality_scores),
                "quality_scores": quality_scores,
                "success": True
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def display_results(self, results: Dict[str, Any]):
        """Display benchmark results"""
        
        self.console.print("\n[bold cyan]📊 Benchmark Results[/bold cyan]")
        
        # Model Loading
        if "loading_model" in results:
            loading = results["loading_model"]
            if loading.get("success"):
                table = Table(title="Model Loading Performance")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Load Time", f"{loading['load_time']:.2f} seconds")
                table.add_row("Memory Increase", f"{loading['memory_increase']:.1f} MB")
                
                self.console.print(table)
        
        # Text Generation
        if "text_generation" in results:
            text_gen = results["text_generation"]
            if text_gen.get("success"):
                table = Table(title="Text Generation Performance")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Avg Generation Time", f"{text_gen['avg_time']:.2f} seconds")
                table.add_row("Tokens per Second", f"{text_gen['tokens_per_second']:.1f}")
                table.add_row("Avg Tokens", f"{text_gen['avg_tokens']:.0f}")
                
                self.console.print(table)
        
        # Memory Usage
        if "memory_usage" in results:
            memory = results["memory_usage"]
            if memory.get("success"):
                table = Table(title="Memory Usage")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Initial Memory", f"{memory['initial_memory']:.1f} MB")
                table.add_row("Loaded Memory", f"{memory['loaded_memory']:.1f} MB")
                table.add_row("Peak Memory", f"{memory['peak_memory']:.1f} MB")
                table.add_row("Memory Increase", f"{memory['memory_increase']:.1f} MB")
                
                self.console.print(table)
        
        # CPU Performance
        if "cpu_performance" in results:
            cpu = results["cpu_performance"]
            if cpu.get("success"):
                table = Table(title="CPU Performance")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Avg CPU Usage", f"{cpu['avg_cpu_usage']:.1f}%")
                table.add_row("Peak CPU Usage", f"{cpu['peak_cpu_usage']:.1f}%")
                table.add_row("CPU Cores", str(cpu['cpu_cores']))
                
                self.console.print(table)
        
        # Response Quality
        if "response_quality" in results:
            quality = results["response_quality"]
            if quality.get("success"):
                table = Table(title="Response Quality")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("Avg Quality Score", f"{quality['avg_quality_score']:.2%}")
                
                self.console.print(table)
        
        # Save results
        self.save_results(results)
    
    def save_results(self, results: Dict[str, Any]):
        """Save benchmark results to file"""
        
        results_file = Path(f"benchmark_results_{int(time.time())}.json")
        
        try:
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.console.print(f"\n[green]✅ Results saved to {results_file}[/green]")
            
        except Exception as e:
            self.console.print(f"\n[red]❌ Failed to save results: {e}[/red]") 