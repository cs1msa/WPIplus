# Licensed under the MIT License. See LICENSE-CODE in the repository root for details.
# Copyright (c) 2025 Christos Papadopoulos

"""
Output Manager for PatentFusion

This module handles output generation in multiple formats (CSV, JSON, XML),
individual patent file creation, and sample generation for inspection.
"""

import os
import logging
from utils import truncate_text

logger = logging.getLogger(__name__)

def construct_original_directory_path(source_file_path, patent_office, base_output_dir):
    """
    Construct the output path using the original dataset directory structure.
    
    Args:
        source_file_path (str): Path to the base (highest priority) source file
        patent_office (str): Patent office code (e.g., 'CN', 'EP')
        base_output_dir (str): Base output directory
        
    Returns:
        str: Output directory path in original structure format
        
    Example:
        Input: '/dataset/CN/20140820/A/000103/99/27/45/CN-103992745-A.xml'
        Output: '/results/CN/20140820/VP/000103/99/27/45/'
    """
    try:
        # Parse the source file path to extract components
        # Expected format: .../PatentOffice/Date/KindCode/DocPath/FileName.xml
        path_parts = source_file_path.split(os.sep)
        
        # Find patent office position in path
        office_index = -1
        for i, part in enumerate(path_parts):
            if part == patent_office:
                office_index = i
                break
        
        if office_index == -1 or office_index + 3 >= len(path_parts):
            return None
            
        # Extract date folder (next after patent office)
        date_folder = path_parts[office_index + 1]
        
        # Extract document path (everything after kind code folder)
        kind_code_index = office_index + 2
        doc_path_parts = path_parts[kind_code_index + 1:-1]  # Exclude filename
        doc_path = os.sep.join(doc_path_parts)
        
        # Construct new path: base_output_dir/PatentOffice/Date/VP/DocPath/
        result_path = os.path.join(
            base_output_dir,
            patent_office,
            date_folder,
            'VP',
            doc_path
        )
        
        return result_path
        
    except (IndexError, AttributeError) as e:
        logger.warning(f"Failed to parse original directory structure from {source_file_path}: {e}")
        return None

def apply_text_truncation_to_xml(element, config):
    """
    Apply text truncation to XML element and all its children
    
    Args:
        element: XML element to process
        config (dict): Configuration dictionary with max_text_length
    """
    max_length = config.get('max_text_length', 300)
    
    # Truncate element text
    if element.text and element.text.strip():
        element.text = truncate_text(element.text.strip(), max_length)
    
    # Truncate element tail text
    if element.tail and element.tail.strip():
        element.tail = truncate_text(element.tail.strip(), max_length)
    
    # Process all child elements recursively
    for child in element:
        apply_text_truncation_to_xml(child, config)

def flatten_xml_element(element, prefix, record_dict, config):
    """
    Recursively flatten XML element into a dictionary with text truncation
    
    Args:
        element: XML element to flatten
        prefix (str): Current prefix for field names
        record_dict (dict): Dictionary to store flattened data
        config (dict): Configuration dictionary with max_text_length
    """
    # Create field name
    field_name = f"{prefix}_{element.tag}" if prefix else element.tag
    
    # Add attributes as separate fields
    for attr_name, attr_value in element.attrib.items():
        attr_field_name = f"{field_name}_attr_{attr_name}"
        record_dict[attr_field_name] = attr_value
    
    # Handle text content with truncation
    if element.text and element.text.strip():
        max_length = config.get('max_text_length', 300)
        original_text = element.text.strip()
        text_content = truncate_text(original_text, max_length)
        record_dict[field_name] = text_content
        
        # Debug logging removed
    
    # Handle tail text (text that follows this element)
    if element.tail and element.tail.strip():
        tail_content = truncate_text(element.tail.strip(), config.get('max_text_length', 300))
        tail_field_name = f"{field_name}_tail"
        record_dict[tail_field_name] = tail_content
    
    # Process child elements with indexing for duplicate tag names
    child_tag_counts = {}
    for child in element:
        if hasattr(child, 'tag') and isinstance(child.tag, str):
            child_tag = child.tag
            
            # Track how many times we've seen this tag
            if child_tag not in child_tag_counts:
                child_tag_counts[child_tag] = 0
            else:
                child_tag_counts[child_tag] += 1
            
            # Create indexed field name for duplicate tags
            if child_tag_counts[child_tag] > 0:
                indexed_field_name = f"{field_name}_{child_tag}_{child_tag_counts[child_tag] + 1}"
            else:
                # First occurrence, check if there will be more
                total_count = sum(1 for c in element if hasattr(c, 'tag') and c.tag == child_tag)
                if total_count > 1:
                    indexed_field_name = f"{field_name}_{child_tag}_1"
                else:
                    indexed_field_name = field_name
            
            flatten_xml_element(child, indexed_field_name, record_dict, config)


