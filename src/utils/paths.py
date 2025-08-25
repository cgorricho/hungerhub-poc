from pathlib import Path
import os

# Paths utility for consistent directory handling

def get_project_root() -> Path:
    """Return the project root directory robustly by reading an environment variable.

    This method avoids filesystem searches during module import, which can cause
    issues with the Streamlit execution environment. The PROJECT_ROOT environment
    variable should be set by the launch script.
    """
    root_path = os.getenv('PROJECT_ROOT')
    if root_path:
        return Path(root_path)
    
    # Fallback for cases where the env var is not set (e.g., local dev without script)
    # This is less robust and retains the original risk, but provides a backup.
    print("Warning: PROJECT_ROOT environment variable not set. Falling back to file-based discovery.")
    return Path(__file__).resolve().parent.parent.parent


def get_data_dir(kind: str = 'processed/unified_real') -> Path:
    """Return a data directory path under the project data root.

    kind examples: 'processed/real', 'processed/unified_real', 'raw/oracle'
    """
    root = get_project_root()
    path = root / 'data'
    if kind:
        for part in kind.split('/'):
            if part:  # skip empty segments
                path = path / part
    # Ensure the directory exists for write scenarios; harmless if it already exists
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_logs_dir() -> Path:
    """Return the logs directory, creating it if necessary. Allow override via LOG_DIR env var."""
    root = get_project_root()
    log_dir_env = os.getenv('LOG_DIR')
    path = Path(log_dir_env) if log_dir_env else (root / 'logs')
    path.mkdir(parents=True, exist_ok=True)
    return path

