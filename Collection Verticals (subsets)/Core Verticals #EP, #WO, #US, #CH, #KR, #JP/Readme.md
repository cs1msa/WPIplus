# Core Vertical Organization
Each folder contains a core vertical file (*.vertical) along with five supplementary files providing key information related to the specific vertical. Additionally, a help CSV file used in generating these outputs is included, along with links to the relevant source code.

## Vertical File
#### [VerticalName].vertical
This file provides the list of patent documents included in the corresponding vertical. 

           | 'xml_file_name' | 
 
## Five Supplementary Files 
#### [VerticalName]_PatDocs.csv
This file contains a list of all patent documents in the specific vertical, sorted by patent number.
This file contains three columns:

           | 'xml_file_name' | 'ucid' | 'patent_number' |

#### [VerticalName]_Pat.csv
This file contains a list of all patent numbers in the specific vertical.
This file contains one column:

           | 'patent_number' |

#### [VerticalName]_ClassInfoIPC.csv
This file contains the IPC classification codes for all patent documents in the specific vertical, sorted by patent number. 
This file contains three columns"

           | 'ucid' | 'main_classification' | 'further_classification' |

#### [VerticalName]_ClassInfoIPCR.csv
This file contains the IPCR classification codes for all patent documents in the specific vertical, sorted by patent number.
This file contains two columns:

           | 'ucid' | 'classification_ipcr' |

#### [VerticalName]_ClassInfoCPC.csv
It contains the CPC classification codes for all patent documents in the specific vertical, sorted by patent number.
This file contains two columns:

           | 'ucid' | 'classification_cpc' |

## Help CSV file
The (help) CSV file contains essential data for analyzing patent documents in a core vertical of the WPI dataset.

## Source Code
Scripts for generating the help CSV file and the five key files.
