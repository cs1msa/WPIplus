# Licensed under the MIT License. See LICENSE-CODE in the repository root for details.
# Copyright (c) 2025 Christos Papadopoulos

"""
XML Parser for PatentFusion

This module handles the parsing of patent XML files and extraction of patent data
according to configuration flags.
"""

import os
import re
import copy
import logging
from lxml import etree
from utils import truncate_text

logger = logging.getLogger(__name__)

def process_file_batch(file_batch, folder_order, batch_id, config, test_patents_set=None):
    """
    Process a batch of files and create virtual patents with full XML structure preservation
    
    Args:
        file_batch (list): List of file paths to process
        folder_order (dict): Dictionary mapping folder names to order indices
        batch_id (int): Batch identifier for logging
        config (dict): Configuration dictionary
        test_patents_set (set, optional): Set of patents to skip (test dataset)
        
    Returns:
        list: List of virtual patent XML elements
    """
    # Group files by patent number first
    patent_groups = group_files_by_patent(file_batch, test_patents_set)
    
    # Process each patent group to create virtual patents
    virtual_patents = []
    
    for patent_number, file_list in patent_groups.items():
        try:
            # Sort files by global priority
            sorted_files = sort_files_by_priority(file_list, config['global_priority'])
            
            if sorted_files:
                # Create virtual patent from sorted files
                virtual_patent_xml = create_virtual_patent(sorted_files, folder_order, config)
                if virtual_patent_xml is not None:
                    virtual_patents.append(virtual_patent_xml)
                    
        except Exception as e:
            logger.error(f"Error processing patent group {patent_number}: {e}")
            continue
    
    return virtual_patents

def group_files_by_patent(file_batch, test_patents_set=None):
    """
    Group files by patent number extracted from filename
    
    Args:
        file_batch (list): List of file paths
        test_patents_set (set, optional): Set of patents to skip
        
    Returns:
        dict: Dictionary mapping patent_number -> list of file paths
    """
    patent_groups = {}
    
    for file_path in file_batch:
        try:
            file_name = os.path.basename(file_path)
            patent_number = file_name.split(".")[0].split("-")[1]
            
            # Skip if in test dataset
            if test_patents_set and patent_number in test_patents_set:
                continue
                
            if patent_number not in patent_groups:
                patent_groups[patent_number] = []
            patent_groups[patent_number].append(file_path)
            
        except Exception as e:
            logger.debug(f"Could not extract patent number from {file_name}: {e}")
            continue
    
    return patent_groups

def sort_files_by_priority(file_list, global_priority):
    """
    Sort files by kind code priority according to global priority list
    Only includes files with kind codes that are in the global priority list

    Args:
        file_list (list): List of file paths for the same patent
        global_priority (list): List of kind codes in priority order

    Returns:
        list: Sorted list of file paths by priority (highest first), only including files with kind codes in global_priority
    """
    def get_priority_index(file_path):
        try:
            file_name = os.path.basename(file_path)
            kind_code = file_name.split(".")[0].split("-")[2]
            try:
                return global_priority.index(kind_code)
            except ValueError:
                # If kind code not in priority list, exclude it by returning None
                return None
        except Exception:
            return None

    # Filter files to only include those with kind codes in global_priority
    priority_files = []
    for file_path in file_list:
        priority_index = get_priority_index(file_path)
        if priority_index is not None:
            priority_files.append((file_path, priority_index))

    # Sort by priority index and return just the file paths
    return [file_path for file_path, _ in sorted(priority_files, key=lambda x: x[1])]

