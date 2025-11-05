# Licensed under the MIT License. See LICENSE-CODE in the repository root for details.
# Copyright (c) 2025 Christos Papadopoulos

"""
Data Processing Module for PatentFusion

This module handles post-processing of virtual patent XML elements,
including format conversion, filtering, and file output generation.
"""

import os
import json
import logging
import pandas as pd
from lxml import etree
from output_manager import construct_original_directory_path, xml_to_hierarchical_dict
from output_manager import remove_metadata_attributes, apply_text_truncation_to_xml, xml_to_flat_dict, has_kind_merging
from utils import ensure_directory_exists

logger = logging.getLogger(__name__)

def save_individual_vpatents_sequential(virtual_patents, patent_office, output_formats, destination_path, config):
    """
    Save individual virtual patent files sequentially (without multiprocessing)
    to avoid daemon process issues when called from multiprocessing workers

    Args:
        virtual_patents (list): List of virtual patent XML elements
        patent_office (str): Patent office code (e.g., 'EP', 'CN')
        output_formats (list): List of formats to save ('csv', 'xml', 'json')
        destination_path (str): Destination directory path
        config (dict): Configuration dictionary

    Returns:
        tuple: (files_saved, merged_patents_count)
    """
    if not virtual_patents:
        return 0, 0


    files_saved = 0
    merged_patents_count = 0

    # Process each virtual patent sequentially
    for virtual_patent in virtual_patents:
        try:
            # Extract patent information
            ucid = virtual_patent.get('ucid', '')
            if ucid:
                patent_number = ucid.split('-')[1] if '-' in ucid else 'UNKNOWN'
            else:
                patent_number = 'UNKNOWN'

            # Create base filename: PatentOffice-PatentNumber-VP
            base_filename = f"{patent_office}-{patent_number}-VP"

            # Check if this is a merged patent
            is_merged_patent = has_kind_merging(virtual_patent)
            enable_merged_inspection = config.get('enable_merged_inspection', True)
            save_to_inspection = is_merged_patent and enable_merged_inspection

            # Extract source file path before removing metadata (needed for original directory structure)
            source_file_path = virtual_patent.get('_source_file_path', '')

            # Remove metadata attributes before any processing
            remove_metadata_attributes(virtual_patent)

            # Count merged patents
            if is_merged_patent:
                merged_patents_count += 1

            # Save in each requested format
            for fmt in output_formats:
                try:
                    # Check if original directory structure is enabled
                    use_original_structure = config.get('original_directory_structure', False)

                    if use_original_structure:
                        # Use pre-extracted source file path
                        if source_file_path:
                            # Construct path using original directory structure
                            original_dir = construct_original_directory_path(source_file_path, patent_office, destination_path)
                            if original_dir:
                                format_dir = original_dir
                            else:
                                # Fallback to regular structure if parsing fails
                                office_dir = os.path.join(destination_path, patent_office)
                                format_dir = os.path.join(office_dir, fmt)
                        else:
                            # Fallback to regular structure if no source path
                            office_dir = os.path.join(destination_path, patent_office)
                            format_dir = os.path.join(office_dir, fmt)
                    else:
                        # Create nested folder structure: individual_vpatents/EP/xml/
                        office_dir = os.path.join(destination_path, patent_office)
                        format_dir = os.path.join(office_dir, fmt)

                    # Ensure directories exist
                    ensure_directory_exists(format_dir)

                    output_path = os.path.join(format_dir, f"{base_filename}.{fmt}")

                    # Also prepare inspection path if needed
                    inspection_path = None
                    if save_to_inspection:
                        base_dest_path = os.path.dirname(destination_path)

                        if use_original_structure:
                            # Use original directory structure for inspection folder too
                            if source_file_path:
                                # Construct inspection path using original directory structure
                                original_dir = construct_original_directory_path(source_file_path, patent_office, base_dest_path)
                                if original_dir:
                                    # Replace the base output path with merged_patents_inspection path
                                    relative_path = os.path.relpath(original_dir, base_dest_path)
                                    inspection_dir = os.path.join(base_dest_path, "merged_patents_inspection", relative_path)
                                else:
                                    # Fallback to regular structure if parsing fails
                                    inspection_dir = os.path.join(base_dest_path, "merged_patents_inspection", patent_office, fmt)
                            else:
                                # Fallback to regular structure if no source path
                                inspection_dir = os.path.join(base_dest_path, "merged_patents_inspection", patent_office, fmt)
                        else:
                            # Use regular structure
                            inspection_dir = os.path.join(base_dest_path, "merged_patents_inspection", patent_office, fmt)

                        ensure_directory_exists(inspection_dir)
                        inspection_path = os.path.join(inspection_dir, f"{base_filename}.{fmt}")

                    if fmt == 'xml':
                        # Save XML format
                        # Config-based filtering is applied during virtual patent creation
                        apply_text_truncation_to_xml(virtual_patent, config)

                        tree = etree.ElementTree(virtual_patent)
                        tree.write(output_path, encoding="utf-8", xml_declaration=True, pretty_print=True)

                        if inspection_path:
                            tree.write(inspection_path, encoding="utf-8", xml_declaration=True, pretty_print=True)

                    elif fmt == 'csv':
                        # Save CSV format
                        record_dict = xml_to_flat_dict(virtual_patent, config)
                        df = pd.DataFrame([record_dict])
                        df.to_csv(output_path, sep=';', index=False)

                        if inspection_path:
                            df.to_csv(inspection_path, sep=';', index=False)

                    elif fmt == 'json':
                        # Save JSON format - use hierarchical dictionary to preserve XML structure
                        hierarchical_dict = xml_to_hierarchical_dict(virtual_patent, config)
                        with open(output_path, 'w', encoding='utf-8') as f:
                            json.dump(hierarchical_dict, f, ensure_ascii=False, indent=4)

                        if inspection_path:
                            with open(inspection_path, 'w', encoding='utf-8') as f:
                                json.dump(hierarchical_dict, f, ensure_ascii=False, indent=4)

                    files_saved += 1

                except Exception as e:
                    logger.error(f"Error saving {fmt} format for patent {base_filename}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error processing virtual patent: {e}")
            continue

    return files_saved, merged_patents_count