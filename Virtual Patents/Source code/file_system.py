# Licensed under the MIT License. See LICENSE-CODE in the repository root for details.
# Copyright (c) 2025 Christos Papadopoulos

"""
File System Operations for PatentFusion

This module handles file discovery, directory traversal, and file system operations
for patent XML processing.
"""

import os
import logging
import multiprocessing
from utils import ensure_directory_exists

logger = logging.getLogger(__name__)

def scan_directory(directory):
    """
    Scan a single directory (not recursively) for XML files and collect statistics
    
    Args:
        directory (str): Directory path to scan
        
    Returns:
        tuple: (directory_path, list_of_xml_files, directory_stats)
            - directory_stats: dict with file counts and sizes for this directory
    """
    file_paths = []
    dir_stats = {
        'total_files': 0,
        'xml_files': 0,
        'total_size_mb': 0,
        'xml_file_sizes': []  # For calculating min/max later
    }
    
    try:
        for file in sorted(os.listdir(directory)):
            full_path = os.path.join(directory, file)
            if os.path.isfile(full_path):
                dir_stats['total_files'] += 1
                
                # Get file size
                try:
                    file_size = os.path.getsize(full_path)
                    file_size_mb = file_size / (1024 * 1024)
                    dir_stats['total_size_mb'] += file_size_mb
                    
                    if file.endswith('.xml'):
                        file_paths.append(full_path)
                        dir_stats['xml_files'] += 1
                        dir_stats['xml_file_sizes'].append(file_size_mb)
                except OSError:
                    # Skip files we can't get size for
                    pass
                    
    except (OSError, PermissionError) as e:
        logger.warning(f"Error scanning directory {directory}: {e}")
    
    return directory, file_paths, dir_stats

def get_dirs_chunk(start_dir):
    """
    Get all directories recursively from a starting directory
    
    Args:
        start_dir (str): Starting directory path
        
    Returns:
        list: List of directory paths
    """
    dirs_found = []
    try:
        for root, dirs, _ in os.walk(start_dir):
            dirs_found.append(root)
            # Sort directories for deterministic order
            dirs.sort()
    except (OSError, PermissionError) as e:
        logger.warning(f"Error walking directory {start_dir}: {e}")
    
    return dirs_found

def get_all_file_paths(root_dir, cpu_count=None):
    """
    Get all file paths in a directory structure with ordered traversal using multiprocessing
    
    Args:
        root_dir (str): Root directory to scan
        cpu_count (int, optional): Number of CPU cores to use. If None, uses all available.
        
    Returns:
        tuple: (all_file_paths, folder_order)
            - all_file_paths: List of all XML file paths found
            - folder_order: Dictionary mapping relative directory paths to order indices
    """
    if cpu_count is None:
        cpu_count = multiprocessing.cpu_count()
    
    # Validate root directory
    if not os.path.exists(root_dir):
        raise ValueError(f"Root directory does not exist: {root_dir}")
    
    if not os.path.isdir(root_dir):
        raise ValueError(f"Root path is not a directory: {root_dir}")
    
    # Get immediate subdirectories to use as starting points
    immediate_subdirs = []
    try:
        for d in sorted(os.listdir(root_dir)):
            full_path = os.path.join(root_dir, d)
            if os.path.isdir(full_path):
                immediate_subdirs.append(full_path)
    except (OSError, PermissionError) as e:
        logger.warning(f"Error listing root directory {root_dir}: {e}")
    
    # If there are no subdirectories, just use the root
    if not immediate_subdirs:
        immediate_subdirs = [root_dir]
    
    # Use multiprocessing to discover directories in parallel
    try:
        with multiprocessing.Pool(processes=cpu_count) as pool:
            nested_dirs_results = pool.map(get_dirs_chunk, immediate_subdirs)
    except Exception as e:
        logger.error(f"Error during parallel directory discovery: {e}")
        # Fallback to sequential processing
        nested_dirs_results = [get_dirs_chunk(subdir) for subdir in immediate_subdirs]
    
    # Flatten the results
    all_dirs = [dir_path for sublist in nested_dirs_results for dir_path in sublist]
    
    # Ensure root_dir is included and there are no duplicates
    if root_dir not in all_dirs:
        all_dirs.insert(0, root_dir)
    all_dirs = list(dict.fromkeys(all_dirs))  # Remove duplicates while preserving order
    
    # Sort all directories for deterministic order
    all_dirs.sort()
    
    # Use multiprocessing to scan directories in parallel
    try:
        with multiprocessing.Pool(processes=cpu_count) as pool:
            results = pool.map(scan_directory, all_dirs)
    except Exception as e:
        logger.error(f"Error during parallel directory scanning: {e}")
        # Fallback to sequential processing
        results = [scan_directory(dir_path) for dir_path in all_dirs]
    
    # Process results and create folder_order, aggregate statistics
    all_file_paths = []
    folder_order = {}
    
    # Initialize aggregate statistics
    total_stats = {
        'total_directories': len(all_dirs),
        'total_files': 0,
        'xml_files': 0,
        'total_size_mb': 0,
        'largest_file_mb': 0,
        'smallest_file_mb': float('inf')
    }
    
    all_xml_sizes = []
    
    # Process each directory's results
    for idx, (dir_path, files, dir_stats) in enumerate(results):
        relative_dir = os.path.relpath(dir_path, root_dir)
        folder_order[relative_dir] = idx
        all_file_paths.extend(files)
        
        # Aggregate statistics
        total_stats['total_files'] += dir_stats['total_files']
        total_stats['xml_files'] += dir_stats['xml_files']
        total_stats['total_size_mb'] += dir_stats['total_size_mb']
        all_xml_sizes.extend(dir_stats['xml_file_sizes'])
    
    # Calculate min/max XML file sizes
    if all_xml_sizes:
        total_stats['largest_file_mb'] = max(all_xml_sizes)
        total_stats['smallest_file_mb'] = min(all_xml_sizes)
    else:
        total_stats['smallest_file_mb'] = 0
    
    # Sort all file paths to maintain deterministic order
    all_file_paths.sort()
    
    # Log directory statistics (replacing the separate log_directory_stats call)
    logger.info(f"Directory Statistics for {root_dir}:")
    logger.info(f"  Total directories: {total_stats['total_directories']}")
    logger.info(f"  Total files: {total_stats['total_files']}")
    logger.info(f"  XML files: {total_stats['xml_files']}")
    logger.info(f"  Total size: {total_stats['total_size_mb']:.2f} MB")
    logger.info(f"  Largest XML file: {total_stats['largest_file_mb']:.2f} MB")
    logger.info(f"  Smallest XML file: {total_stats['smallest_file_mb']:.2f} MB")
    
    return all_file_paths, folder_order

