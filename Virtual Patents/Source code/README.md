# PatentFusion

PatentFusion is a high-performance virtual patent processing system that creates unified patent records from multiple patent kind codes while preserving complete XML hierarchy and enabling flexible output generation.

## Architecture Overview

The system processes patent XML files to create virtual patents that combine information from multiple kind codes of the same patent while maintaining full XML structure integrity.

### Core Modules

1. **`config_manager.py`** - Configuration handling and validation
2. **`xml_parser.py`** - Virtual patent creation with full XML hierarchy preservation
3. **`file_system.py`** - File discovery and directory operations with statistics
4. **`data_processor.py`** - Virtual patent post-processing
5. **`memory_manager.py`** - Memory-efficient virtual patent processing
6. **`output_manager.py`** - Multi-format virtual patent output generation
7. **`parallel_processor.py`** - Multiprocessing coordination with XML serialization
8. **`utils.py`** - Shared utilities and helper functions
9. **`PatentFusion.py`** - Main orchestration and entry point
10. **`constants.py`** - Shared constants and configuration defaults

### Configuration File

- **`config.ini`** - Configuration settings for virtual patent processing and output filtering

## Key Features

### 🔄 **Virtual Patent Creation**
- Combines multiple patent kind codes into unified virtual patents
- Preserves complete XML hierarchy from highest priority patents with **full 3-level hierarchical merging**
- **Advanced hierarchical merging within bibliographic-data**: Merges Level 2 elements (technical-data, parties) and Level 3 elements (invention-title, citations) from additional patents
- Transforms ucid attributes to VP suffix for patent-document elements only
- Implements kind="VP" and kind-merging for all virtual patents (single-kind shows one code, multi-kind shows comma-separated codes)
- **Comprehensive kind-source traceability**: Adds kind-source attributes at all hierarchy levels - Level 2 children for bibliographic-data, Level 3 children within merged Level 2 elements, Level 1 elements for abstract/description/claims/copyright
- Intelligent abstract duplicate detection: preserves unique abstracts based on language, source, and content analysis while filtering true duplicates
- Reorders XML elements: moves <dates-of-public-availability> between <priority-claims> and <technical-data>, positions <search-report-data> just before <copyright>, moves <copyright> to absolute last position
- Preserves publication-reference elements unchanged from original parsed files

### 🚀 **High Performance**
- **Streaming Multiprocessing**: Handles unlimited dataset sizes without memory constraints
- **Parallel Temp File Processing**: Multiple workers process temp files concurrently with real-time progress
- **Memory-Efficient Architecture**: Processes one temp file per worker, supports 38GB+ datasets with immediate cleanup
- **Auto-Scaling Processing**: Automatically adjusts worker count based on available resources
- Optimized batch processing with AUTO or manual chunk size configuration
- Multi-level progress tracking with individual worker and overall progress bars
- Integrated merged patents inspection during VP file saving to avoid duplicate processing

### 🔧 **Flexible Configuration**
- Configurable parsing flags for output filtering
- Advanced language filtering (ALL, PRIMARY, or specific languages like EN,FR,DE)
- Support for multiple output formats: XML (hierarchical), CSV (flat with indexed fields), JSON (hierarchical)
- Consistent text truncation across all output formats with configurable word limits
- Memory and performance tuning options with AUTO chunk size calculation
- Priority-based patent kind code ordering
- Optional merged patents inspection for quality control
- **Original Directory Structure**: Option to preserve original dataset directory hierarchy with VP directories replacing kind code directories

### 📊 **Advanced Data Processing**
- Priority-based virtual patent creation
- Full XML structure preservation
- Configuration-based output filtering
- Individual virtual patent file generation

### 💾 **Memory Management**
- Configurable memory limits with automatic monitoring
- XML element streaming and serialization
- Garbage collection optimization
- Memory usage reporting per worker

## Installation

1. Ensure you have Python 3.7+ installed
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install manually:
   ```bash
   pip install pandas lxml tqdm psutil
   ```

### Dependencies

The PatentFusion system requires the following third-party packages:

- **lxml>=4.6.0** - Essential for XML parsing and manipulation of patent documents
- **pandas>=1.3.0** - Used for data analysis, DataFrame operations, and CSV/JSON output generation  
- **tqdm>=4.62.0** - Provides progress bars during parallel processing operations
- **psutil>=5.8.0** - Used for system and process monitoring, memory management

