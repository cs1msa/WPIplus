import os
from bs4 import BeautifulSoup
import shutil

# Define directory paths
wpi_directory = "<path_to_wpi_files>"

# Initialize data structures and counters
wpi_dict = {}

# Build a dictionary of WPI patents with citations
for subdir, _, files in os.walk(wpi_directory):
    for file in files:
        patent_path = os.path.join(subdir, file)
        with open(patent_path, encoding='utf-8') as f:
            patent = f.read()

        root = BeautifulSoup(patent, 'xml')
        citations = root.find_all('patcit')

        if citations:
            cit_list = [cit.get('ucid') for cit in citations if cit.get('ucid')]
            file_id = file.split('.')[0]
            wpi_dict[file_id] = cit_list

    print(f"Processed directory: {subdir}")

# Create ground truth file
with open('wpi_ground_truths.txt', 'a') as writer:
    for key, citations in wpi_dict.items():
        if len(citations) >= 2 and all(cit in wpi_dict for cit in citations):
            writer.write(f"{key}<sep>{' '.join(citations)}\n")

# Create qrels file
with open('wpi_qrels.txt', 'w', encoding='utf-8') as writer:
    with open('wpi_ground_truths.txt', 'r') as reader:
        for line in reader:
            topic, gd = line.strip().split("<sep>")
            for citation in gd.split():
                writer.write(f"{topic}\t0\t{citation}\t1\n")