def remove_metadata_attributes(xml_element):
    """
    Remove metadata attributes from XML element
    
    Args:
        xml_element: XML element to clean
    """
    metadata_attrs = ['xml_file_name', 'relative_dir', 'folder_index', '_source_file_path']
    for attr in metadata_attrs:
        if attr in xml_element.attrib:
            del xml_element.attrib[attr]

def xml_to_flat_dict(virtual_patent, config):
    """
    Convert virtual patent XML to flat dictionary based on config flags
    
    Args:
        virtual_patent: XML element of virtual patent
        config (dict): Configuration dictionary with parse flags
        
    Returns:
        dict: Flat dictionary representation of the patent
    """
    
    # Flatten the XML structure into a dictionary
    record_dict = {}
    flatten_xml_element(virtual_patent, '', record_dict, config)
    
    # Remove metadata fields (check for both simple and flattened names)
    metadata_keywords = {'xml_file_name', 'relative_dir', 'folder_index'}
    cleaned_record_dict = {field_name: field_value for field_name, field_value in record_dict.items() 
                          if not any(metadata_keyword in field_name for metadata_keyword in metadata_keywords)}
    
    # Apply config-based filtering (remove fields that are disabled)
    # Config-based filtering is applied during virtual patent creation
    return cleaned_record_dict

def xml_to_hierarchical_dict(virtual_patent, config):
    """
    Convert virtual patent XML to hierarchical dictionary preserving XML structure for JSON
    
    Args:
        virtual_patent: XML element of virtual patent
        config (dict): Configuration dictionary with parse flags
        
    Returns:
        dict: Hierarchical dictionary representation of the patent
    """
    def element_to_dict(elem):
        """Convert XML element to dictionary recursively"""
        result = {}
        
        # Add attributes with @attr prefix to distinguish from elements
        # Only include string attributes to avoid cython function serialization issues
        for attr_name, attr_value in elem.attrib.items():
            if isinstance(attr_name, str) and isinstance(attr_value, (str, int, float, bool, type(None))):
                result[f"@{attr_name}"] = attr_value
        
        # Handle text content with truncation
        if elem.text and elem.text.strip():
            text_content = truncate_text(elem.text.strip(), config.get('max_text_length', 300))
            if len(elem) == 0:  # Leaf element with only text
                return text_content
            else:  # Element with both text and children
                result["#text"] = text_content
        
        # Handle child elements
        for child in elem:
            # Ensure child.tag is a string to avoid cython function issues
            if hasattr(child, 'tag') and isinstance(child.tag, str):
                child_tag = child.tag
                child_dict = element_to_dict(child)
                
                if child_tag in result:
                    # Multiple elements with same tag - convert to array
                    if not isinstance(result[child_tag], list):
                        result[child_tag] = [result[child_tag]]
                    result[child_tag].append(child_dict)
                else:
                    result[child_tag] = child_dict
        
        # Handle tail text (text after element)
        if elem.tail and elem.tail.strip():
            result["#tail"] = elem.tail.strip()
        
        return result
    
    # Convert the virtual patent element to hierarchical dictionary
    hierarchical_dict = element_to_dict(virtual_patent)
    
    # Ensure all keys and values are JSON serializable
    def sanitize_for_json(obj):
        """Recursively sanitize object to ensure JSON compatibility"""
        if isinstance(obj, dict):
            sanitized = {}
            for k, v in obj.items():
                # Only include keys that are strings
                if isinstance(k, str):
                    sanitized_value = sanitize_for_json(v)
                    if sanitized_value is not None:  # Skip None values
                        sanitized[k] = sanitized_value
            return sanitized
        elif isinstance(obj, list):
            return [sanitize_for_json(item) for item in obj if sanitize_for_json(item) is not None]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            # Skip any other types that can't be JSON serialized (like cython functions)
            return None
    
    sanitized_dict = sanitize_for_json(hierarchical_dict)
    
    # Config-based filtering is applied during virtual patent creation
    return sanitized_dict

def has_kind_merging(virtual_patent):
    """
    Check if a virtual patent has kind-merging with multiple kind codes (indicating it was merged from multiple kind codes)
    
    Args:
        virtual_patent: XML element of virtual patent
        
    Returns:
        bool: True if patent has kind-merging with multiple kind codes
    """
    try:
        # Check for kind-merging attribute in the root element
        kind_merging_attr = virtual_patent.get('kind-merging')
        if kind_merging_attr and ',' in kind_merging_attr:
            return True
        
        # Check for kind-merging elements in descendants
        for elem in virtual_patent.iter():
            # Check kind-merging attribute
            kind_merging_attr = elem.get('kind-merging')
            if kind_merging_attr and ',' in kind_merging_attr:
                return True
            
            # Check kind-merging element text
            if elem.tag == 'kind-merging' and elem.text and ',' in elem.text:
                return True
                
        return False
        
    except Exception as e:
        logger.error(f"Error checking kind-merging for virtual patent: {e}")
        return False