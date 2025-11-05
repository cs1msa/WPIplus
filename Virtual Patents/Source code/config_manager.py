# Licensed under the MIT License. See LICENSE-CODE in the repository root for details.
# Copyright (c) 2025 Christos Papadopoulos

"""
Configuration Manager for PatentFusion

This module handles configuration loading, validation, and provides access to
configuration settings throughout the application.
"""

import os
import configparser
import multiprocessing
import psutil
import logging

logger = logging.getLogger(__name__)

# Import constants
from constants import VALID_PATENT_OFFICES, VALID_OUTPUT_FORMATS, DEFAULT_CONFIG


def load_config(config_file_path):
    """
    Load configuration settings from a config file
    
    Args:
        config_file_path: Path to the configuration file
        
    Returns:
        dict: Dictionary containing all configuration values
    """
    # Check if config file exists
    if not os.path.exists(config_file_path):
        raise FileNotFoundError(f"Configuration file not found: {config_file_path}")
    
    # Create config parser and read file
    config = configparser.ConfigParser()
    config.read(config_file_path)
    
    # Create a dictionary to hold all settings
    settings = {}
    
    # Parse Paths section
    settings['vertical_origin_path'] = config.get('Paths', 'vertical_origin_path')
    settings['destination_path'] = config.get('Paths', 'destination_path')
    
    # Get patent office code and construct full vertical path
    patent_office = config.get('Paths', 'patent_office')
    if patent_office in VALID_PATENT_OFFICES:
        settings['patent_office'] = patent_office
        # Combine the base path with the patent office code
        settings['vertical_origin_path'] = os.path.join(settings['vertical_origin_path'], patent_office)
    else:
        raise ValueError(f"Invalid patent_office value: '{patent_office}'. Must be one of: {', '.join(VALID_PATENT_OFFICES)}")
    
    # Parse General section
    
    # Handle max_text_length special case
    try:
        max_text_value = config.get('General', 'max_text_length')
        if max_text_value.upper() == "ALL":
            settings['max_text_length'] = "ALL"
        else:
            settings['max_text_length'] = config.getint('General', 'max_text_length')
    except ValueError:
        # If it's not an integer or "ALL", default to 300
        settings['max_text_length'] = DEFAULT_CONFIG['max_text_length']
    

    # Parse output formats
    formats = config.get('General', 'output_formats').lower().split(',')
    settings['output_formats'] = [fmt.strip() for fmt in formats if fmt.strip() in VALID_OUTPUT_FORMATS]
    if not settings['output_formats']:
        # Default to CSV if no valid formats specified
        settings['output_formats'] = DEFAULT_CONFIG['output_formats']
    
    # Parse enable_merged_inspection setting
    try:
        settings['enable_merged_inspection'] = config.getboolean('General', 'enable_merged_inspection')
    except (configparser.NoOptionError, ValueError):
        # Default to True if not specified or invalid
        settings['enable_merged_inspection'] = True
        
    # Parse original_directory_structure setting
    try:
        settings['original_directory_structure'] = config.getboolean('General', 'original_directory_structure')
    except (configparser.NoOptionError, ValueError):
        # Default to False if not specified or invalid
        settings['original_directory_structure'] = False

    # Parse ParseFlags section - get all items as integers except parse_lang
    for key, value in config.items('ParseFlags'):
        if key == 'parse_lang':
            # parse_lang is a string value (ALL, PRIMARY, or language codes)
            settings[key] = config.get('ParseFlags', key)
        else:
            # All other parse flags are integers
            settings[key] = config.getint('ParseFlags', key)
    
    # Parse Performance section
    settings['batch_size'] = config.getint('Performance', 'batch_size')
    
    # Handle chunk_size special case - support AUTO calculation
    try:
        chunk_value = config.get('Performance', 'chunk_size')
        if chunk_value.upper() == "AUTO":
            # Import here to avoid circular imports
            from utils import calculate_optimal_chunk_size
            settings['chunk_size'] = calculate_optimal_chunk_size()
        else:
            settings['chunk_size'] = int(chunk_value)
    except (ValueError, configparser.NoOptionError):
        # If it's not defined or not valid, calculate automatically
        from utils import calculate_optimal_chunk_size
        settings['chunk_size'] = calculate_optimal_chunk_size()
        logger.warning("chunk_size not specified or invalid, using auto-calculation")
    
    # Handle cpu_count special case
    try:
        cpu_value = config.get('Performance', 'cpu_count')
        if cpu_value.upper() == "ALL" or int(cpu_value) == 0:
            settings['cpu_count'] = multiprocessing.cpu_count()
        else:
            settings['cpu_count'] = min(int(cpu_value), multiprocessing.cpu_count())
    except (ValueError, configparser.NoOptionError):
        # If it's not defined or not valid, default to all cores
        settings['cpu_count'] = multiprocessing.cpu_count()
    
    # Handle memory_limit special case
    try:
        memory_value = config.get('Performance', 'memory_limit')
        if memory_value.upper() == "ALL":
            # Use 80% of available memory (leave 20% for OS and other processes)
            total_memory_gb = psutil.virtual_memory().total / (1024**3)
            settings['memory_limit'] = int(total_memory_gb * 0.8)
        else:
            settings['memory_limit'] = config.getint('Performance', 'memory_limit')
    except (ValueError, configparser.NoOptionError):
        # If it's not defined or not valid, default to 8GB
        settings['memory_limit'] = DEFAULT_CONFIG['memory_limit']
        logger.warning("Memory limit not specified or invalid, defaulting to 8GB")
    
    # Create temp directory path based on destination path
    settings['temp_dir'] = os.path.join(settings['destination_path'], "temp_files")
    
    # Parse vpatent_creation section if it exists
    if config.has_section('vpatent_creation'):
        # Parse global priority
        global_priority_str = config.get('vpatent_creation', 'global_priority', fallback='')
        if global_priority_str.strip():
            settings['global_priority'] = [k.strip().upper() for k in global_priority_str.split(',') if k.strip()]
        else:
            settings['global_priority'] = DEFAULT_CONFIG['global_priority']
        
        # Parse field-specific priorities
        settings['field_priorities'] = {}
        for option, value in config.items('vpatent_creation'):
            if option != 'global_priority' and option.endswith('_priority'):
                # Extract field name (remove '_priority' suffix)
                field_name = option[:-9]  # Remove '_priority'
                if value.strip():
                    field_priority = [k.strip().upper() for k in value.split(',') if k.strip()]
                    settings['field_priorities'][field_name] = field_priority
    else:
        settings['global_priority'] = DEFAULT_CONFIG['global_priority']
        settings['field_priorities'] = DEFAULT_CONFIG['field_priorities']
    
    # Create individual VP directory path
    settings['individual_vp_dir'] = os.path.join(settings['destination_path'], "individual_vpatents")

    return settings


