import pyscript
from pyscript import window, document, when, display, config, HTML
from pyweb import pydom
import js
from js import URL, document, window, console
from pyodide.ffi.wrappers import add_event_listener
from file_manager import download_file, upload_json
from manager import Manager, ID_UNKNOWN, STR_UNKNOWN_CAT
from fileformat_handler import FFHandler, EXT
import os
import shutil
import json
import random

"""
This file manage the interactions between the GUI and the business logic manager
"""
# GLOBAL VARs -------------------------------------------------------------------------------------------
class AppManager():
    def __init__(self) -> None:
        self.manager = None
        self.input_bb_image_id = -1

projectfile_h = FFHandler() #handler for save/load the project file
app = AppManager() # the manager contains all the business logic 

# m = None # it contains all the business logic 
# input_bb_image_id = -1

all_bbs = {}
#all_bbs[8] = [[[100,200],[200,200],[200,100],[100,100]],[[1000,600],[600,600],[600,1000],[1000,1000]]]

project_file_name = document.querySelector("#project_file_name")
project_file_name = project_file_name.value # it's a str


# Interface methods -----------------------------------------------------------------------------------
@when("change", "#file-input")
async def handle_upload(event):
    """
    Load a project File
    """

    open_load()

    file_input = document.getElementById("file-input")
    
    # if not file_input.files.length:
    #     document.getElementById("output").innerText = "No file selected."
    #     return
    
    file = file_input.files.item(0)  # Get the first selected file

    array_buf = await file.arrayBuffer() # Get arrayBuffer from file
    file_bytes = array_buf.to_bytes() # convert to raw bytes array 

    project_dic = json.loads(file_bytes)

    load_project(project_dic)
    init()



def _update_all_bbs(key_id):
    bbs_list = app.manager.get_list_annotations_per_class_byID(key_id, image_ID=app.input_bb_image_id)
    
    bbs = []

    for elem in bbs_list:
        json_bb = elem["bbox"]
        x = json_bb[0]
        y = -1*(json_bb[1]-app.manager.img_height)
        w = json_bb[2]
        h = json_bb[3]

        th_bb = [[y,x],[y,x+w],[y-h,x+w],[y-h,x]]

        bbs.append(th_bb)

    all_bbs[key_id] = bbs


@when("click", "#downloadjson-but")
def get_current_state_json(event):
    tmp_folder = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVXWZ", k=5))

    while os.path.exists(tmp_folder):
        tmp_folder = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVXWZ", k=5))

    os.mkdir(tmp_folder)

    json_filemane = os.path.join(tmp_folder, app.manager.get_json_path())
    
    app.manager.save_json(json_filemane)

    download_file(json_filemane)

    shutil.rmtree(tmp_folder)


@when("click", "#downloadproj-but")
def get_current_state_projfile(event):
    tmp_folder = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVXWZ", k=5))

    while os.path.exists(tmp_folder):
        tmp_folder = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVXWZ", k=5))

    os.mkdir(tmp_folder)

    json_filemane = os.path.join(tmp_folder, app.manager.get_json_path())
    img_filename = os.path.join(tmp_folder, app.manager.img_name)
    projfile_filename = os.path.join(tmp_folder, os.path.splitext(app.manager.img_name)[0]+EXT)

    app.manager.save_json(json_filemane)
    app.manager.save_img(img_filename)

    projectfile_h.save_formattedfile(img_filename, json_filemane, output_path=tmp_folder)

    download_file(projfile_filename)

    shutil.rmtree(tmp_folder)




# #@when("click", "#upload_json")
# async def set_current_state_json(event):
#     open_load()
#     current_json_filemane = app.manager.get_json_path()

#     new_file = document.getElementById("upload_json").files
#     new_file = new_file.item(0)
    
#     json_bytes: bytes = await get_bytes_from_file(new_file)

#     upload_json(current_json_filemane, json_bytes)
#     app.manager.reload_json() #Set to BT1 all annotation without bt
#     view_original_image()
#     #click_selector_category(None)
#     close_load()

