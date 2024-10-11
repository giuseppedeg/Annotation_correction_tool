from pyscript import window, document, when, display, config, HTML
from pyweb import pydom
from js import URL, document, window, console
from pyodide.ffi.wrappers import add_event_listener
from file_manager import download_json, upload_json
from PIL import Image
from manager import Manager
import os

"""
This file manage the interactions between the GUI and the business logic manager
"""
# FULL IMAGE VIEWER -------------------------------------------------------------------------------------------

input_bb_image_name = document.querySelector("#bb_image_name")
input_bb_json_name = document.querySelector("#bb_json_name")

input_bb_image_name = input_bb_image_name.value # it's a str
input_bb_json_name = input_bb_json_name.value # it's a str
input_bb_image_id = os.path.splitext(os.path.basename(input_bb_image_name))[0]

m = Manager(input_bb_image_name, input_bb_json_name,  font="assets/Anonymous_Pro.ttf")
m.set_all_bt_categories_default() #Set to BT1 all annotation without bt

@when("click", "#save_json")
def get_current_state_json(event):
    m.save_json()

    json_filemane = m.get_json_path()

    download_json(json_filemane)

#@when("click", "#upload_json")
async def set_current_state_json(event):
    open_load()
    current_json_filemane = m.get_json_path()

    new_file = document.getElementById("upload_json").files
    new_file = new_file.item(0)
    
    

    json_bytes: bytes = await get_bytes_from_file(new_file)

    upload_json(current_json_filemane, json_bytes)
    m.reload_json() #Set to BT1 all annotation without bt
    view_full_bb_image(None)
    #click_selector_category(None)
    close_load()

async def get_bytes_from_file(file):
    array_buf = await file.arrayBuffer()
    return array_buf.to_bytes()



@when("click", "#load_bb_image_button")
def view_full_bb_image(event, zoom=0, x=0.50, y=0):
    """
    Called when the buttoin load_bb_image_button is clicked
    The image dispalys the full images with bb
    """

    all_bb = document.querySelector("#all_cat_in_full_img").checked

    if all_bb == False:
        filter_cat = []
        for ind, _ in enumerate(m.get_categories()):
            if document.getElementById(f'{ind}_cat_in_full_img').checked:
                filter_cat.append(int(document.getElementById(f'{ind}_cat_in_full_img').value))
    else:
        filter_cat = "all"

    image = m.get_img_bboxes(filter_cat=filter_cat)
    display(image, target="labelled_img", append=False)
    document.querySelector(f"#labelled_img img").setAttribute("id", "full_image")
    #document.querySelector(f"#labelled_img img").setAttribute("id", "full_image")

    window.load_imgViewer(zoom,x,y)


@when("click", "#img_focus_box")
def change_full_bb_view(event):
    current_bb_image_id = document.querySelector("#current_bb_image_id").value
    current_bb_image_id = int(current_bb_image_id.split("_")[-1])
     
    bb = m.get_bb(current_bb_image_id)
    img_size = m.get_img_size()

    img_width = img_size[0]
    img_height = img_size[1]

    bb_x = bb[0]
    bb_y = bb[1]
    bb_height = bb[3] 

    zoom = 0.5*img_height/bb_height
    x = bb_x/img_width
    y = (bb_y/img_height) + bb_height/img_height*0.5

    view_full_bb_image(None, zoom=zoom,x=x,y=y)


def set_checkboxes_full_img():
    all_cat = m.get_categories()

    for ind, cat in enumerate(all_cat):
        id_cat = cat['id']
        text_cat = cat['name']

        new_checkbox = document.createElement('label')
        new_checkbox.className = "checkbox-inline"

        new_checkbox_input = document.createElement('input')
        new_checkbox_input.type = 'checkbox'
        new_checkbox_input.value = id_cat
        new_checkbox_input.id = f'{ind}_cat_in_full_img'
        new_checkbox_input.setAttribute('py-click', 'view_full_bb_image');
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
    document.querySelector("#focus_tab_but").click()

    click_x = int(document.querySelector("#click_x").value)
    click_y = int(document.querySelector("#click_y").value)

    annotations = m.get_list_annotations_per_point(x=click_x, y=click_y, image_ID=input_bb_image_id)

    view_bboxes(annotations, "focus")


# ANNOTATION VIEWER -------------------------------------------------------------------------------------------
@when("click", "#annotation_tab_but")
def click_annotation_tab(event):
    clear_content()
    display(f"", target="out_category_overl", append=False)

    click_selector_category(None)

def set_selector_category():
    all_cat = m.get_categories()

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

    all_bbs = m.get_list_annotations_per_class_byID(cat_id, image_ID=input_bb_image_id)

    view_bboxes(all_bbs, "annot")

@when("click", ".display-focus-class-btn")
def dispay_focus(event):
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

        # set annotatiion catefory
        all_cat = m.get_categories()
        #selector_category = document.querySelector("#selector_category")
        #cat_id = int(selector_category.selectedOptions[0].value)
        cat_id = m.get_category_byID(current_bb_image_id)

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
        all_bts = m.get_bt_categoty_list()
        current_BT = m.get_bt_category(current_bb_image_id)[0]
        for bt_cat in all_bts:
            new_option = document.createElement("option")
            new_option.value = bt_cat
            new_option.text = bt_cat

            if bt_cat == current_BT:
                new_option.setAttribute('selected', True)

            pydom[f"#BT_cat_selector_all"][0].append(new_option)
        

        # FOCUS bb image box

        bb_img = m.get_large_bb_image(current_bb_image_id)

        display(bb_img, target=f"img_focus_box", append=False)       


