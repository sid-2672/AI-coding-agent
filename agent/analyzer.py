"""
Advanced code analyzer with AI-powered insights
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import json

from .model import CodeAssistant
from .code_tools import CodeTools

class CodeAnalyzer:
    """Advanced code analysis with AI insights"""
    
    def __init__(self, model_path: str):
        self.assistant = CodeAssistant(model_path)
        self.code_tools = CodeTools()
        
    def analyze_code(self, path: Path, deep_analysis: bool = False, generate_docs: bool = False, security_scan: bool = False) -> Dict[str, Any]:
        """Analyze code file or directory"""
        
        if path.is_file():
            return self.analyze_file(path, deep_analysis, generate_docs, security_scan)
        elif path.is_dir():
            return self.analyze_directory(path, deep_analysis, generate_docs, security_scan)
        else:
            raise ValueError(f"Path not found: {path}")
    
    def analyze_file(self, file_path: Path, deep_analysis: bool = False, generate_docs: bool = False, security_scan: bool = False) -> Dict[str, Any]:
        """Analyze a single file"""
        
        try:
            code = file_path.read_text(encoding='utf-8')
            language = self.code_tools.detect_language(str(file_path))
            
            results = {
                'file_path': str(file_path),
                'language': language,
                'file_size': file_path.stat().st_size,
                'line_count': len(code.split('\n'))
            }
            
            # Basic analysis
            results['complexity'] = self.code_tools.estimate_complexity(code, language)
            results['imports'] = self.code_tools.extract_imports(code, language)
            results['functions'] = self.code_tools.find_functions(code, language)
            
            # Syntax validation
            is_valid, error = self.code_tools.validate_syntax(code, language)
            results['syntax_valid'] = is_valid
            if not is_valid:
                results['syntax_error'] = error
            
            # Deep analysis with AI
            if deep_analysis:
                results['ai_insights'] = self.get_ai_insights(code, language)
                results['improvement_suggestions'] = self.get_improvement_suggestions(code, language)
            
            # Documentation generation
            if generate_docs:
                results['generated_docs'] = self.generate_documentation(code, language)
            
            # Security analysis
            if security_scan:
                results['security_issues'] = self.scan_security_issues(code, language)
            
            return results
            
        except Exception as e:
            return {'error': str(e), 'file_path': str(file_path)}
    
    def analyze_code_string(self, code: str, language: str = "python", deep_analysis: bool = False) -> Dict[str, Any]:
        """Analyze code from string"""
        
        results = {
            'language': language,
            'line_count': len(code.split('\n'))
        }
        
        # Basic analysis
        results['complexity'] = self.code_tools.estimate_complexity(code, language)
        results['imports'] = self.code_tools.extract_imports(code, language)
        results['functions'] = self.code_tools.find_functions(code, language)
        
        # Syntax validation
        is_valid, error = self.code_tools.validate_syntax(code, language)
        results['syntax_valid'] = is_valid
        if not is_valid:
            results['syntax_error'] = error
        
        # AI insights
        if deep_analysis:
            results['ai_insights'] = self.get_ai_insights(code, language)
        
        return results
    
    def analyze_directory(self, dir_path: Path, deep_analysis: bool = False, generate_docs: bool = False, security_scan: bool = False) -> Dict[str, Any]:
        """Analyze entire directory"""
        
        results = {
            'directory_path': str(dir_path),
            'files_analyzed': [],
            'summary': {}
        }
        
        total_files = 0
        total_lines = 0
        languages = {}
        issues = []
        
        # Analyze each code file
        for file_path in dir_path.rglob('*'):
            if file_path.is_file() and self.is_code_file(file_path):
                try:
                    file_results = self.analyze_file(file_path, deep_analysis, generate_docs, security_scan)
                    results['files_analyzed'].append(file_results)
                    
                    total_files += 1
                    total_lines += file_results.get('line_count', 0)
                    
                    lang = file_results.get('language', 'unknown')
                    languages[lang] = languages.get(lang, 0) + 1
                    
                    if not file_results.get('syntax_valid', True):
                        issues.append(f"{file_path}: {file_results.get('syntax_error', 'Syntax error')}")
                        
                except Exception as e:
                    issues.append(f"{file_path}: {str(e)}")
        
        # Create summary
        results['summary'] = {
            'total_files': total_files,
            'total_lines': total_lines,
            'languages': languages,
            'issues_found': len(issues),
            'issues': issues
        }
        
        return results
    
    def get_ai_insights(self, code: str, language: str) -> str:
        """Get AI-powered insights about the code"""
        
        prompt = f"""Analyze this {language} code and provide insights:

{code}

Please provide:
1. Code quality assessment
2. Potential issues or bugs
3. Performance considerations
4. Best practices suggestions
5. Overall architecture assessment

Be concise but thorough."""
        
        try:
            return self.assistant.generate_response(prompt)
        except Exception as e:
            return f"AI analysis failed: {str(e)}"
    
    def get_improvement_suggestions(self, code: str, language: str) -> str:
        """Get specific improvement suggestions"""
        
        prompt = f"""Review this {language} code and suggest specific improvements:

