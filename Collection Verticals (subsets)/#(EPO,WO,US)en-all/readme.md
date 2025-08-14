# 📘 #(EPO,WO,US)en-all Vertical

The `#(EPO,WO,US)en-all` vertical was developed to support **prior-art search tasks** and other IR/NLP experiments requiring high-quality, complete patent texts. This vertical includes **only patent documents that contain all three core textual sections—`abstract`, `description`, and `claims`—in English**. This filtering ensures a consistent and reliable dataset, closely reflecting real-world scenarios where complete texts are needed for indexing, retrieval, and analysis.

To reduce ambiguity and the risk of duplicate representation, only **one full-text document per patent** is included. Although the initial process identified 1,804,870 patent documents, the final vertical contains **1,803,293 unique patents** from the US, EP, and WO offices, each represented by a single, complete document.

---

## 📦 Dataset Overview

- **Vertical Name**: #(EPO,WO,US)en-all
- **Parent Collection**: WPI
- **Included Offices**: EP, WO, US
- **Total Documents Processed**: 1,804,870
- **Total Unique Patents**: 1,803,293
- **Language Filter**: English (abstract, description, and claims required)

For transparency, the full list of patent IDs/documents included in the vertical is available here: [🔗 Patent ID List (Google Drive)](https://drive.google.com/file/d/17g6XzmTnXIStdTUhrZki8PpHwU93bh2s/view?usp=sharing)

---

### 📊 Distribution by Patent Office

| Office | Documents     | % of Total |
|--------|---------------|------------|
| US     | 1,358,256     | 75.32%     |
| WO     | 218,774       | 12.13%     |
| EP     | 226,263       | 12.54%     |

---

### 📄 Distribution by Kind Code

| Kind Code | Description         | % of Total |
|-----------|---------------------|------------|
| A1        | Application docs     | 63%        |
| B2        | Granted patents      | 31%        |
| B1        | Granted (w/o search) | 3%         |
| A2, A9, A4, B9 | Other types     | <1% each   |

---

## 🚀 Sample Subset

A **60,000-document** sample from the vertical is available for rapid experimentation and prototyping.
- Format: SGML
- Includes: full text, metadata, and citation-based ground truth
  
---

## 🔗 Access

- 📂 [(EPO,WO,US)en-all Full Dataset](https://github.com/cs1msa/WPIplus/tree/main/Collection%20Verticals%20(subsets)/%23(EPO%2CWO%2CUS)en-all%20-%20Created%20for%20Priot-Art%20Search%20Tasks)
- ⚡ [60K Sample Subset (SGML)](https://github.com/cs1msa/WPIplus/tree/main/Collection%20Verticals%20(subsets)/%23Sample(EPO,WO,US)en-all%20-%20Created%20for%20Priot-Art%20Search%20Tasks)
- 📄 [Patent ID List (Google Drive)](https://drive.google.com/file/d/17g6XzmTnXIStdTUhrZki8PpHwU93bh2s/view?usp=sharing)

