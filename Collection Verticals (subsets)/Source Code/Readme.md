# Source Code Organization
This folder contains scripts for both the entire collection and specific verticals. These scripts have been used to generate files for the respective verticals.

## Extraction
- [7z Files Extraction and Organization by Vertical](https://github.com/cs1msa/WPIplus/blob/main/Collection%20Verticals%20(subsets)/Source%20Code/7z%20Files%20Extraction%20and%20Organization%20by%20Vertical.ipynb): This script extracts all 7z files from the WPI collection, organizing them into separate folders (EP, WO, US, CN, JP and KR) within the destination folder.
## CSV File Creation
### Core Verticals
- [Core Verticals - CSV File Creation for Patent Document Analysis](https://github.com/cs1msa/WPIplus/blob/main/Collection%20Verticals%20(subsets)/Source%20Code/CSV%20File%20Creation%20for%20Patent%20Document%20Analysis.ipynb): This script generates a CSV file containing essential data for analyzing patent documents in a core vertical of the WPI dataset.
## Patent Document Analysis
### Core Verticals
- [Core Verticals - Patent Document Analysis](https://github.com/cs1msa/WPIplus/blob/main/Collection%20Verticals%20(subsets)/Source%20Code/Core%20Verticals%20-%20Patent%20Document%20Analysis.ipynb): This script processes a CSV file containing essential data for analyzing patent documents of a core vertical (e.g., EP) and generates five output files.
### Virtual Verticals
- [Virtual Patent Verticals - Patent Analysis](https://github.com/cs1msa/WPIplus/blob/main/Collection%20Verticals%20(subsets)/Source%20Code/Virtual%20Patent%20Verticals%20-%20Patent%20Analysis.ipynb): This script processes a CSV file containing essential data for analyzing patent documents of a core vertical (e.g., EP) and generates five output files refering to virtual patents.
## Representative Sample Creation
- [Subpart Creation - EP, US, WO_all_ipcr](): This script processes the EP, WO, and US CSV files and generates a representative sample dataset derived from the full (EPO, WO, US)en-all corpus, containing approximately 95,000 unique patents labeled with IPCR codes.
- [Subpart Creation - EP, US, WO_all_cpc](): This script processes the EP, WO, and US CSV files and generates a representative sample dataset derived from the full (EPO, WO, US)en-all corpus, containing approximately 95,000 unique patents labeled with CPC codes.
- [Parsing subpart.ipynb](): This script parses the EP, WO, and US collections and creates the split datasets.