def create_directory_structure(config):
    """
    Create necessary directory structure for processing
    
    Args:
        config (dict): Configuration dictionary
        
    Returns:
        dict: Dictionary with created directory paths
    """
    directories = {}
    
    # Create output directory if it doesn't exist
    ensure_directory_exists(config['destination_path'])
    directories['output'] = config['destination_path']
    
    # Create individual VP directory (always needed for virtual patent workflow)
    ensure_directory_exists(config['individual_vp_dir'])
    directories['individual_vp'] = config['individual_vp_dir']
    logger.info(f"Individual VP files will be saved to: {config['individual_vp_dir']}")
    
    # Pre-create subdirectories for all output formats and patent office
    # This prevents race conditions in multiprocessing
    patent_office = config['patent_office']
    output_formats = config['output_formats']
    
    # Create subdirectories for individual virtual patents (only if not using original directory structure)
    use_original_structure = config.get('original_directory_structure', False)
    if not use_original_structure:
        for fmt in output_formats:
            format_dir = os.path.join(config['individual_vp_dir'], patent_office, fmt)
            ensure_directory_exists(format_dir)
            logger.debug(f"Created format directory: {format_dir}")
    else:
        logger.info("Skipping pre-creation of format directories due to original_directory_structure setting")
    
    # Create a temporary directory for intermediate files
    ensure_directory_exists(config['temp_dir'])
    directories['temp'] = config['temp_dir']
    
    # Create merged patents inspection directory conditionally
    enable_merged_inspection = config.get('enable_merged_inspection', True)
    if enable_merged_inspection:
        merged_dir = os.path.join(config['destination_path'], "merged_patents_inspection")
        ensure_directory_exists(merged_dir)
        directories['merged'] = merged_dir
        logger.info(f"Merged patents inspection folder ready: {merged_dir}")
        
        # Pre-create subdirectories for merged patents inspection (only if not using original directory structure)
        if not use_original_structure:
            for fmt in output_formats:
                format_dir = os.path.join(merged_dir, patent_office, fmt)
                ensure_directory_exists(format_dir)
                logger.debug(f"Created merged patents format directory: {format_dir}")
        else:
            logger.info("Skipping pre-creation of merged inspection format directories due to original_directory_structure setting")
    else:
        directories['merged'] = None
        logger.info("Merged patents inspection directory creation disabled in config")
    
    return directories