def create_virtual_patent(sorted_files, folder_order, config):
    """
    Create a virtual patent XML from sorted files by priority
    
    Args:
        sorted_files (list): List of file paths sorted by priority (highest first)
        folder_order (dict): Dictionary mapping folder names to order indices
        config (dict): Configuration dictionary
        
    Returns:
        etree.Element: Virtual patent XML element or None if failed
    """
    if not sorted_files:
        return None
    
    # Start with the highest priority file
    base_file = sorted_files[0]
    
    try:
        # Parse the base file and create the virtual patent structure
        parser = etree.XMLParser(recover=True)
        base_tree = etree.parse(base_file, parser)
        base_root = base_tree.getroot()
        
        # Create a copy of the base XML structure
        virtual_patent = copy.deepcopy(base_root)
        
        # Add metadata for original directory structure (will be removed before final output)
        virtual_patent.set('_source_file_path', base_file)
        
        # Transform ucid attributes to v-patent-ucid
        transform_ucid_attributes(virtual_patent)
        
        # Collect kind codes for kind-merging
        base_kind_code = extract_kind_code_from_file(base_file)
        kind_codes = [base_kind_code]
        
        # Add kind-source attribute to direct children of base patent
        add_kind_source_to_direct_children(virtual_patent, base_kind_code)
        
        # Merge additional files if any
        for additional_file in sorted_files[1:]:
            try:
                additional_tree = etree.parse(additional_file, parser)
                additional_root = additional_tree.getroot()
                
                # Extract kind code
                kind_code = extract_kind_code_from_file(additional_file)
                if kind_code and kind_code not in kind_codes:
                    kind_codes.append(kind_code)
                
                
                # Merge new tags from additional file
                merge_xml_elements(virtual_patent, additional_root, config, kind_code)
                
            except Exception as e:
                logger.error(f"Error merging file {additional_file}: {e}")
                continue
        
        # Update kind attributes and elements for all virtual patents
        update_kind_to_kind_merging(virtual_patent, kind_codes)
        
        # Add metadata
        add_virtual_patent_metadata(virtual_patent, base_file, folder_order)
        
        # Reorder XML elements according to specification
        reorder_xml_elements(virtual_patent)
        
        # Apply config-based filtering to remove unwanted elements
        filter_virtual_patent_by_config(virtual_patent, config)
        
        return virtual_patent
        
    except Exception as e:
        logger.error(f"Error creating virtual patent from {base_file}: {e}")
        return None

def filter_multi_language_content(virtual_patent, lang_setting):
    """
    Filter multi-language content based on language settings
    
    Args:
        virtual_patent: XML element of virtual patent to filter
        lang_setting (str): Language setting - specific languages (e.g., 'EN,FR'), 'PRIMARY', or 'ALL'
    """
    from constants import SUPPORTED_LANGUAGES, PRIMARY_LANGUAGE_PRIORITY
    
    if lang_setting == 'ALL':
        return  # Keep all languages
    
    # Determine target languages
    if lang_setting == 'PRIMARY':
        # Find the primary language from the document
        target_languages = get_primary_language(virtual_patent)
    else:
        # Parse specific language codes (e.g., 'EN,FR,DE')
        target_languages = [lang.strip().upper() for lang in lang_setting.split(',') 
                          if lang.strip().upper() in SUPPORTED_LANGUAGES]
    
    if not target_languages:
        return  # No valid languages specified, keep all
    
    # Filter multi-language elements
    multi_lang_elements = ['abstract', 'description', 'claims', 'invention-title']
    
    for element_type in multi_lang_elements:
        elements = virtual_patent.xpath(f".//{element_type}")
        
        if len(elements) <= 1:
            continue  # Single element, no filtering needed
        
        # Group elements by language
        lang_groups = {}
        for elem in elements:
            lang = elem.get('lang', '').upper()
            if not lang:
                # Try to find language in parent elements or document context
                lang = get_element_language(elem) or 'UNKNOWN'
            
            if lang not in lang_groups:
                lang_groups[lang] = []
            lang_groups[lang].append(elem)
        
        # Keep only target language versions
        elements_to_keep = []
        for target_lang in target_languages:
            if target_lang in lang_groups:
                elements_to_keep.extend(lang_groups[target_lang])
                break  # Keep first matching language only
        
        # If no target language found, keep the first language by priority
        if not elements_to_keep and lang_groups:
            for priority_lang in PRIMARY_LANGUAGE_PRIORITY:
                if priority_lang in lang_groups:
                    elements_to_keep.extend(lang_groups[priority_lang])
                    break
            
            # If still nothing found, keep the first available
            if not elements_to_keep:
                first_lang = next(iter(lang_groups.keys()))
                elements_to_keep.extend(lang_groups[first_lang])
        
        # Remove unwanted language versions
        for elem in elements:
            if elem not in elements_to_keep:
                elem.getparent().remove(elem)

def get_primary_language(virtual_patent):
    """
    Determine the primary language of a patent document
    
    Args:
        virtual_patent: XML element of virtual patent
        
    Returns:
        list: List containing the primary language code
    """
    from constants import PRIMARY_LANGUAGE_PRIORITY
    
    # Check root element lang attribute
    root_lang = virtual_patent.get('lang', '').upper()
    if root_lang and root_lang in PRIMARY_LANGUAGE_PRIORITY:
        return [root_lang]
    
    # Find most common language in the document
    lang_counts = {}
    for elem in virtual_patent.xpath(".//*[@lang]"):
        lang = elem.get('lang', '').upper()
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
    
    if lang_counts:
        # Return the most frequent language that's in our priority list
        for priority_lang in PRIMARY_LANGUAGE_PRIORITY:
            if priority_lang in lang_counts:
                return [priority_lang]
        
        # If no priority language found, return the most frequent
        most_common = max(lang_counts.items(), key=lambda x: x[1])[0]
        return [most_common]
    
    # Default to English if no language info found
    return ['EN']

