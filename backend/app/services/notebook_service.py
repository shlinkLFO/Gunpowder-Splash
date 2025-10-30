"""
Jupyter Notebook Service
Handles parsing, executing, and managing .ipynb files
"""

import json
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, List, Any
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Per-session execution contexts
# Key format: "filepath:session_id" or just "filepath" for single-user demo
_notebook_contexts: Dict[str, Dict[str, Any]] = {}
_context_last_used: Dict[str, datetime] = {}

# Cleanup old contexts after 1 hour of inactivity
CONTEXT_TIMEOUT = timedelta(hours=1)


def _get_context_key(filepath: str, session_id: str = "default") -> str:
    """Generate a unique context key for this notebook session"""
    return f"{filepath}:{session_id}"


def _cleanup_old_contexts():
    """Remove contexts that haven't been used recently"""
    now = datetime.now()
    to_remove = []
    for key, last_used in _context_last_used.items():
        if now - last_used > CONTEXT_TIMEOUT:
            to_remove.append(key)
    
    for key in to_remove:
        _notebook_contexts.pop(key, None)
        _context_last_used.pop(key, None)


def _get_or_create_context(filepath: str, session_id: str = "default") -> Dict[str, Any]:
    """Get or create an isolated execution context for this notebook session"""
    _cleanup_old_contexts()
    
    context_key = _get_context_key(filepath, session_id)
    _context_last_used[context_key] = datetime.now()
    
    if context_key not in _notebook_contexts:
        _notebook_contexts[context_key] = {
            '__name__': '__main__',
            'pd': pd,
            'px': px,
            'go': go,
            'json': json,
        }
    
    return _notebook_contexts[context_key]


def parse_notebook(notebook_content: str) -> Dict[str, Any]:
    """
    Parse a Jupyter notebook JSON file
    Returns the parsed notebook structure
    """
    try:
        # Handle empty files by returning a new notebook structure
        if not notebook_content or notebook_content.strip() == '':
            return {
                'success': True,
                'cells': [],
                'metadata': {},
                'nbformat': 4,
                'nbformat_minor': 5,
                'is_new': True
            }
        
        notebook = json.loads(notebook_content)
        return {
            'success': True,
            'cells': notebook.get('cells', []),
            'metadata': notebook.get('metadata', {}),
            'nbformat': notebook.get('nbformat', 4),
            'nbformat_minor': notebook.get('nbformat_minor', 0)
        }
    except json.JSONDecodeError as e:
        return {
            'success': False,
            'error': f'Invalid notebook JSON: {str(e)}'
        }


