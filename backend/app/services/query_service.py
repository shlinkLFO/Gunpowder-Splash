import pandas as pd
from typing import Dict, Any
from app.services import data_service


def execute_sql_query(sql_query: str) -> Dict[str, Any]:
    """
    Execute SQL query on loaded datasets using pandas
    Note: This is a simplified implementation. For production,
    consider using pandasql or a proper SQL engine with better security.
    """
    try:
        # Get all available datasets
        datasets_dict = {}
        for name in data_service.datasets.keys():
            datasets_dict[name] = data_service.datasets[name]
        
        # Also check for common variable name 'df'
        if datasets_dict:
            datasets_dict['df'] = list(datasets_dict.values())[0]
        
        if not datasets_dict:
            return {
                'success': False,
                'error': 'No datasets loaded. Upload data using Data Explorer first.'
            }
        
        # Basic SQL parsing and execution using pandas
        # This is a simplified approach - for full SQL support, use pandasql
        query_lower = sql_query.lower().strip()
        
        # Simple SELECT * queries
        if query_lower.startswith('select'):
            # Extract dataset name (very basic parsing)
            if 'from' in query_lower:
                parts = query_lower.split('from')
                if len(parts) > 1:
                    table_part = parts[1].split()[0].strip()
                    
                    if table_part in datasets_dict:
                        df = datasets_dict[table_part]
                        
                        # Apply LIMIT if present
                        limit = 100
                        if 'limit' in query_lower:
                            limit_parts = query_lower.split('limit')
                            if len(limit_parts) > 1:
                                try:
                                    limit = int(limit_parts[1].strip().split()[0])
                                except:
                                    pass
                        
                        # Apply WHERE filtering (basic)
                        if 'where' in query_lower and '=' in query_lower:
                            where_part = parts[1].split('where')[1].split('limit')[0]
                            # Very basic WHERE parsing
                            if '=' in where_part:
                                condition_parts = where_part.split('=')
                                col = condition_parts[0].strip()
                                val = condition_parts[1].strip().strip("'\"")
                                
                                if col in df.columns:
                                    df = df[df[col].astype(str) == val]
                        
                        result_df = df.head(limit)
                        
                        return {
                            'success': True,
                            'columns': list(result_df.columns),
                            'data': result_df.to_dict('records'),
                            'row_count': len(result_df),
                            'total_rows': len(df)
                        }
        
        return {
            'success': False,
            'error': 'Query not supported. Use simple SELECT queries like: SELECT * FROM dataset_name LIMIT 10'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Query execution error: {str(e)}'
        }


def filter_dataset(dataset_name: str, column: str, value: str) -> Dict[str, Any]:
    """
    Filter a dataset by column value
    """
    try:
        df = data_service.get_dataset(dataset_name)
        if df is None:
            return {'success': False, 'error': 'Dataset not found'}
        
        if column not in df.columns:
            return {'success': False, 'error': f'Column {column} not found'}
        
        filtered_df = df[df[column].astype(str) == value]
        
        return {
            'success': True,
            'columns': list(filtered_df.columns),
            'data': filtered_df.head(100).to_dict('records'),
            'row_count': len(filtered_df)
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def search_dataset(dataset_name: str, search_text: str) -> Dict[str, Any]:
    """
    Search for text across all columns in a dataset
    """
    try:
        df = data_service.get_dataset(dataset_name)
        if df is None:
            return {'success': False, 'error': 'Dataset not found'}
        
        # Search across all string columns
        mask = pd.Series([False] * len(df))
        for col in df.columns:
            try:
                mask |= df[col].astype(str).str.contains(search_text, case=False, na=False)
            except:
                pass
        
        result_df = df[mask]
        
        return {
            'success': True,
            'columns': list(result_df.columns),
            'data': result_df.head(100).to_dict('records'),
            'row_count': len(result_df)
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}