def get_element_language(element):
    """
    Get the language of an element by checking its attributes or parent elements
    
    Args:
        element: XML element
        
    Returns:
        str: Language code or None
    """
    # Check element itself
    if element.get('lang'):
        return element.get('lang').upper()
    
    # Check parent elements
    parent = element.getparent()
    while parent is not None:
        if parent.get('lang'):
            return parent.get('lang').upper()
        parent = parent.getparent()
    
    return None

def filter_virtual_patent_by_config(virtual_patent, config):
    """
    Remove XML elements and attributes from virtual patent based on configuration flags
    
    Args:
        virtual_patent: XML element of virtual patent to filter
        config (dict): Configuration dictionary with parse flags
    """
    # Remove attributes and elements globally throughout the document if disabled
    if not config.get('parse_country', True):
        # Remove country attributes from root element
        if 'country' in virtual_patent.attrib:
            del virtual_patent.attrib['country']
        # Remove country attributes from all elements throughout the document
        for elem in virtual_patent.xpath(".//*[@country]"):
            del elem.attrib['country']
        # Remove <country> elements throughout the document
        for elem in virtual_patent.xpath(".//country"):
            elem.getparent().remove(elem)
    
    if not config.get('parse_date', True):
        # Remove date attributes from root element
        if 'date' in virtual_patent.attrib:
            del virtual_patent.attrib['date']
        # Remove date attributes from all elements throughout the document
        for elem in virtual_patent.xpath(".//*[@date]"):
            del elem.attrib['date']
        # Remove <date> elements throughout the document
        for elem in virtual_patent.xpath(".//date"):
            elem.getparent().remove(elem)
    
    if not config.get('parse_family_id', True):
        # Remove family-id attributes from root element
        if 'family-id' in virtual_patent.attrib:
            del virtual_patent.attrib['family-id']
        # Remove family-id attributes from all elements throughout the document
        for elem in virtual_patent.xpath(".//*[@family-id]"):
            del elem.attrib['family-id']
        # Remove <family-id> elements throughout the document
        for elem in virtual_patent.xpath(".//family-id"):
            elem.getparent().remove(elem)
    
    if not config.get('parse_file_reference_id', True):
        # Remove file-reference-id attributes from root element
        if 'file-reference-id' in virtual_patent.attrib:
            del virtual_patent.attrib['file-reference-id']
        # Remove file-reference-id attributes from all elements throughout the document
        for elem in virtual_patent.xpath(".//*[@file-reference-id]"):
            del elem.attrib['file-reference-id']
        # Remove <file-reference-id> elements throughout the document
        for elem in virtual_patent.xpath(".//file-reference-id"):
            elem.getparent().remove(elem)
    
    if not config.get('parse_date_produced', True):
        # Remove date-produced attributes from root element
        if 'date-produced' in virtual_patent.attrib:
            del virtual_patent.attrib['date-produced']
        # Remove date-produced attributes from all elements throughout the document
        for elem in virtual_patent.xpath(".//*[@date-produced]"):
            del elem.attrib['date-produced']
        # Remove <date-produced> elements throughout the document
        for elem in virtual_patent.xpath(".//date-produced"):
            elem.getparent().remove(elem)
    
    # Handle language filtering
    lang_setting = config.get('parse_lang', 'ALL')
    if lang_setting != 'ALL':
        filter_multi_language_content(virtual_patent, lang_setting)
    # Remove text content elements if disabled
    if not config.get('parse_abstract', True):
        for elem in virtual_patent.xpath(".//abstract"):
            elem.getparent().remove(elem)
    
    if not config.get('parse_claims', True):
        for elem in virtual_patent.xpath(".//claims"):
            elem.getparent().remove(elem)
    
    if not config.get('parse_description', True):
        for elem in virtual_patent.xpath(".//description"):
            elem.getparent().remove(elem)
    
    if not config.get('parse_title', True):
        for elem in virtual_patent.xpath(".//invention-title"):
            elem.getparent().remove(elem)
    
    # Remove classification elements if disabled
    if not config.get('parse_ipcr', True):
        for elem in virtual_patent.xpath(".//classifications-ipcr | .//classification-ipcr"):
            elem.getparent().remove(elem)
    
    if not config.get('parse_cpc', True):
        for elem in virtual_patent.xpath(".//classifications-cpc | .//classification-cpc"):
            elem.getparent().remove(elem)
    
    if not config.get('parse_main_classification', True):
        for elem in virtual_patent.xpath(".//main-classification"):
            elem.getparent().remove(elem)
    
    if not config.get('parse_further_classification', True):
        for elem in virtual_patent.xpath(".//further-classification"):
            elem.getparent().remove(elem)
    
    # Remove party elements if disabled
    if not config.get('parse_applicants', True):
        for elem in virtual_patent.xpath(".//applicants"):
            elem.getparent().remove(elem)
    
    if not config.get('parse_inventors', True):
        for elem in virtual_patent.xpath(".//inventors"):
            elem.getparent().remove(elem)
    
    if not config.get('parse_agents', True):
        for elem in virtual_patent.xpath(".//agents"):
            elem.getparent().remove(elem)
    
    # Remove citation elements if disabled
    if not config.get('parse_citations', True):
        for elem in virtual_patent.xpath(".//citations"):
            elem.getparent().remove(elem)
    
    # Remove drawings if disabled
    if not config.get('parse_drawings', True):
        for elem in virtual_patent.xpath(".//drawings"):
            elem.getparent().remove(elem)

