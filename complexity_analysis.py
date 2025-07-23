#!/usr/bin/env python3
import ast
import os
import re
from typing import List, Dict, Tuple
from collections import defaultdict

class ComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.imports = []
        self.current_function = None
        self.complexity_score = 0
        self.nesting_level = 0
        
    def visit_FunctionDef(self, node):
        func_info = {
            'name': node.name,
            'line_start': node.lineno,
            'line_end': node.end_lineno if hasattr(node, 'end_lineno') else None,
            'length': (node.end_lineno - node.lineno + 1) if hasattr(node, 'end_lineno') else 0,
            'has_docstring': ast.get_docstring(node) is not None,
            'complexity': 1,  # Start with 1 for the function itself
            'has_type_hints': False,
            'nested_structures': 0,
            'error_handling': 0,
        }
        
        # Check for type hints
        if node.returns or any(arg.annotation for arg in node.args.args):
            func_info['has_type_hints'] = True
            
        # Store current state
        old_function = self.current_function
        old_complexity = self.complexity_score
        old_nesting = self.nesting_level
        
        self.current_function = func_info
        self.complexity_score = 1
        self.nesting_level = 0
        
        # Visit function body
        self.generic_visit(node)
        
        func_info['complexity'] = self.complexity_score
        func_info['nested_structures'] = self.nesting_level
        self.functions.append(func_info)
        
        # Restore state
        self.current_function = old_function
        self.complexity_score = old_complexity
        self.nesting_level = old_nesting
        
    def visit_If(self, node):
        self.complexity_score += 1
        if hasattr(node, 'orelse') and node.orelse:
            self.complexity_score += len([n for n in node.orelse if isinstance(n, ast.If)])
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_While(self, node):
        self.complexity_score += 1
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_For(self, node):
        self.complexity_score += 1
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_Try(self, node):
        self.complexity_score += 1
        if self.current_function:
            self.current_function['error_handling'] += 1
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_ExceptHandler(self, node):
        self.complexity_score += 1
        self.generic_visit(node)
        
    def visit_With(self, node):
        self.complexity_score += 1
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
            
    def visit_ImportFrom(self, node):
        if node.module:
            for alias in node.names:
                self.imports.append(f"{node.module}.{alias.name}")
        else:
            for alias in node.names:
                self.imports.append(alias.name)

def analyze_file(file_path: str) -> Dict:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Count lines
        lines = content.split('\n')
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        # Parse AST
        tree = ast.parse(content)
        analyzer = ComplexityAnalyzer()
        analyzer.visit(tree)
        
        # Check for duplicate patterns
        duplicate_patterns = find_duplicate_patterns(content)
        
        return {
            'file_path': file_path,
            'total_lines': total_lines,
            'code_lines': code_lines,
            'functions': analyzer.functions,
            'imports': analyzer.imports,
            'duplicate_patterns': duplicate_patterns
        }
        
    except Exception as e:
        return {
            'file_path': file_path,
            'error': str(e),
            'total_lines': 0,
            'code_lines': 0,
            'functions': [],
            'imports': [],
            'duplicate_patterns': []
        }

def find_duplicate_patterns(content: str) -> List[str]:
    """Find potential duplicate patterns in code"""
    patterns = []
    
    # Look for repeated error handling patterns
    error_patterns = re.findall(r'except\s+\w+\s+as\s+\w+:(.*?)(?=\n\s*(?:except|else|finally|\S))', content, re.DOTALL)
    if len(error_patterns) > 1:
        # Check if similar error handling exists
        similar_patterns = defaultdict(int)
        for pattern in error_patterns:
            # Normalize the pattern
            normalized = re.sub(r'\s+', ' ', pattern.strip())
            if 'logging.error' in normalized or 'return func.HttpResponse' in normalized:
                similar_patterns[normalized] += 1
        
        for pattern, count in similar_patterns.items():
            if count > 1:
                patterns.append(f"Duplicate error handling pattern (appears {count} times)")
    
    # Look for repeated JSON response patterns
    json_responses = re.findall(r'return func\.HttpResponse\((.*?)\)', content, re.DOTALL)
    if len(set(json_responses)) < len(json_responses):
        patterns.append("Duplicate JSON response patterns")
    
    return patterns

