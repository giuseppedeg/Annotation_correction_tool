import os
import shutil
import json

"""
The scrip analyses the folder data/docs and creates:
   - the data/docs.json file
   - updates the pyscript.toml   
"""

DATA_DOCU_FOLDER = "data/docs"
DOC_JSON_FILENAME = "docs.json"
TOML_FILE = "pyscript.toml"
TOML_OUT_FOLDER = "toml"
TOML_EOF_LINE = "# END COMMON PART\n"
PROJFILE_EXT = ".pap"

def create_docs_files():
    if os.path.exists(TOML_OUT_FOLDER):
        shutil.rmtree(TOML_OUT_FOLDER)
    os.mkdir(TOML_OUT_FOLDER)


     # create base TOML file content:
    base_toml_file_lines=[]
    with open(TOML_FILE, "r") as toml_file:
        for line in toml_file.readlines():
            base_toml_file_lines.append(line)
            if line == TOML_EOF_LINE:
                break

    documents = []
    for doc_id_folder in (os.listdir(DATA_DOCU_FOLDER)):
        elements_infolder = os.listdir(os.path.join(DATA_DOCU_FOLDER, doc_id_folder))

        # cocojson_name = "none.json"
        # for elem in elements_infolder:
        #     if ".json" in elem:
        #         cocojson_name = elem
        #         elements_infolder.remove(elem)
        
        # image_name = elements_infolder[0]

        # if cocojson_name == "none.json":
        #     with open(os.path.join(DATA_DOCU_FOLDER,doc_id_folder, "none.json"), "w") as f:
        #         f.write('{"info": {},"licenses": {},"categories": [],"images": [],"annotations": [],"zones": []}')
            

        # documents.append({
        #     "image_id": doc_id_folder,
        #     "image_name": image_name,
        #     "cocojson_name": cocojson_name
        # })

        proj_file = None

        for elem in elements_infolder:
            if os.path.splitext(elem)[-1] == PROJFILE_EXT:
                proj_file = elem
                break

        if proj_file is None:
            continue

        documents.append({
            "image_id": doc_id_folder,
            "proj_file": proj_file
        })

        # create TOML files:
        toml_file_lines = base_toml_file_lines.copy()

        # toml_file_lines.append(f'"{{FROM}}{"/"}{"/".join([DATA_DOCU_FOLDER, doc_id_folder, image_name])}" = "{{TO}}/{"/".join([DATA_DOCU_FOLDER, doc_id_folder, image_name])}"\n')
        # toml_file_lines.append(f'"{{FROM}}{"/"}{"/".join([DATA_DOCU_FOLDER, doc_id_folder, cocojson_name])}" = "{{TO}}/{"/".join([DATA_DOCU_FOLDER, doc_id_folder, cocojson_name])}"\n')
        toml_file_lines.append(f'"{{FROM}}{"/"}{"/".join([DATA_DOCU_FOLDER, doc_id_folder, proj_file])}" = "{{TO}}/{"/".join([DATA_DOCU_FOLDER, doc_id_folder, proj_file])}"\n')
        toml_file_lines.append("\n")

        with open(os.path.join(TOML_OUT_FOLDER, doc_id_folder+".toml"), "w", encoding='utf-8') as toml_file:
            for line in toml_file_lines:
                toml_file.write(line)

    docs_json = {'documents': documents}
    with open(os.path.join("data", DOC_JSON_FILENAME), "w") as outfile:
        json.dump(docs_json, outfile, indent=4)




if __name__ == "__main__":
    create_docs_files()
    print("Document Loaded!!")

   