## Usage

### Basic Usage

```bash
python PatentFusion.py
```

This will use the default `config.ini` file in the same directory.

### Using Custom Configuration

```bash
python PatentFusion.py path/to/custom/config.ini
```

### Configuration Options

Edit `config.ini` to customize processing:

```ini
[Paths]
vertical_origin_path = /path/to/patent/xml/files
patent_office = EP
destination_path = /path/to/output

[General]
max_text_length = ALL
output_formats = xml,csv,json
enable_merged_inspection = 1
original_directory_structure = 0

[Performance]
batch_size = 50
chunk_size = AUTO
cpu_count = ALL
memory_limit = ALL

[ParseFlags]
parse_title = 1
parse_abstract = 1
parse_claims = 1
parse_lang = ALL  # ALL, PRIMARY, or specific languages (EN,FR,DE)
# ... other flags for output filtering

[vpatent_creation]
global_priority = B9,B8,B6,B3,B2,B1,B,A9,A8,A6,A5,A4,A3,A2,A1,A
```

## Module Details

### config_manager.py
- **Purpose**: Centralized configuration management for virtual patent processing
- **Key Features**:
  - Configuration validation and loading
  - Virtual patent priority settings
  - Output format configuration
  - Performance parameter validation

### xml_parser.py
- **Purpose**: Virtual patent creation with XML hierarchy preservation
- **Key Features**:
  - Groups patent files by patent number
  - Creates virtual patents from highest priority files
  - Transforms ucid attributes to VP suffix for all virtual patents
  - Sets kind="VP" for all virtual patents
  - Adds kind-merging attributes/elements for consistency (single-kind shows one code, multi-kind shows comma-separated codes)
  - Reorders XML elements according to specification
  - Advanced multi-language content filtering (ALL, PRIMARY, specific languages)
  - Preserves complete XML structure and attribute ordering

### file_system.py
- **Purpose**: File discovery and directory management
- **Key Features**:
  - Recursive patent file discovery
  - Directory structure creation for individual virtual patents
  - Temporary XML file management with immediate cleanup
  - File validation and statistics

### data_processor.py
- **Purpose**: Virtual patent post-processing
- **Key Features**:
  - Simple virtual patent validation
  - XML element processing
  - Memory-efficient handling of virtual patent collections

### memory_manager.py
- **Purpose**: Streaming multiprocessing for unlimited dataset sizes
- **Key Features**:
  - **Streaming Temp File Processing**: Processes large datasets without memory overflow
  - **Immediate Temp File Cleanup**: Deletes each temp file immediately after processing
  - **Multi-Level Progress Tracking**: Individual worker and overall progress bars
  - **Chunked Worker Architecture**: Distributes temp files across parallel workers
  - **Sequential File Saving**: Avoids nested multiprocessing issues
  - Memory monitoring and garbage collection optimization
  - Coordinates scalable output generation

### output_manager.py
- **Purpose**: Multi-format virtual patent output generation
- **Key Features**:
  - Individual virtual patent file creation
  - XML (hierarchical), CSV (flat), JSON (hierarchical) output formats
  - Configuration-based output filtering
  - Parallel output generation with XML serialization
  - Organized directory structure (office/format/files)
  - Integrated merged patents inspection during VP file saving

### parallel_processor.py
- **Purpose**: Multiprocessing coordination for virtual patent creation
- **Key Features**:
  - Parallel batch processing of patent files
  - XML virtual patent creation in workers
  - Progress tracking across multiple processes
  - XML serialization for multiprocessing compatibility

### utils.py
- **Purpose**: Shared utilities for virtual patent processing
- **Key Features**:
  - XML processing utilities
  - System information functions
  - Logging setup and configuration
  - Memory usage monitoring

## Output Structure

Virtual patents are organized based on the `original_directory_structure` setting:

### Traditional Structure (original_directory_structure = 0)
```
destination_path/
├── individual_vpatents/
│   └── EP/
│       ├── xml/
│       │   ├── EP-0767426-VP.xml
│       │   └── EP-0787017-VP.xml
│       ├── csv/
│       │   ├── EP-0767426-VP.csv
│       │   └── EP-0787017-VP.csv
│       └── json/
│           ├── EP-0767426-VP.json
│           └── EP-0787017-VP.json
├── merged_patents_inspection/
│   └── EP/
│       ├── xml/
│       ├── csv/
│       └── json/
└── temp_files/
```

