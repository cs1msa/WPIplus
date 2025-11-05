# Licensed under the MIT License. See LICENSE-CODE in the repository root for details.
# Copyright (c) 2025 Christos Papadopoulos

"""
Memory Management Module for PatentFusion

This module handles memory-efficient processing, monitoring, and optimization
for large-scale virtual patent processing.
"""

import os
import gc
import time
import json
import logging
import multiprocessing
import pandas as pd
import tqdm
from lxml import etree
from data_processor import save_individual_vpatents_sequential
from file_system import cleanup_single_temp_file
from utils import get_memory_usage_gb, format_duration

logger = logging.getLogger(__name__)

def chunked_memory_efficient_processing(all_temp_files, config):
    """
    Process virtual patent XML files with streaming multiprocessing approach

    Args:
        all_temp_files (list): List of temporary XML file paths containing virtual patents
        config (dict): Configuration dictionary

    Returns:
        int: Success code (0 for success)
    """
    logger.info(f"Starting virtual patent post-processing and file generation from {len(all_temp_files)} temporary files...")
    
    # Start timing for virtual patent processing
    vp_start_time = time.time()
    
    # Use multiprocessing to process temp files in parallel streams
    cpu_count = min(config['cpu_count'], len(all_temp_files))
    total_files_processed = 0
    
    # Create chunks for parallel processing (similar to parsing)
    chunk_size = max(1, len(all_temp_files) // cpu_count)
    chunks = []
    for i in range(0, len(all_temp_files), chunk_size):
        chunks.append(all_temp_files[i:i + chunk_size])
    
    effective_cpu_count = min(cpu_count, len(chunks))
    
    try:
        
        with multiprocessing.Manager() as manager:
            progress_dict = manager.dict()
            progress_lock = manager.Lock()
            
            with multiprocessing.Pool(processes=effective_cpu_count) as pool:
                # Add spacing and header like during parsing
                print(f"\nStarting virtual patent processing with {len(chunks)} workers:")
                print("=" * 60)
                
                # Create progress bars for each worker
                progress_bars = {}
                for chunk_id in range(len(chunks)):
                    progress_bars[chunk_id] = tqdm.tqdm(total=len(chunks[chunk_id]), 
                                                       desc=f"Worker {chunk_id}", 
                                                       position=chunk_id, leave=True, 
                                                       dynamic_ncols=True, unit="file")
                
                # Overall progress bar  
                overall_pbar = tqdm.tqdm(total=len(all_temp_files), desc="Overall Progress", 
                                       position=len(chunks), leave=True, 
                                       dynamic_ncols=True, unit="file")
                
                # Initialize progress tracking
                for chunk_id, chunk in enumerate(chunks):
                    progress_dict[chunk_id] = {
                        'current': 0,
                        'total': len(chunk),
                        'patents_processed': 0
                    }
                
                # Start async processing
                chunk_args = []
                for chunk_id, chunk in enumerate(chunks):
                    args = (chunk, config, chunk_id, progress_dict, progress_lock)
                    chunk_args.append(args)
                
                async_results = [pool.apply_async(process_temp_file_chunk_worker, args) for args in chunk_args]
                
                # Monitor progress
                completed = False
                while not completed:
                    time.sleep(0.1)
                    
                    # Update progress bars
                    overall_current = 0
                    total_patents = 0
                    
                    with progress_lock:
                        for chunk_id in range(len(chunks)):
                            if chunk_id in progress_dict:
                                worker_info = progress_dict[chunk_id]
                                current = worker_info.get('current', 0)
                                total = worker_info.get('total', 1)
                                patents = worker_info.get('patents_processed', 0)
                                
                                # Update worker progress bar
                                progress_bars[chunk_id].n = current
                                progress_bars[chunk_id].set_postfix({"Patents": patents})
                                progress_bars[chunk_id].refresh()
                                
                                overall_current += current
                                total_patents += patents
                    
                    # Update overall progress bar
                    overall_pbar.n = overall_current
                    overall_pbar.set_postfix({"Total Patents": total_patents})
                    overall_pbar.refresh()
                    
                    # Check if all workers are done
                    completed = all(result.ready() for result in async_results)
                
                # Collect results
                results = []
                for result in async_results:
                    try:
                        results.extend(result.get())
                    except Exception as e:
                        logger.error(f"Error getting worker result: {e}")
                
                # Close progress bars
                for pbar in progress_bars.values():
                    pbar.close()
                overall_pbar.close()
                
                # Add separator like during parsing
                print("=" * 60)
                
                # Aggregate results - each result is a tuple of (patents_count, merged_count)
                total_files_processed = sum(result[0] for result in results if result is not None)
                total_merged_patents = sum(result[1] for result in results if result is not None)
    
    except Exception as e:
        logger.error(f"Error in streaming multiprocessing: {e}")
        return 1
    
    # Calculate virtual patent processing duration
    vp_end_time = time.time()
    vp_duration = vp_end_time - vp_start_time
    logger.info(f"Virtual patent processing complete in {format_duration(vp_duration)}. Processed {total_files_processed} virtual patents from {len(all_temp_files)} temp files")
    
    # Log merged patents inspection if enabled and merged patents were found
    if config.get('enable_merged_inspection', True) and total_merged_patents > 0:
        merged_patents_dir = os.path.join(os.path.dirname(config['individual_vp_dir']), "merged_patents_inspection")
        logger.info(f"Successfully copied {total_merged_patents} merged patents to inspection folder: {merged_patents_dir}")
    
    return 0


def process_temp_file_chunk_worker(temp_file_chunk, config, chunk_id, progress_dict, progress_lock):
    """
    Worker function to process a chunk of temp files with progress tracking

    Args:
        temp_file_chunk (list): List of temp file paths to process
        config (dict): Configuration dictionary
        chunk_id (int): Worker ID for progress tracking
        progress_dict (dict): Shared progress dictionary
        progress_lock: Lock for progress updates

    Returns:
        list: List of (patents_count, merged_count) tuples from each file
    """
    results = []
    
    for i, temp_file_path in enumerate(temp_file_chunk):
        try:
            # Process single temp file
            patents_count, merged_count = process_single_temp_file_worker(temp_file_path, config)
            results.append((patents_count, merged_count))
            
            # Update progress
            with progress_lock:
                worker_info = dict(progress_dict[chunk_id])
                worker_info['current'] = i + 1
                worker_info['patents_processed'] = sum(r[0] for r in results if r is not None)
                progress_dict[chunk_id] = worker_info
                
        except Exception as e:
            logger.error(f"Error processing temp file {temp_file_path}: {e}")
            results.append((0, 0))
            
            # Update progress even on error
            with progress_lock:
                worker_info = dict(progress_dict[chunk_id])
                worker_info['current'] = i + 1
                worker_info['patents_processed'] = sum(r[0] for r in results if r is not None)
                progress_dict[chunk_id] = worker_info
    
    return results


def process_single_temp_file_worker(temp_file_path, config):
    """
    Worker function to process a single temp file

    Args:
        temp_file_path (str): Path to temporary XML file
        config (dict): Configuration dictionary

    Returns:
        tuple: (patents_count, merged_patents_count)

    Note:
        Temp file is immediately deleted after processing to save disk space
    """
    processed_patents = []  # Initialize to avoid scoping issues
    
    try:
        # Load virtual patents from single temp file
        virtual_patents = load_single_temp_file(temp_file_path)
        
        if not virtual_patents:
            return 0
        
        # Save individual virtual patent files WITHOUT nested multiprocessing
        # Use single-threaded approach to avoid daemon process issues
        files_saved, merged_count = save_individual_vpatents_sequential(
            virtual_patents, config['patent_office'], config['output_formats'],
            config['individual_vp_dir'], config
        )
        
        # Clean up memory
        patents_count = len(virtual_patents)
        del virtual_patents
        gc.collect()
        
        # Immediately delete the temp file to save disk space
        cleanup_single_temp_file(temp_file_path)
        
        return patents_count, merged_count
        
    except Exception as e:
        logger.error(f"Error processing temp file {temp_file_path}: {e}")
        
        # Clean up temp file even if processing failed to avoid disk space issues
        cleanup_single_temp_file(temp_file_path)
        
        return 0, 0


def load_single_temp_file(temp_file_path):
    """
    Load virtual patents from a single temporary XML file
    
    Args:
        temp_file_path (str): Path to temporary XML file
        
    Returns:
        list: List of virtual patent XML elements
    """
    try:
        # Parse temp XML file
        tree = etree.parse(temp_file_path)
        root = tree.getroot()
        
        # Extract virtual patents from the temporary file
        virtual_patents = root.xpath("//virtual-patents/*")
        
        # Clean up
        del tree, root
        gc.collect()
        
        return virtual_patents
        
    except Exception as e:
        logger.error(f"Error loading temp file {temp_file_path}: {e}")
        return []
