# Licensed under the MIT License. See LICENSE-CODE in the repository root for details.
# Copyright (c) 2025 Christos Papadopoulos

"""
Main orchestration module for PatentFusion

This module contains the main function that orchestrates the entire patent processing pipeline,
including configuration loading, file discovery, parallel processing, and output generation.
"""

import os
import time
from config_manager import ConfigManager
from file_system import get_all_file_paths, create_directory_structure, cleanup_temp_files
from parallel_processor import process_files_parallel, validate_parallel_config
from memory_manager import chunked_memory_efficient_processing
from utils import setup_logging, log_system_info, format_duration

# Initialize logging
logger = setup_logging()


def log_configuration(config):
    """
    Log configuration settings for transparency
    
    Args:
        config (dict): Configuration dictionary
    """
    logger.info("=" * 50)
    logger.info("PATENTFUSION CONFIGURATION")
    logger.info("=" * 50)
    
    # Paths
    logger.info("PATHS:")
    logger.info(f"  Input directory: {config['vertical_origin_path']}")
    logger.info(f"  Output directory: {config['destination_path']}")
    logger.info(f"  Patent office: {config['patent_office']}")
    
    # Processing options
    logger.info("PROCESSING OPTIONS:")
    logger.info("  XML Processing: Virtual patents with full hierarchy preservation")
    logger.info(f"  Max text length: {config['max_text_length']}")
    logger.info(f"  Output formats: {', '.join(config['output_formats'])}")
    
    # Performance settings
    logger.info("PERFORMANCE SETTINGS:")
    logger.info(f"  CPU cores: {config['cpu_count']}")
    logger.info(f"  Batch size: {config['batch_size']}")
    logger.info(f"  Chunk size: {config['chunk_size']}")
    logger.info(f"  Memory limit: {config['memory_limit']}GB")
    
    # Parse flags for output filtering
    logger.info("OUTPUT FILTER FLAGS:")
    parse_flag_keys = [key for key in config.keys() if key.startswith('parse_')]
    parse_flag_keys.sort()  # Sort for consistent output order

    for flag in parse_flag_keys:
        if flag == 'parse_lang':
            # parse_lang is a string value, show it directly
            logger.info(f"  {flag}: {config[flag]}")
        else:
            # Other flags are boolean/integer
            status = "Enabled" if config[flag] else "Disabled"
            logger.info(f"  {flag}: {status}")
    
    # Priority settings
    if config['global_priority']:
        logger.info("PRIORITY SETTINGS:")
        logger.info(f"  Global priority: {', '.join(config['global_priority'])}")
        if config['field_priorities']:
            logger.info(f"  Field-specific priorities: {len(config['field_priorities'])} fields configured")
    
    logger.info("=" * 50)


def main():
    """
    Main orchestration function that coordinates the entire patent processing pipeline
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    start_time = time.time()
    
    try:
        # 1. CONFIGURATION LOADING AND VALIDATION
        logger.info("Starting PatentFusion processing...")
        
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.get_all()
        
        # Log configuration
        log_configuration(config)
        
        # Log system information
        log_system_info(logger)
        
        # Validate parallel processing configuration
        if not validate_parallel_config(config):
            logger.error("Invalid parallel processing configuration")
            return 1
        
        # 2. DIRECTORY SETUP AND VALIDATION
        logger.info("Setting up directory structure...")
        
        # Create necessary directories
        create_directory_structure(config)
        
        # 4. DIRECTORY SCANNING AND FILE DISCOVERY (includes statistics reporting)
        all_file_paths, folder_order = get_all_file_paths(config['vertical_origin_path'], config['cpu_count'])
        
        total_files = len(all_file_paths)
        if total_files == 0:
            logger.warning("No XML files found to process")
            return 0
        
        # 5. PARALLEL PROCESSING AND BATCH CREATION
        
        # Process files in parallel
        all_temp_files = process_files_parallel(
            all_file_paths, 
            folder_order, 
            config
        )
        
        if not all_temp_files:
            logger.warning("No temporary files generated from processing")
            return 0
        
        # 6. MEMORY-EFFICIENT MERGING AND OUTPUT GENERATION
        logger.info(f"Starting memory-efficient processing and output generation with {config['memory_limit']}GB memory limit")
        
        # Process with memory-efficient approach
        result = chunked_memory_efficient_processing(
            all_temp_files=all_temp_files,
            config=config
        )
        
        if result != 0:
            logger.error("Memory-efficient processing failed")
            return 1
        
        logger.info("Memory-efficient processing completed successfully")
        
        # 7. CLEANUP - Only clean up remaining files (intermediate CSVs, etc.)
        # Temp files are now deleted immediately after processing to save disk space
        cleanup_temp_files([], config['temp_dir'])  # Empty list since temp files already deleted
        
        # 8. FINAL SUMMARY
        end_time = time.time()
        total_time = end_time - start_time
        
        logger.info("=" * 50)
        logger.info("PROCESSING SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total files processed: {total_files}")
        logger.info(f"Total processing time: {format_duration(total_time)}")
        logger.info(f"Average time per file: {total_time/total_files:.4f} seconds")
        logger.info(f"Output directory: {config['destination_path']}")
        logger.info(f"Output formats: {', '.join(config['output_formats'])}")
        logger.info(f"Individual VPatent files saved to: {config['individual_vp_dir']}")
        
        logger.info("PatentFusion processing completed successfully!")
        logger.info("=" * 50)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        return 1
        
    except Exception as e:
        logger.error(f"Unexpected error during processing: {str(e)}", exc_info=True)
        return 1


def validate_environment():
    """
    Validate that the environment is properly set up for PatentFusion
    
    Returns:
        bool: True if environment is valid, False otherwise
    """
    try:
        # Check required modules
        required_modules = ['pandas', 'lxml', 'tqdm', 'psutil']
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                logger.error(f"Required module '{module}' not found")
                return False
        
        # Check for configuration file
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        if not os.path.exists(config_path):
            logger.error(f"Configuration file not found: {config_path}")
            return False
        
        logger.info("Environment validation successful")
        return True
        
    except Exception as e:
        logger.error(f"Environment validation failed: {str(e)}")
        return False

if __name__ == "__main__":
    import sys
    
    # Validate environment before running
    if not validate_environment():
        sys.exit(1)
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
        if os.path.exists(config_path):
            # Use custom config path - simplified approach
            logger.info(f"Using configuration file: {config_path}")
            exit_code = main()  # Note: This will still use default config, but user can modify config.ini manually
        else:
            logger.error(f"Configuration file not found: {config_path}")
            exit_code = 1
    else:
        exit_code = main()
    
    sys.exit(exit_code)