# async def get_bytes_from_file(file):
#     array_buf = await file.arrayBuffer()
#     return array_buf.to_bytes()



#@when("click", "#load_bb_image_button")
def view_full_bb_image(event, zoom=0, x=0.50, y=0):
    """
    Called when a letter is selected in the list of options (or at lunching)
    The image dispalys the full images with bb
    """
    all_bb = document.querySelector("#all_cat_in_full_img").checked

    if all_bb == False:
        filter_cat = []
        for ind, _ in enumerate(app.manager.get_categories()):
            if document.getElementById(f'{ind}_cat_in_full_img').checked:
                filter_cat.append(int(document.getElementById(f'{ind}_cat_in_full_img').value))
    else:
        filter_cat = "all"

    #print("Loading an Image!!", filter_cat)

    image = app.manager.get_img_bboxes(filter_cat=filter_cat)
    view_original_image(img=image, zoom=zoom, x=x, y=y)


def view_original_image(img=None, zoom=0, x=0.50, y=0):
    """
    The mothod visualize the original big image in the image div
    """

    # if img is None:
    #     image = m.get_img()
    # else:
    #     image = img

    # display(image, target="labelled_img", append=False)
    # document.querySelector(f"#labelled_img img").setAttribute("id", "full_image")

    # image_path = m.get_img_path()
    # document.querySelector(f"#full_image").setAttribute("src", image_path)

    image = app.manager.get_img()
    display(image, target="labelled_img", append=False)
    document.querySelector(f"#labelled_img img").setAttribute("id", "full_image")

    window.load_imgViewer(zoom,x,y)


def view_level_bb_image(event):
    """
    when you click on the chechbox of the character class on the big image, 
    the system can show on the image all the boundingboxes releated to the character
    """
    value = int(event.srcElement.value)
    checked = event.srcElement.checked
    label = app.manager.decode_category(value)

    if checked:
        _update_all_bbs(value)
        color = app.manager.get_color_category(value)
        window.add_bbs_layer(value, all_bbs[value], label, color)
    else:
        window.remove_bbs_layer(value)


@when("click", "#load_bb_image_button")
def view_bb_level(event):
    is_selected_class = document.querySelector("#test_ch").checked ##check the current bb

    if is_selected_class:
        print("add bbs")
        window.add_bbs_layer(8, all_bbs[8], "red")
    else:
        print("Remove bbs")
        window.remove_bbs_layer(8)

    
@when("click", "#img_focus_box")
def change_full_bb_view(event):
    current_bb_image_id = document.querySelector("#current_bb_image_id").value
    current_bb_image_id = int(current_bb_image_id.split("_")[-1])
     
    bb = app.manager.get_bb(current_bb_image_id)
    img_size = app.manager.get_img_size()

    img_width = img_size[0]
    img_height = img_size[1]

    bb_x = bb[0]
    bb_y = bb[1]
    bb_height = bb[3] 

    zoom = 0.25*img_height/bb_height
    x = bb_x/img_width
    y = (bb_y/img_height) + bb_height/img_height*0.5

    set_fullimg_zoom_and_position(zoom=zoom,x=x,y=y) # do not reload the widjet!


def set_fullimg_zoom_and_position(zoom=1,x=0.5,y=0):
    window.set_zoom_and_position(zoom,x,y)


def set_checkboxes_full_img():
    all_cat = app.manager.get_categories()

    for ind, cat in enumerate(all_cat):
        id_cat = cat['id']
        text_cat = cat['name']

        new_checkbox = document.createElement('label')
        new_checkbox.className = "checkbox-inline"

        new_checkbox_input = document.createElement('input')
        new_checkbox_input.type = 'checkbox'
        new_checkbox_input.value = id_cat
        new_checkbox_input.id = f'{ind}_cat_in_full_img'
        new_checkbox_input.setAttribute('py-click', 'view_level_bb_image')
        #new_checkbox_input.checked = True

        new_checkbox.appendChild(new_checkbox_input)

        new_checkbox_label = document.createElement('p')
        new_checkbox_label.innerText =  text_cat
        new_checkbox.appendChild(new_checkbox_label)


        document.getElementById('checkboxes_full_img').append(new_checkbox)