### Original Directory Structure (original_directory_structure = 1)
```
destination_path/
├── individual_vpatents/
│   └── EP/
│       ├── 20140108/
│       │   └── VP/
│       │       └── 000002/
│       │           └── 61/
│       │               └── 57/
│       │                   └── 47/
│       │                       ├── EP-2615747-VP.xml
│       │                       ├── EP-2615747-VP.csv
│       │                       └── EP-2615747-VP.json
│       └── 20140115/
│           └── VP/
│               └── 000002/
│                   └── 68/
│                       └── 04/
│                           └── 49/
│                               ├── EP-2680449-VP.xml
│                               ├── EP-2680449-VP.csv
│                               └── EP-2680449-VP.json
├── merged_patents_inspection/
│   └── EP/
│       ├── 20140108/
│       │   └── VP/
│       │       └── 000002/
│       │           └── 68/
│       │               └── 05/
│       │                   └── 07/
│       │                       └── EP-2680507-VP.xml
│       └── 20140115/
│           └── VP/
│               └── 000002/
│                   └── 68/
│                       └── 04/
│                           └── 49/
│                               └── EP-2680449-VP.xml
└── temp_files/
```

**Key Features of Original Directory Structure:**
- Preserves the original dataset's date-based organization (YYYYMMDD folders)
- Replaces kind code directories (A1, A4, B2, etc.) with "VP" directories
- Places all output formats (XML, CSV, JSON) in the same directory
- For merged patents, uses the highest priority file's date folder
- Both individual and inspection folders follow the same structure

## Virtual Patent Features

### XML Structure Preservation
- Maintains complete XML hierarchy from highest priority patent files
- Preserves all original tags, attributes, and text content
- Transforms ucid attributes to VP suffix for patent-document elements only
- Preserves publication-reference elements exactly as parsed from original files
- Adds kind-source attributes using differentiated strategy: Level 2 children for bibliographic-data, Level 1 elements for abstract/description/claims/copyright

### Kind Code Merging
- Combines multiple kind codes of the same patent
- Uses priority-based selection (B9 > B8 > B6 > ... > A1 > A)
- All virtual patents get kind="VP" and kind-merging attributes/elements for consistency
- Single-kind patents: kind-merging="B1" (one code)
- Multi-kind patents: kind-merging="B1,A4,A1" (comma-separated codes)

### Unified Merging Strategy with Intelligent Abstract Detection
- **Simplified merging approach for all Level 1 elements** (bibliographic-data, abstract, description, claims, copyright)
- **Bibliographic-data**: Smart hierarchical merging - preserves highest priority elements while adding missing Level 2 and Level 3 elements from additional patents
  - **Level 2 merging**: Adds missing Level 2 elements (e.g., dates-of-public-availability, technical-data, parties)
  - **Level 3 merging**: Adds missing Level 3 elements within Level 2 containers (e.g., invention-title, citations within technical-data)
  - **Complete hierarchy preservation**: Maintains full XML structure while merging at appropriate granularity
- **Abstract elements**: Intelligent duplicate detection based on language, source, and text content to preserve unique abstracts from all priority levels
- **Other Level 1 elements**: Complete elements taken from highest priority patent, missing elements added from additional patents
- Base patent (highest priority) serves as foundation for all merging decisions
- Additional patents contribute missing elements at all hierarchy levels within bibliographic-data and missing Level 1 elements to other sections
- Prevents duplicate abstracts while ensuring all unique bibliographic and content elements are preserved across priority levels

### Source Traceability
- **Differentiated kind-source strategy** based on element type and structure with hierarchical support
- **Bibliographic-data**: kind-source added to Level 2 children (publication-reference, application-reference, etc.) and Level 3 children within merged Level 2 elements
- **Abstract, Description, Claims**: kind-source added to the Level 1 element itself
- **Copyright and childless elements**: kind-source added directly to the element
- Shows which original kind code each element originated from during merging at all hierarchy levels
- Examples: 
  - `<abstract kind-source="A4">` indicates the abstract came from the A4 patent
  - `<publication-reference kind-source="A1">` shows this Level 2 element came from A1
  - `<invention-title kind-source="A">` shows this Level 3 element came from the A patent
  - `<citations kind-source="A">` shows this Level 3 element came from the A patent
  - `<copyright kind-source="A4">` shows copyright element came from A4
