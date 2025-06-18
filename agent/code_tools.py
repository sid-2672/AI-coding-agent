"""
Code analysis and utility tools.
"""

import re
import ast
from typing import List, Dict, Optional, Tuple
from pathlib import Path

class CodeTools:
    """Utility class for code analysis and processing."""
    
    def __init__(self):
        self.language_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css',
            '.sql': 'sql',
            '.sh': 'bash',
            '.r': 'r',
            '.m': 'matlab'
        }
    
    def detect_language(self, file_path: str) -> str:
        """
        Detect programming language from file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected language
        """
        ext = Path(file_path).suffix.lower()
        return self.language_extensions.get(ext, 'text')
    
    def extract_imports(self, code: str, language: str = 'python') -> List[str]:
        """
        Extract import statements from code.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            List of import statements
        """
        if language == 'python':
            return self._extract_python_imports(code)
        elif language in ['javascript', 'typescript']:
            return self._extract_js_imports(code)
        else:
            return []
    
    def _extract_python_imports(self, code: str) -> List[str]:
        """Extract Python import statements."""
        imports = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(f"import {alias.name}")
                    else:
                        module = node.module or ""
                        names = [alias.name for alias in node.names]
                        imports.append(f"from {module} import {', '.join(names)}")
        except SyntaxError:
            # Fallback to regex for invalid syntax
            import_pattern = r'^(?:from\s+(\w+(?:\.\w+)*)\s+import\s+(.+)|import\s+(.+))'
            for line in code.split('\n'):
                match = re.match(import_pattern, line.strip())
                if match:
                    imports.append(line.strip())
        return imports
    
    def _extract_js_imports(self, code: str) -> List[str]:
        """Extract JavaScript/TypeScript import statements."""
        imports = []
        import_patterns = [
            r'import\s+.*?from\s+[\'"][^\'"]+[\'"];?',
            r'import\s+.*?;?',
            r'const\s+.*?=\s+require\s*\([\'"][^\'"]+[\'"]\);?',
            r'let\s+.*?=\s+require\s*\([\'"][^\'"]+[\'"]\);?',
            r'var\s+.*?=\s+require\s*\([\'"][^\'"]+[\'"]\);?'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, code, re.MULTILINE)
            imports.extend(matches)
        
        return imports
    
    def find_functions(self, code: str, language: str = 'python') -> List[Dict]:
        """
        Find function definitions in code.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            List of function information
        """
        if language == 'python':
            return self._find_python_functions(code)
        else:
            return []
    
    def _find_python_functions(self, code: str) -> List[Dict]:
        """Find Python function definitions."""
        functions = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node)
                    })
        except SyntaxError:
            # Fallback to regex for invalid syntax
            func_pattern = r'def\s+(\w+)\s*\(([^)]*)\):'
            for i, line in enumerate(code.split('\n'), 1):
                match = re.match(func_pattern, line.strip())
                if match:
                    functions.append({
                        'name': match.group(1),
                        'line': i,
                        'args': [arg.strip() for arg in match.group(2).split(',') if arg.strip()],
                        'docstring': None
                    })
        return functions
    
    def validate_syntax(self, code: str, language: str = 'python') -> Tuple[bool, Optional[str]]:
        """
        Validate code syntax.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if language == 'python':
            return self._validate_python_syntax(code)
        else:
            return True, None
    
    def _validate_python_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """Validate Python syntax."""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, str(e)
    
    def format_code(self, code: str, language: str = 'python') -> str:
        """
        Basic code formatting.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            Formatted code
        """
        if language == 'python':
            return self._format_python_code(code)
        else:
            return code
    
    def _format_python_code(self, code: str) -> str:
        """Basic Python code formatting."""
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Handle indentation
            if stripped.endswith(':'):
                formatted_lines.append('    ' * indent_level + stripped)
                indent_level += 1
            elif stripped in ['pass', 'break', 'continue', 'return']:
                formatted_lines.append('    ' * indent_level + stripped)
            elif stripped.startswith(('if ', 'elif ', 'else:', 'for ', 'while ', 'try:', 'except', 'finally:', 'with ', 'def ', 'class ')):
                formatted_lines.append('    ' * indent_level + stripped)
                if stripped.endswith(':'):
                    indent_level += 1
            else:
                formatted_lines.append('    ' * indent_level + stripped)
        
        return '\n'.join(formatted_lines)
    
    def extract_code_blocks(self, text: str) -> List[str]:
        """
        Extract code blocks from markdown or plain text.
        
        Args:
            text: Text containing code blocks
            
        Returns:
            List of code blocks
        """
        # Match code blocks with language specification
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        code_blocks = []
        for lang, code in matches:
            code_blocks.append(code.strip())
        
        return code_blocks
    
    def estimate_complexity(self, code: str, language: str = 'python') -> Dict:
        """
        Estimate code complexity metrics.
        
        Args:
            code: Source code
            language: Programming language
            
        Returns:
            Complexity metrics
        """
        lines = code.split('\n')
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        
        functions = self.find_functions(code, language)
        
        return {
            'total_lines': total_lines,
            'code_lines': code_lines,
            'comment_lines': comment_lines,
            'function_count': len(functions),
            'comment_ratio': comment_lines / max(code_lines, 1)
        } 