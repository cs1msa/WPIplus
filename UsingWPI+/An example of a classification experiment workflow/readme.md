# Overview
The WPI collection can be used to train and evaluate various classification models. It offers a wide array of information that can be used as distinct signals by individual classifiers or ensembles of classifiers.

As an example, we trained three classifiers on the EP vertical and report their performance in the below Table. For this experiment, we used the classification test set 1 for the #EP core vertical and IPCR labels, referred to as #CLTSep-ipcr{filter: B, all, 20151001}. Specifically, we used the [#CLTSep_VP_ipcr_1.csv](https://github.com/cs1msa/WPIplus/blob/main/Ground%20Truths/Classification/%23CLTSep/%23CLTSep-ipcr%7Bfilter%3A%20B%2C%20all%2C%2020151001%7D/CLTSep_VP_ipcr_1.csv) file. We began by creating the training and the testing dataset corresponding to the classification test set
 by retrieving and structuring patent data from the WPI collection.  


and those missing essential sections (abstract, description, claims).

<div class="alert alert-block alert-info">
<b>Important Note:</b> For the training set, patents listed in the test set MUST be excluded.
</div>
For the training dataset, we retain only patents that have all textual fields completed. Moreover, for both datasets labels are converted to subclass format (e.g., "G06F 17/30" → "G06F" and the Description and Claims sections are filtered to retain the first 300 words.

We employed the Bert-for-Patents model [24], incorporating concatenated GlobalAveragePooling and GlobalMaxPooling layers, followed by normalization, dense, dropout, and a final dense layers. Training utilized 128 tokens for abstracts and 256 tokens for descriptions and claims, with 3 epochs and a batch size of 4. Evaluation was conducted using precision, recall, and F1-score.
