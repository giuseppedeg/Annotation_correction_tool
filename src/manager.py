import json
from PIL import Image, ImageDraw, ImageFont
import distinctipy
import os
import io

FONT="./assets/Anonymous_Pro.ttf"
FONT_SIZE = 30
WIDTH_BB = 3

DEFAULT_BT = "bt1"

ID_UNKNOWN = -1
STR_UNKNOWN_CAT = "Unknown"


OVERLAPPING_TH = 0.75

class Overlappinglist:
    
    class Node:
        def __init__(self, data) -> None:
            self.data = data
            self.next = None
            self.prev = None

    def __init__(self):
        self.head = None
        self.current_node = None
        self.lenght = 0
        self.current_id = None

    def len(self):
        return self.lenght

    def insertHead(self, data):
        new_node = self.Node(data)
        if self.head is None:
            self.head = new_node
            self.current_node = new_node
            self.current_id = 0
        else:
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
        self.lenght += 1
    
    def append(self, data):
        new_node = self.Node(data)
        if self.head is None:
            self.head = new_node
            self.current_node = new_node
            self.current_id = 0
        else:
            current_node = self.head
            while(current_node.next):
                current_node = current_node.next

            current_node.next = new_node
            new_node.prev = current_node
        self.lenght += 1

    def remove_node(self, data):
        if data is None:
            return
        removed_node = None

        current_node = self.head

        while current_node != None:
            if current_node.data == data:
                current_node.prev = current_node.next
                current_node.next = current_node.prev
                removed_node = current_node
                self.lenght -= 1
                break
            current_node = current_node.next

        return removed_node
    
    def set_current(self, id):
        self.current_node = self.head

        to_range = min(id, self.lenght)

        for ind in range(to_range):
            self.current_node = self.current_node.next
            self.current_id = ind

    def next(self):
        if self.current_node.next == None:
            return None
        else:
           self.current_node =  self.current_node.next
           self.current_id += 1
           return self.current_node.data
    
    def prev(self):
        if self.current_node.prev == None:
            return None
        else:
           self.current_node =  self.current_node.prev
           self.current_id -= 1
           return self.current_node.data
    
    def current(self):
        return self.current_node.data


    