def extract_kind_code_from_file(file_path):
    """
    Extract kind code from file path
    
    Args:
        file_path (str): Path to patent file
        
    Returns:
        str: Kind code or empty string if not found
    """
    try:
        file_name = os.path.basename(file_path)
        return file_name.split(".")[0].split("-")[2]
    except Exception:
        return ""

def transform_ucid_attributes(xml_element):
    """
    Transform ucid attributes with VP suffix for patent-document elements only
    Publication-reference elements remain unchanged as parsed from original files
    
    Args:
        xml_element: XML element to transform
    """
    # Transform in patent-document element
    patent_doc = xml_element.xpath("//patent-document[@ucid]")
    for elem in patent_doc:
        ucid = elem.get('ucid', '')
        if ucid:
            # Remove kind code and add VP
            ucid_parts = ucid.rsplit('-', 1)
            if len(ucid_parts) == 2:
                new_ucid = f"{ucid_parts[0]}-VP"
                
                # Reorder attributes: helper tags first, then ucid, then original order
                reorder_attributes(elem, new_ucid, 'ucid')
    
    # Publication-reference elements remain unchanged - keep original ucid and structure as parsed

def reorder_attributes(element, new_ucid_value, ucid_attr_name):
    """
    Reorder attributes to maintain consistency with original patent file structure
    
    Args:
        element: XML element to reorder
        new_ucid_value: Value for the v-patent-ucid attribute  
        ucid_attr_name: Name of the ucid attribute to use
        
    Note:
        For patent-document elements, places kind/kind-merging in 4th position (after doc-number)
        to match the position of 'kind' attribute in original patent files
    """
    # Get all current attributes except ucid (which we're replacing)
    current_attrs = dict(element.attrib)
    if 'ucid' in current_attrs:
        del current_attrs['ucid']
    
    # Clear all attributes
    element.attrib.clear()
    
    # Check if this is a publication-reference element (has fvid attribute)
    is_pub_ref = 'fvid' in current_attrs
    
    if is_pub_ref:
        # For publication-reference: fvid first, then ucid with VP suffix, then others
        if 'fvid' in current_attrs:
            element.set('fvid', current_attrs['fvid'])
            del current_attrs['fvid']
        
        # ucid comes second (now with VP suffix for all virtual patents)
        element.set(ucid_attr_name, new_ucid_value)
        
        # Add remaining attributes in their original order
        for attr_name, attr_value in current_attrs.items():
            element.set(attr_name, attr_value)
    else:
        # For patent-document: helper tags first, then v-patent-ucid, then others in specific order
        helper_tags = ['xml_file_name', 'relative_dir', 'folder_index']
        for helper_tag in helper_tags:
            if helper_tag in current_attrs:
                element.set(helper_tag, current_attrs[helper_tag])
                del current_attrs[helper_tag]
        
        # ucid comes after helper tags
        element.set(ucid_attr_name, new_ucid_value)
        
        # Set specific attributes in the correct order to match original patent files
        # Order: ucid, country, doc-number, kind, kind-merging (4th and 5th position), then others
        attribute_order = ['country', 'doc-number', 'kind', 'kind-merging', 'date', 'family-id', 
                          'file-reference-id', 'date-produced', 'status', 'lang']
        
        # Add attributes in the specified order if they exist
        for attr_name in attribute_order:
            if attr_name in current_attrs:
                element.set(attr_name, current_attrs[attr_name])
                del current_attrs[attr_name]
        
        # Add any remaining attributes that weren't in our ordered list
        for attr_name, attr_value in current_attrs.items():
            element.set(attr_name, attr_value)

