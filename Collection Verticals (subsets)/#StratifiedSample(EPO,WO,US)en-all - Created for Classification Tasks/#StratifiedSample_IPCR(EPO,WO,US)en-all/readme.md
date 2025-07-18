## 📊 Dataset Statistics

### 🧾 General Information
- **Total patents**: 93,589  
- **Total unique labels**: 602 subclasses 5,392 groups 

### 📁 Dataset Splits
| Split       | # of Patents |
|-------------|--------------|
| Train       | 71,407       |
| Validation  | 11,065       |
| Test        | 11,117       |

---

### 🏷️ Label Coverage per Split

#### 🔹 Subclass Counts
| Split       | # of Subclasses |
|-------------|-----------------|
| Train       | 598             |
| Validation  | 534             |
| Test        | 534             |
| **Total**   | 602             |

#### 🔹 Group Counts
| Split       | # of Groups     |
|-------------|-----------------|
| Train       | 5,201           |
| Validation  | 2,904           |
| Test        | 2,911           |
| **Total**   | 5,392           |

---

### 🔄 Label Overlap Between Splits

#### 📌 Subclass Differences
- In **validation** but **not in train**: 1  
- In **train** but **not in validation**: 65  
- In **test** but **not in train**: 1  
- In **train** but **not in test**: 65  

#### 📌 Group Differences
- In **validation** but **not in train**: 114  
- In **train** but **not in validation**: 2,411  
- In **test** but **not in train**: 94  
- In **train** but **not in test**: 2,384  

---

## Plots
### Distribution per office
![Plot the distribution of patents per office.png](Plot%20per%20office.png)

### Distribution per section label
![Plot the distribution of patents per section label.png](Plot%20the%20distribution%20of%20patents%20per%20section%20label.png)

### Distribution per month
![Plot the distribution of patents per month.png](Distribution%20of%20Entries%20Over%20Time.png)

---

For more details on the dataset preparation pipeline and objectives, refer to the [📄 Documentation: Stratified Sample Description](https://github.com/cs1msa/WPIplus/tree/main/Collection%20Verticals%20(subsets)/%23StratifiedSample(EPO%2CWO%2CUS)en-all%20-%20Created%20for%20Classification%20Tasks).

---

## 💻 Source Code

- For accessing the dataset preparation pipeline, refer to this notebook: [📄 Subpart Creation - EP, US, WO_all_ipcr](https://github.com/cs1msa/WPIplus/blob/main/Collection%20Verticals%20(subsets)/Source%20Code/Subpart%20Creation%20-%20EP%2C%20US%2C%20WO_all_ipcr.ipynb).
- For parsing the EP, WO, and US collections, see: [📄 Parsing subpart.ipynb](https://github.com/cs1msa/WPIplus/blob/main/Collection%20Verticals%20(subsets)/Source%20Code/Parsing%20subpart.ipynb).