class Manager:
    def __init__(self, img, coco_json, font=FONT, font_size=FONT_SIZE, width_bb=WIDTH_BB):
        self.img_path = img
        self.img_name = os.path.basename(img)
        self.img = Image.open(img)
        self.font = ImageFont.truetype(font=font, size=font_size)
        self.width_bb = width_bb
        self.cocojsaon_name = coco_json

        self.category_encoding = {}
        self.category_decoding = {}
        
        self._load_json()
        self._init_overappling_list(image_id=os.path.splitext(self.img_name)[0])
        
        
    def _load_json(self):
        self.BT_category_list = ["bt1", "bt2", "bt3"]

        with open(self.cocojsaon_name, encoding="utf-8") as f:
            self.jcoco = json.load(f)

        is_unknown_cat_present = False
        for cat in self.jcoco["categories"]:
            self.category_decoding[cat['id']] = cat['name']
            self.category_encoding[cat['name']] = cat['id']

            if cat['id'] == -1:
                is_unknown_cat_present = True
        
        if not is_unknown_cat_present:
            self.jcoco["categories"].append({"id":ID_UNKNOWN, "name":STR_UNKNOWN_CAT})
            self.category_encoding[STR_UNKNOWN_CAT] = ID_UNKNOWN
            self.category_decoding[ID_UNKNOWN] = STR_UNKNOWN_CAT

        self.next_annotationID = self._get_next_annotationID()
        for cat in self.jcoco["annotations"]:
            if not 'id' in cat:
                cat['id'] = self.next_annotationID
                self.next_annotationID += 1        

    def _init_overappling_list(self, image_id=None):
        if hasattr(self, "overlappinglist"):
            current_id = self.overlappinglist.current_id
        else:
            current_id = 0

        self.overlappinglist = Overlappinglist()

        for ind_current, current_ann in enumerate(self.jcoco["annotations"]):
            if image_id is not None:
                if current_ann["image_id"] != image_id:
                    continue

            overlapping_list = []
            current_ann['bbox']
            for next_ann in self.jcoco["annotations"][ind_current+1:]:
                if image_id is not None:
                    if next_ann["image_id"] != image_id:
                        continue
                if self._are_bbs_overlapping(current_ann['bbox'], next_ann['bbox'], th=OVERLAPPING_TH):
                    overlapping_list.append(next_ann)

            if len(overlapping_list) > 0:
                overlapping_list.append(current_ann)
                self.overlappinglist.append(overlapping_list)

        self.overlappinglist.set_current(current_id)
            

    def _are_bbs_overlapping(self, bb1, bb2, th=0.1):
        # overlapping =  not (bb1[0]+bb1[2] < bb2[0]
        #             or bb1[0] > bb2[0]+bb2[2]
        #             or bb1[1] > bb2[1]+bb2[3]
        #             or bb1[1]+bb1[3] < bb2[1])
        
        area_bb = min((bb1[2] * bb1[3]), (bb2[2] * bb2[3]))
        overlapping_w = min(bb1[0]+bb1[2],bb2[0]+bb2[2])-max(bb1[0],bb2[0])
        overlapping_h = min(bb1[1]+bb1[3],bb2[1]+bb2[3])-max(bb1[1],bb2[1])

        if overlapping_w >=0 and overlapping_w >=0:
            area_overl = overlapping_w * overlapping_h

            if area_overl >= th*area_bb:
                return True
        return False
        

    def _get_next_annotationID(self):
        next_annotationID = 0
        for cat in self.jcoco["annotations"]:
            if 'id' in cat:
                if cat['id'] > next_annotationID:
                     next_annotationID = int(cat['id']) + 1
        return next_annotationID

    def get_json_path(self):
        return self.cocojsaon_name

    def reload_json(self):
        self._load_json()
        self._init_overappling_list(image_id=os.path.splitext(self.img_name)[0])

    def get_img_size(self):
        """
        return the sahpe of the entire image
        """

        return self.img.size
    

    def get_img_bboxes(self, filter_cat="all"):
        """The method returns the image with all the bounding boxes

        params:
            - filter: list
              list of categories ID to display. If empty, the methods dysplays all the categories bbs
        """

        if filter_cat == "all":
            filter_cat = list(self.category_decoding.keys())
        color_categories = {}
        n_categories = len(filter_cat)
        colors = distinctipy.get_colors(n_categories)

        for idx, cat_id in enumerate(filter_cat):
            col = colors[idx]
            color_categories[cat_id] = (int(255*col[0]), int(255*col[1]), int(255*col[2]))

        for image in self.jcoco["images"]:
            if self.img_name == image['file_name']:
                id_image = image['id']
                break
        
        img_bb = self.img.copy()         
        img_dr = ImageDraw.Draw(img_bb)   

        for annot in self.jcoco["annotations"]:
            if annot['image_id'] == id_image and annot['category_id'] in filter_cat:
                shape = [annot['bbox'][0], annot['bbox'][1], annot['bbox'][0]+annot['bbox'][2], annot['bbox'][1]+annot['bbox'][3]]
                color = color_categories[annot['category_id']]

                img_dr.rectangle(shape, outline=color, width=self.width_bb) 
                img_dr.text((annot['bbox'][0], annot['bbox'][1]), str(self.category_decoding[annot['category_id']]), font=self.font)

        return img_bb


    def get_list_bbox_per_class(self, category, image_ID=None, min_score=0, max_score=1):
        """The method return a list of all bounding-Boxes of a given category

        Parameters
        ----------
        category: str
            the string of the class to get all the bounding-boxes
        min_score: int [0,1]
            minimum annotation score to add it to the return list
        max_score: int [0,1]
            maximum annotation score to add it to the return list
        """

        assert category in self.category_encoding, f"{category} not a valid category!"

        category_id = self.category_encoding[category]

        return self.get_list_annotations_per_class_byID(category_id, image_ID, min_score, max_score)

    
    def get_list_annotations_per_class_byID(self, ID_category:int, image_ID=None, min_score=0, max_score=1):
        """The method return a list of all bounding-Boxes of a given category

        Parameters
        ----------
        ID_category: int
            the identifier of the class to get all the bounding-boxes
        min_score: int [0,1]
            minimum annotation score to add it to the return list
        max_score: int [0,1]
            maximum annotation score to add it to the return list
        """

        assert ID_category in self.category_decoding, f"{ID_category} not a valid ID category!"

        all_annotations = []
        for ann in self.jcoco["annotations"]:
            if not(image_ID is not None and ann['image_id'] != image_ID):
                if ann['category_id'] == ID_category:
                    if min_score <= ann['score']<= max_score:
                        all_annotations.append(ann)

        return all_annotations
    

    def get_list_annotations_per_point(self, x:int, y:int, image_ID=None, min_score=0, max_score=1):
        """The method return a list of all annotations that overlapp the given coordinates

        Parameters
        ----------
        x: int
            x coordinates to looking for annotations
        y: int
            y coordinates to looking for annotations
        min_score: int [0,1]
            minimum annotation score to add it to the return list
        max_score: int [0,1]
            maximum annotation score to add it to the return list
        """

        all_annotations = []
        for ann in self.jcoco["annotations"]:
            if not(image_ID is not None and ann['image_id'] != image_ID):
                if (int(ann['bbox'][0]) <= x <= int(ann['bbox'][0])+int(ann['bbox'][2])) and \
                    (int(ann['bbox'][1]) <= y <= int(ann['bbox'][1])+int(ann['bbox'][3])):
                    if min_score <= ann['score']<= max_score:
                        all_annotations.append(ann)

        return all_annotations


    def get_categories(self):
        """ returns a list of all categories
        """
        return self.jcoco["categories"]
    

    def decode_category(self, category_code):
        return self.category_decoding[category_code]


    def set_category_byID(self, id_annotation, new_ID_category:int):
        """Modifies the category if a give annotation

        Parameters
        ----------
        id_annotation: int
            ID of the annotation to modify
        new_ID_category: int
            ID of new category
        """
        assert new_ID_category in self.category_decoding, f"{new_ID_category} not a valid category!"

        for ann in self.jcoco["annotations"]:
            if ann['id'] == id_annotation:
                ann['category_id'] = new_ID_category
                break


    def get_category_byID(self, id_annotation):
        """returns the category id for a given annotation

        Parameters
        ----------
        id_annotation: int
            ID of the annotation to looking for the category
        
        retrun : int
            ID of category
        """
        for ann in self.jcoco["annotations"]:
            if ann['id'] == id_annotation:
                 return ann['category_id']


    def set_category(self, id_annotation, new_category):
        """Modifies the category if a give annotation

        Parameters
        ----------
        id_annotation: int
            ID of the annotation to modify
        new_category: str
            new category
        """
        assert new_category in self.category_encoding, f"{new_category} not a valid category!"

        self.category_encoding[new_category]

        for ann in self.jcoco["annotations"]:
            if ann['id'] == id_annotation:
                ann['category_id'] = self.category_encoding[new_category]
                break

    
    def delete_annotation(self, id_annotation):
        """Deletes the annotation with id_annotation from all annotations

        Parameters
        ----------
        id_annotation: int or list of int
            ID of the annotation to delete
        """

        if type(id_annotation) == int:
            id_annotation = [id_annotation]
        
        deleted_element = []
        for idx, ann in enumerate(self.jcoco["annotations"]):
            if ann['id'] in id_annotation:
                current_deleted_element = self.jcoco["annotations"].pop(idx)
                deleted_element.append(current_deleted_element)
                id_annotation.remove(ann['id'])
                if len(id_annotation) == 0:
                    break

        self._init_overappling_list(image_id=os.path.splitext(self.img_name)[0])

        return deleted_element
        

    def get_bb(self,id_annotation):
        """returns the bounding-box values

        Parameters
        ----------
        id_annotation: int
            ID of the annotation to get the BB
        """
        bb = None

        for ann in self.jcoco["annotations"]:
            if ann['id'] == id_annotation:
                bb = ann['bbox']
                left = ann['bbox'][0]
                top = ann['bbox'][1]
                right = ann['bbox'][0] + ann['bbox'][2]
                bottom = ann['bbox'][3] + ann['bbox'][1]
                
        return bb


    def get_bb_image(self,id_annotation):
        """returns the cropped image in the bounding-box

        Parameters
        ----------
        id_annotation: int
            ID of the annotation to get the image
        """
        im1 = None

        for ann in self.jcoco["annotations"]:
            if ann['id'] == id_annotation:
                left = ann['bbox'][0]
                top = ann['bbox'][1]
                right = ann['bbox'][0] + ann['bbox'][2]
                bottom = ann['bbox'][3] + ann['bbox'][1]
                im1 = self.img.crop((left, top, right, bottom))
                
        return im1


    def get_large_bb_image(self,id_annotation, margin=50, color=(0,255,0)):
        """returns the large image containing the bounding-box

        Parameters
        ----------
        id_annotation: int
            ID of the annotation to get the image
        """
        im1 = None

        for ann in self.jcoco["annotations"]:
            if ann['id'] == id_annotation:
                left = ann['bbox'][0] - 2*margin
                top = ann['bbox'][1]  - margin
                right = ann['bbox'][0] + ann['bbox'][2] + 2*margin
                bottom = ann['bbox'][3] + ann['bbox'][1] + margin
                im1 = self.img.crop((left, top, right, bottom))
                
                img_dr = ImageDraw.Draw(im1) 

                shape = [2*margin, margin, 2*margin+ann['bbox'][2], margin+ann['bbox'][3]]

                img_dr.rectangle(shape, outline=color, width=1) 
                
        return im1

    
    def set_bt_category(self, id_annotation, bt_cat):
        """Modifies the BT category for a give annotation

        Parameters
        ----------
        id_annotation: int
            ID of the annotation to modify
        bt_cat: str
            new BT category. choose between "BT1", "BT2", "BT3"
        """
        assert bt_cat in self.BT_category_list, f"{bt_cat} not a valid category!"

        for ann in self.jcoco["annotations"]:
            if ann['id'] == id_annotation:
                if not 'tags' in ann:
                    ann['tags'] = {}
                ann['tags']['BaseType'] = [bt_cat]

                break
    

    def get_bt_category(self, id_annotation):
        """Get the BT category for a give annotation

        Parameters
        ----------
        id_annotation: int
            ID of the annotation to get the category VB
        
        Return: list of str
            only one element between "BT1", "BT2", "BT3" or None
        """
        return_cat = None
        for ann in self.jcoco["annotations"]:
            if ann['id'] == id_annotation:
                if 'tags' in ann:
                    if 'BaseType' in ann['tags']:
                       return_cat = ann['tags']['BaseType']
            
        return return_cat


    def set_all_bt_categories_default(self):
        """
        Set the bt category to the DEFAULT value to all annotations do noty have one.
        """
        for ann in self.jcoco["annotations"]:
            if not 'tags' in ann:
                ann['tags'] = {}
            if not 'BaseType' in ann['tags']:
                self.set_bt_category(id_annotation=ann['id'], bt_cat=DEFAULT_BT)


    def get_bt_categoty_list(self):
        return self.BT_category_list


    def save_json(self, out_path=None):
        """Save all on a coco_json file

        Parameters
        ----------
        out_path: str
            file path for the .json out file
        """
        if out_path is None:
            out_path = self.cocojsaon_name

        with open(out_path, 'w', encoding="utf-8") as outfile:
            json.dump(self.jcoco, outfile, indent=4)

    
    def get_current_state_json_stream(self):

        json_filemane = f".tmp.json"

        with open(json_filemane, 'w', encoding="utf-8") as outfile:
            json.dump(self.jcoco, outfile, indent=4)

        with open(json_filemane, 'r', encoding="utf-8") as outfile:
            jcoco_string = outfile.read()

        
        json_stream = io.BytesIO(jcoco_string.encode("utf-8"))
        bytes_len = len(jcoco_string)      


        return bytes_len, json_stream





