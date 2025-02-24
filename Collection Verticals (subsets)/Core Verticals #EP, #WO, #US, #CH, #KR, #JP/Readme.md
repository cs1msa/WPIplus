## Core Vertical Organization
Each folder contains five files with key information about the specific vertical. These files include:

1. **\[VerticalName\]_PatDocs.csv** – A list of all patent documents in the specific vertical, sorted by patent number (fields: 'xml_file_name', 'ucid', 'patent_number').
2. **\[VerticalName\]_Pat.csv** – A list of all patent numbers in the specific vertical (field: 'patent_number').
3. **\[VerticalName\]_ClassInfoIPC.csv** – Contains the IPC classification codes for all patent documents in the specific vertical, sorted by patent number (fields: 'xml_file_name', 'ucid', 'patent_number', 'main_classification', 'further_classification').
4. **\[VerticalName\]_ClassInfoIPCR.csv** – Contains the IPCR classification codes for all patent documents in the specific vertical, sorted by patent number (fields: 'xml_file_name', 'ucid', 'patent_number', 'classification_ipcr').
5. **\[VerticalName\]_ClassInfoCPC.csv** – Contains the CPC classification codes for all patent documents in the specific vertical, sorted by patent number (fields: 'ucid', 'patent_number', 'xml_file_name').
