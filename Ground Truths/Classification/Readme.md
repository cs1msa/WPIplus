# Test Set Construction Methodology

Our test set construction methodology consists of two main stages:

## 1. Analyzing Label Distributions
In the first stage, we analyze the distribution of subclass-level labels (IPCR/CPC) across the vertical of interest. This helps us define task-specific test sets, as described below:
- **#CLTS1**: All available subclass labels are selected to prepare this test set. Thus, the first test set includes patents with all observed labels, representing the full range of natural label distribution in real-world data.
- **#CLTS2**: The most frequently occurring labels, excluding outliers. Thus, the second test set includes patents that fall within a specific statistical range—excluding outliers outside the 5th to 95th percentile. This approach ensures that the dataset focuses on the most representative patents, minimizing the influence of extreme cases.
- **#CLTS3**: Well-represented subclass labels are used to create this test set. Thus, the third test set includes patents with well-represented labels, specifically those occurring over 100 patents.
- **#CLTS4**: Low-represented subclass labels are assigned to the last test set. Thus, the fourth test set includes patents with few-shot labels, which are those appearing in fewer than 20 patents, to evaluate performance on rare categories.

## 2. Generating Test Sets
After identifying the labels of interest for each test set, we curate the test set collections by selecting patents that meet the following criteria:
- **Complete textual fields**: The patent must have all three key fields (abstract, description, and claims) fully completed.
- **B kind code**: The patent must be assigned a B kind code (e.g., B1, B2, B3, etc.).
- **Issued date**: The patent must have an issue date after October 1, 2015.
- **Relevant labels**: The patent must contain at least one of those labels assigned in the respective test set.

**Exception:** For the fourth test set (#CLTS4), applying the above criteria results in very few patent documents, which finally correspond to even fewer single patents. To overcome this limitation, we relaxed the criteria by including both A and B documents issued within the second year of the WPI dataset (i.e. after January 1, 2015). 

## Generalizable Methodology

This process is repeatable for constructing classification test sets across different verticals and classification schemes (Main-Further/IPCR/CPC), ensuring consistent evaluation across various patent datasets.

# Classification Test Set Organization 
Each #CLST folder contains four CLTS files referring to virtual patents (VP) and four CLTS files referring to individual patent documents, the help CSV file used to generate these CLTS files and links to the relevant source code.

## CLTS files referring to VP 
Inside each #CLST folder, you'll find six CLTS files referring to VP:

- #CLTS[VerticalName]\_VP_[ClassificationSystem]_1.csv
- #CLTS[VerticalName]\_VP_[ClassificationSystem]_2.csv
- #CLTS[VerticalName]\_VP_[ClassificationSystem]_3.csv
- #CLTS[VerticalName]\_VP_[ClassificationSystem]_4.csv

## CLTS files referring to Patent Documents 
Inside each #CLST folder, you'll find six CLTS files referring to patent documents:

- #CLTS[VerticalName]\_PatDocs_[ClassificationSystem]_1.csv
- #CLTS[VerticalName]\_PatDocs_[ClassificationSystem]_2.csv
- #CLTS[VerticalName]\_PatDocs_[ClassificationSystem]_3.csv
- #CLTS[VerticalName]\_PatDocs_[ClassificationSystem]_4.csv

## Help CSV file
Inside each #CLST folder, you'll find the (help) CSV file used to generate the above files. This file contains essential data for analyzing patent documents in a core vertical of the WPI dataset. 

## Source Code
Scripts for generating the help CSV file and the #CLTS files.