# FOCUS VIEWER -------------------------------------------------------------------------------------------
@when("click", "#focus_tab_but")
def view_current_focus(event):
    clear_content()

@when("click", "#click_full_img")
def click_on_big_img(event):
    if document.add_new:
        document.add_new = False
        document.getElementById('new-bb-func-btn').style.backgroundColor = "transparent"

    document.querySelector("#focus_tab_but").click()

    click_x = int(document.querySelector("#click_x").value)
    click_y = int(document.querySelector("#click_y").value)

    annotations = app.manager.get_list_annotations_per_point(x=click_x, y=click_y, image_ID=app.input_bb_image_id)

    view_bboxes(annotations, "focus")


# ANNOTATION VIEWER -------------------------------------------------------------------------------------------
@when("click", "#annotation_tab_but")
def click_annotation_tab(event):
    clear_content()
    display(f"", target="out_category_overl", append=False)

    click_selector_category(None)

def set_selector_category():
    all_cat = app.manager.get_categories()

    for cat in all_cat:
        id_cat = cat['id']
        text_cat = cat['name']
        new_option = pydom.create("option")
        new_option.value = id_cat
        new_option.text = text_cat
        pydom['#selector_category'][0].append(new_option)


@when("click", '#selector_category')
def click_selector_category(event):
    display(f"", target="annot_message", append=False)

    selector_category = document.querySelector("#selector_category")

    cat_id = int(selector_category.selectedOptions[0].value)
    cat_text = selector_category.selectedOptions[0].text

    all_bbs = app.manager.get_list_annotations_per_class_byID(cat_id, image_ID=app.input_bb_image_id)

    view_bboxes(all_bbs, "annot")

@when("click", ".display-focus-class-btn")
def display_focus(event):
    """
    dispalys the focus image of an annotation.
    """
    current_bb_image_id = document.querySelector("#current_bb_image_id").value
    current_list_bb_image_ids = document.querySelector("#selected_bb_image_id").value
    
    if current_list_bb_image_ids == "None":
        # clear focus box
        clear_focus_bb()

    else:
        if current_bb_image_id == "None":
            current_bb_image_id = int(current_list_bb_image_ids.split(",")[-1].split("_")[-1])
        else:
            current_bb_image_id = int(current_bb_image_id.split("_")[-1])
        
        display(f"", target="annot_message", append=False)


        # control categories box
        new_letter_div_str = f" \
            Annotations Category: \
            <select class='annot_selector_category' id='cat_selector_all'> </select>\
            BT Type: \
            <select class='annot_selector_category' id='BT_cat_selector_all'> \
            </select>\
            <div class='btns-bb'>\
                <span class='btn btn-success btn-bb btn-save-bb' py-click='save_new_category_list'>Save</span>\
                <span class='btn btn-danger btn-bb btn-delete-bb' py-click='delete_annotation_list'>Delete</span>\
            </div>"
        
        display(HTML(new_letter_div_str), target="focus_correction_box", append=False)

        # set annotatiion category
        all_cat = app.manager.get_categories()
        #selector_category = document.querySelector("#selector_category")
        #cat_id = int(selector_category.selectedOptions[0].value)
        cat_id = app.manager.get_category_byID(current_bb_image_id)

        for cat in all_cat:
            curr_id_cat = cat['id']
            curr_text_cat = cat['name']

            new_option = document.createElement("option")
            new_option.value = curr_id_cat
            new_option.text = curr_text_cat

            if curr_id_cat == cat_id:
                new_option.setAttribute('selected', True)
        
            #document.getElementById(f"#cat_selector_{bb_info['id']}").add(new_option)
            #display(HTML(new_option_str), target=f"cat_selector_{bb_info['id']}", append=True)
            pydom[f"#cat_selector_all"][0].append(new_option)

        # set BT category
        all_bts = app.manager.get_bt_categoty_list()
        current_BT = app.manager.get_bt_category(current_bb_image_id)

        if isinstance(current_BT, list):
            current_BT = current_BT[0]

        for bt_cat in all_bts:
            new_option = document.createElement("option")
            new_option.value = bt_cat
            new_option.text = bt_cat

            if bt_cat == current_BT:
                new_option.setAttribute('selected', True)

            pydom[f"#BT_cat_selector_all"][0].append(new_option)
        

        # FOCUS bb image box

        bb_img = app.manager.get_large_bb_image(current_bb_image_id)

        display(bb_img, target=f"img_focus_box", append=False)     


        # get extra info from json
        extra_info = app.manager.get_all_extra_info(current_bb_image_id)

        new_extrainfo_div_str = f"<table class='styled-table'>  <tbody>"

        for pr_name, pr_value in extra_info.items():
            if type(pr_value) is dict:
                for pr_in_name, pr_in_value in pr_value.items():
                    new_extrainfo_div_str += f"<tr> <td>{pr_name}:{pr_in_name}</td> <td>{pr_in_value}</td> </tr>"
            else:
                if pr_name == "zone_id":
                    zone_name = app.manager.get_zone_name(pr_value)
                    if zone_name is None:
                        zone_name = pr_value
                    new_extrainfo_div_str += f"<tr> <td>{pr_name}</td> <td>{zone_name}</td> </tr>"
                else:
                    new_extrainfo_div_str += f"<tr> <td>{pr_name}</td> <td>{pr_value}</td> </tr>"
         
        new_extrainfo_div_str += f"</tbody>  </table>"

        display(HTML(new_extrainfo_div_str), target="extra-info-bb", append=False)




