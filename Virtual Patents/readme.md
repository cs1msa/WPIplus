# 🧠 Technical Note: The Virtual Patent (VP-WPI) Test Collection

This repository introduces the **VP-WPI Test Collection**, a novel dataset that aggregates patent documents from the **WPI (World Patent Information)** corpus at the *kind-code* level to create unified **“Virtual Patent” (VP)** documents.

---

## 1. Background: The WPI Foundation

The **WPI Test Collection** is a major, publicly available resource for patent research.  
It stands out due to its **multimodal** and **multilingual** data from **six major patent authorities**, a feature rarely found in other public collections.

**Coverage:** 2014–2015

**Key Features:**
- 📄 Full patent texts in XML format  
- 🧩 Comprehensive bibliographic metadata and citation networks  
- 🧠 Well-structured data across all technical fields  

**Key Resources:**
- M. Lupu *et al.*, “*The WPI patent test collection*,” *World Patent Information*, vol. 56, pp. 78–85, 2019.  
- XML data available on Zenodo: [https://doi.org/10.5281/zenodo.1489994](https://doi.org/10.5281/zenodo.1489994)

---

## 2. From WPI to WPI+

The **WPI+ resource** extends the original WPI collection with several enhancements, including:

- 🧮 Analysis source code and collection statistics  
- 🧱 Thematic subsets (“verticals”) and extraction tools  
- 🎯 Ground-truth data for tasks like *prior-art retrieval*  
- 🧠 Python notebooks with ML/DL usage examples  

**Key Resource:**  
M. Salampasis *et al.*, “*Towards a new paradigm for patent experimentation: WPI+*,” *World Patent Information*, vol. 83, 102389, 2025.

---

## 3. The Concept: What is a Virtual Patent?

A **Virtual Patent (VP)** is a synthesized document representing a single patent by **merging the most up-to-date information** from its various publication stages (e.g., *A1, A2, B1, B2*).

Patent offices often release multiple documents for the same invention, where later publications may include only partial updates or amendments.  
A **Virtual Patent** consolidates these into one **coherent, unified document**, ensuring that researchers always work with the **most complete and current** information.

> **Figure 1:** Creation of a Virtual Patent by merging fields from different patent documents.

---

## 4. The VP-WPI Collection

**VP-WPI** is a specialized *vertical* of the **WPI+ resource** that implements the **Virtual Patent** concept.  
It provides a unified, non-redundant view of patents by aggregating all related documents for a single invention into one **VP entity**.

**Key Advantages:**
- 🔁 **Simplifies analysis** by reducing document redundancy  
- ✅ **Enhances data consistency** with a single source of truth  
- 🔗 **Preserves traceability** with links to all original source documents  

---

## 5. Further Information

For complete technical details, including **collection statistics**, **data specifications**, and the **creation process**, please refer to:

- 📘 [TU WIEN Research Data Portal](#) *(Link placeholder)*  
- 💻 [Official WPI+ Documentation & Source Code – GitHub Repository](#)  
- 🎓 Papadopoulos, C. *MSc Thesis (in Greek)*, International Hellenic University  
  [https://repository.ihu.gr/handle/11544/47881](https://repository.ihu.gr/handle/11544/47881)

---

## 👥 Creators & Contributors

- **Christos Papadopoulos**  
- **Eleni Kamateri**  
- **Prof. Michail Salampasis**  
- **Dr. Florina Piroi**

---

### 📄 Citation

If you use this dataset in your research, please cite the relevant publications listed above.
