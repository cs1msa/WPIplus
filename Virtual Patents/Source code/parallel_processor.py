# Licensed under the MIT License. See LICENSE-CODE in the repository root for details.
# Copyright (c) 2025 Christos Papadopoulos

"""
Parallel Processor for PatentFusion

This module handles multiprocessing coordination, worker management, and
parallel processing of patent data for optimal performance.
"""

import os
import gc
import time
import logging
import multiprocessing
import threading
import tqdm
from file_system import get_file_batches, create_temp_file_path
from xml_parser import process_file_batch
from utils import get_memory_usage_gb, format_duration
from lxml import etree

logger = logging.getLogger(__name__)

def chunk_processor_with_progress(chunk_args):
    """
    Process a chunk of batches with shared progress tracking
    
    Args:
        chunk_args (tuple): Tuple containing (batches, folder_order, chunk_id, chunk_start, chunk_end, config, progress_dict, progress_lock)
        
    Returns:
        list: List of result file paths
    """
    batches, folder_order, chunk_id, chunk_start, chunk_end, config, progress_dict, progress_lock = chunk_args
    
    # Get process ID for uniqueness
    pid = os.getpid()
    
    results_files = []
    total_batches = chunk_end - chunk_start
    
    # Initialize progress tracking for this worker
    with progress_lock:
        progress_dict[chunk_id] = {
            'current': 0,
            'total': total_batches,
            'memory': 0.0,
            'desc': f"Worker {chunk_id}"
        }
    
    
    try:
        for i, batch in enumerate(batches[chunk_start:chunk_end]):
            batch_id = f"{chunk_id}_{i}_{pid}"
            
            try:
                # Process batch
                result_data = process_file_batch(batch, folder_order, batch_id, config)
                
                # Save virtual patents to temporary file
                if result_data:
                    temp_file_path = create_temp_file_path(config['temp_dir'], batch_id, 'xml')
                    
                    # Save virtual patents as XML
                    save_virtual_patents_to_temp_file(result_data, temp_file_path)
                    
                    if os.path.exists(temp_file_path) and os.path.getsize(temp_file_path) > 0:
                        results_files.append(temp_file_path)
                    
                    # Clear memory
                    del result_data
                    gc.collect()
                
                # Update progress in shared dictionary (replace entire dict for manager sync)
                with progress_lock:
                    worker_info = dict(progress_dict[chunk_id])
                    worker_info['current'] = i + 1
                    progress_dict[chunk_id] = worker_info
                
                # Update memory usage periodically
                if (i + 1) % 10 == 0:
                    memory_usage = get_memory_usage_gb()
                    with progress_lock:
                        worker_info = dict(progress_dict[chunk_id])
                        worker_info['memory'] = memory_usage
                        progress_dict[chunk_id] = worker_info
                
            except Exception as e:
                logger.error(f"Error processing batch {batch_id}: {e}")
                with progress_lock:
                    worker_info = dict(progress_dict[chunk_id])
                    worker_info['current'] = i + 1
                    progress_dict[chunk_id] = worker_info
                continue
    
    finally:
        # Mark as completed
        with progress_lock:
            worker_info = dict(progress_dict[chunk_id])
            worker_info['current'] = total_batches
            progress_dict[chunk_id] = worker_info
        
        # Clean up worker resources
        gc.collect()
    
    return results_files

def save_virtual_patents_to_temp_file(virtual_patents, temp_file_path):
    """
    Save virtual patents to temporary XML file
    
    Args:
        virtual_patents (list): List of virtual patent XML elements
        temp_file_path (str): Path to temporary file
    """
    try:
        # Create root element for multiple virtual patents
        root = etree.Element("virtual-patents")
        
        # Add each virtual patent to the root
        for virtual_patent in virtual_patents:
            root.append(virtual_patent)
        
        # Write to file
        tree = etree.ElementTree(root)
        tree.write(temp_file_path, encoding="utf-8", xml_declaration=True, pretty_print=True)
        
    except Exception as e:
        logger.error(f"Error saving virtual patents to temp file {temp_file_path}: {e}")
        raise

