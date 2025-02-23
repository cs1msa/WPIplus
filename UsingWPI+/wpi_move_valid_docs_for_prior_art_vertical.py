import os
from bs4 import BeautifulSoup
import shutil

# Define directory paths with descriptions
input_directory = "<path_to_input_patent_files>"
output_directory = "<path_to_output_patent_files>"

# Initialize counters
folder_counter = 0
current_folder = folder_counter
general_counter = 0

# Create the initial output folder
os.makedirs(os.path.join(output_directory, str(folder_counter)), exist_ok=True)

# Traverse through the input directory
for subdir, _, files in os.walk(input_directory):
    for file in files:
        counter = 0

        # Load and parse the patent file
        patent_path = os.path.join(subdir, file)
        with open(patent_path, encoding='utf-8') as f:
            patent = f.read()

        root = BeautifulSoup(patent, 'xml')

        # Check for the presence of key elements in English
        sections = {
            'invention-title': False,
            'abstract': False,
            'description': False,
            'claims': False
        }

        for section in sections:
            elements = root.find_all(section)
            if elements:
                for element in elements:
                    if element.get('lang') == 'EN' and len(element.text.strip()) > 1:
                        sections[section] = True
                        break

        # If all sections are present, copy the file
        if all(sections.values()):
            general_counter += 1
            destination_path = os.path.join(output_directory, str(current_folder), file)
            shutil.copyfile(patent_path, destination_path)

            # Create a new folder every 30,000 files
            if general_counter % 30000 == 0:
                folder_counter += 1
                os.makedirs(os.path.join(output_directory, str(folder_counter)), exist_ok=True)
                current_folder = folder_counter