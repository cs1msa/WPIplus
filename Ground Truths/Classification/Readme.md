# Test Set Construction Methodology

Our test set construction process consists of two main stages:

## Analyzing Label Distributions
In the first stage, we analyze the distribution of subclass-level labels across the entire collection. This helps define task-specific test sets, as described below:
- #CLTS1: The first test set includes patents with all observed labels, representing the full range of natural label distributions in real-world data.
- #CLTS2: The second test set includes patents that fall within a specific statistical range—excluding outliers outside the 5th to 95th percentile. This approach ensures that the dataset focuses on the most representative patents, minimizing the influence of extreme cases.
- #CLTS3: The third test set includes patents with well-represented labels, specifically those occurring in over 50 patents (#CLTS3a) or more than 100 patents (#CLTS3b).
- #CLTS4: The fourth test set includes patents with few-shot labels, which are those appearing in fewer than 50 patents (#CLTS4a) or fewer than 100 patents (#CLTS4b), to evaluate performance on rare categories.

## Generating Test Sets
After identifying the labels of interest for each test set, we curate the test sets by selecting patents that meet the following conditions:
- Complete textual fields: The patent must have all three key fields (abstract, description, and claims) fully populated.
- B kind code: The patent must be assigned a B kind code (e.g., B1, B2, B3, etc.).
- Issued date: The patent must have an issue date after October 1, 2015.
- Relevant labels: The patent must include at least one label from the respective test set’s label set.

# Generalizable Methodology

This process is repeatable for constructing classification test sets across different verticals and classification schemes, ensuring consistent evaluation across various patent datasets.
