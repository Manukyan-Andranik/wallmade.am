import os
import logging
from logging.handlers import RotatingFileHandler

class AppLogger:
    """Application logger class to handle logging configuration and operations"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize logging for the application"""
        # Configure logging level from config
        log_level = app.config.get('LOG_LEVEL', logging.INFO)
        
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(app.root_path, 'logs')
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)
        
        # Configure file handler with rotation
        file_handler = RotatingFileHandler(
            os.path.join(logs_dir, 'wallmade.log'),
            maxBytes=1024 * 1024 * 10,  # 10 MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(log_level)
        
        # Configure console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s'
        ))
        console_handler.setLevel(log_level)
        
        # Remove any existing handlers
        if app.logger.handlers:
            for handler in app.logger.handlers:
                app.logger.removeHandler(handler)
        
        # Add handlers to the app logger
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(log_level)
        
        # Log application startup
        app.logger.info('Wallmade application starting up')
        app.logger.info(f"Environment: {app.config.get('ENV', 'production')}")
        app.logger.info(f"Debug mode: {app.debug}")
        
        # Store logger reference in app
        app.extensions['logger'] = self