def parallel_batch_processor(all_file_paths, folder_order, config):
    """
    Process file batches in parallel using multiprocessing
    
    Args:
        all_file_paths (list): List of all file paths to process
        folder_order (dict): Dictionary mapping folder names to order indices
        config (dict): Configuration dictionary
        
    Returns:
        list: List of temporary file paths containing results
    """
    batch_size = config['batch_size']
    cpu_count = config['cpu_count']
    
    # Create batches
    batches = get_file_batches(all_file_paths, batch_size)
    
    # Calculate chunk size for parallel processing
    chunk_size = max(1, len(batches) // cpu_count)
    
    # Create chunks for parallel processing
    chunks = []
    for i in range(0, len(batches), chunk_size):
        chunks.append((i, min(i + chunk_size, len(batches))))
    
    # If we have fewer chunks than CPU cores, adjust the CPU count
    effective_cpu_count = min(cpu_count, len(chunks))
    
    logger.info(f"Processing {len(batches)} batches in {len(chunks)} chunks using {effective_cpu_count} processes")
    
    # Process chunks in parallel with individual progress bars
    all_temp_files = []
    
    try:
        # Create shared progress dictionary with proper locking
        with multiprocessing.Manager() as manager:
            progress_dict = manager.dict()
            progress_lock = manager.Lock()
            
            with multiprocessing.Pool(processes=effective_cpu_count) as pool:
                # Create arguments for each chunk
                chunk_args = []
                for chunk_id, (chunk_start, chunk_end) in enumerate(chunks):
                    args = (batches, folder_order, chunk_id, chunk_start, chunk_end, config, progress_dict, progress_lock)
                    chunk_args.append(args)
                
                # Add some spacing for the progress bars
                print(f"\nStarting parallel processing with {len(chunks)} workers:")
                print("=" * 60)
                
                # Create progress bars for each worker (start with total=1, will be updated)
                progress_bars = {}
                for chunk_id in range(len(chunks)):
                    progress_bars[chunk_id] = tqdm.tqdm(total=1, desc=f"Worker {chunk_id}", 
                                                       position=chunk_id, leave=True, 
                                                       dynamic_ncols=True)
                
                # Overall progress bar
                overall_pbar = tqdm.tqdm(total=len(batches), desc="Overall Progress", 
                                       position=len(chunks), leave=True, dynamic_ncols=True)
                
                
                # Start all workers
                results = []
                for args in chunk_args:
                    result = pool.apply_async(chunk_processor_with_progress, (args,))
                    results.append(result)
                
                # Monitor progress in a separate thread
                def monitor_progress():
                    last_totals = {}
                    loop_count = 0
                    
                    while any(not r.ready() for r in results):
                        overall_total = 0
                        loop_count += 1
                        
                        try:
                            # Create a copy of the dictionary to avoid concurrent access issues
                            with progress_lock:
                                progress_data = dict(progress_dict)
                            
                            for chunk_id in range(len(chunks)):
                                if chunk_id in progress_data:
                                    worker_info = progress_data[chunk_id]
                                    current = worker_info['current']
                                    total = worker_info['total']
                                    memory = worker_info.get('memory', 0.0)
                                    
                                    # Update individual worker progress bar
                                    if chunk_id not in last_totals:
                                        progress_bars[chunk_id].total = total
                                        last_totals[chunk_id] = 0
                                    
                                    if current > last_totals[chunk_id]:
                                        diff = current - last_totals[chunk_id]
                                        progress_bars[chunk_id].update(diff)
                                        last_totals[chunk_id] = current
                                    
                                    # Update postfix with memory info
                                    if memory > 0:
                                        progress_bars[chunk_id].set_postfix({"Memory": f"{memory:.1f}GB"})
                                    
                                    overall_total += current
                            
                            # Update overall progress
                            if overall_total > overall_pbar.n:
                                overall_pbar.update(overall_total - overall_pbar.n)
                                
                        except Exception as e:
                            logger.error(f"Error in progress monitoring: {e}")
                        
                        time.sleep(0.05)  # Much faster polling
                
                # Start monitoring thread AFTER results are defined
                monitor_thread = threading.Thread(target=monitor_progress)
                monitor_thread.daemon = True
                monitor_thread.start()
                
                # Give the monitoring thread a moment to start
                time.sleep(0.1)
                
                # Wait for all results
                for result in results:
                    try:
                        temp_files = result.get(timeout=86400)  # 24 hour timeout
                        all_temp_files.extend(temp_files)
                    except Exception as e:
                        logger.error(f"Error getting result from worker: {e}")
                
                # Wait for monitoring thread to finish
                monitor_thread.join(timeout=1)
                
                # Close all progress bars
                for pbar in progress_bars.values():
                    pbar.close()
                overall_pbar.close()
                
                # Clear references to manager objects to prevent leaks
                progress_dict.clear()
                del progress_dict
                
                # Add spacing after progress bars
                print("=" * 60 + "\n")
    
    except Exception as e:
        logger.error(f"Error during parallel processing: {e}")
        # Force cleanup of any remaining resources
        gc.collect()
    
    # Parallel processing complete - detailed logging handled by process_files_parallel
    
    # Final cleanup to prevent semaphore leaks
    gc.collect()
    
    return all_temp_files


def process_files_parallel(file_paths, folder_order, config):
    """
    High-level function to process files in parallel
    
    Args:
        file_paths (list): List of file paths to process
        folder_order (dict): Dictionary mapping folder names to order indices
        config (dict): Configuration dictionary
        
    Returns:
        list: List of temporary file paths containing virtual patents
    """
    if not file_paths:
        logger.warning("No files to process")
        return []
    
    start_time = time.time()
    logger.info(f"Starting parallel processing of {len(file_paths)} files")
    
    # Process files in parallel
    temp_files = parallel_batch_processor(file_paths, folder_order, config)
    
    # Log completion
    end_time = time.time()
    processing_time = end_time - start_time
    logger.info(f"Parallel processing completed in {format_duration(processing_time)} and generated {len(temp_files)} temporary files")
    
    return temp_files


def validate_parallel_config(config):
    """
    Validate parallel processing configuration
    
    Args:
        config (dict): Configuration dictionary
        
    Returns:
        bool: True if configuration is valid
    """
    try:
        # Check CPU count
        if config['cpu_count'] <= 0:
            logger.error("CPU count must be greater than 0")
            return False
        
        if config['cpu_count'] > multiprocessing.cpu_count():
            logger.warning(f"Requested CPU count {config['cpu_count']} exceeds available {multiprocessing.cpu_count()}")
        
        # Check batch size
        if config['batch_size'] <= 0:
            logger.error("Batch size must be greater than 0")
            return False
        
        # Check memory limit
        if config['memory_limit'] <= 0:
            logger.error("Memory limit must be greater than 0")
            return False
        
        logger.info(f"Parallel configuration validated: {config['cpu_count']} cores, "
                   f"batch size {config['batch_size']}, memory limit {config['memory_limit']}GB")
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating parallel configuration: {e}")
        return False