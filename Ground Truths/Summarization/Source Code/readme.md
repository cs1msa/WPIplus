# Source Code Organization
This folder contains scripts that assist in the creation of summarization test sets for the WPI dataset. These scripts help process and structure patent text, organizing it into test sets based on predefined criteria. They ensure the selection of relevant patents with high-quality summaries, facilitating the construction of test sets for various verticals and enabling comprehensive summarization analysis.

## Summarization Test Set Creation for Core Verticals
- [Summarization Test Set Creation](https://github.com/cs1msa/WPIplus/blob/main/Ground%20Truths/Summarization/Source%20Code/Summarization%20Test%20Set%20Creation.ipynb): This script facilitates the creation of summarization test sets (i.e., ground truth), using a CSV file as input. It retrieves key textual sections (abstract, description, claims, title) from patent documents within a specific core vertical (e.g., EP) and extracts critical sections such as the brief description, summary section, and first claim.

## CSV File Creation for Core Verticals
- [Core Verticals - CSV File Creation for Patent Document Analysis](https://github.com/cs1msa/WPIplus/blob/main/Collection%20Verticals%20(subsets)/Source%20Code/CSV%20File%20Creation%20for%20Patent%20Document%20Analysis.ipynb): This script generates a CSV file containing essential data for analyzing patent documents in a core vertical of the WPI dataset.
