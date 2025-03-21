# Description of the #(EPO,WO,US)en-all Vertical
For the prior-art task, we developed a new vertical called #(EPO, WO, US)en-all. 
This subset was created to address potential issues and biases arising from incomplete text sections in patent documents. 
Specifically, this vertical includes only those patent documents that contain all critical sections—Abstract, Description, and Claims—in English, ensuring a more reliable and consistent dataset for analysis. 
This decision is in line with real-world scenarios where the complete texts of patent documents are available for indexing and searching. 
We systematically iterated through all core verticals of the WPI collection (i.e. #EP, #WO, #US, #CH, #KR, #JP), processing each document, if it meets this text completeness criterion. 
This process returned a total of 1,804,870 patent documents, corresponding to 1,803,293 unique patents from the US, EP, and WO patent offices. 
To prevent unnecessary complexity and reduce the risk of errors that could arise from overlooking this detail (i.e., some patents are represented by multiple patent documents), 
we include only the 1,803,293 unique patents as members of this vertical. By doing this, in the #(EPO, WO, US)en-all vertical, 
each patent is represented by only one patent document, rather than multiple. This approach helps avoid a common source of confusion, 
particularly for researchers who may not be familiar with the unique characteristics and intricacies of patent documents. 

The 1,803,293 patent IDs/files composing this vertical are as follows:
https://drive.google.com/file/d/17g6XzmTnXIStdTUhrZki8PpHwU93bh2s/view?usp=sharing
