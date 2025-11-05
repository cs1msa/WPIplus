# Licensed under the MIT License. See LICENSE-CODE in the repository root for details.
# Copyright (c) 2025 Christos Papadopoulos

"""
Utility functions and constants for PatentFusion

This module contains shared utilities, constants, and helper functions used
across the PatentFusion application.
"""

import os
import logging
import psutil

# Import constants from constants module
from constants import (
    VALID_PATENT_OFFICES, VALID_OUTPUT_FORMATS,
    DEFAULT_CONFIG, PROGRESS_REPORT_INTERVAL
)


# Setup logging
def setup_logging():
    """Setup basic logging configuration"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    return logging.getLogger(__name__)

# Text processing utilities
def truncate_text(text, max_length=300):
    """
    Truncate text to specified number of words
    Returns full text if set to 0 or "ALL"
    
    Args:
        text (str): Text to truncate
        max_length (int or str): Maximum number of words, or "ALL" for full text
        
    Returns:
        str: Truncated text
    """
    if not text:
        return ""
    
    # If max_length is 0 or "ALL" (case insensitive), return the full text
    if max_length == 0 or (isinstance(max_length, str) and max_length.upper() == "ALL"):
        return text
    
    # Otherwise, truncate to the specified number of words
    words = text.split()
    return " ".join(words[:max_length])


# Memory utilities
def get_memory_usage_gb():
    """Get current memory usage in GB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024**3)

# Time formatting utilities
def format_duration(seconds):
    """
    Format duration in seconds to human-readable MM:SS or H:MM:SS format
    
    Args:
        seconds (float): Duration in seconds
        
    Returns:
        str: Formatted duration string
        
    Examples:
        - Less than 60s: "4.87 seconds"
        - 60s to 3600s: "2:34"
        - More than 3600s: "1:23:45"
    """
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    else:
        # Convert to integer seconds for time formatting
        total_seconds = int(seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        remaining_seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{remaining_seconds:02d}"
        else:
            return f"{minutes}:{remaining_seconds:02d}"


def ensure_directory_exists(directory_path):
    """
    Ensure that a directory exists, creating it if necessary
    
    Args:
        directory_path (str): Path to the directory
        
    Raises:
        OSError: If directory cannot be created due to permissions or other issues
    """
    if not directory_path:
        raise ValueError("Directory path cannot be empty")
    
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
            logger = logging.getLogger(__name__)
            logger.debug(f"Created directory: {directory_path}")
        elif not os.path.isdir(directory_path):
            raise OSError(f"Path exists but is not a directory: {directory_path}")
    except PermissionError as e:
        raise OSError(f"Permission denied creating directory {directory_path}: {e}")
    except OSError as e:
        raise OSError(f"Failed to create directory {directory_path}: {e}")



def get_system_info():
    """
    Get system information for logging and diagnostics
    
    Returns:
        dict: System information dictionary
    """
    return {
        'total_memory_gb': psutil.virtual_memory().total / (1024**3),
        'available_memory_gb': psutil.virtual_memory().available / (1024**3),
        'cpu_count': psutil.cpu_count(),
        'cpu_count_logical': psutil.cpu_count(logical=True),
        'current_memory_usage_gb': get_memory_usage_gb()
    }

def log_system_info(logger):
    """
    Log system information for diagnostics
    
    Args:
        logger: Logger instance
    """
    info = get_system_info()
    logger.info(f"System Info - Total Memory: {info['total_memory_gb']:.2f} GB, "
               f"Available: {info['available_memory_gb']:.2f} GB, "
               f"CPU Cores: {info['cpu_count']} physical, {info['cpu_count_logical']} logical")

def calculate_optimal_chunk_size():
    """
    Calculate optimal chunk size balancing memory usage and multiprocessing efficiency
    
    Uses a balanced approach considering:
    - Available memory (conservative 30% usage)
    - CPU core count for work distribution
    - Memory per file estimates
    - Performance sweet spot bounds
    
    Returns:
        int: Optimal chunk size (bounded between 50-5000)
    """
    # Get system resources
    available_memory_gb = psutil.virtual_memory().available / (1024**3)
    cpu_count = psutil.cpu_count()
    
    # Conservative estimates for memory usage per file:
    # - XML serialization: ~20KB
    # - JSON/CSV conversion: ~40KB (2x XML)
    # - Processing overhead: ~60KB total per file
    memory_per_file_mb = 0.06  # 60KB per file in MB
    
    # Use only 30% of available memory (more conservative for better performance)
    usable_memory_gb = available_memory_gb * 0.3
    
    # Calculate memory-based chunk size
    memory_based_size = int((usable_memory_gb * 1024) / memory_per_file_mb)
    
    # Calculate CPU-balanced chunk size (aim for ~10-20 chunks per CPU core)
    cpu_based_size = max(100, memory_based_size // (cpu_count * 15))
    
    # Use the smaller of the two to avoid both memory pressure and poor work distribution
    calculated_size = min(memory_based_size, cpu_based_size)
    
    # Apply performance-optimized bounds (sweet spot range)
    min_chunk = 50    # Minimum for efficiency 
    max_chunk = 5000  # Maximum for good work distribution and cache efficiency
    
    bounded_chunk_size = max(min_chunk, min(calculated_size, max_chunk))
    
    # Create logger for this function
    logger = logging.getLogger(__name__)
    logger.info(f"Chunk size calculation:")
    logger.info(f"  Available memory: {available_memory_gb:.2f} GB, Usable (30%): {usable_memory_gb:.2f} GB")
    logger.info(f"  CPU cores: {cpu_count}")
    logger.info(f"  Memory-based size: {memory_based_size:,}")
    logger.info(f"  CPU-balanced size: {cpu_based_size:,}")
    logger.info(f"  Applied bounds: {min_chunk:,} - {max_chunk:,}")
    logger.info(f"  Final chunk size: {bounded_chunk_size:,}")
    
    return bounded_chunk_size
