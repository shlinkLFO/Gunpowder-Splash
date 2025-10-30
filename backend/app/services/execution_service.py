import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json


# Global execution context to persist variables between runs
execution_globals = {
    'pd': pd,
    'px': px,
    'go': go,
    'json': json,
    '__name__': '__main__'
}


def execute_python_code(code: str) -> Dict[str, Any]:
    """
    Execute Python code in a restricted environment for data analysis.
    
    SECURITY NOTICE: This is an EDUCATIONAL/DEMO environment with limited safety measures.
    - NOT suitable for untrusted code execution
    - NOT suitable for production deployment
    - Designed for learning data analysis with pandas/plotly
    
    For production, use:
    - Container-based isolation (Docker with resource limits)
    - Process sandboxing (RestrictedPython, PyPy sandbox)
    - Proper authentication and access controls
    """
    
    # Create a restricted builtins dict with only safe operations
    safe_builtins = {
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
        'True': True,
        'False': False,
        'None': None,
    }
    
    # Create restricted execution environment
    restricted_globals = {
        '__builtins__': safe_builtins,
        'pd': pd,
        'px': px,
        'go': go,
        'json': json,
        '__name__': '__main__',
    }
    
    # Preserve any DataFrames from previous executions
    for key, value in execution_globals.items():
        if key not in ['__name__', '__builtins__'] and not key.startswith('_'):
            if isinstance(value, (pd.DataFrame, pd.Series)):
                restricted_globals[key] = value
    
    output_capture = io.StringIO()
    error_capture = io.StringIO()
    
    try:
        with redirect_stdout(output_capture), redirect_stderr(error_capture):
            exec(code, restricted_globals)
        
        output_text = output_capture.getvalue()
        error_text = error_capture.getvalue()
        
        # Update global context with new variables
        for key, value in restricted_globals.items():
            if key not in ['__name__', '__builtins__', 'pd', 'px', 'go', 'json']:
                execution_globals[key] = value
        
        # Extract DataFrames
        dataframes = {}
        for key, value in restricted_globals.items():
            if key not in ['__name__', '__builtins__', 'pd', 'px', 'go', 'json']:
                if isinstance(value, pd.DataFrame):
                    dataframes[key] = {
                        'shape': list(value.shape),
                        'columns': list(value.columns)
                    }
        
        return {
            'success': True,
            'output': output_text,
            'error': error_text,
            'dataframes': dataframes
        }
    except Exception as e:
        return {
            'success': False,
            'output': output_capture.getvalue(),
            'error': str(e)
        }


def get_loaded_dataframes() -> Dict[str, Any]:
    """Get information about loaded DataFrames"""
    dataframes = {}
    for key, value in execution_globals.items():
        if key not in ['pd', 'px', 'go', 'json', '__name__', '__builtins__']:
            if isinstance(value, pd.DataFrame):
                dataframes[key] = {
                    'shape': list(value.shape),
                    'columns': list(value.columns),
                    'dtypes': {col: str(dtype) for col, dtype in value.dtypes.items()}
                }
    return dataframes


def clear_execution_context():
    """Clear all user-defined variables"""
    global execution_globals
    keys_to_remove = [
        k for k in execution_globals.keys() 
        if k not in ['pd', 'px', 'go', 'json', '__name__', '__builtins__']
    ]
    for key in keys_to_remove:
        del execution_globals[key]
    return {'success': True, 'message': 'Execution context cleared'}