def update_kind_to_kind_merging(xml_element, kind_codes):
    """
    Update kind attributes and elements for virtual patents
    - Only modifies patent-document elements: set kind="VP" and add kind-merging attribute
    - Publication-reference elements remain unchanged as parsed from original files
    
    Args:
        xml_element: XML element to update
        kind_codes (list): List of kind codes to merge
    """
    kind_merging_value = ','.join(kind_codes)
    
    # Update in patent-document element
    patent_doc = xml_element.xpath("//patent-document[@kind]")
    for elem in patent_doc:
        # Always set kind="VP" for virtual patents
        elem.set('kind', 'VP')
        
        # Always add kind-merging attribute for all virtual patents
        elem.set('kind-merging', kind_merging_value)
    
    # Publication-reference elements remain unchanged - keep original structure as parsed from files
    # No modifications to publication-reference ucid, kind elements, or document-id structure

def is_duplicate_element(element1, element2):
    """
    Check if two elements are duplicates based on lang, source, and text content.
    
    Args:
        element1: First XML element to compare
        element2: Second XML element to compare
        
    Returns:
        bool: True if elements are considered duplicates, False otherwise
    """
    try:
        # Compare lang attribute (case-insensitive)
        lang1 = element1.get('lang', '').lower()
        lang2 = element2.get('lang', '').lower()
        
        # Compare source attribute (check both 'source' and 'load-source')
        source1 = element1.get('source', element1.get('load-source', '')).lower()
        source2 = element2.get('source', element2.get('load-source', '')).lower()
        
        # Extract text content from all child elements (like <p> tags)
        def get_element_text(elem):
            text_parts = []
            if elem.text and elem.text.strip():
                text_parts.append(elem.text.strip())
            for child in elem:
                if child.text and child.text.strip():
                    text_parts.append(child.text.strip())
                if child.tail and child.tail.strip():
                    text_parts.append(child.tail.strip())
            return ' '.join(text_parts).strip()
        
        text1 = get_element_text(element1).lower()
        text2 = get_element_text(element2).lower()
        
        # Elements are duplicates if they have:
        # 1. Same language (if both have lang attribute)
        # 2. Same source (if both have source attribute) 
        # 3. Same or very similar text content
        
        # If both have lang attributes, they must match
        if lang1 and lang2 and lang1 != lang2:
            return False
            
        # If both have source attributes, they must match
        if source1 and source2 and source1 != source2:
            return False
            
        # Check text similarity (exact match or one is substring of other for truncated content)
        if text1 and text2:
            # Exact match
            if text1 == text2:
                return True
            # Check if one is a truncated version of the other (for cases where text was cut off)
            if len(text1) > 50 and len(text2) > 50:
                shorter = text1 if len(text1) < len(text2) else text2
                longer = text2 if len(text1) < len(text2) else text1
                if shorter in longer and len(shorter) > len(longer) * 0.8:
                    return True
        
        # If we get here and both have same lang/source but different text, still consider duplicates
        # This handles cases where same content source has minor text variations
        if lang1 and lang2 and lang1 == lang2 and source1 and source2 and source1 == source2:
            return True
            
        return False
        
    except Exception as e:
        # If comparison fails, assume not duplicate to be safe
        logger.debug(f"Error comparing elements for duplicates: {e}")
        return False

def add_kind_source_to_direct_children(xml_element, kind_code):
    """
    Add kind-source attribute with different strategies per Level 1 element type:
    - bibliographic-data: Add kind-source to Level 2 children (unified strategy)
    - abstract, description, claims: Add kind-source to Level 1 element itself
    - copyright and other childless elements: Add kind-source to Level 1 element itself
    
    Args:
        xml_element: Patent-document root element
        kind_code (str): Kind code to set as source (e.g., "A1", "B1")
    """
    try:
        for child in xml_element:
            # Skip non-element nodes (text, comments, etc.)
            if not hasattr(child, 'set') or not hasattr(child, 'tag'):
                continue
                
            try:
                tag_name = child.tag
                
                # Special handling for bibliographic-data: unified strategy (Level 2 children get kind-source)
                if tag_name == 'bibliographic-data':
                    for level2_child in child:
                        # Skip non-element nodes
                        if hasattr(level2_child, 'set') and hasattr(level2_child, 'tag'):
                            level2_child.set('kind-source', kind_code)
                else:
                    # For all other Level 1 elements (abstract, description, claims, copyright, etc.):
                    # Add kind-source to the Level 1 element itself
                    child.set('kind-source', kind_code)
                    
            except (AttributeError, TypeError) as e:
                # Skip elements that don't support attributes or length operations
                logger.debug(f"Skipping kind-source for element {getattr(child, 'tag', 'unknown')}: {e}")
                continue
    except Exception as e:
        logger.error(f"Error adding kind-source to direct children: {e}")