# BB OVERLAPPING VIEW -------------------------------------------------------------------------------------------
@when("click", "#overlapp_tab_but")
def view_current_overl(event):
    #clear_content()
    display(f"", target="out_category_annot", append=False)

    annotations = m.overlappinglist.current()

    display(annotations[0]["id"], target="annot_message", append=False)

    view_bboxes(annotations, "overl")

@when("click", "#prev_overl_btn")
def view_prev_overl(event):
    annotations = m.overlappinglist.prev()

    if annotations is not None:
        view_bboxes(annotations, "overl")

@when("click", "#next_overl_btn")
def view_next_overl(event):
    annotations = m.overlappinglist.next()

    if annotations is not None:
        view_bboxes(annotations, "overl")


# utils -------------------------------------------------------------------------------------------------------
def view_bboxes(annotations, target):
    """
    Visualizes the list of boundingbozes in the target caontainer

    params:
        - annotations: list of annotations
        - target: target id container. between [focus|annot|overl|]
    """
    all_cat = m.get_categories()
    #clear focus bb image
    clear_content()

    #clear out categories div
    display(f"Num of Annotations:{len(annotations)}", target=f"out_category_head_{target}", append=False)
    if target in ["overl"]:
        display(f"Overlapping Zones:{m.overlappinglist.current_id+1}/{m.overlappinglist.len()}", target="out_category_head_overl_2", append=False)

    for idx, bb_info in enumerate(annotations):
        bb_img = m.get_bb_image(bb_info["id"])
        cat_id = bb_info["category_id"]

        new_letter_div = pydom.create("div", classes=["letter"])
        new_letter_div.id = f"letter_{bb_info['id']}"

        pydom[f'#out_category_{target}'][0].append(new_letter_div)

        new_letter_div_str = f" \
            <a id='a_img_{bb_info['id']}' class='show_hide' py-click='dispay_focus'> </a>\
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
            display(f"{m.decode_category(bb_info['category_id'])}", target=f"a_img_{bb_info['id']}", append=True)
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
    display("", target="current_selected", append=False)       
    display("", target="focus_correction_box", append=False)
    display("", target="img_focus_box", append=False)
  
    document.querySelector("#current_bb_image_id").value = "None"
    document.querySelector("#selected_bb_image_id").value = "None"

def update_views():
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
def delete_annotation_single(event):
    current_bb_image_id = document.querySelector("#current_bb_image_id").value

    if current_bb_image_id == "None":
        display("Error in deleting annotation!", target="annot_message", append=True)

    else:
        current_bb_image_id = int(current_bb_image_id.split("_")[-1])

        delete_annotation(current_bb_image_id)
        #m._init_overappling_list(image_id=input_bb_image_id)

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
    deleted = m.delete_annotation(bb_id)

    # reload GUI
    update_views()
    
    display(f"Annotation Deleted.", target="annot_message", append=False)

def save_new_category_single(event):
    current_bb_image_id = document.querySelector("#current_bb_image_id").value
    display(f"", target="annot_message", append=False)
    display(f"", target="current_selected", append=False)

    if current_bb_image_id == "None":
        display("Error in changing annotation!", target="annot_message", append=True)
    else:
        current_bb_image_id = int(current_bb_image_id.split("_")[-1])

        select_id = f'cat_selector_{current_bb_image_id}'

        selector_category = document.querySelector(f"#{select_id}")

        new_cat_id = int(selector_category.selectedOptions[0].value)

        save_new_category(current_bb_image_id,new_cat_id)
        m.save_json()
        display(f"New category {m.decode_category(new_cat_id)}.", target="annot_message", append=False)

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
        for current_bb_image_id in list_selected_bb:
            current_bb_image_id = int(current_bb_image_id.split("_")[-1])

            current_cat_id = m.get_category_byID(current_bb_image_id)
            current_BT_cat = m.get_bt_category(current_bb_image_id)[0]

            if new_cat_id != current_cat_id:
                save_new_category(current_bb_image_id,new_cat_id)
                m.save_json()
            if new_BT_cat != current_BT_cat:
                save_new_BT_category(current_bb_image_id,new_BT_cat)
                m.save_json()
          
def save_new_category(bb_id, new_cat_id):
            
    m.set_category_byID(bb_id, new_cat_id)

    # reload GUI
    update_views()
    
    display(f"New category {m.decode_category(new_cat_id)}.", target="annot_message", append=True)

def save_new_BT_category(bb_id, new_BT_cat):
    display(f"New BT Type {new_BT_cat}.", target="annot_message", append=True)
        
    m.set_bt_category(bb_id, new_BT_cat)

    # reload GUI
    # click_selector_category(None)





# Initialization ------------
def init():
    
    set_selector_category()
    set_checkboxes_full_img()
    view_full_bb_image(None)
    click_selector_category(None)
    close_load()
    add_event_listener(document.getElementById("upload_json"), "change", set_current_state_json)

def close_load():
    loading = document.getElementById('loading')
    #loading.close()
    loading.style.display = "none"
    print("Loaded!")

def open_load():
    display("", target="labelled_img", append=False)
    loading = document.getElementById('loading')
    #loading.open()
    loading.style.display = "flex"
    
init()
