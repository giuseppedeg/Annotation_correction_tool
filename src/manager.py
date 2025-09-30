import json
from PIL import Image, ImageDraw, ImageFont
import distinctipy
import os
import io
import const

FONT="./assets/Anonymous_Pro.ttf"
FONT_SIZE = 30
WIDTH_BB = 3

DEFAULT_BT = "bt1"

ID_UNKNOWN = 0
STR_UNKNOWN_CAT = "Unknown"


OVERLAPPING_TH = 0.75 # % of overlapping area to ywo bbs to be considered overlapped
SCORE_TH = 0

class Overlappinglist:
    
    class Node:
        def __init__(self, data) -> None:
            self.data = data
            self.next = None
            self.prev = None

    def __init__(self, id_elements_innode=True):
        self.head = None
        self.current_node = None
        self.lenght = 0
        self.current_id = None

        self.id_elements_innode = id_elements_innode
        if id_elements_innode:
            self.ids_innode = {}

    def len(self):
        return self.lenght
    
    def __len__(self):
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

        if self.id_elements_innode:
            self._insert_idelement_innode(new_node)
    
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

        if self.id_elements_innode:
            self._insert_idelement_innode(new_node)

    def _insert_idelement_innode(self, node):
        for element in node.data:
            if element["id"] in self.ids_innode:
                old_node = self.ids_innode[element["id"]]

                if len(node.data) > len(old_node.data):
                    self.ids_innode[element["id"]] = node
            else:
                self.ids_innode[element["id"]] = node
            

    def remove_node(self, data):
        if data is None:
            return
        removed_node = None

        current_node = self.head

        while current_node != None:
            if current_node.data == data:
                prev_node = current_node.prev
                next_node = current_node.next
                current_node.prev = next_node
                current_node.next = prev_node
                removed_node = current_node
                self.lenght -= 1
                #self.current_id -= 1
                if next_node is not None:
                    self.current_node = next_node
                else:
                    self.current_node = prev_node
                    self.current_id -= 1
                break
            current_node = current_node.next
        
        return removed_node
    
    
    def remove_element_in_node(self, id_element):
        if id_element in self.ids_innode:
            node = self.ids_innode[id_element]
            for ind, element in enumerate(node.data):
                if id_element == element["id"]:
                    node.data.pop(ind)
                    del self.ids_innode[id_element]
            if len(node.data) <= 1:
                for element in node.data:
                    del self.ids_innode[element["id"]]
                # No more overlapping BBs, delete the Node!
                if node.prev != None:
                    node.prev.next = node.next
                if node.next != None:
                    node.next.prev = node.prev
                self.lenght -= 1
                #self.current_id -= 1
                if node.next is not None:
                    self.current_node = node.next
                else:
                    self.current_node = node.prev
            

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


class Overlappinglist2:
    def __init__(self) -> None:
        pass

    