def add_kind_source_recursively(xml_element, kind_code):
    """
    Add kind-source attribute to structural XML elements and their structural descendants
    Skips low-level content/formatting elements that are commonly used in patent documents
    
    Args:
        xml_element: XML element to add kind-source to
        kind_code (str): Kind code to set as source (e.g., "A1", "B1")
    """
    # Elements to skip - low-level content/formatting elements used in patent documents
    skip_elements = {
        # Text formatting elements
        'p', 'b', 'i', 'u', 'strong', 'em', 'span', 'div', 'br', 'hr',
        
        # List elements  
        'ul', 'ol', 'li',
        
        # Table elements
        'table', 'tr', 'td', 'th', 'tbody', 'thead', 'tfoot', 'colgroup', 'col',
        
        # Math/scientific notation elements
        'sup', 'sub', 'math', 'mrow', 'mi', 'mn', 'mo', 'msup', 'msub', 'mfrac',
        
        # Drawing/image elements (low-level)
        'img', 'figcaption',
        
        # Generic content elements
        'text', 'content'
    }
    
    try:
        # Only add kind-source to structural XML elements (not text nodes or content elements)
        if (hasattr(xml_element, 'set') and hasattr(xml_element, 'tag') and 
            xml_element.tag not in skip_elements):
            xml_element.set('kind-source', kind_code)
        
        # Recursively add to all children
        for child in xml_element:
            add_kind_source_recursively(child, kind_code)
    except (AttributeError, TypeError) as e:
        # Skip elements that don't support attributes
        logger.debug(f"Skipping kind-source for element type {type(xml_element)}: {e}")
        pass

def merge_xml_elements(base_xml, additional_xml, config, kind_code):
    """
    Merge new non-empty tags from additional XML into base XML
    
    Args:
        base_xml: Base XML element to merge into
        additional_xml: Additional XML element to merge from
        config (dict): Configuration dictionary
        kind_code (str): Kind code of the additional XML for kind-source tracking
    """
    # Recursively merge elements from additional_xml into base_xml
    merge_element_recursive(base_xml, additional_xml, config, kind_code)

