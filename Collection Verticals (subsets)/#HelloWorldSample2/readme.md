# Patent Classification Dataset Preparation Pipeline
We provide two representative sample datasets derived from the full (EPO, WO, US)en-all corpus, each containing approximately 95,000 unique patents—one labeled with IPC codes and the other with CPC codes. These datasets are designed for quick experimentation with multi-label patent classification.

## Objective
The goal is to construct clean, representative datasets for machine learning tasks in patent classification. Each dataset includes only patents with complete English-language content across the abstract, description, and claims sections, and non-empty classification labels (IPC or CPC). To ensure quality and label balance:
- Labels with fewer than 20 occurrences are removed.
- A stratified sampling strategy retains 5% of instances per label (with a minimum of one), yielding a representative and balanced subset.
    
## Pipeline Overview
The preprocessing pipeline performs the following operations to standardize and curate the dataset:
### Key Features
- **Multi-source integration:** Merges patent data from European (EP), United States (US), and World Intellectual Property Organization (WO) sources.
- **English content filtering:** Retains only patents with English-language abstract, description, and claims sections.
- **Label standardization:** Uses IPC or CPC classifications; subclass/group formatting is unified.
- **Rare label filtering:** Removes under-represented labels (less than 20 samples) using a "take at least one" strategy.
- **Stratified sampling:** A representative 5% portion of the dataset is sampled to maintain label diversity.
- **Train/validation/test splits:** Generated using iterative stratification for balanced label distribution across splits.

## Output
- Cleaned, labeled datasets in CSV format (one for IPC, one for CPC)
- Predefined train, validation, and test splits
- Summary statistics and label frequency distributions by section, subclass, and group

For direct access to the datasets and further details, please see below.
## [\#Sample(EPO, WO, US)en-all-ipcr](https://github.com/cs1msa/WPIplus/tree/main/Collection%20Verticals%20(subsets)/%23HelloWorldSample2/%23Sample(EPO%2C%20WO%2C%20US)en-all-ipcr)
## [\#Sample(EPO, WO, US)en-all-cpc](https://github.com/cs1msa/WPIplus/tree/main/Collection%20Verticals%20(subsets)/%23HelloWorldSample2/%23Sample(EPO%2C%20WO%2C%20US)en-all-cpc)

