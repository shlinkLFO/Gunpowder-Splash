import io
import json
import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path

# In-memory storage for uploaded datasets
datasets: Dict[str, pd.DataFrame] = {}

# Persistent storage directory
DATA_DIR = Path("workspace/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def upload_and_process_file(filename: str, content: bytes) -> Dict[str, Any]:
    """
    Upload and process a data file (JSON or CSV)
    """
    try:
        # Determine file type and parse
        if filename.endswith('.json'):
            data_str = content.decode('utf-8')
            data = json.loads(data_str)
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                return {'success': False, 'error': 'Invalid JSON structure'}
        
        elif filename.endswith('.csv'):
            data_str = content.decode('utf-8')
            df = pd.read_csv(io.StringIO(data_str))
        
        else:
            return {'success': False, 'error': 'Unsupported file type. Use JSON or CSV'}
        
        # Store in memory
        dataset_name = Path(filename).stem
        datasets[dataset_name] = df
        
        # Save to disk for persistence
        save_path = DATA_DIR / f"{dataset_name}.parquet"
        df.to_parquet(save_path)
        
        return {
            'success': True,
            'dataset_name': dataset_name,
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def get_dataset_preview(dataset_name: str, limit: int = 100) -> Dict[str, Any]:
    """
    Get preview of a dataset
    """
    try:
        if dataset_name not in datasets:
            # Try loading from disk
            save_path = DATA_DIR / f"{dataset_name}.parquet"
            if save_path.exists():
                datasets[dataset_name] = pd.read_parquet(save_path)
            else:
                return {'success': False, 'error': 'Dataset not found'}
        
        df = datasets[dataset_name]
        preview_df = df.head(limit)
        
        return {
            'success': True,
            'columns': list(df.columns),
            'data': preview_df.to_dict('records'),
            'total_rows': len(df),
            'preview_rows': len(preview_df),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
    
    except Exception as e:
        return {'success': False, 'error': str(e)}


def export_dataset(dataset_name: str, format: str = 'csv') -> Optional[bytes]:
    """
    Export dataset to CSV or JSON
    """
    try:
        if dataset_name not in datasets:
            return None
        
        df = datasets[dataset_name]
        
        if format == 'csv':
            return df.to_csv(index=False).encode('utf-8')
        elif format == 'json':
            return df.to_json(orient='records', indent=2).encode('utf-8')
        else:
            return None
    
    except Exception:
        return None


def list_datasets() -> Dict[str, Any]:
    """
    List all available datasets
    """
    dataset_info = {}
    for name, df in datasets.items():
        dataset_info[name] = {
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns)
        }
    return dataset_info


def get_dataset(dataset_name: str) -> Optional[pd.DataFrame]:
    """
    Get a dataset by name (for use in queries)
    """
    if dataset_name in datasets:
        return datasets[dataset_name]
    
    # Try loading from disk
    save_path = DATA_DIR / f"{dataset_name}.parquet"
    if save_path.exists():
        df = pd.read_parquet(save_path)
        datasets[dataset_name] = df
        return df
    
    return None