class Manager:
    def __init__(self, img, coco_json, img_name, font=FONT, font_size=FONT_SIZE, width_bb=WIDTH_BB, score_th=SCORE_TH):
        
        # self.img_path = img
        # self.img_name = os.path.basename(img)
        # self.img = Image.open(img)
        
        self.img_name = img_name
        self.img = img
        if self.img.mode != "RGB":
            self.img = self.img.convert("RGB")

        self.img_width, self.img_height = self.img.size
        self.font = ImageFont.truetype(font=font, size=font_size)
        self.width_bb = width_bb

        self.category_encoding = {}
        self.category_decoding = {}
        
        self.color_encoding = {}
        
        self.cocojsaon_name = os.path.splitext(img_name)[0]+".json"
        self.jcoco = coco_json
        self._load_json()

        self.img_id = None
        for image in self.jcoco["images"]:
            if self.img_name == image['file_name']:
                self.img_id = image['id']
                break

        self.overlappinglist = None
        # if 0 < score_th < 1:
        for annotation in self.jcoco["annotations"]:
            # add standard BT
            if "tags" not in  annotation:
                annotation['tags'] = {'BaseType': [DEFAULT_BT]}
            elif 'BaseType' not in annotation['tags']:
                annotation['tags'] = {'BaseType': [DEFAULT_BT]}

            # Filter by SCORE
            if 'score' in annotation:
                if annotation['score'] < score_th:
                    self.delete_annotation(annotation['id'])
        
        self.last_annotation_id = 0
        self.init_overappling_list()
        

    def _load_json(self):
        self.BT_category_list = const.BT_TYPE_LIST

        # with open(self.cocojsaon_name, encoding="utf-8") as f:
        #     self.jcoco = json.load(f)

        is_unknown_cat_present = False
        for ind, cat in enumerate(self.jcoco["categories"]):
            if cat['id'] == -1:
                cat['id'] = ID_UNKNOWN
                is_unknown_cat_present = True

            if cat['id'] == ID_UNKNOWN:
                is_unknown_cat_present = True
                
            self.category_decoding[cat['id']] = cat['name']
            self.category_encoding[cat['name']] = cat['id']
            color_ind =  ind % len(const.colors)
            self.color_encoding[cat['id']] = const.colors[color_ind]

        self.color_encoding[-1] = const.colors[-1]
        
        if not is_unknown_cat_present:
            self.jcoco["categories"].append({"id":ID_UNKNOWN, "name":STR_UNKNOWN_CAT})
            self.category_encoding[STR_UNKNOWN_CAT] = ID_UNKNOWN
            self.category_decoding[ID_UNKNOWN] = STR_UNKNOWN_CAT

        self.next_annotationID = self._get_next_annotationID()
        for cat in self.jcoco["annotations"]:
            if not 'id' in cat:
                cat['id'] = self.next_annotationID
                self.next_annotationID += 1        


    def init_overappling_list(self, image_id=None):
        if self.overlappinglist is not None:
            current_id = self.overlappinglist.current_id
        else:
            current_id = 0

        self.overlappinglist = Overlappinglist()

        sorted_annotation_by_id = sorted(self.jcoco["annotations"], key=lambda x:x['id'])

        if sorted_annotation_by_id:

            if int(sorted_annotation_by_id[-1]['id']) > self.last_annotation_id:
                    self.last_annotation_id = sorted_annotation_by_id[-1]['id']

            for ind_current, current_ann in enumerate(sorted_annotation_by_id):
                if image_id is not None:
                    if current_ann["image_id"] != image_id:
                        continue
                
                

                overlapping_list = []
                for next_ann in sorted_annotation_by_id[ind_current+1:]:
                #for next_ann in self.jcoco["annotations"]:
                    if current_ann['id'] != next_ann['id']:
                        if image_id is not None:
                            if next_ann["image_id"] != image_id:
                                continue
                        if self._are_bbs_overlapping(current_ann['bbox'], next_ann['bbox'], th=OVERLAPPING_TH):
                            if ('score' in current_ann and 'score' in next_ann) and (current_ann['category_id'] == next_ann['category_id']):
                                # Keep the one with big score
                                if next_ann['score'] > current_ann['score']:
                                    to_delete = current_ann
                                    current_ann = next_ann
                                else:
                                    to_delete = next_ann
                                self.delete_annotation(to_delete['id'])
                            else:
                                overlapping_list.append(next_ann)
                            sorted_annotation_by_id.remove(next_ann)

                if len(overlapping_list) > 0:
                    overlapping_list.append(current_ann)
                    self.overlappinglist.append(overlapping_list)

        self.overlappinglist.set_current(current_id)


    def _remove_from_overlapping(self, image_id):
        pass

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
        self.init_overappling_list(self.img_id)
        #self.overlappinglist = None

    def get_img(self):
        return self.img
    
    # def get_img_path(self):
    #     return self.img_path

    def get_img_id(self):
        return self.img_id

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

        #assert ID_category in self.category_decoding, f"{ID_category} not a valid ID category!"

        all_annotations = []
        for ann in self.jcoco["annotations"]:
            if not(image_ID is not None and ann['image_id'] != image_ID):
                if ann['category_id'] == ID_category:
                    if 'score' in ann:
                        if min_score <= ann['score']<= max_score:
                            all_annotations.append(ann)
                    else:
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
                    if 'score' in ann:
                        if min_score <= ann['score']<= max_score:
                            all_annotations.append(ann)
                    else:
                        all_annotations.append(ann)

        return all_annotations


    def get_categories(self):
        """ returns a list of all categories
        """
        categories = []
        def_cat = None
        for cat in self.jcoco["categories"]:
            if cat['id'] != ID_UNKNOWN:
                categories.append(cat)
            else:
                def_cat = cat
        if def_cat:
            categories.append(def_cat)

        return categories
    

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

        if type(id_annotation) == int:
            all_ids = [id_annotation]
        else:
            all_ids = id_annotation.copy()

        #assert new_ID_category in self.category_decoding, f"{new_ID_category} not a valid category!"

        for ann in self.jcoco["annotations"]:
            if ann['id'] in all_ids:
                ann['category_id'] = new_ID_category
                all_ids.remove(ann['id'])
                if len(all_ids) == 0:
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

    
    def add_new_annotation(self, bb, category=-1):
        """Add a new annotation to the json

        Parameters
        ----------
              bb: bounding box of the new annotation in format [x,y,w,h]
        category: category ID of the new annotation. (default -1 is 'UNKNOWN' annotation)
        """

        self.last_annotation_id += 1

        self.jcoco["annotations"].append(
        {
            'image_id': self.img_id, 
            'category_id': category, 
            'bbox': bb, 
            'score': 1, 
            'id': self.last_annotation_id, 
            'tags': {'BaseType': [DEFAULT_BT]}
        })


    def delete_annotation(self, id_annotation):
        """Deletes the annotation with id_annotation from all annotations

        Parameters
        ----------
        id_annotation: int or list of int
            ID of the annotation to delete
        """

        if type(id_annotation) == int:
            all_ids = [id_annotation]
        else:
            all_ids = id_annotation.copy()
        
        deleted_element = []
        for idx, ann in enumerate(self.jcoco["annotations"]):
            if ann['id'] in all_ids:
                current_deleted_element = self.jcoco["annotations"].pop(idx)
                if self.overlappinglist is not None:
                    self.overlappinglist.remove_element_in_node(ann['id'])

                deleted_element.append(current_deleted_element)
                all_ids.remove(ann['id'])
                if len(all_ids) == 0:
                    break

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
        #assert bt_cat in self.BT_category_list, f"{bt_cat} not a valid category!"
        if type(id_annotation) == int:
            all_ids = [id_annotation]
        else:
            all_ids = id_annotation.copy()
        
        for ann in self.jcoco["annotations"]:
            if ann['id'] in all_ids:
                if not 'tags' in ann:
                    ann['tags'] = {}
                ann['tags']['BaseType'] = [bt_cat]

                all_ids.remove(ann['id'])
                if len(all_ids) == 0:
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

    def get_all_extra_info(self, id_annotation):
        """
        The method gets all the extra info for an annotation defined in the JSONs
        """
        common_info = ["bbox", "category_id", "image_id"] # these info is not considered as extra info
        common_info = [] # these info is not considered as extra info
        
        return_dic = {}
        for ann in self.jcoco["annotations"]:
            if ann['id'] == id_annotation:
                for pr_name, pr_value in ann.items():
                    if pr_name == "id":
                        pr_name = "annotation_id"
                    if pr_name not in common_info:
                        return_dic[pr_name] = pr_value
                return return_dic
        return None
    
    def get_zone_name(self, zone_id):
        """
        if in the json the 'zones' are defined, it returns the zone name given the zone id.
        if no zone is fonded with the given id, the methods returns None
        """
        if "zones" in self.jcoco:
            for zone in self.jcoco["zones"]:
                if zone["id"] == zone_id:
                    return zone["name"]
        
        return None
        

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


    def delete_json(self, json_path=None):
        """Delete the coco_json file

        Parameters
        ----------
        out_path: str
            file path for the .json file to delete
        """
        if json_path is None:
            json_path = self.cocojsaon_name

        os.remove(json_path)

    
    def save_img(self, out_path=None):
        """Save the image file

        Parameters
        ----------
        out_path: str
            file path for the img out file
        """
        if out_path is None:
            out_path = self.img_name

        self.img.save(out_path)
    

    def delete_img(self, img_path=None):
        """Delete the img  file

        Parameters
        ----------
        out_path: str
            file path for the image file to delete
        """
        if img_path is None:
            img_path = self.img_name

        os.remove(img_path)


    
    def get_current_state_json_stream(self):

        json_filemane = f".tmp.json"

        with open(json_filemane, 'w', encoding="utf-8") as outfile:
            json.dump(self.jcoco, outfile, indent=4)

        with open(json_filemane, 'r', encoding="utf-8") as outfile:
            jcoco_string = outfile.read()

        
        json_stream = io.BytesIO(jcoco_string.encode("utf-8"))
        bytes_len = len(jcoco_string)      


        return bytes_len, json_stream


    def get_color_category(self, id_category):
        if id_category not in self.color_encoding:
            return "#7A7A7A"
        return self.color_encoding[id_category]