def execute_notebook_cell(cell: Dict[str, Any], cell_index: int, filepath: str = "", session_id: str = "default") -> Dict[str, Any]:
    """
    Execute a single notebook cell
    Returns execution results with outputs
    """
    cell_type = cell.get('cell_type', 'code')
    source = cell.get('source', [])
    
    # Join source lines if it's a list
    if isinstance(source, list):
        code = ''.join(source)
    else:
        code = source
    
    # For markdown cells, just return the content
    if cell_type == 'markdown':
        return {
            'success': True,
            'cell_type': 'markdown',
            'cell_index': cell_index,
            'content': code,
            'outputs': []
        }
    
    # For code cells, execute the code
    if cell_type == 'code':
        # Create builtins for notebook execution
        # Include essential builtins for data analysis and imports
        import builtins
        safe_builtins = {
            '__import__': __import__,  # Required for import statements
            '__build_class__': builtins.__build_class__,  # Required for class definitions
            'print': print,
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'set': set,
            'tuple': tuple,
            'min': min,
            'max': max,
            'sum': sum,
            'abs': abs,
            'round': round,
            'sorted': sorted,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'type': type,
            'isinstance': isinstance,
            'hasattr': hasattr,
            'getattr': getattr,
            'setattr': setattr,
            'dir': dir,
            'open': open,  # For file operations
            'help': help,  # For documentation
            'True': True,
            'False': False,
            'None': None,
        }
        
        # Create execution environment with restricted builtins
        exec_globals = {
            '__builtins__': safe_builtins,
            '__name__': '__main__',
            'pd': pd,
            'px': px,
            'go': go,
            'json': json,
        }
        
        # Get per-session context and preserve variables from previous cells
        notebook_globals = _get_or_create_context(filepath, session_id)
        for key, value in notebook_globals.items():
            if key not in ['__name__', '__builtins__']:
                exec_globals[key] = value
        
        output_capture = io.StringIO()
        error_capture = io.StringIO()
        
        try:
            with redirect_stdout(output_capture), redirect_stderr(error_capture):
                exec(code, exec_globals)
            
            # Update global context with new variables
            for key, value in exec_globals.items():
                if key not in ['__name__', '__builtins__', 'pd', 'px', 'go', 'json']:
                    notebook_globals[key] = value
            
            output_text = output_capture.getvalue()
            error_text = error_capture.getvalue()
            
            # Extract any DataFrames created
            dataframes = {}
            for key, value in exec_globals.items():
                if key not in ['__name__', '__builtins__', 'pd', 'px', 'go', 'json']:
                    if isinstance(value, pd.DataFrame):
                        dataframes[key] = {
                            'shape': list(value.shape),
                            'columns': list(value.columns),
                            'head': value.head(5).to_dict('records')
                        }
            
            return {
                'success': True,
                'cell_type': 'code',
                'cell_index': cell_index,
                'source': code,
                'outputs': [
                    {
                        'output_type': 'stream',
                        'name': 'stdout',
                        'text': output_text
                    }
                ] if output_text else [],
                'error': error_text if error_text else None,
                'dataframes': dataframes
            }
        except Exception as e:
            return {
                'success': False,
                'cell_type': 'code',
                'cell_index': cell_index,
                'source': code,
                'error': str(e),
                'outputs': []
            }
    
    # Raw cells or other types
    return {
        'success': True,
        'cell_type': cell_type,
        'cell_index': cell_index,
        'content': code,
        'outputs': []
    }


def execute_all_cells(cells: List[Dict[str, Any]], filepath: str = "", session_id: str = "default") -> List[Dict[str, Any]]:
    """
    Execute all cells in a notebook sequentially
    Returns list of execution results
    """
    results = []
    for index, cell in enumerate(cells):
        result = execute_notebook_cell(cell, index, filepath, session_id)
        results.append(result)
    return results


def reset_notebook_context(filepath: str = "", session_id: str = "default"):
    """
    Reset the notebook execution context for a specific session
    Clears all variables except built-in libraries
    """
    context_key = _get_context_key(filepath, session_id)
    _notebook_contexts[context_key] = {
        '__name__': '__main__',
        'pd': pd,
        'px': px,
        'go': go,
        'json': json,
    }
    _context_last_used[context_key] = datetime.now()
    return {'success': True, 'message': 'Notebook context reset'}


def get_notebook_variables(filepath: str = "", session_id: str = "default") -> Dict[str, Any]:
    """
    Get all variables currently in the notebook context for a specific session
    """
    notebook_globals = _get_or_create_context(filepath, session_id)
    variables = {}
    for key, value in notebook_globals.items():
        if key not in ['__name__', '__builtins__', 'pd', 'px', 'go', 'json']:
            var_type = type(value).__name__
            if isinstance(value, pd.DataFrame):
                variables[key] = {
                    'type': 'DataFrame',
                    'shape': list(value.shape),
                    'columns': list(value.columns)
                }
            elif isinstance(value, (int, float, str, bool)):
                variables[key] = {
                    'type': var_type,
                    'value': str(value)
                }
            else:
                variables[key] = {
                    'type': var_type,
                    'value': repr(value)[:100]  # Limit to 100 chars
                }
    return variables
