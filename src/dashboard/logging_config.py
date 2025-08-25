import logging
import logging.handlers
import os
from datetime import datetime
from src.utils.paths import get_logs_dir

def setup_dashboard_logging():
    """
    Configure comprehensive logging for the Dash dashboard
    Captures both Python errors and Dash-specific callback errors
    """
    
    # Ensure logs directory exists
    logs_path = get_logs_dir()
    
    # Create timestamp for log files
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Configure root logger
    level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
    level = getattr(logging, level_str, logging.INFO)
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler for all logs
            logging.handlers.RotatingFileHandler(
                str(logs_path / f'dashboard_{timestamp}.log'),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            # Separate file handler for errors only
            logging.handlers.RotatingFileHandler(
                str(logs_path / f'dashboard_errors_{timestamp}.log'),
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3
            ),
            # Console handler for important messages
            logging.StreamHandler()
        ]
    )
    
    # Configure error-only handler
    error_handler = logging.handlers.RotatingFileHandler(
        str(logs_path / f'dashboard_errors_{timestamp}.log'),
        maxBytes=5*1024*1024,
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Get loggers for different components
    dash_logger = logging.getLogger('dash')
    dash_logger.setLevel(logging.DEBUG)
    dash_logger.addHandler(error_handler)
    
    plotly_logger = logging.getLogger('plotly')
    plotly_logger.setLevel(logging.DEBUG)
    plotly_logger.addHandler(error_handler)
    
    # Create application logger
    app_logger = logging.getLogger('hungerhub_dashboard')
    app_logger.setLevel(logging.INFO)
    
    # Log startup message
    app_logger.info("🍽️ HungerHub Dashboard Logging Initialized")
    app_logger.info(f"📝 Main log file: {logs_path / f'dashboard_{timestamp}.log'}")
    app_logger.info(f"❌ Error log file: {logs_path / f'dashboard_errors_{timestamp}.log'}")
    
    return app_logger

def log_callback_error(callback_name, error, context=None):
    """
    Log callback-specific errors with context
    """
    logger = logging.getLogger('hungerhub_dashboard.callbacks')
    
    error_msg = f"Callback Error in '{callback_name}': {str(error)}"
    if context:
        error_msg += f" | Context: {context}"
    
    logger.error(error_msg, exc_info=True)

def log_data_error(operation, error, data_info=None):
    """
    Log data-related errors
    """
    logger = logging.getLogger('hungerhub_dashboard.data')
    
    error_msg = f"Data Error in '{operation}': {str(error)}"
    if data_info:
        error_msg += f" | Data Info: {data_info}"
    
    logger.error(error_msg, exc_info=True)