def merge_element_recursive(base_element, additional_element, config, kind_code, path=""):
    """
    Simplified merging strategy for ALL Level 1 elements with selective duplicate detection:
    - Merge Level 2 and Level 3 elements within bibliographic-data as complete units
    - Add kind-source to appropriate levels: Level 2 and Level 3 for bibliographic-data
    - Preserve complete Level 2/3 units from highest priority patent
    - Add missing Level 2/3 elements from additional patents within bibliographic-data
    - Uses intelligent duplicate detection for abstract elements (lang, source, text content)
    - Uses simple tag-based detection for all other elements (original behavior)
    - Prevents duplicate abstracts while preserving unique content from all priority levels
    
    Args:
        base_element: Base XML element to merge into
        additional_element: Additional XML element to merge from
        config (dict): Configuration dictionary
        kind_code (str): Kind code of the additional XML for kind-source tracking
        path (str): Current XML path for logging
    """
    # Check if we're inside a Level 1 element (direct child of patent-document)
    is_level1_element = "/" not in path
    
    # Check if we're inside bibliographic-data at Level 2 or Level 3
    is_bibliographic_level2 = path == "bibliographic-data"
    is_bibliographic_level3 = path.startswith("bibliographic-data/") and path.count("/") == 1
    
    # Create a list of existing children in base element (preserves multiple elements with same tag)
    base_children_list = list(base_element)
    
    # Process each child in additional element (skip XML comments and other non-element nodes)
    for additional_child in additional_element:
        # Skip XML comments and other non-element nodes (they have function objects as tags)
        if not isinstance(additional_child.tag, str):
            # These are typically XML comments like <!--EXTERNAL ATTACHMENTS--> or <!--SEQUENCE LISTING-->
            continue
            
        tag_name = additional_child.tag
        child_path = f"{path}/{tag_name}" if path else tag_name
        
        
        # Check if this child element is at Level 3 within bibliographic-data
        is_child_bibliographic_level3 = child_path.startswith("bibliographic-data/") and child_path.count("/") == 2
        
        
        # Check if this tag has content
        has_content = (
            (additional_child.text and additional_child.text.strip()) or
            additional_child.attrib or
            len(additional_child) > 0
        )
        
        if not has_content:
            continue  # Skip empty tags
        
        # Check if this element already exists in base
        is_duplicate = False
        matching_base_element = None
        
        # Apply intelligent duplicate detection only to abstract elements
        if tag_name == 'abstract':
            # For abstracts: Use intelligent duplicate detection (lang, source, text content)
            for base_child in base_children_list:
                if base_child.tag == tag_name:
                    if is_duplicate_element(base_child, additional_child):
                        is_duplicate = True
                        matching_base_element = base_child
                        break
        else:
            # For all other elements: Use simple tag-based detection (original logic)
            for base_child in base_children_list:
                if base_child.tag == tag_name:
                    is_duplicate = True
                    matching_base_element = base_child
                    break
        
        if is_duplicate and matching_base_element is not None:
            # Handle bibliographic-data Level 2/3 elements FIRST (higher priority than general Level 1 logic)
            if is_bibliographic_level2 or is_bibliographic_level3:
                # Inside bibliographic-data at Level 2 or Level 3: continue merging to add missing elements
                merge_element_recursive(matching_base_element, additional_child, config, kind_code, child_path)
            elif is_level1_element:
                # Special handling for bibliographic-data: merge Level 2 and Level 3 elements individually  
                if tag_name == 'bibliographic-data':
                    # For bibliographic-data: continue merging to add missing Level 2 and Level 3 elements
                    merge_element_recursive(matching_base_element, additional_child, config, kind_code, child_path)
                else:
                    # For other Level 1 elements: Skip merging (keep base as-is)
                    # This preserves complete Level 1 units from highest priority patent
                    pass
            else:
                # Deeper than Level 3: Continue recursive merging for edge cases
                merge_element_recursive(matching_base_element, additional_child, config, kind_code, child_path)
                
                # Merge attributes
                for attr_name, attr_value in additional_child.attrib.items():
                    if attr_value and attr_value.strip():
                        if attr_name not in ['kind-source'] and attr_name not in matching_base_element.attrib:
                            matching_base_element.set(attr_name, attr_value)
                
                # Merge text content
                if additional_child.text and additional_child.text.strip():
                    if not matching_base_element.text or not matching_base_element.text.strip():
                        matching_base_element.text = additional_child.text
        else:
            # Element is unique (not a duplicate), add it
            new_element = copy.deepcopy(additional_child)
            
            if is_level1_element:
                # Inside Level 1 elements: Apply differentiated kind-source strategy
                try:
                    tag_name = new_element.tag
                    
                    # Special handling for bibliographic-data: unified strategy (Level 2 children get kind-source)
                    if tag_name == 'bibliographic-data':
                        for level2_child in new_element:
                            # Skip non-element nodes
                            if hasattr(level2_child, 'set') and hasattr(level2_child, 'tag'):
                                level2_child.set('kind-source', kind_code)
                    else:
                        # For all other Level 1 elements (abstract, description, claims, copyright, etc.):
                        # Add kind-source to the Level 1 element itself
                        new_element.set('kind-source', kind_code)
                        
                except (AttributeError, TypeError) as e:
                    # Skip elements that don't support attributes or length operations
                    logger.debug(f"Skipping kind-source for element {getattr(new_element, 'tag', 'unknown')}: {e}")
            elif is_bibliographic_level2:
                # Level 2 elements within bibliographic-data: add kind-source to Level 2 element itself
                # and also add kind-source to Level 3 children if they exist
                try:
                    new_element.set('kind-source', kind_code)
                    # Also add kind-source to Level 3 children
                    for level3_child in new_element:
                        if hasattr(level3_child, 'set') and hasattr(level3_child, 'tag'):
                            level3_child.set('kind-source', kind_code)
                except (AttributeError, TypeError) as e:
                    logger.debug(f"Skipping kind-source for Level 2 element {getattr(new_element, 'tag', 'unknown')}: {e}")
            elif is_child_bibliographic_level3:
                # Level 3 elements within bibliographic-data: add kind-source to Level 3 element itself
                try:
                    new_element.set('kind-source', kind_code)
                except (AttributeError, TypeError) as e:
                    logger.debug(f"Skipping kind-source for Level 3 element {getattr(new_element, 'tag', 'unknown')}: {e}")
            else:
                # Deeper levels: Only add kind-source recursively for elements OUTSIDE bibliographic-data
                # L4+ elements within bibliographic-data inherit traceability from their L2/L3 parents
                if not child_path.startswith("bibliographic-data/"):
                    add_kind_source_recursively(new_element, kind_code)
            
            base_element.append(new_element)