if __name__ == "__main__":
    print("Test class for manager of Viewer&Corrector")

    img_test = "data/docs/00001/TM065797_The_Curse_of_Artemisia_Fragment_WDL4310.jpg"
    jcoco_test = "data/docs/00001/predictions_9.json"


    m = Manager(img_test, jcoco_test)

    current_list = m.overlappinglist.current()

    current_list = m.overlappinglist.next()

    m.overlappinglist.remove_node(current_list)

    m._init_overappling_list()
    
    categories = m.get_categories()

    # get annnotation given a category
    all_alphas = m.get_list_bbox_per_class("Α", min_score=0.97, max_score=1)
    all_beta = m.get_list_bbox_per_class("Β")
    print(f"Len A:{len(all_alphas)}  len B:{len(all_beta)}")

    # get overlapping annotations
    all_annot = m.get_list_annotations_per_point(x=951, y=471, image_ID="TM065797_The_Curse_of_Artemisia_Fragment_WDL4310")

    print(all_annot)

    # modify a vategory
    m.set_category(id_annotation=2, new_category="Β")

    all_alphas = m.get_list_annotations_per_class_byID(8, image_ID="TM065797_The_Curse_of_Artemisia_Fragment_WDL4310")
    all_beta = m.get_list_bbox_per_class("Β")
    print(f"Len A:{len(all_alphas)}  len B:{len(all_beta)}")

    # delete an annotation
    deleted_ann = m.delete_annotation(7) # 7 is an alpha

    all_alphas = m.get_list_bbox_per_class("Α")
    all_beta = m.get_list_bbox_per_class("Β")
    print(f"Len A:{len(all_alphas)}  len B:{len(all_beta)}")

    # set BNT category
    m.set_all_bt_categories_default()
    annotation_id_test = 8
    print(f"category BT for annotation {annotation_id_test}: {m.get_bt_category(annotation_id_test)}")
    m.set_bt_category(id_annotation=8, bt_cat="bt1")
    print(f"category BT for annotation {annotation_id_test}: {m.get_bt_category(annotation_id_test)}")
    m.set_bt_category(id_annotation=8, bt_cat="bt2")
    print(f"category BT for annotation {annotation_id_test}: {m.get_bt_category(annotation_id_test)}")
    m.set_all_bt_categories_default()
    print(f"category BT for annotation {annotation_id_test}: {m.get_bt_category(annotation_id_test)}")



    # simge bb image
    bb_img = m.get_bb_image(2)
    bb_img.show() 
    
    bb_img = m.get_large_bb_image(2)
    bb_img.show() 
    
    # bboxes image
    img_bb = m.get_img_bboxes(filter_cat=[8, 9])
    img_bb = m.get_img_bboxes()
    img_bb.show() 

    m.save_json()

    m.save_json("save_json_test.json")
