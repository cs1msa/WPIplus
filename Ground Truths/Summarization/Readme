# Test Set Construction Methodology

This methodology ensures a structured, high-quality dataset for training and evaluating summarization models on patent data. Our test set construction process consists of four main parts. 

## Selection Criteria for Test Set (Part I)
Patents included in the test sets must meet the following criteria:

1. Complete textual fields: The patent must include an abstract, description, and claims.
2. B kind code selection: The patent must have a B kind code (e.g., B1, B2, B3, B6, B8, B9).
3. Date restriction: The patent must have been submitted in the last quarter of 2015 (i.e., after October 1, 2015). 

## Textual Data Retrieval (Part II)
To create a summarization dataset that is ready for use, we need to retrieve key textual sections from the original WPI collection:

1. Abstract – Serves as the reference summary.
2. Description – Typically used as input for generating summaries.
3. Claims – Typically included in the input text, as they define the scope of the invention.
4. Title – Provides additional context and may help improve summarization quality.

By ensuring these sections are included, the dataset will be structured and comprehensive, supporting high-quality summarization tasks.

<div class="alert alert-block alert-info">
<b>Tip for Part III:</b> To ensure proper extraction of patent text in Part III, the get function should separate the text it retrieves using a line separator ('\n ').
</div>

## Brief Description, Summary, and First Claim Extraction (Part III)
This step extracts key sections from each patent:

- Brief description
- Summary section
- First claim

<div class="alert alert-block alert-info">
<b>Tip:</b> To ensure proper extraction of patent text:
    
- description section must include author-annotated headings.
    
- claims section must follow a standard numbering format (e.g., starting from "1."). If these structural markers are missing, the algorithm may not detect the first claim. 
</div>

## Additional Criteria for Test Set (Part IV) (Optional)
Further refinement of the summarization test set may be applied by:

1. Filtering patents without a distinct summary segment
2. Removing patents where the abstract has low similarity with the description and summary segment

These additional filters help maintain high-quality and coherent summarization data.

## Final Summarization Test Set Outcomes
Three final test sets are defined:
- **#SMTS1**: Includes patents that meet the selection criteria from Part I (e.g., complete textual fields, B kind code, submitted after Oct 1, 2015). Full-text data (abstract, description, claims, title) is retrieved and key sections (brief description, summary section, first claim) are extracted.
- **#SMTS2**: Derived from #SMTS1 but excludes patents without a distinct summary segment. Ensures that only patents with clearly defined summaries are retained.
- **#SMTS3**: Derived from #SMTS2, applying an additional filter removing patents where the abstract has low similarity with the description & summary. Guarantees that abstracts are coherent and representative of the patent’s content.

# Summarization Test Set Organization 
Each #SLST folder contains three SMTS files referring to virtual patents (VP), the help CSV file used to generate these files and links to the relevant source code.

## SMTS files
Inside each #SMST folder, you'll find three SMTS files referring to VP:

- #SMTS[VerticalName]\_VP_1.csv
- #SMTS[VerticalName]\_VP_2.csv
- #SMTS[VerticalName]\_VP_3.csv

## Help CSV file
Inside each #SMST folder, you'll find the (help) CSV file used to generate the above files. This file contains essential data for analyzing patent documents in a core vertical of the WPI dataset. 

## Source Code
Scripts for generating the help CSV file and the #SMTS files.
