import os
from js import Uint8Array, File, URL, document, FileReader, window, console
import io
from datetime import datetime

class FileManagewr():
    def __init__(self) -> None:
        pass




def download_json(json_filemane, date_format="%d_%m_%Y_%H_%M_%S"):
    """
    Download current CocoJSON file
    """
    with open(json_filemane, 'r', encoding="utf-8") as outfile:
        jcoco_string = outfile.read()

    json_stream = io.BytesIO(jcoco_string.encode("utf-8"))
    bytes_len = len(jcoco_string) 

    js_array = Uint8Array.new(bytes_len)
    js_array.assign(json_stream.getbuffer())

    now = datetime.now()

    dt_string = now.strftime(date_format)

    json_filemane = f"{os.path.splitext(json_filemane)[0]}__{dt_string}.json"

    file = File.new([js_array], json_filemane, {type: "application/json"})
    url = URL.createObjectURL(file)

    hidden_link = document.createElement("a")
    hidden_link.setAttribute("download", json_filemane)
    hidden_link.setAttribute("href", url)
    hidden_link.click()

def upload_json(current_json_filemane, json_bytes):
    """#write JSON file"""
    with open(current_json_filemane, "wb") as binary_file:
        binary_file.write(json_bytes)