def cleanup_temp_files(temp_file_paths, temp_dir):
    """
    Clean up temporary files and directories
    
    Args:
        temp_file_paths (list): List of temporary file paths to remove
        temp_dir (str): Temporary directory path
    """
    if temp_file_paths:
        logger.info("Cleaning up remaining temporary files...")
        
        # Remove individual temporary files
        for file_path in temp_file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Removed temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {file_path} - {str(e)}")
    else:
        logger.info("Cleaning up temporary directory and intermediate files...")
    
    # Remove intermediate CSV files (intermediate_*.csv)
    try:
        if os.path.exists(temp_dir):
            import glob
            intermediate_files = glob.glob(os.path.join(temp_dir, "intermediate_*.csv"))
            for intermediate_file in intermediate_files:
                try:
                    os.remove(intermediate_file)
                    logger.debug(f"Removed intermediate file: {intermediate_file}")
                except Exception as e:
                    logger.warning(f"Failed to remove intermediate file: {intermediate_file} - {str(e)}")
    except Exception as e:
        logger.warning(f"Error during intermediate file cleanup: {str(e)}")
    
    # Clean up temp directory if it's empty
    try:
        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)
            logger.info(f"Removed empty temporary directory: {temp_dir}")
    except Exception as e:
        logger.warning(f"Failed to remove temporary directory: {temp_dir} - {str(e)}")

def cleanup_single_temp_file(temp_file_path):
    """
    Clean up a single temporary file immediately after processing
    
    Args:
        temp_file_path (str): Path to temporary file to remove
        
    Returns:
        bool: True if successfully removed, False otherwise
    """
    try:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.debug(f"Immediately removed processed temp file: {temp_file_path}")
            return True
        else:
            logger.debug(f"Temp file already removed or doesn't exist: {temp_file_path}")
            return True
    except Exception as e:
        logger.warning(f"Failed to remove temp file {temp_file_path}: {str(e)}")
        return False

def get_file_batches(file_paths, batch_size):
    """
    Split file paths into batches of specified size while keeping files 
    for the same patent number together
    
    Args:
        file_paths (list): List of file paths
        batch_size (int): Number of files per batch
        
    Returns:
        list: List of batches (each batch is a list of file paths)
    """
    # First, group files by patent number to ensure they stay together
    patent_groups = {}
    for file_path in file_paths:
        try:
            file_name = os.path.basename(file_path)
            patent_number = file_name.split(".")[0].split("-")[1]
            
            if patent_number not in patent_groups:
                patent_groups[patent_number] = []
            patent_groups[patent_number].append(file_path)
        except Exception as e:
            logger.debug(f"Could not extract patent number from {file_name}: {e}")
            # Add files we can't parse to a special group
            if 'unparseable' not in patent_groups:
                patent_groups['unparseable'] = []
            patent_groups['unparseable'].append(file_path)
    
    # Now create batches ensuring patent groups stay together
    # Minimum batch size to handle edge cases (e.g., patents with many kind codes)
    MIN_BATCH_SIZE = 10
    
    batches = []
    current_batch = []
    
    for patent_number, files in patent_groups.items():
        # If adding this patent group would exceed batch size and current batch meets minimum size
        if len(current_batch) + len(files) > batch_size and len(current_batch) >= MIN_BATCH_SIZE:
            # Start a new batch
            batches.append(current_batch)
            current_batch = []
        
        # Add all files for this patent to the current batch
        current_batch.extend(files)
        
        # If current batch is at or over batch size and meets minimum size, finalize it
        if len(current_batch) >= batch_size and len(current_batch) >= MIN_BATCH_SIZE:
            batches.append(current_batch)
            current_batch = []
    
    # Handle remaining files - merge with last batch if too small
    if current_batch:
        if len(current_batch) >= MIN_BATCH_SIZE or not batches:
            # Either meets minimum size or it's the only batch
            batches.append(current_batch)
        else:
            # Merge small remainder with the last batch to avoid tiny batches
            if batches:
                batches[-1].extend(current_batch)
            else:
                # No existing batches, keep as is
                batches.append(current_batch)
    
    # Log batch statistics
    batch_sizes = [len(batch) for batch in batches]
    min_size = min(batch_sizes) if batch_sizes else 0
    max_size = max(batch_sizes) if batch_sizes else 0
    avg_size = sum(batch_sizes) / len(batch_sizes) if batch_sizes else 0
    
    logger.info(f"Created {len(batches)} batches with {batch_size} files each, ensuring patent groups stay together")
    logger.info(f"Batch sizes - Min: {min_size}, Max: {max_size}, Avg: {avg_size:.1f}")
    logger.debug(f"Patent groups found: {len(patent_groups)} (including {len(patent_groups.get('unparseable', []))} unparseable files)")
    
    return batches


def create_temp_file_path(temp_dir, batch_id, file_type='csv'):
    """
    Create a temporary file path for intermediate processing
    
    Args:
        temp_dir (str): Temporary directory path
        batch_id (int): Batch identifier
        file_type (str): File extension (default: 'csv')
        
    Returns:
        str: Temporary file path
    """
    return os.path.join(temp_dir, f"temp_batch_{batch_id}.{file_type}")