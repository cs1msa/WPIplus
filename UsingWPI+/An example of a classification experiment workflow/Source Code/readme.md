# Source Code Organization
This folder contains scripts that assist in the creation of the training and testing datasets corresponding to the Classification Test Set 1 for the #EP core vertical and IPCR labels, referred to as #CLTSep-ipcr{filter: B, all, 20151001} and, specifically, the #CLTSep_VP_ipcr_1.csv file. 

## CLTS Testing Dataset Creation
- [CLTS Testing Dataset Creation](https://github.com/cs1msa/WPIplus/blob/main/UsingWPI%2B/An%20example%20of%20a%20classification%20experiment%20workflow/Source%20Code/CLTS%20Testing%20Dataset%20Creation.ipynb): This script creates testing datasets corresponding to the classification test sets (CLTS) by retrieving and structuring patent data from the WPI collection.
  
## CLTS Training Dataset Creation
- [CLTS Training Dataset Creation](https://github.com/cs1msa/WPIplus/blob/main/UsingWPI%2B/An%20example%20of%20a%20classification%20experiment%20workflow/Source%20Code/CLTS%20Training%20Dataset%20Creation.ipynb): This script creates training datasets corresponding to the classification test sets (CLTS) by retrieving and structuring patent data from the WPI collection. The process is similar to the [CLTS Testing Dataset Creation](), with one key difference that instead of retrieving patent data included in the CLTS, this script retrieves all patent data that is NOT part of the CLTS.