# BB OVERLAPPING VIEW -------------------------------------------------------------------------------------------
@when("click", "#overlapp_tab_but")
def view_current_overl(event):
    # if m.overlappinglist is None:
    #     js.window.dispatchEvent(js.pyLoading_overlapping) # JS event
    #     m.init_overappling_list(image_id=input_bb_image_id)
    #     js.window.dispatchEvent(js.pyReady_overlapping) # JS event

    #clear_content()
    display(f"", target="out_category_annot", append=False)

    annotations = app.manager.overlappinglist.current()

    display(annotations[0]["id"], target="annot_message", append=False)

    view_bboxes(annotations, "overl")

@when("click", "#prev_overl_btn")
def view_prev_overl(event):
    annotations = app.manager.overlappinglist.prev()

    if annotations is not None:
        view_bboxes(annotations, "overl")

@when("click", "#next_overl_btn")
def view_next_overl(event):
    annotations = app.manager.overlappinglist.next()

    if annotations is not None:
        view_bboxes(annotations, "overl")


# utils -------------------------------------------------------------------------------------------------------
def view_bboxes(annotations, target):
    """
    Visualizes the list of boundingboxes in the target caontainer

    params:
        - annotations: list of annotations
        - target: target id container. between [focus|annot|overl|]
    """
    all_cat = app.manager.get_categories()
    #clear focus bb image
    clear_content()

    #clear out categories div
    display(f"Num of Annotations:{len(annotations)}", target=f"out_category_head_{target}", append=False)
    if target in ["overl"]:
        display(f"Overlapping Zones:{app.manager.overlappinglist.current_id+1}/{app.manager.overlappinglist.len()}", target="out_category_head_overl_2", append=False)

    for idx, bb_info in enumerate(annotations):
        bb_img = app.manager.get_bb_image(bb_info["id"])
        cat_id = bb_info["category_id"]

        new_letter_div = pydom.create("div", classes=["letter"])
        new_letter_div.id = f"letter_{bb_info['id']}"

        pydom[f'#out_category_{target}'][0].append(new_letter_div)

        new_letter_div_str = f" \
            <a id='a_img_{bb_info['id']}' class='show_hide' py-click='display_focus'> </a>\
            <div class='correction_letter'>\
                <select class='annot_selector_category' id='cat_selector_{bb_info['id']}'> </select>\
                <div class='btns-bb'>\
                    <span class='btn btn-success btn-bb btn-save-bb' py-click='save_new_category_single'>Save</span>\
                    <span class='btn btn-danger btn-bb btn-delete-bb' py-click='delete_annotation_single'>Delete</span>\
                </div>\
            </div>"

        display(HTML(new_letter_div_str), target=f"letter_{bb_info['id']}", append=False)

        display(bb_img, target=f"a_img_{bb_info['id']}", append=False)
        if target in ["focus","overl"]:
            display(f"{app.manager.decode_category(bb_info['category_id'])}", target=f"a_img_{bb_info['id']}", append=True)
        if 'score' in bb_info:
            display(f"Score:{bb_info['score']:.2f}", target=f"a_img_{bb_info['id']}", append=True)

        for cat in all_cat:
            curr_id_cat = cat['id']
            curr_text_cat = cat['name']

            new_option = document.createElement("option")
            new_option.value = curr_id_cat
            new_option.text = curr_text_cat

            if curr_id_cat == cat_id:
                new_option.setAttribute('selected', True)
        
            pydom[f"#cat_selector_{bb_info['id']}"][0].append(new_option)
    
    # apply JavaScript function to click and select
    window.function_letter_clickAndHide()

