import os
from bs4 import BeautifulSoup
import re
import shutil

# Define directory paths
wpi_xml_directory = "<path_to_wpi_files>"
wpi_sgml_directory = "<path_to_wpi_sgml_output>"

# Load query topics from qrels
queries = set()
with open('wpi_qrels.txt', 'r') as qrels:
    for query in qrels:
        topic = query.split()[0]
        queries.add(topic)


# Text cleaning function
def clean_text(text):
    text = text.lower()
    remove_chars = r"[\n\t'\-\.\!@#\$%&\*\=\+0-9\(\)\{\}\[\],\"\?<>;¬°:]"
    text = re.sub(remove_chars, ' ', text)
    text = re.sub(' +', ' ', text)
    return text.strip()


# Initialize counters
folder_counter = 0
file_count = 0

# Create initial output folder
os.makedirs(os.path.join(wpi_sgml_directory, str(folder_counter)), exist_ok=True)

# Process WPI XML files
for subdir, _, files in os.walk(wpi_xml_directory):
    for file in files:
        file_id = file.replace('.xml', '')
        patent_path = os.path.join(subdir, file)

        # Handle topic files separately
        if file_id in queries:
            shutil.copy(patent_path, os.path.join(wpi_sgml_directory, 'topics'))
            continue

        file_count += 1

        # Parse the XML
        with open(patent_path, encoding='utf-8') as f:
            patent = f.read()
        root = BeautifulSoup(patent, 'xml')

        patent_doc = root.find('patent-document')
        if not patent_doc:
            continue

        patent_id = patent_doc.get('ucid', 'unknown')
        patent_date = patent_doc.get('date', 'unknown')

        # Split folders after 20,000 files
        if file_count > 20000:
            file_count = 0
            folder_counter += 1
            os.makedirs(os.path.join(wpi_sgml_directory, str(folder_counter)), exist_ok=True)

        output_path = os.path.join(wpi_sgml_directory, str(folder_counter), f"{patent_id}.txt")

        # Write SGML output
        with open(output_path, "w", encoding="utf-8") as writer:
            writer.write(f"<DOC>\n<DOCNO>{patent_id}</DOCNO>\n<DATE>{patent_date}</DATE>\n<TEXT>\n")


            def write_section(tag, label):
                elements = root.find_all(tag)
                if elements:
                    writer.write(f"<{label}>\n")
                    for element in elements:
                        if element.get('lang') == 'EN':
                            cleaned_text = clean_text(element.text)
                            writer.write(cleaned_text + "\n")
                            break
                    writer.write(f"</{label}>\n")


            # Write sections
            write_section('classification-ipcr', 'IPCR-CLASSIFICATIONS')
            write_section('classification-cpc', 'CPC-CLASSIFICATIONS')
            write_section('invention-title', 'TITLE')
            write_section('applicant', 'APPLICANT')
            write_section('inventor', 'INVENTOR')
            write_section('abstract', 'ABSTRACT')
            write_section('description', 'DESCRIPTION')
            write_section('claims', 'CLAIMS')

            writer.write("</TEXT>\n</DOC>")