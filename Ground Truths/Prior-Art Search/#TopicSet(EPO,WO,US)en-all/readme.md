# 📘 README: Ground Truth Construction for #(EPO,WO,US)en-all Vertical

## 📌 Overview

This page documents the methodology and structure behind the ground truth topic sets developed from the **#(EPO,WO,US)en-all** vertical. This vertical includes only those patent documents that contain **complete English text** (abstract, description, claims), ensuring a high-quality dataset for prior-art retrieval and evaluation tasks.

---

## 🧠 Methodology

Ground truth construction is based on **citation analysis**, inspired by the methodology presented in \[20] (CLEF-IP). In this framework:

* Each **topic** is a patent document.
* **Relevant documents** are other patents it cites **within the dataset**.

### 🏗️ Step-by-Step Construction

#### 1️⃣ Dataset Processing

* Parsed all patent documents from the #(EPO,WO,US)en-all vertical.
* Extracted citations from `<patcit>` tags using the `ucid` attribute.

#### 2️⃣ Citation Analysis

* Retained only documents where **all citations** exist within the dataset.
* Ensured each topic has **at least 2 citations**.
* Guaranteed dataset **self-sufficiency** (no reliance on external sources).

#### 3️⃣ Topic Definition

* **Topics**: Patent documents with valid internal citations.
* **Relevant Docs**: Cited patents that are also present in the dataset.

---

## 🧪 Topics and Relevance Judgments

A total of **2,592 topics** were constructed:

* **Training Set**: 1,669 topics with **exactly 2 relevant documents** each.
* **Test Set**: 923 topics with **3 or more relevant documents** each.

### 📈 Citation Count Distribution

| Min. # of Citations | ≥2      | ≥3      | ≥4      | ≥5      | ≥6      | ≥7      |
| ------------------- | ------- | ------- | ------- | ------- | ------- | ------- |
| # of Docs           | \~1.29M | \~1.16M | \~1.03M | \~0.90M | \~0.81M | \~0.73M |

---

## 📥 Download Links

* 📦 **All Topics**:
  [Google Drive Folder](https://drive.google.com/drive/folders/1WxEbo5WDWswTPqWlyOpjxd7mOhbq14Ig?usp=sharing)

* 🎓 **Training Set** (1,669 topics):
  [Google Drive Folder](https://drive.google.com/drive/folders/1oEPlsNg9wC5XsQnK2YoiJCTCe5_58CNM?usp=sharing)

* 🧪 **Test Set** (923 topics):
  [Google Drive Folder](https://drive.google.com/drive/folders/1byS9-5-ireaxfFmJ3QE3dOTqrs8El3jG?usp=sharing)

* ✅ **Relevance Judgments (Qrels File)**:
  [Download File](https://drive.google.com/file/d/1ZWAb7T_s5qg6OILwVgJw8Hu9lZIJ5KXf/view?usp=sharing)

---

## 📚 References

* \[1] M. Lupu, F. Piroi and A. Hanbury, “Aspects and analysis of patent test collections,” in PaIR '10: Proceedings of the 3rd international workshop on Patent information retrieval, 2010.
* \[2] G. Roda, Tait, P. F. J. and V. Zenz, “CLEF-IP 2009: Retrieval Experiments in the Intellectual Property Domain,” In: Peters, C., et al. Multilingual Information Access Evaluation I. Text Retrieval Experiments. CLEF 2009. Lecture Notes in Computer Science, vol. 6241, 2010.
* \[3] E. Graf and L. Azzopardi, “A Methodology for Building a Patent Test Collection for Prior Art Search,” in In: The Second International Workshop on Evaluating Information Access (EVIA)@NTCIR, 2008.
 
 

---

