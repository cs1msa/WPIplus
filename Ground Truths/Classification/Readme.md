# Test Set Construction Methodology

Our test set construction process consists of two main stages:

## Analyzing Label Distributions
In the first stage, we analyze the distribution of subclass-level labels across the entire collection. This helps define task-specific test sets, as described below:
- **#CLTS1**: The first test set includes patents with all observed labels, representing the full range of natural label distributions in real-world data.
- **#CLTS2**: The second test set includes patents that fall within a specific statistical range—excluding outliers outside the 5th to 95th percentile. This approach ensures that the dataset focuses on the most representative patents, minimizing the influence of extreme cases.
- **#CLTS3**: The third test set includes patents with well-represented labels, specifically those occurring in over 50 patents **(#CLTS3a)** or more than 100 patents **(#CLTS3b)**.
- **#CLTS4**: The fourth test set includes patents with few-shot labels, which are those appearing in fewer than 50 patents **(#CLTS4a)** or fewer than 100 patents **(#CLTS4b)**, to evaluate performance on rare categories.

## Generating Test Sets
After identifying the labels of interest for each test set, we curate the test sets by selecting patents that meet the following conditions:
- **Complete textual fields**: The patent must have all three key fields (abstract, description, and claims) fully populated.
- **B kind code**: The patent must be assigned a B kind code (e.g., B1, B2, B3, etc.).
- **Issued date**: The patent must have an issue date after October 1, 2015.
- **Relevant labels**: The patent must include at least one label from the respective test set’s label set.

## Generalizable Methodology

This process is repeatable for constructing classification test sets across different verticals and classification schemes, ensuring consistent evaluation across various patent datasets.

# Classification Test Set Organization 
Each #CLST folder contains six CLTS files referring to virtual patents (VP) and six CLTS files referring to individual patent documents, the help CSV file used to generate these files and links to the relevant source code.

## CLTS files referring to VP 
Inside each #CLST folder, you'll find six CLTS files referring to VP:

- #CLTS[VerticalName]\_VP_[ClassificationSystem]_1.csv
- #CLTS[VerticalName]\_VP_[ClassificationSystem]_2.csv
- #CLTS[VerticalName]\_VP_[ClassificationSystem]_3a.csv
- #CLTS[VerticalName]\_VP_[ClassificationSystem]_3b.csv
- #CLTS[VerticalName]\_VP_[ClassificationSystem]_4a.csv
- #CLTS[VerticalName]\_VP_[ClassificationSystem]_4b.csv

## CLTS files referring to Patent Documents 
Inside each #CLST folder, you'll find six CLTS files referring to patent documents:

- #CLTS[VerticalName]\_PatDocs_[ClassificationSystem]_1.csv
- #CLTS[VerticalName]\_PatDocs_[ClassificationSystem]_2.csv
- #CLTS[VerticalName]\_PatDocs_[ClassificationSystem]_3a.csv
- #CLTS[VerticalName]\_PatDocs_[ClassificationSystem]_3b.csv
- #CLTS[VerticalName]\_PatDocs_[ClassificationSystem]_4a.csv
- #CLTS[VerticalName]\_PatDocs_[ClassificationSystem]_4b.csv

## Help CSV file
Inside each #CLST folder, you'll find the (help) CSV file used to generate the above files. This file contains essential data for analyzing patent documents in a core vertical of the WPI dataset. 

## Source Code
Scripts for generating the help CSV file and the #CLTS files.
