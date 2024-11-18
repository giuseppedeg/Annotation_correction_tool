import os
import json

"""
The scrip analyses the folder data/docs and creates:
   - the data/docs.json file
   - updates the pyscript.toml   
"""

DATA_DOCU_FOLDER = "data/docs"
DOC_JSON_FILENAME = "docs.json"
TOML_FILE = "pyscript.toml"
TOML_FILE_OUT = "pyscript.toml"
TOML_EOF_LINE = "# DOCS_FILE\n"

def create_docs_files():
    # Create docs.json file --------
    documents = []
    for doc_id_dolder in os.listdir(DATA_DOCU_FOLDER):
        elements_infolder = os.listdir(os.path.join(DATA_DOCU_FOLDER, doc_id_dolder))
        ind = 0
        for elem in elements_infolder:
            if ".json" in elem:
                cocojson_name = elem
                elements_infolder.remove(elem)
        
        image_name = elements_infolder[0]

        documents.append({
            "image_id": doc_id_dolder,
            "image_name": image_name,
            "cocojson_name": cocojson_name
        })
    
    docs_json = {'documents': documents}
    with open(os.path.join("data", DOC_JSON_FILENAME), "w") as outfile:
        json.dump(docs_json, outfile, indent=4)


    # Update pyscript.tompl file --------
    toml_file_lines=[]
    with open(TOML_FILE, "r") as toml_file:
        for line in toml_file.readlines():
            toml_file_lines.append(line)
            if line == TOML_EOF_LINE:
                break

    for doc in documents:
        toml_file_lines.append(f'"{{FROM}}{"/"}{"/".join([DATA_DOCU_FOLDER, doc["image_id"], doc["image_name"]])}" = "{{TO}}/{"/".join([DATA_DOCU_FOLDER, doc["image_id"], doc["image_name"]])}"\n')
        toml_file_lines.append(f'"{{FROM}}{"/"}{"/".join([DATA_DOCU_FOLDER, doc["image_id"], doc["cocojson_name"]])}" = "{{TO}}/{"/".join([DATA_DOCU_FOLDER, doc["image_id"], doc["cocojson_name"]])}"\n')
        toml_file_lines.append("\n")

    with open(TOML_FILE_OUT, "w") as toml_file:
        for line in toml_file_lines:
            toml_file.write(line)
    


if __name__ == "__main__":
    create_docs_files()
    print("Done!")

   