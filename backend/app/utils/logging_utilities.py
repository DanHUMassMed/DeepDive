import logging.config
import os
import subprocess
import sys
import inspect
import platform
from functools import wraps
import threading
import logging
from functools import wraps


import functools
import inspect


# Define TRACE level constant
TRACE_LEVEL = 5

# logging_util.py
def setup_logging(logger_nm="app", config_path='logging_config.ini'):
    """Sets up logging configuration."""

    logging.addLevelName(TRACE_LEVEL, "TRACE")

    # Create a custom function for TRACE level logging
    def trace(self, message, *args, **kwargs):
        if self.isEnabledFor(TRACE_LEVEL):
            self._log(TRACE_LEVEL, message, args, **kwargs)

    # Add the custom method to the Logger class
    logging.Logger.trace = trace

    
    # If we are just given a file name for the config_path
    # Try to resolve to absolute path by searching the sys.path
    if os.path.dirname(config_path) == '':
        config_path = find_file_on_sys_path(config_path)
        
    if os.path.exists(config_path):
        logging.config.fileConfig(config_path)
    else:
        logging.basicConfig(level=logging.DEBUG)
        logging.warning(f"Logging configuration file '{config_path}' not found. Using default logging configuration.")
        logging.warning('\n'.join(sys.path))

    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    logger =logging.getLogger(logger_nm)
    set_log_level(logger, LOG_LEVEL)
    return logger

def set_log_level(logger, level_str):
    level_str = level_str.upper()  # Ensure the string is in uppercase for consistency
    level_mapping = {
        "TRACE": TRACE_LEVEL,
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "WARN": logging.WARNING,  # 'WARN' is an alias for 'WARNING'
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    
    level = level_mapping.get(level_str)
    
    if level is None:
        raise ValueError(f"Invalid log level: {level_str}")
    
    logger.setLevel(level)

class IndentManager:
    _lock = threading.Lock()
    _indent = 0

    @classmethod
    def increment(cls):
        try:
            with cls._lock:
                cls._indent += 1
        finally:
            pass

    @classmethod
    def decrement(cls):
        try:
            with cls._lock:
                if cls._indent > 0:
                    cls._indent -= 1
        finally:
            pass

    @classmethod
    def get_indent(cls):
        with cls._lock:
            return cls._indent


def trace(logger):
    """Decorator to log function entry and exit at TRACE level, using the provided logger."""
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get the effective log level from the logger
            log_level = logger.getEffectiveLevel()
            
            # Only log if the log level is TRACE (log_level == 5)
            if log_level == TRACE_LEVEL:  # Assuming TRACE is defined in your logger
                # Indentation for visual hierarchy
                indent = '\t' * IndentManager.get_indent()
                
                if args and hasattr(args[0], '__class__'):
                    log_message_core = f"{args[0].__class__.__name__}.{func.__name__}"
                else:
                    log_message_core = f"{func.__module__} {func.__name__}"
                
                logger.trace(f"{IndentManager.get_indent():02d} {indent}ENTERING {log_message_core}")
                IndentManager.increment()

                try:
                    result = await func(*args, **kwargs)
                except Exception:
                    logger.trace(f"{IndentManager.get_indent():02d} {indent}EXCEPTION {log_message_core}")
                finally:
                    IndentManager.decrement()
                
                logger.trace(f"{IndentManager.get_indent():02d} {indent}EXITING  {log_message_core}")
                if IndentManager.get_indent()==0:
                    logger.trace("")
                                    
                return result
            else:
                # If log level is not TRACE, simply call the function without logging
                return await func(*args, **kwargs)

        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get the effective log level from the logger
            log_level = logger.getEffectiveLevel()
            
            # Only log if the log level is TRACE (log_level == 5)
            if log_level == TRACE_LEVEL:  # Assuming TRACE is defined in your logger
                # Indentation for visual hierarchy
                indent = '\t' * IndentManager.get_indent()
                
                if args and hasattr(args[0], '__class__'):
                    log_message_core = f"{args[0].__class__.__name__}.{func.__name__}"
                else:
                    log_message_core = f"{func.__module__} {func.__name__}"
                
                logger.trace(f"{IndentManager.get_indent():02d} {indent}ENTERING {log_message_core}")
                IndentManager.increment()

                try:
                    result = func(*args, **kwargs)
                except Exception:
                    logger.trace(f"{IndentManager.get_indent():02d} {indent}EXCEPTION {log_message_core}")
                finally:
                    IndentManager.decrement()
                
                logger.trace(f"{IndentManager.get_indent():02d} {indent}EXITING  {log_message_core}")
                if IndentManager.get_indent()==0:
                    logger.trace("")
                
                return result
            else:
                # If log level is not TRACE, simply call the function without logging
                return func(*args, **kwargs)
            


        # Check if the function is asynchronous and choose the appropriate wrapper
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    return decorator


def find_file_on_sys_path(file_name):
    """
    Finds and returns the full path of a file if it exists in the system's PATH.
    """
    for directory in sys.path:
        # Join the directory path with the file name
        full_path = os.path.join(directory, file_name)
        # Check if the file exists
        if os.path.isfile(full_path):
            return full_path
    return file_name
   

     