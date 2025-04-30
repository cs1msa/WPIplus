# Overview

The WPI collection serves as a valuable resource for training and evaluating classification models, providing diverse information that can be leveraged as distinct signals by individual classifiers or ensembles.

As an example, we trained three classifiers on the EP vertical and evaluated their performance, as shown in the table below. For this experiment, we used Classification Test Set 1 for the #EP core vertical and IPCR labels, referred to as [#CLTSep-ipcr{filter: B, all, 20151001}](https://github.com/cs1msa/WPIplus/tree/main/Ground%20Truths/Classification/%23CLTSep/%23CLTSep-ipcr%7Bfilter%3A%20B%2C%20all%2C%2020151001%7D). Specifically, we used the [#CLTSep_VP_ipcr_1.csv](https://github.com/cs1msa/WPIplus/blob/main/Ground%20Truths/Classification/%23CLTSep/%23CLTSep-ipcr%7Bfilter%3A%20B%2C%20all%2C%2020151001%7D/CLTSep_VP_ipcr_1.csv) file.

#### Important Note: For the training dataset, patents listed in the test set MUST be excluded.

## Data Preparation

To prepare the training and testing datasets, we extracted and structured patent data from the WPI collection. For the training dataset, we retain only patents that have all textual fields completed (abstract, description, claims). Moreover, for both datasets labels are converted to subclass format (e.g., "G06F 17/30" → "G06F") and the Description and Claims sections are filtered to retain the first 300 words.

## Model Training Details

We employed the [Bert-for-Patents model](https://huggingface.co/anferico/bert-for-patents), incorporating:
1. Concatenated GlobalAveragePooling & GlobalMaxPooling layers
2. Normalization, Dense, and Dropout layers
3. Final Dense output layer

Training was conducted with the following parameters:
- 128 tokens for abstracts
- 256 tokens for descriptions and claims
- Epochs: 3
- Batch size: 4

## Model Evaluation

Model evaluation was performed using precision, recall, and F1-score to assess classification performance.

Table: Classification performance using a prediction threshold of 0.5
| Classifier type |  @3 | @5 | @10 | 
| ------------- | ------------- | ------------- | ------------- |
|  P@3 | R@3 | F1@3 |  P@5 | R@5 | F1@5  | P@10 | R@10 | F1@10 |
| Classifier #1 (Abstract) | 77.49%	 | 64.87% | 70.62% |
| Classifier #2 (Description)	| 76.47%  | 68.14%  | 72.07%  |
| Classifier #3 (Claims) | 76.68%  | 64.54%	  | 70.09%  |


## Help files
The testing dataset (processed as described above in "Data Preparation"):
- [CLTSep_VP_ipcr_1_test_dataset(processed).csv](https://drive.google.com/file/d/11DJqucRTxIfFUG_A0ZB35zDQG3xJeQUE/view?usp=sharing)

The training dataset. We provide the UCID of patent documents included in the training dataset and the processed dataset as described above in "Data Preparation"):
- [CLTSep_VP_ipcr_1_train_dataset_PatDocs.csv](https://drive.google.com/file/d/1U7pJAsXwh8jSA2Og_QvvMjaCvzM8w-oI/view?usp=sharing)
- [CLTSep_VP_ipcr_1_train_dataset(processed).csv](https://drive.google.com/file/d/1bTR1R98HKVlGZsUx8Wz1MZxAQba65xEJ/view?usp=sharing)

## Source Code
The scripts for generating the help files and the script for training the classifiers can be found under the [Source Code](https://github.com/cs1msa/WPIplus/tree/main/UsingWPI%2B/An%20example%20of%20a%20classification%20experiment%20workflow/Source%20Code) folder.
