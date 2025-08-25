"""
Logging configuration for Dash dashboard
"""
import logging
import os
from datetime import datetime

def setup_dashboard_logging():
    """Setup logging configuration for Dash dashboard"""
    # Create logs directory (relative to project root)
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"{log_dir}/dash_app_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Dash dashboard logging initialized")
    return logger

def log_callback_error(error, callback_name):
    """Log callback errors"""
    logger = logging.getLogger(__name__)
    logger.error(f"Error in {callback_name}: {str(error)}")

def log_data_error(error, data_operation):
    """Log data operation errors"""
    logger = logging.getLogger(__name__)
    logger.error(f"Data error in {data_operation}: {str(error)}")