if __name__ == "__main__":
    import time
    from fileformat_handler import FFHandler

    print("Test class for manager of Viewer&Corrector")

    projectfile_h = FFHandler()

    papfile_test = "data\docs\\00000\TM065797_The_Curse_of_Artemisia_Fragment_WDL4310.pap"

    image, json_data, name, img_ext = projectfile_h.load_formattedfile(papfile_test)
    img_name = f"{name}{img_ext}"

    start = time.time()
    m = Manager(image, json_data, img_name, score_th=0)
    print(f"Time to load Manager: {time.time()-start}")

    # start = time.time()
    # m = Manager(img_test, jcoco_test, score_th=SCORE_TH)
    # print(f"Time to load Manager with score filter: {time.time()-start}")

    # current_list = m.overlappinglist.current()

    # current_list = m.overlappinglist.next()

    # m.overlappinglist.remove_node(current_list)

    # start = time.time()
    # m.init_overappling_list()
    # print(f"Time to Reload Overlapping list: {time.time()-start}")

    print(f"Element in overlapping list: { len(m.overlappinglist)}")




    
    infos = m.get_all_extra_info(123008)


    start = time.time()
    deleted_ann = m.delete_annotation(14) # 7 is an alpha
    print(f"Time to delete element: {time.time()-start}")
    print(f"Element in overlapping list: { len(m.overlappinglist)}")

    start = time.time()
    deleted_ann = m.delete_annotation(16) 
    print(f"Time to delete element: {time.time()-start}")
    print(f"Element in overlapping list: { len(m.overlappinglist)}")

    start = time.time()
    deleted_ann = m.delete_annotation(49) 
    print(f"Time to delete element: {time.time()-start}")
    print(f"Element in overlapping list: { len(m.overlappinglist)}")


    #m.init_overappling_list() # VORREI NON DOVERLO FARE DOPO LE ELIMINAZIONI!!!
    

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

    # Save JSON and IMAGE
    m.save_json()
    m.save_json("save_json_test.json")
    m.delete_json()
    m.delete_json("save_json_test.json")

    m.save_img()
    m.delete_img()
