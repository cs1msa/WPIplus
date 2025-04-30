# Classification Test Set Organization 
## CLTS files referring to VP 
Inside each #CLST folder, you'll find six CLTS files referring to VP:

- #CLTSep\_VP_ipcr_1.csv
- #CLTSep\_VP_ipcr_2.csv
- #CLTSep\_VP_ipcr_3a.csv
- #CLTSep\_VP_ipcr_3b.csv
- #CLTSep\_VP_ipcr_4a.csv
- #CLTSep\_VP_ipcr_4b.csv

## CLTS files referring to Patent Documents 
Inside each #CLST folder, you'll find six CLTS files referring to patent documents:

- #CLTSep\_PatDocs_ipcr_1.csv
- #CLTSep\_PatDocs_ipcr_2.csv
- #CLTSep\_PatDocs_ipcr_3a.csv
- #CLTSep\_PatDocs_ipcr_3b.csv
- #CLTSep\_PatDocs_ipcr_4a.csv
- #CLTSep\_PatDocs_ipcr_4b.csv

## CLTS files referring to Subclass Codes
You'll find six CLTS files referring to subclass codes (associated with their frequency) belonging to the specific classification test set:

    #CLTSep_codes_ipcr_1.csv
    #CLTSep_codes_ipcr_2.csv
    #CLTSep_codes_ipcr_3a.csv
    #CLTSep_codes_ipcr_3b.csv
    #CLTSep_codes_ipcr_4a.csv
    #CLTSep_codes_ipcr_4b.csv

## Help CSV file
The (help) CSV file used to generate the above files is:
- [EP_csv_file_for_wpi_analysis.csv](https://drive.google.com/file/d/1Chacl6rF8Yk0_dScPnt4JT3IkEeDXqCv/view?usp=sharing)

## Source Code
The scripts for generating the CLTS files and the help CSV file can be found under the [Source Code](https://github.com/cs1msa/WPIplus/tree/main/Ground%20Truths/Classification/Source%20Code) folder.

# Demonstration of the Test Set Construction Methodology
## Stage 1: Label Definition and Analysis

To define the labels for each test set, we first analyze the subclass-level distribution of IPCR labels across the EP vertical. The process is as follows:

**1. Extract IPCR Labels from EP Patents:**
We begin by extracting the IPCR labels from the EP patents.

**2. Infer Subclass and Calculate Frequencies:**
After extracting the labels, we infer the subclass for each patent and calculate the frequency of each subclass label. In cases where a patent exists with more than one kind code (e.g., EP-2678998-A1.xml and EP-2678998-B1.xml), we select the latest kind code as it carries the most up-to-date and accurate classification information for that patent.

**3. Resulting Data:**
After processing the labels, we are left with 469,757 patent documents from the latest kind codes, containing 7,163 group labels and 632 subclass labels.

### Test Set Assignment

We then assign IPCR labels to each of the test sets based on the predefined criteria:
- **#EP-CLTS1:** This test set includes all available subclass labels (632 total).
- **#EP-CLTS2:** The most frequently occurring subclass labels are selected, excluding outliers, resulting in 565 labels.
- **#EP-CLTS3:** This test set includes either:
571 labels that are represented in more than 50 patents (#CLTS3a), or
524 labels represented in more than 100 patents (#CLTS3b).
- **#EP-CLTS4:** This test set focuses on low-represented subclass labels, including:
61 labels appearing in fewer than 50 patents (#CLTS4a), or
108 labels appearing in fewer than 100 patents (#CLTS4b).

## Stage 2: Patent Document Selection

In the second stage, we search for patent documents that meet the following criteria and contain at least one of the labels assigned to the respective test set:

**1.Textual Fields Completion:** The patent must have all textual fields (abstract, description, and claims) completed.

**2. Kind Code Filter:** The patent must be assigned a B kind code (e.g., B1, B2, B3, etc.).

**3. Issued Date Filter:** The patent must have been issued after October 1, 2015.

**4. Label Match:** The patent must include at least one of the assigned labels from the respective test set.

After applying these filters, 6,181 patent documents are identified, satisfying these criteria. These documents are then used to construct the following test set collections:
Test Set Collections

- **#EP-CLTS1:** This test set contains 6,181 patent documents (corresponding to 2,847 single patents). 
**Coverage:** 461 subclass labels out of 632 available labels, leaving 171 labels missing from the test set.

- **#EP-CLTS2:** This test set contains 4,267 patent documents (corresponding to 1,967 single patents). 
**Coverage:** 428 subclass labels out of 565 initially assigned labels. 33 subclass labels are included from outliers.

- **#EP-CLTS3:**
        
**Alternative 1 (>50 patents):** Includes 6,179 patent documents (corresponding to 2,846 single patents) with 456 labels out of 565 assigned, plus 4 additional labels not included in the test set labels.
        
**Alternative 2 (>100 patents):** Includes 6,175 patent documents (corresponding to 2,844 single patents) with 443 labels out of 515 assigned, plus 16 additional labels not included in the test set labels.

- **#EP-CLTS4:**
        
**Alternative 1 (<50 patents):** Includes 5 few-shot subclass labels (out of 61) that are present in only 13 patent documents (corresponding to 6 single patents). These documents also include 10 labels not categorized as few-shot labels.
        
**Alternative 2 (<100 patents):** Includes 51 patent documents (corresponding to 23 single patents) that cover 18 few-shot subclass labels out of 108, plus 36 additional labels not categorized as few-shot labels.

## Conclusion

The construction of the classification test sets maintains the same label distribution found across the entire WPI collection, ensuring that the test sets accurately reflect the overall distribution of categorization in the dataset. This methodology can be replicated for the construction of test sets for other verticals and classification schemes as needed.
