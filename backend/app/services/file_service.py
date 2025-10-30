from pathlib import Path
from typing import List, Dict, Optional
import shutil
import json

WORKSPACE_DIR = Path("workspace")
WORKSPACE_DIR.mkdir(exist_ok=True)


def ensure_workspace():
    """Ensure workspace directory exists"""
    WORKSPACE_DIR.mkdir(exist_ok=True)


def build_file_tree(base_path: Path = WORKSPACE_DIR) -> List[Dict]:
    """Build hierarchical file tree structure"""
    if not base_path.exists():
        return []
    
    def scan_directory(path: Path, relative_to: Path) -> List[Dict]:
        items = []
        try:
            for item in sorted(path.iterdir()):
                rel_path = item.relative_to(relative_to)
                if item.is_dir():
                    items.append({
                        'name': item.name,
                        'path': str(rel_path),
                        'type': 'folder',
                        'children': scan_directory(item, relative_to)
                    })
                elif item.is_file():
                    items.append({
                        'name': item.name,
                        'path': str(rel_path),
                        'type': 'file',
                        'extension': item.suffix
                    })
        except PermissionError:
            pass
        return items
    
    return scan_directory(base_path, base_path)


def read_file(file_path: str) -> Optional[str]:
    """Read file content"""
    try:
        full_path = WORKSPACE_DIR / file_path
        if not full_path.exists() or not full_path.is_file():
            return None
        return full_path.read_text()
    except Exception:
        return None


def create_file(file_path: str, content: str = "") -> bool:
    """Create a new file"""
    try:
        full_path = WORKSPACE_DIR / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        return True
    except Exception:
        return False


def update_file(file_path: str, content: str) -> bool:
    """Update existing file"""
    try:
        full_path = WORKSPACE_DIR / file_path
        if not full_path.exists():
            return False
        full_path.write_text(content)
        return True
    except Exception:
        return False


def delete_file_or_folder(file_path: str) -> bool:
    """Delete a file or folder"""
    try:
        full_path = WORKSPACE_DIR / file_path
        if not full_path.exists():
            return False
        
        if full_path.is_dir():
            shutil.rmtree(full_path)
        else:
            full_path.unlink()
        return True
    except Exception:
        return False


def move_file(source_path: str, target_folder: str) -> Optional[str]:
    """Move a file to a different folder"""
    try:
        source = WORKSPACE_DIR / source_path
        target_dir = WORKSPACE_DIR / target_folder
        
        if not source.exists():
            return None
        
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / source.name
        
        source.rename(target_path)
        return str(target_path.relative_to(WORKSPACE_DIR))
    except Exception:
        return None


def create_folder(folder_path: str) -> bool:
    """Create a new folder"""
    try:
        full_path = WORKSPACE_DIR / folder_path
        full_path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_file_info(file_path: str) -> Optional[Dict]:
    """Get file information"""
    try:
        full_path = WORKSPACE_DIR / file_path
        if not full_path.exists():
            return None
        
        stat = full_path.stat()
        return {
            "name": full_path.name,
            "path": file_path,
            "type": "folder" if full_path.is_dir() else "file",
            "size": stat.st_size if full_path.is_file() else 0,
            "modified": stat.st_mtime,
            "extension": full_path.suffix if full_path.is_file() else None
        }
    except Exception:
        return None
