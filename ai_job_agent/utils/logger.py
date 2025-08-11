"""Logging utilities for the AI job agent."""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Custom colored formatter for console output."""
    
    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        """Format log record with colors."""
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        record.msg = f"{log_color}{record.msg}{self.RESET}"
        return super().format(record)


class JobAgentLogger:
    """Centralized logging configuration for the job agent."""
    
    def __init__(self, name: str = "ai_job_agent", log_dir: str = "logs"):
        """Initialize the logger.
        
        Args:
            name (str): Logger name
            log_dir (str): Directory for log files
        """
        self.name = name
        self.log_dir = Path(log_dir)
        self.logger = None
        self._setup_log_directory()
    
    def _setup_log_directory(self):
        """Create log directory if it doesn't exist."""
        self.log_dir.mkdir(exist_ok=True)
    
    def get_logger(self, component: Optional[str] = None, 
                  level: int = logging.INFO, 
                  console_output: bool = True,
                  file_output: bool = True,
                  max_file_size: int = 10 * 1024 * 1024,  # 10MB
                  backup_count: int = 5) -> logging.Logger:
        """Get configured logger instance.
        
        Args:
            component (str, optional): Component name for logger
            level (int): Logging level
            console_output (bool): Enable console output
            file_output (bool): Enable file output
            max_file_size (int): Maximum file size before rotation
            backup_count (int): Number of backup files to keep
            
        Returns:
            logging.Logger: Configured logger
        """
        logger_name = f"{self.name}.{component}" if component else self.name
        logger = logging.getLogger(logger_name)
        
        # Clear existing handlers to avoid duplicates
        logger.handlers.clear()
        logger.setLevel(level)
        
        # Console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = ColoredFormatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        # File handler with rotation
        if file_output:
            log_filename = self.log_dir / f"{logger_name.replace('.', '_')}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_filename,
                maxBytes=max_file_size,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_formatter = logging.Formatter(
                fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        self.logger = logger
        return logger
    
    def log_performance(self, operation: str, duration: float, 
                       metadata: Optional[Dict[str, Any]] = None):
        """Log performance metrics.
        
        Args:
            operation (str): Operation name
            duration (float): Operation duration in seconds
            metadata (dict, optional): Additional metadata
        """
        if self.logger:
            msg = f"Performance: {operation} completed in {duration:.3f}s"
            if metadata:
                msg += f" | Metadata: {metadata}"
            self.logger.info(msg)
    
    def log_error_context(self, error: Exception, context: Dict[str, Any]):
        """Log error with detailed context.
        
        Args:
            error (Exception): The exception that occurred
            context (dict): Contextual information
        """
        if self.logger:
            self.logger.error(
                f"Error: {type(error).__name__}: {str(error)} | Context: {context}",
                exc_info=True
            )
    
    def log_state_change(self, component: str, old_state: str, new_state: str):
        """Log state changes in components.
        
        Args:
            component (str): Component name
            old_state (str): Previous state
            new_state (str): New state
        """
        if self.logger:
            self.logger.info(f"State change in {component}: {old_state} -> {new_state}")
    
    def create_session_logger(self, session_id: str) -> logging.Logger:
        """Create a logger for a specific session.
        
        Args:
            session_id (str): Unique session identifier
            
        Returns:
            logging.Logger: Session-specific logger
        """
        session_log_dir = self.log_dir / "sessions"
        session_log_dir.mkdir(exist_ok=True)
        
        session_logger = logging.getLogger(f"{self.name}.session.{session_id}")
        session_logger.handlers.clear()
        session_logger.setLevel(logging.INFO)
        
        # Session file handler
        session_log_file = session_log_dir / f"session_{session_id}.log"
        session_handler = logging.FileHandler(session_log_file, encoding='utf-8')
        session_formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        session_handler.setFormatter(session_formatter)
        session_logger.addHandler(session_handler)
        session_logger.propagate = False
        
        return session_logger


# Global logger instance
_global_logger_instance = None


def get_logger(component: Optional[str] = None, **kwargs) -> logging.Logger:
    """Get the global logger instance.
    
    Args:
        component (str, optional): Component name
        **kwargs: Additional configuration options
        
    Returns:
        logging.Logger: Configured logger
    """
    global _global_logger_instance
    
    if _global_logger_instance is None:
        _global_logger_instance = JobAgentLogger()
    
    return _global_logger_instance.get_logger(component, **kwargs)


def setup_logging(log_level: str = "INFO", log_dir: str = "logs", 
                 console_output: bool = True) -> JobAgentLogger:
    """Setup logging configuration.
    
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir (str): Directory for log files
        console_output (bool): Enable console output
        
    Returns:
        JobAgentLogger: Configured logger instance
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger_instance = JobAgentLogger(log_dir=log_dir)
    logger_instance.get_logger(level=level, console_output=console_output)
    
    global _global_logger_instance
    _global_logger_instance = logger_instance
    
    return logger_instance


def log_function_call(func_name: str, args: tuple = (), kwargs: dict = None):
    """Log function call details.
    
    Args:
        func_name (str): Function name
        args (tuple): Function arguments
        kwargs (dict): Function keyword arguments
    """
    logger = get_logger("function_calls")
    kwargs = kwargs or {}
    logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")


def log_data_flow(data_type: str, data_size: int, source: str, destination: str):
    """Log data flow between components.
    
    Args:
        data_type (str): Type of data being transferred
        data_size (int): Size of data in bytes
        source (str): Source component
        destination (str): Destination component
    """
    logger = get_logger("data_flow")
    logger.info(f"Data flow: {data_type} ({data_size} bytes) from {source} to {destination}")
