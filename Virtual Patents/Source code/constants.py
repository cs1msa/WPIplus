# Licensed under the MIT License. See LICENSE-CODE in the repository root for details.
# Copyright (c) 2025 Christos Papadopoulos

"""
Constants for PatentFusion

This module contains shared constants used across the application.
"""

# Valid patent office codes
VALID_PATENT_OFFICES = ['CN', 'EP', 'JP', 'KR', 'US', 'WO']

# Valid output formats
VALID_OUTPUT_FORMATS = ['csv', 'xml', 'json']

# Language priorities for multi-language processing
LANGUAGE_PRIORITY = ['EN', 'ZH', 'JA', 'KO']

# Progress reporting intervals
PROGRESS_REPORT_INTERVAL = 100000  # Report every 100K records

# Default configuration values
DEFAULT_CONFIG = {
    'max_text_length': 300,
    'memory_limit': 8,
    'output_formats': ['csv'],
    'global_priority': [],
    'field_priorities': {},
    'batch_size': 50,
    'chunk_size': 250,
    'parse_lang': 'ALL'
}


# Supported languages for patent documents
SUPPORTED_LANGUAGES = ['EN', 'ZH', 'JA', 'KO', 'FR', 'DE', 'ES', 'IT', 'RU', 'PT', 'NL', 'SV', 'DA', 'NO', 'FI']

# Default primary language priority order
PRIMARY_LANGUAGE_PRIORITY = ['EN', 'FR', 'DE', 'ES', 'IT', 'ZH', 'JA', 'KO', 'RU']