- Enables complete identification of the source of every merged element with optimal granularity across all XML hierarchy levels
- Balances traceability with XML structure clarity and processing efficiency

### Intelligent Abstract Duplicate Detection
- **Smart content analysis**: Compares language (`lang`), source (`source`/`load-source`), and text content to identify truly unique abstracts
- **Preserves unique content**: Multiple abstracts with different languages, sources, or content are all preserved in virtual patents
- **Prevents true duplicates**: Abstracts with identical language, source, and text content are merged to avoid redundancy
- **Multi-priority merging**: Unique abstracts from A4, A3, A1, etc. are all included if they meet uniqueness criteria
- **Text similarity detection**: Handles exact matches and truncated content scenarios for robust duplicate identification
- **Selective application**: Intelligent detection applies only to abstract elements; other elements use standard merging logic

### XML Element Ordering
- **dates-of-public-availability positioning**: Moved between priority-claims and technical-data within bibliographic-data
- **search-report-data positioning**: Positioned just before copyright element, or as last element if no copyright exists
- **Copyright positioning**: Copyright element is always positioned as the absolute last element in virtual patents
- **Automatic reordering**: Elements are repositioned regardless of their original positions during merging
- **Consistent structure**: Ensures predictable XML document structure across all virtual patents with standardized element order

### Output Filtering
- Applies configuration-based filtering during output generation
- Supports selective field extraction based on parse flags
- **Text Truncation**: Consistent word-based truncation across all output formats
  - `max_text_length = 50`: Limit text fields to 50 words
  - `max_text_length = ALL`: Keep full text content
- **Advanced Language Filtering** with multiple options:
  - `parse_lang = ALL`: Keep all language versions (default)
  - `parse_lang = PRIMARY`: Keep only primary language (most common in document)
  - `parse_lang = EN`: Keep only English content
  - `parse_lang = EN,FR,DE`: Keep English, French, and German content
- **Format-Specific Output Generation**:
  - **XML**: Preserves complete hierarchical structure with full XML formatting
  - **CSV**: Flat structure with indexed field names for duplicate elements (`abstract_p_1`, `abstract_p_2`)
  - **JSON**: Hierarchical structure preserving XML organization (not flattened like CSV)
- **CSV Indexed Fields**: Automatically creates indexed field names for duplicate XML elements
  - Example: `abstract_p_1`, `abstract_p_2`, `description_p_1`, `description_p_2`
  - Ensures no data loss from multi-element XML structures
- Maintains full XML structure while filtering output formats

### Merged Patents Inspection
- Optional separate directory for patents that had multiple kind codes merged
- Enabled/disabled via `enable_merged_inspection` configuration setting
- Useful for quality control and analysis of the kind-merging process
- Contains only patents where actual merging occurred (multiple kind codes with commas in kind-merging)
- Excludes single-kind patents even though they have kind-merging attributes for consistency
- Saves disk space and processing time when disabled for large datasets

## Performance Optimization

### Memory Management
- **Streaming Multiprocessing**: Processes large datasets without loading everything into memory
- **Chunked Temp File Processing**: Handles temporary files in manageable chunks to prevent memory overflow
- **Immediate Temp File Deletion**: Removes each temp file as soon as it's processed to minimize disk space usage
- Configure `memory_limit` in config.ini for virtual patent processing
- XML serialization enables multiprocessing compatibility
- Automatic garbage collection and memory monitoring
- **Memory-Efficient Architecture**: Never loads more than one temp file per worker at a time

### Parallel Processing
- Set `cpu_count` to match your system capabilities
- Adjust `batch_size` for optimal memory usage
- AUTO chunk size calculation based on available memory and CPU cores
- Virtual patent creation distributed across workers

### Output Optimization
- Individual virtual patent files enable distributed access
- Multiple output formats generated in parallel with format-specific optimizations
- Organized directory structure for easy navigation
- Integrated merged patents inspection eliminates duplicate processing

### Large Dataset Optimization
- **Streaming Architecture**: Handles datasets of any size (tested with 38GB+ temp files)
- **No Memory Limits**: System can process unlimited dataset sizes without crashing
- **Immediate Cleanup**: Deletes temp files as they're processed, preventing disk space buildup
- **Sequential File Saving**: Avoids nested multiprocessing issues in worker processes
- Disable `enable_merged_inspection` when processing millions of files
- Reduces disk space usage and processing time for production workflows
- Enable only when quality control analysis of merged patents is needed

