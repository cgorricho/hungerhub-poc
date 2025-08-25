import logging
import os
from datetime import datetime
from src.utils.paths import get_logs_dir

def setup_logging():
    """Setup logging configuration for Streamlit app"""
    # Create logs directory
    logs_path = get_logs_dir()
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_path / f"streamlit_app_{timestamp}.log"
    
    # Configure logging
    level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
    level = getattr(logging, level_str, logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(str(log_file)),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    return logging.getLogger(__name__)
