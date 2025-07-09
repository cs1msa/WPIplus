# Stratified Sample Description
This vertical contains two representative, stratified sample datasets derived from the core #EP, #WO, and #US verticals. 

Both datasets were produced using **stratified sampling** and contain approximately **95,000 unique patents** each. The first dataset is stratified by **IPC codes**, and the other by **CPC codes**. Both are intended to support rapid **experimentation and benchmarking for multi-label patent classification tasks**.

---

## Preparation 
The following criteria were applied during dataset preparation:
- Only patents with **complete English-language content** across the abstract, description, and claims sections were included.
- Each patent has **non-empty classification labels**.
- **Labels with fewer than 20 occurrences** in the full corpus were excluded and a **stratified sampling strategy** was used to retain **5% of instances per label** (with a minimum of one per label), to ensure label quality and balance.

---

## Preparation Pipeline Overview
The preprocessing pipeline performs the following operations to standardize and curate the dataset:
- **Step 1: Multi-source integration:** Merges patent data from European (EP), United States (US), and World Intellectual Property Organization (WO) sources.
- **Step 2: English content filtering:** Retains only patents with English-language abstract, description, and claims sections.
- **Step 3: Label standardization:** Uses IPC or CPC classifications; subclass/group formatting is unified.
- **Step 4: Rare label filtering:** Removes under-represented labels (less than 20 samples at group level) using a "take at least one" strategy.
- **Step 4: Stratified sampling:** A representative 5% portion of the dataset is sampled to maintain label diversity.
- **Step 5: Train/validation/test splits:** Generated using iterative stratification for balanced label distribution across splits.

---

## Output
- Cleaned, labeled datasets in CSV format (one for IPC, one for CPC)
- Predefined train, validation, and test splits
- Summary statistics and label frequency distributions by section, subclass, and group

---

## 🔗 Access

For direct access to the datasets and further details, please see below.

- ## [\#StratifiedSample_IPCR(EPO,WO,US)en-all](https://github.com/cs1msa/WPIplus/tree/main/Collection%20Verticals%20(subsets)/%23StratifiedSample(EPO%2CWO%2CUS)en-all%20-%20Created%20for%20Classification%20Tasks/%23StratifiedSample_IPCR(EPO%2CWO%2CUS)en-all)
- ## [\#StratifiedSample_CPC(EPO,WO,US)en-all](https://github.com/cs1msa/WPIplus/tree/main/Collection%20Verticals%20(subsets)/%23StratifiedSample(EPO%2CWO%2CUS)en-all%20-%20Created%20for%20Classification%20Tasks/%23StratifiedSample_CPC(EPO%2CWO%2CUS)en-all)

