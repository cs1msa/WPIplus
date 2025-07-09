## 📊 Dataset Statistics

### 🧾 General Information
- **Total patents**: 97,063  
- **Total unique labels**: 621 subclasses 7,984 groups 

### 📁 Dataset Splits
| Split       | # of Patents |
|-------------|--------------|
| Train       | 71,199       |
| Validation  | 10,013       |
| Test        | 9,851       |

---

### 🏷️ Label Coverage per Split

#### 🔹 Subclass Counts
| Split       | # of Subclasses |
|-------------|-----------------|
| Train       | 619             |
| Validation  | 562             |
| Test        | 561             |
| **Total**   | 621             |

#### 🔹 Group Counts
| Split       | # of Groups     |
|-------------|-----------------|
| Train       | 7,729           |
| Validation  | 4,752           |
| Test        | 4,687           |
| **Total**   | 7,984           |

---

### 🔄 Label Overlap Between Splits

#### 📌 Subclass Differences
- In **validation** but **not in train**: 1  
- In **train** but **not in validation**: 58 
- In **test** but **not in train**: 1  
- In **train** but **not in test**: 59  

#### 📌 Group Differences
- In **validation** but **not in train**: 143 
- In **train** but **not in validation**: 3,120  
- In **test** but **not in train**: 138  
- In **train** but **not in test**: 3,180  

---

For more details on the dataset preparation pipeline and objectives, refer to the [📄 Documentation: Stratified Sample Description](https://github.com/cs1msa/WPIplus/tree/main/Collection%20Verticals%20(subsets)/%23StratifiedSample(EPO%2CWO%2CUS)en-all%20-%20Created%20for%20Classification%20Tasks).

---

## Plots
### Distribution per office
![Plot the distribution of patents per office.png](Plot%20per%20office_cpc.png)

### Distribution per section label
![Plot the distribution of patents per section label.png](https://github.com/cs1msa/WPIplus/blob/main/Collection%20Verticals%20(subsets)/%23StratifiedSample(EPO%2CWO%2CUS)en-all%20-%20Created%20for%20Classification%20Tasks/%23StratifiedSample_CPC(EPO%2CWO%2CUS)en-all/Plot%20the%20distribution%20of%20patents%20per%20section%20label_cpc.png)

### Distribution per month
![Plot the distribution of patents per month.png](Distribution%20of%20Entries%20Over%20Time_cpc.png)

---

For more details on the dataset preparation pipeline and objectives, refer to the [📄 Documentation: Stratified Sample Description](https://github.com/cs1msa/WPIplus/tree/main/Collection%20Verticals%20(subsets)/%23StratifiedSample(EPO%2CWO%2CUS)en-all%20-%20Created%20for%20Classification%20Tasks).

---

## 💻 Source Code

- For accessing the dataset preparation pipeline, refer to this notebook: [📄 Subpart Creation - EP, US, WO_all_cpc](https://github.com/cs1msa/WPIplus/blob/main/Collection%20Verticals%20(subsets)/Source%20Code/Subpart%20Creation%20-%20EP%2C%20US%2C%20WO_all_cpc.ipynb).
- For parsing the EP, WO, and US collections, see: [📄 Parsing subpart.ipynb](https://github.com/cs1msa/WPIplus/blob/main/Collection%20Verticals%20(subsets)/Source%20Code/Parsing%20subpart.ipynb).