def clear_content():
    # clear annotations viewers
    display(f"", target="out_category_focus", append=False)
    display(f"", target="out_category_annot", append=False)
    display(f"", target="out_category_overl", append=False)

    clear_focus_bb()

def clear_focus_bb():
    # Clear Focus BB
    display("", target="annot_message", append=False)
    display("", target="extra-info-bb", append=False)       
    display("", target="focus_correction_box", append=False)
    display("", target="img_focus_box", append=False)
  
    document.querySelector("#current_bb_image_id").value = "None"
    document.querySelector("#selected_bb_image_id").value = "None"

@when("click", "#test_btn")
def update_bb_img(e):
    # update big image

    cat_selector = document.querySelectorAll('#checkboxes_full_img > .checkbox-inline')

    for check_elem in cat_selector:
        if check_elem.children[1].innerHTML == "All":
            continue
        else:
            if check_elem.children[0].checked:
                value = int(check_elem.children[0].value)
                color = app.manager.get_color_category(value)
                label = app.manager.decode_category(value)
                window.remove_bbs_layer(value)
                _update_all_bbs(value)
                window.add_bbs_layer(value, all_bbs[value], label, color)


def update_views():
    # update big image
    update_bb_img(None)

    # Update annotation tabs
    is_focus_active = document.querySelector("#focus_tab_but").classList.contains("active")
    is_annotation_active = document.querySelector("#annotation_tab_but").classList.contains("active")
    is_overlapp_active = document.querySelector("#overlapp_tab_but").classList.contains("active")
    
    if is_focus_active:
        click_on_big_img(None)
    elif is_annotation_active:
        click_selector_category(None)
    else:
        view_current_overl(None)

# SAVE AND MODIFY CATEGORIES ---------------------------------------------------------------------------------
@when("click", "#add-new-bb-div")
def add_new_annotation(event):
    bb = event.target.getAttribute("bb").split(",")
    category_id = int(event.target.getAttribute("category_id"))
  
    bb = [float(x) for x in bb]
    bb[1] = app.manager.img_height-bb[1]-bb[3]

    app.manager.add_new_annotation(bb, category=category_id)

    update_bb_img(None)


def delete_annotation_single(event):
    current_bb_image_id = document.querySelector("#current_bb_image_id").value

    if current_bb_image_id == "None":
        display("Error in deleting annotation!", target="annot_message", append=True)

    else:
        current_bb_image_id = int(current_bb_image_id.split("_")[-1])

        delete_annotation(current_bb_image_id)


def delete_annotation_list(event):
    selected_bb_image_id = document.querySelector("#selected_bb_image_id").value

    if selected_bb_image_id == "None":
        display("Error in deleting annotation!", target="annot_message", append=True)

    else:
        delete_ids= []
        list_selected_bb = selected_bb_image_id.split(",")
        for current_bb_image_id in list_selected_bb:
            current_bb_image_id = int(current_bb_image_id.split("_")[-1])
            delete_ids.append(current_bb_image_id)
        delete_annotation(delete_ids)