{code}

Focus on:
- Code structure and organization
- Performance optimizations
- Error handling
- Readability improvements
- Security considerations

Provide concrete, actionable suggestions."""
        
        try:
            return self.assistant.generate_response(prompt)
        except Exception as e:
            return f"Improvement analysis failed: {str(e)}"
    
    def generate_documentation(self, code: str, language: str) -> str:
        """Generate documentation for the code"""
        
        prompt = f"""Generate comprehensive documentation for this {language} code:

{code}

Include:
- Module/class/function descriptions
- Parameter documentation
- Return value descriptions
- Usage examples
- Any important notes or warnings

Format as markdown."""
        
        try:
            return self.assistant.generate_response(prompt)
        except Exception as e:
            return f"Documentation generation failed: {str(e)}"
    
    def scan_security_issues(self, code: str, language: str) -> List[str]:
        """Scan for potential security issues"""
        
        issues = []
        
        if language == 'python':
            # Common Python security issues
            security_patterns = [
                ('eval', 'Use of eval() can be dangerous'),
                ('exec', 'Use of exec() can be dangerous'),
                ('os.system', 'Use of os.system() can be vulnerable to injection'),
                ('subprocess.call', 'Check subprocess.call() for injection vulnerabilities'),
                ('pickle.loads', 'Pickle deserialization can be dangerous'),
                ('yaml.load', 'Use yaml.safe_load() instead of yaml.load()'),
                ('shell=True', 'subprocess with shell=True can be vulnerable'),
                ('input(', 'raw_input/input can be dangerous in Python 2'),
            ]
            
            for pattern, message in security_patterns:
                if pattern in code:
                    issues.append(message)
        
        # Add AI-powered security analysis
        try:
            ai_security_prompt = f"""Analyze this {language} code for security vulnerabilities:

{code}

Look for:
- SQL injection risks
- XSS vulnerabilities  
- Command injection
- Insecure random number generation
- Hardcoded credentials
- Unsafe file operations
- Input validation issues

List any security concerns found."""
            
            ai_security = self.assistant.generate_response(ai_security_prompt)
            if "No security issues" not in ai_security:
                issues.append(f"AI Security Analysis: {ai_security}")
                
        except Exception:
            pass
        
        return issues
    
    def is_code_file(self, file_path: Path) -> bool:
        """Check if file is a code file"""
        
        code_extensions = {
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.php', 
            '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.html', 
            '.css', '.sql', '.sh', '.r', '.m'
        }
        
        return file_path.suffix.lower() in code_extensions
    
    def display_results(self, results: Dict[str, Any]):
        """Display analysis results (used by CLI)"""
        
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel
        from rich.markdown import Markdown
        
        console = Console()
        
        if 'error' in results:
            console.print(f"[red]Error: {results['error']}[/red]")
            return
        
        # File info
        if 'file_path' in results:
            console.print(f"[bold cyan]📄 File: {results['file_path']}[/bold cyan]")
            console.print(f"[dim]Language: {results.get('language', 'unknown')} | Lines: {results.get('line_count', 0)}[/dim]\n")
        
        # Complexity metrics
        if 'complexity' in results:
            comp = results['complexity']
            table = Table(title="📊 Code Metrics")
            table.add_column("Metric", style="bold cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Total Lines", str(comp.get('total_lines', 0)))
            table.add_row("Code Lines", str(comp.get('code_lines', 0)))
            table.add_row("Comment Lines", str(comp.get('comment_lines', 0)))
            table.add_row("Functions", str(comp.get('function_count', 0)))
            table.add_row("Comment Ratio", f"{comp.get('comment_ratio', 0):.2%}")
            
            console.print(table)
        
        # Syntax validation
        if 'syntax_valid' in results:
            if results['syntax_valid']:
                console.print("[green]✅ Syntax: Valid[/green]")
            else:
                console.print(f"[red]❌ Syntax Error: {results.get('syntax_error', 'Unknown error')}[/red]")
        
        # AI Insights
        if 'ai_insights' in results:
            console.print(Panel(
                Markdown(results['ai_insights']),
                title="🧠 AI Insights",
                border_style="purple"
            ))
        
        # Security issues
        if 'security_issues' in results and results['security_issues']:
            console.print("\n[bold red]🔒 Security Issues Found:[/bold red]")
            for issue in results['security_issues']:
                console.print(f"[red]• {issue}[/red]")
        
        # Directory summary
        if 'summary' in results:
            summary = results['summary']
            console.print(f"\n[bold cyan]📁 Directory Summary:[/bold cyan]")
            console.print(f"Files: {summary['total_files']} | Lines: {summary['total_lines']:,}")
            console.print(f"Languages: {', '.join(summary['languages'].keys())}")
            
            if summary['issues']:
                console.print(f"\n[red]Issues found in {len(summary['issues'])} files[/red]") 