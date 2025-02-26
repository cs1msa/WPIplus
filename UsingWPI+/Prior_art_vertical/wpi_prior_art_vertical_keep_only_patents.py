import os
import shutil
from collections import defaultdict

# Define path and initialize variables
all_data_path = '<path_to_all_patent_folders>'
output_file_path = '<path_to_output_file>'

# Define ranking for kind codes
kind_rank = {"B9": 7, "B2": 6, "B1": 5, "A9": 4, "A4": 3, "A2": 2, "A1": 1}

# Collect all patent filenames
patents = []
for folder in os.listdir(all_data_path):
    folder_path = os.path.join(all_data_path, folder)
    if os.path.isdir(folder_path):
        patents.extend(os.listdir(folder_path))

# Dictionary to store the best patent for each base number
best_patents = {}

# Process each patent file name
for patent in patents:
    parts = patent.replace(".txt", "").split("-")
    if len(parts) >= 3:
        base_number = "-".join(parts[:2])
        kind_code = parts[2]

        # Update best patent based on ranking
        if base_number not in best_patents or kind_rank.get(kind_code, 0) > kind_rank.get(best_patents[base_number], 0):
            best_patents[base_number] = kind_code

# Generate the final list
final_list = [f"{base}-{kind}.txt" for base, kind in best_patents.items()]

# Save the filtered list to a file
with open(output_file_path, 'w') as writer:
    writer.write('\n'.join(final_list))