def reorder_xml_elements(xml_element):
    """
    Reorder XML elements in virtual patent:
    - Move <dates-of-public-availability> between <priority-claims> and <technical-data>
    - Move <search-report-data> just before <copyright> or as last element if no copyright
    - Move <copyright> to absolute last position (after all other elements including drawings)
    
    Args:
        xml_element: Virtual patent XML element to reorder
    """
    try:
        # Find elements to move
        dates_elem = xml_element.xpath(".//dates-of-public-availability")
        search_report_elem = xml_element.xpath(".//search-report-data")
        copyright_elem = xml_element.xpath(".//copyright")
        
        # Move <dates-of-public-availability> between <priority-claims> and <technical-data>
        if dates_elem:
            dates_element = dates_elem[0]
            priority_claims = xml_element.xpath(".//priority-claims")
            technical_data = xml_element.xpath(".//technical-data")
            
            # Store original parent as fallback
            original_parent = dates_element.getparent()
            original_position = list(original_parent).index(dates_element)
            
            if priority_claims and technical_data:
                try:
                    # Remove from current position
                    dates_element.getparent().remove(dates_element)
                    
                    # Find the parent that contains both priority-claims and technical-data
                    priority_parent = priority_claims[0].getparent()
                    technical_parent = technical_data[0].getparent()
                    
                    if priority_parent == technical_parent:
                        # Both are in the same parent, insert between them
                        parent = priority_parent
                        priority_index = list(parent).index(priority_claims[0])
                        technical_index = list(parent).index(technical_data[0])
                        
                        # Insert dates-of-public-availability right before technical-data
                        parent.insert(technical_index, dates_element)
                    else:
                        # Different parents, insert after priority-claims in its parent
                        priority_parent = priority_claims[0].getparent()
                        priority_index = list(priority_parent).index(priority_claims[0])
                        priority_parent.insert(priority_index + 1, dates_element)
                        
                except Exception as e:
                    # If reordering fails, restore element to original position
                    logger.warning(f"Failed to reorder dates-of-public-availability, keeping original position: {e}")
                    original_parent.insert(original_position, dates_element)
            else:
                # If priority-claims or technical-data not found, leave element in original position
                logger.debug("priority-claims or technical-data not found, keeping dates-of-public-availability in original position")
        
        # Move <copyright> to absolute last position (after all other elements)
        if copyright_elem:
            copyright_element = copyright_elem[0]
            
            # Remove from current position
            copyright_element.getparent().remove(copyright_element)
            
            # Always append to the very end of the root element to ensure it's last
            xml_element.append(copyright_element)
        
        # Move <search-report-data> to position just before <copyright> or as last element if no copyright
        # This must happen AFTER copyright positioning to ensure correct final order
        if search_report_elem:
            search_report_element = search_report_elem[0]
            
            # Store original parent as fallback
            original_parent = search_report_element.getparent()
            original_position = list(original_parent).index(search_report_element)
            
            try:
                # Remove from current position
                search_report_element.getparent().remove(search_report_element)
                
                if copyright_elem:
                    # Copyright exists and has been moved to end: place search-report-data just before it
                    copyright_element = copyright_elem[0]  # Copyright is now at the end
                    copyright_index = list(xml_element).index(copyright_element)
                    xml_element.insert(copyright_index, search_report_element)
                else:
                    # No copyright: place search-report-data as last element
                    xml_element.append(search_report_element)
                    
            except Exception as e:
                # If positioning fails, restore element to original position
                logger.warning(f"Failed to reorder search-report-data, keeping original position: {e}")
                original_parent.insert(original_position, search_report_element)
                
    except Exception as e:
        logger.error(f"Error reordering XML elements: {e}")

def add_virtual_patent_metadata(xml_element, base_file, folder_order):
    """
    Add metadata to virtual patent XML with consistent attribute ordering
    
    Args:
        xml_element: XML element to add metadata to
        base_file (str): Path to base file
        folder_order (dict): Dictionary mapping folder names to order indices
        
    Note:
        Maintains attribute order consistent with original patent files,
        placing kind/kind-merging in 4th position (after doc-number)
    """
    file_name = os.path.basename(base_file)
    # Extract relative directory correctly - we'll need the config for vertical_origin_path
    # For now, use the parent directory name as relative_dir
    relative_dir = os.path.basename(os.path.dirname(base_file))
    
    # Get current attributes
    current_attrs = dict(xml_element.attrib)
    
    # Clear all attributes
    xml_element.attrib.clear()
    
    # Add helper tags first
    xml_element.set('xml_file_name', file_name)
    xml_element.set('relative_dir', relative_dir)
    xml_element.set('folder_index', str(folder_order.get(relative_dir, 0)))
    
    # Add back attributes in consistent order matching original patent files
    # Order: ucid, country, doc-number, kind, kind-merging (4th and 5th position), then others
    attribute_order = ['ucid', 'country', 'doc-number', 'kind', 'kind-merging', 'date', 'family-id', 
                      'file-reference-id', 'date-produced', 'status', 'lang']
    
    # Add attributes in the specified order if they exist
    for attr_name in attribute_order:
        if attr_name in current_attrs:
            xml_element.set(attr_name, current_attrs[attr_name])
            del current_attrs[attr_name]
    
    # Add any remaining attributes that weren't in our ordered list
    for attr_name, attr_value in current_attrs.items():
        xml_element.set(attr_name, attr_value)