def get_default_config_path():
    """
    Get the default configuration file path relative to the script directory
    
    Returns:
        str: Path to the default config.ini file
    """
    script_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory, "config.ini")


def validate_config(config):
    """
    Validate configuration settings
    
    Args:
        config (dict): Configuration dictionary
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Validate that input paths exist
    input_paths = ['vertical_origin_path']
    for path_key in input_paths:
        if not os.path.exists(config[path_key]):
            raise ValueError(f"Input path does not exist: {config[path_key]} (from {path_key})")
    
    # Note: destination_path will be created if it doesn't exist, so we don't validate its existence
    
    # Validate patent office
    if config['patent_office'] not in VALID_PATENT_OFFICES:
        raise ValueError(f"Invalid patent office: {config['patent_office']}")
    
    # Validate output formats
    for fmt in config['output_formats']:
        if fmt not in VALID_OUTPUT_FORMATS:
            raise ValueError(f"Invalid output format: {fmt}")
    
    # Validate performance settings
    if config['batch_size'] <= 0:
        raise ValueError("batch_size must be greater than 0")
    
    if config['chunk_size'] <= 0:
        raise ValueError("chunk_size must be greater than 0")
    
    if config['memory_limit'] <= 0:
        raise ValueError("memory_limit must be greater than 0")


class ConfigManager:
    """
    Configuration manager class for easier access to configuration values
    """
    
    def __init__(self, config_file_path=None):
        """
        Initialize configuration manager
        
        Args:
            config_file_path (str, optional): Path to configuration file. 
                                            If None, uses default path.
        """
        if config_file_path is None:
            config_file_path = get_default_config_path()
        
        self.config_file_path = config_file_path
        self.config = load_config(config_file_path)
        validate_config(self.config)
    
    def get(self, key, default=None):
        """
        Get configuration value
        
        Args:
            key (str): Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)
    
    def __getitem__(self, key):
        """
        Get configuration value using dictionary notation
        
        Args:
            key (str): Configuration key
            
        Returns:
            Configuration value
        """
        return self.config[key]
    
    def __contains__(self, key):
        """
        Check if configuration key exists
        
        Args:
            key (str): Configuration key
            
        Returns:
            bool: True if key exists
        """
        return key in self.config
    
    def reload(self):
        """
        Reload configuration from file
        """
        self.config = load_config(self.config_file_path)
        validate_config(self.config)
    
    def get_all(self):
        """
        Get all configuration values
        
        Returns:
            dict: All configuration values
        """
        return self.config.copy()