def main():
    # Key files to analyze
    key_files = [
        '/home/joey/Projects/joey-bot/idea-guy/get_pricepoints/__init__.py',
        '/home/joey/Projects/joey-bot/idea-guy/execute_analysis/__init__.py', 
        '/home/joey/Projects/joey-bot/idea-guy/process_idea/__init__.py',
        '/home/joey/Projects/joey-bot/idea-guy/get_instructions/__init__.py',
        '/home/joey/Projects/joey-bot/idea-guy/read_sheet/__init__.py',
        '/home/joey/Projects/joey-bot/common/idea_guy/utils.py',
        '/home/joey/Projects/joey-bot/common/utils.py'
    ]
    
    print("# Codebase Complexity Analysis Report")
    print("=" * 50)
    
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"\n## Analysis of {file_path}")
            print("-" * 40)
            
            analysis = analyze_file(file_path)
            
            if 'error' in analysis:
                print(f"ERROR: {analysis['error']}")
                continue
                
            print(f"**Total Lines:** {analysis['total_lines']}")
            print(f"**Code Lines:** {analysis['code_lines']}")
            print(f"**Number of Functions:** {len(analysis['functions'])}")
            print(f"**Import Count:** {len(set(analysis['imports']))}")
            
            # Analyze functions
            print("\n### Function Analysis:")
            long_functions = []
            complex_functions = []
            no_docstring = []
            no_type_hints = []
            
            for func in analysis['functions']:
                if func['length'] > 30:
                    long_functions.append(func)
                if func['complexity'] > 10:
                    complex_functions.append(func) 
                if not func['has_docstring']:
                    no_docstring.append(func)
                if not func['has_type_hints']:
                    no_type_hints.append(func)
            
            if long_functions:
                print(f"\n**Long Functions (>30 lines):**")
                for func in long_functions:
                    print(f"  - `{func['name']}` (lines {func['line_start']}-{func['line_end']}, {func['length']} lines)")
            
            if complex_functions:
                print(f"\n**High Complexity Functions (>10 complexity):**")
                for func in complex_functions:
                    print(f"  - `{func['name']}` (complexity: {func['complexity']}, nesting: {func['nested_structures']})")
            
            if no_docstring:
                print(f"\n**Functions Missing Docstrings ({len(no_docstring)}):**")
                for func in no_docstring[:5]:  # Show first 5
                    print(f"  - `{func['name']}` (line {func['line_start']})")
                if len(no_docstring) > 5:
                    print(f"  - ... and {len(no_docstring) - 5} more")
            
            if no_type_hints:
                print(f"\n**Functions Missing Type Hints ({len(no_type_hints)}):**")
                for func in no_type_hints[:5]:  # Show first 5
                    print(f"  - `{func['name']}` (line {func['line_start']})")
                if len(no_type_hints) > 5:
                    print(f"  - ... and {len(no_type_hints) - 5} more")
                    
            # Import analysis
            external_imports = [imp for imp in set(analysis['imports']) if not imp.startswith('common')]
            print(f"\n### Import Dependencies:")
            print(f"**External Dependencies:** {len(external_imports)}")
            if external_imports:
                print(f"  - {', '.join(sorted(external_imports)[:10])}")
                if len(external_imports) > 10:
                    print(f"  - ... and {len(external_imports) - 10} more")
            
            # Duplicate patterns
            if analysis['duplicate_patterns']:
                print(f"\n### Code Duplication Issues:")
                for pattern in analysis['duplicate_patterns']:
                    print(f"  - {pattern}")
                    
        else:
            print(f"\n## {file_path} - FILE NOT FOUND")
    
    print("\n" + "=" * 50)
    print("Analysis Complete")

if __name__ == "__main__":
    main()