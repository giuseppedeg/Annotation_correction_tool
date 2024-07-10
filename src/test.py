from pyscript import document, display
from js import document, console, Uint8Array, window, File
from  random import randint
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io


def generate_random_number(event):
    input_max_num = document.querySelector("#max_num")
    max_num = input_max_num.value # it's a str
    max_num = int(max_num)
    
    output_div = document.querySelector("#output")
    output_div.innerText = f"Il  numero generato è: {randint(0, max_num)}"

    x = np.random.rand(max_num)
    y = np.random.rand(max_num)
    colors = np.random.rand(max_num)
    area = (30 * np.random.rand(max_num))**2  # 0 to 15 point radii

    plt.scatter(x, y, s=area, c=colors, alpha=0.5)

    display(plt, target="fig")

def view_images(event):
    img_path = "./data/current_doc/example_bboxes.jpg"

    print(img_path)

    my_image = Image.open(img_path)

    for _ in range(3):

        #elaborate image
        left = randint(0, 500)
        top = randint(0, 500)
        right = left + randint(50, 100)
        bottom = top + randint(50, 100)
        
        # Cropped image of above dimension
        # (It will not change original image)
        im_crop = my_image.crop((left, top, right, bottom))

        #Convert Pillow object array back into File type that createObjectURL will take
        my_stream = io.BytesIO()
        im_crop.save(my_stream, format="PNG")

        #Create a JS File object with our data and the proper mime type
        image_file = File.new([Uint8Array.new(my_stream.getvalue())], "new_image_file.png", {type: "image/png"})

        #create HTML element and add to page
        new_image = document.createElement('img')
        new_image.src = window.URL.createObjectURL(image_file)
        new_image.classList.add("myClass")

        document.getElementById("all_images").appendChild(new_image)

    

    