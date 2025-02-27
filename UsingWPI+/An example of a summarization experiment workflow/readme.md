# Overview
The WPI collection is a valuable resource for training and fine-tuning summarization models, provided that it is carefully curated to exclude the targeted information. Additionally, it can be used for evaluating existing summarization models.

## Summarization Task
For training/fine-tuning new summarization models, different sections of the patent can serve as input:
- Description, claims, or both can be used to generate summaries, with the abstract acting as the reference output.
- The [summarization test sets](https://github.com/cs1msa/WPIplus/tree/main/Ground%20Truths/Summarization) provide additional information that can enhance model performance, including the brief description, summary segment, and first claim.

## Additional Summarization Tasks

Beyond standard abstract generation, the WPI collection supports additional summarization tasks:
### Summary Segment Extraction/Generation:
- The summary segment of the description is a valuable alternative to the abstract, often offering a more comprehensive description of the invention. A model can be trained to generate or extract this segment which is available in the WPI collection.
### First Claim Extraction/Generation:
- The first claim is often considered equivalent to the summary segment, providing a concise legal definition of the invention. A model can be trained to generate or extract the first claim which is available in the WPI collection.

**_(A specific summarization example will be uploaded soon...)_**