def delete_annotation(bb_id):
    deleted = app.manager.delete_annotation(bb_id)
    print("deleted")

    # reload GUI
    update_views()
    
    display(f"Annotation Deleted.", target="annot_message", append=False)


def save_new_category_single(event):
    current_bb_image_id = document.querySelector("#current_bb_image_id").value
    display(f"", target="annot_message", append=False)
    display("", target="extra-info-bb", append=False)       

    if current_bb_image_id == "None":
        display("Error in changing annotation!", target="annot_message", append=True)
    else:
        current_bb_image_id = int(current_bb_image_id.split("_")[-1])

        select_id = f'cat_selector_{current_bb_image_id}'

        selector_category = document.querySelector(f"#{select_id}")

        new_cat_id = int(selector_category.selectedOptions[0].value)

        save_new_category(current_bb_image_id,new_cat_id)
        app.manager.save_json()
        display(f"New category {app.manager.decode_category(new_cat_id)}.", target="annot_message", append=False)


def save_new_category_list(event):
    selected_bb_image_id = document.querySelector("#selected_bb_image_id").value
    display(f"", target="annot_message", append=False)

    if selected_bb_image_id == "None":
        display("Error in changing annotation!", target="annot_message", append=True)
    else:
        selector_category = document.querySelector(f"#cat_selector_all")
        selector_BT_category = document.querySelector(f"#BT_cat_selector_all")

        new_cat_id = int(selector_category.selectedOptions[0].value)
        new_BT_cat = selector_BT_category.selectedOptions[0].value

        list_selected_bb = selected_bb_image_id.split(",")

        list_ids= []
        for current_bb_image_id in list_selected_bb:
            current_bb_image_id = int(current_bb_image_id.split("_")[-1])
            list_ids.append(current_bb_image_id)
        
        app.manager.set_category_byID(list_ids, new_cat_id)
        app.manager.set_bt_category(list_ids, new_BT_cat)
        # m.save_json() ## PERCHE?
        
        # reload GUI
        update_views()    


def save_new_category(bb_id, new_cat_id):
            
    app.manager.set_category_byID(bb_id, new_cat_id)

    # reload GUI
    update_views()
    
    display(f"New category {app.manager.decode_category(new_cat_id)}.", target="annot_message", append=True)


def save_new_BT_category(bb_id, new_BT_cat):
    display(f"New BT Type {new_BT_cat}.", target="annot_message", append=True)
        
    app.manager.set_bt_category(bb_id, new_BT_cat)

    # reload GUI
    # click_selector_category(None)





# Initialization ------------
def load_project(project_dic):
    image, json_data, name, img_ext = projectfile_h.decode_formattedfile(project_dic)
    img_name = f"{name}{img_ext}"

    #document.getElementById("output_new").innerText = app
    
    app.manager = Manager(image, json_data, img_name,  font="assets/Anonymous_Pro.ttf")
    app.input_bb_image_id = app.manager.get_img_id()


def init():
    set_selector_category()
    set_checkboxes_full_img()
    view_original_image()
    click_selector_category(None)
    close_load()
    #add_event_listener(document.getElementById("upload_json"), "change", set_current_state_json)

    document.getElementById('downloadproj-but').disabled = False
    document.getElementById('downloadjson-but').disabled = False
    document.getElementById('loadproj-but').setAttribute("disabled", True)


def close_load():
    loading = document.getElementById('loading')
    #loading.close()
    loading.style.display = "none"
    print("Loaded!")


def open_load():
    # display("", target="labelled_img", append=False)
    #document.querySelector(f"#full_image").setAttribute("src", "")
    loading = document.getElementById('loading')
    #loading.open()
    loading.style.display = "flex"


if project_file_name == "new":
    # print("Nuovo progetto")
    close_load()

else:
    # print("Carica progetto")
    file_bytes = projectfile_h.load_coded_formattedfile(project_file_name)

    load_project(file_bytes)
    init()

    
    