## Error Handling

The system includes comprehensive error handling:
- Configuration validation for virtual patent settings
- XML parsing error recovery
- Memory limit enforcement during processing
- Graceful handling of malformed patent files

## Monitoring and Logging

- Comprehensive logging throughout the virtual patent pipeline
- **Multi-Level Progress Tracking**: Individual worker progress bars plus overall progress with separator bars
- **Real-Time Processing Stats**: Shows files processed per second and patents generated per worker
- **Memory Usage Monitoring**: Per-process memory tracking and optimization
- Performance metrics and processing statistics
- Detailed timing reports for parallel processing and VP file saving phases
- Config-based filtering enforcement across all output formats
- **Clean Progress Display**: Eliminates excessive logging while maintaining visibility

## Streaming Architecture for Large Datasets

PatentFusion implements a sophisticated streaming multiprocessing architecture designed to handle datasets of unlimited size without memory constraints.

### Key Architecture Components

1. **Chunked Temp File Processing**
   - Distributes temporary files across multiple worker processes
   - Each worker processes files sequentially to avoid memory buildup
   - Automatic load balancing based on available CPU cores

2. **Memory-Efficient File Handling**
   - Never loads more than one temp file per worker at a time
   - Aggressive garbage collection and immediate temp file deletion after processing
   - Tested with 38GB+ temporary file datasets

3. **Sequential Individual File Saving**
   - Avoids nested multiprocessing issues by using sequential saves within workers
   - Maintains parallelism at the temp file level while ensuring stability
   - Supports all output formats (XML, CSV, JSON) with full feature preservation

4. **Real-Time Progress Monitoring**
   - Individual progress bars for each worker showing file processing rate
   - Overall progress bar aggregating all workers with total patent counts
   - Clean separator bars matching the parsing phase display
   - Dynamic rate display (files/s or s/file) based on processing speed

### Benefits for Large Datasets

- **Unlimited Scalability**: Can process datasets larger than available system memory
- **Crash Prevention**: Eliminates memory overflow crashes during processing with minimal disk usage
- **Performance Optimization**: Maintains high throughput through parallel processing
- **Progress Visibility**: Clear real-time feedback on processing status
- **Resource Efficiency**: Optimal memory usage with automatic cleanup

## Virtual Patent Workflow

1. **File Discovery**: Scans patent XML files and groups by patent number
2. **Priority Sorting**: Orders files by kind code priority (B9 > B8 > ... > A)
3. **Virtual Patent Creation**: Creates unified patents preserving XML hierarchy with config-based filtering and language filtering
4. **Parallel Processing**: Distributes virtual patent creation across workers
5. **Output Generation**: Creates individual files in multiple formats with integrated merged patents inspection
6. **Cleanup & Reporting**: Removes temp files during processing and reports detailed timing statistics

## Testing

The virtual patent system can be validated by:
- Checking ucid transformation to VP suffix in patent-document elements only
- Verifying publication-reference elements remain unchanged from original files
- Confirming kind-merging logic for all virtual patents (single and multi-kind)
- Validating differentiated kind-source attributes: Level 2 children for bibliographic-data, Level 1 elements for abstract/description/claims/copyright, and Level 3 children within merged Level 2 elements
- Testing hierarchical merging: Level 2 elements (e.g., technical-data, parties) and Level 3 elements (e.g., invention-title, citations within technical-data) are correctly merged from additional patents
- Testing intelligent abstract duplicate detection: unique abstracts with different lang/source/content are preserved, true duplicates are filtered
- Verifying copyright positioning as absolute last element after all other elements including drawings
- Verifying complete XML hierarchy preservation across all levels
- Testing memory efficiency with large datasets
- Verifying config-based filtering works across all output formats (XML, CSV, JSON)
- Confirming metadata helper tags are properly cleaned from all outputs

## Support

For issues or questions:
1. Check the configuration file for proper virtual patent settings
2. Verify that merged inspection only contains patents with multiple kind codes (comma-separated in kind-merging attributes)
3. Review log output for processing errors
4. Verify input XML files are valid patent documents
5. Ensure sufficient memory and disk space for virtual patent creation
6. Consider disabling `enable_merged_inspection` for large datasets to save resources

## License

- Licensed under the MIT License. See LICENSE-CODE in the repository root for details.
- Copyright (c) 2025 Christos Papadopoulos