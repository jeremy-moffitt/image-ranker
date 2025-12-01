#!/usr/bin/env python
import FreeSimpleGUI as sg
import os
from PIL import Image, ImageTk
import io
import random
import google.generativeai as genai
import os

"""
Simple Image Browser based on PySimpleGUI
--------------------------------------------
There are some improvements compared to the PNG browser of the repository:
1. Paging is cyclic, i.e. automatically wraps around if file index is outside
2. Supports all file types that are valid PIL images
3. Limits the maximum form size to the physical screen
4. When selecting an image from the listbox, subsequent paging uses its index
5. Paging performance improved significantly because of using PIL

Dependecies
------------
Python3
PIL
"""

# Get the folder containin:g the images from the user
folder = sg.popup_get_folder('Image folder to open', default_path='')
if not folder:
    sg.popup_cancel('Cancelling')
    raise SystemExit()

# PIL supported image types
img_types = ('.png', '.jpg', 'jpeg', '.tiff', '.bmp')

# get list of files in folder
flist0 = os.listdir(folder)

# create sub list of image files (no sub folders, no wrong file types)
fnames = [f for f in flist0 if os.path.isfile(
    os.path.join(folder, f)) and f.lower().endswith(img_types)]

num_files = len(fnames)                # number of iamges found
if num_files == 0:
    sg.popup('No files in folder')
    raise SystemExit()

del flist0                             # no longer needed

# ------------------------------------------------------------------------------
# use PIL to read data of one image
# ------------------------------------------------------------------------------


def get_img_data(f, maxsize=(1200, 850), first=False):
    """Generate image data using PIL
    """
    img = Image.open(f)
    img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format='PNG')
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)
# ------------------------------------------------------------------------------


# make these 2 elements outside the layout as we want to "update" them later
# initialize to the first file in the list
i = 0
j = 0
filename = os.path.join(folder, fnames[i])  # name of first file in list
compare_filename = os.path.join(folder, fnames[0])
if(num_files > 1):
    j = 1
    compare_filename = os.path.join(folder, fnames[j])
image_elem = sg.Image(data=get_img_data(filename, first=True), enable_events=True, key='-BASEIMG-')
compare_image_elem = sg.Image(data=get_img_data(compare_filename, first=True), enable_events=True, key='-COMPAREIMG-')
filename_display_elem = sg.Text(filename, size=(80, 3))
compare_filename_display_elem = sg.Text(compare_filename, size=(80, 3))
file_num_display_elem = sg.Text('File 1 of {}'.format(num_files), size=(15, 1))

# define layout, show and read the form
col = [[compare_image_elem],[filename_display_elem]]

compare_col = [[image_elem], [compare_filename_display_elem]]

col_files = [[sg.Listbox(values=fnames, change_submits=True, size=(60, 30), key='listbox', default_values=fnames[0])],
             [sg.Button('Next', size=(8, 2)), sg.Button('Prev', size=(8, 2)), file_num_display_elem],
             [sg.Button('Random', size=(8,2))],
             [
                sg.Button('Gemini Eval (left photo)', key='-Gemini photo eval-', size=(8,2)),
                sg.Button('Gemini Compare', key='-Gemini photo compare-', size=(8,2)),
                sg.Button('Gemini Rank next 5', key='-Gemini photo rank-', size=(8,2))
             ]]

layout = [[sg.Column(col_files), sg.Column(compare_col), sg.Column(col)]]

window = sg.Window('Image Ranker', layout, return_keyboard_events=True,
                   location=(0, 0), use_default_focus=False)

# loop reading the user input and displaying image, filename

while True:
    # read the form
    event, values = window.read()
    print(event, values)
    # perform button and keyboard operations
    if event == sg.WIN_CLOSED:
        break
    elif event in ('Next', 'MouseWheel:Down', 'Down:40', 'Next:34'):
        i += 1
        if i >= num_files:
            i -= num_files
        filename = os.path.join(folder, fnames[i])
    elif event in ('Prev', 'MouseWheel:Up', 'Up:38', 'Prior:33'):
        i -= 1
        if i < 0:
            i = num_files + i
        filename = os.path.join(folder, fnames[i])
    elif event in ('Random'):
        i = random.randrange(0,num_files)
        j = random.randrange(0,num_files)
        while(j == i):
            j = random.randrange(0,num_files)        
        filename = os.path.join(folder, fnames[i])
        compare_filename = os.path.join(folder, fnames[j])
    elif event == 'listbox':            # something from the listbox
        f = values['listbox'][0]            # selected filename
        filename = os.path.join(folder, f)  # read this file
        i = fnames.index(f)                 # update running index
    elif event == '-BASEIMG-':
        i = random.randrange(0,num_files)
        filename = os.path.join(folder, fnames[i])
    elif event == '-COMPAREIMG-':
        j = random.randrange(0,num_files)
        while(j == i):
            j = random.randrange(0,num_files)        
        compare_filename = os.path.join(folder, fnames[j])        
    elif event == '-Gemini photo eval-':
        # asks Gemini to evaluate the sharpness of the current photo on a scale of 0-10
        if 'GEMINI_API_KEY' not in os.environ:
            sg.popup('No Gemini Key in os.environ, cannot perform AI evaluation')
        else:
            gemini_key = os.environ['GEMINI_API_KEY']
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel(model_name='gemini-2.5-flash')
            filename = os.path.join(folder, fnames[i])
            image_for_gemini = Image.open(filename)
            response = model.generate_content(['Rate this image for sharpness on a scale of 0-10', image_for_gemini])

            sg.popup(f'Gemini evaluation for {filename}:\n\n {response.text}')
            image_for_gemini.close()
    elif event == '-Gemini photo compare-':
        # this will ask Gemini to compare the two photos on screen for sharpness
        # the result from Gemini will pop on screen
        if 'GEMINI_API_KEY' not in os.environ:
            sg.popup('No Gemini Key in os.environ, cannot perform AI comparison')
        else:
            gemini_key = os.environ['GEMINI_API_KEY']
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel(model_name='gemini-2.5-flash')
            file1 = os.path.join(folder, fnames[i])
            file2 = os.path.join(folder, fnames[j])
            image1 = Image.open(file1)
            image2 = Image.open(file2)
            response = model.generate_content(['Compare these two images and indicate which picture is technically superior. Start your response with 1 or 2 to indicate which image is the answer before giving details. If they are equivalent, randomly select 1 or 2.', image1, image2])

            # print the full response for now, might remove this later
            print(f'Gemini comparison for {file1} vs {file2}:\n\n {response.text}')
            if(response.text.startswith("1")):
                sg.popup(f"Gemini votes for image1: {file1}")
            else:
                sg.popup(f"Gemini votes for image2: {file2}")
            image1.close()
            image2.close()
    elif event == '-Gemini photo rank-':
        # this will ask Google to rank the currently selected photo along with the next 4 in the list
        # the rankings are based on Googles perception of sharpness of the image
        if 'GEMINI_API_KEY' not in os.environ:
            sg.popup('No Gemini Key in os.environ, cannot perform AI ranking')
        else:
            gemini_key = os.environ['GEMINI_API_KEY']
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel(model_name='gemini-2.5-flash')
            k = i
            query_contents = []
            query_image_names = []
            while k < num_files:
                file1 = os.path.join(folder, fnames[k])
                image1 = Image.open(file1)
                query_contents.append(image1)
                query_image_names.append(fnames[k])
                k += 1
                if len(query_contents) == 5 or len(query_contents) == num_files:
                    # if all files are in the query contents, or 5 files are in, break out
                    break
                elif k >= num_files:
                    # this wraps k around from the bottom to the top of the list
                    k = 0
                image1.close()
            query_contents.append('rank these photos by sharpness, return the result as a list of the image names')
            query_contents.append(f'the image names in order are {','.join(query_image_names)}')
            response = model.generate_content(query_contents)

            sg.popup(f'Gemini image ranking:\n\n {response.text}')
    else:
        filename = os.path.join(folder, fnames[i])

    # update the selection in the listbox to the left side photo
    listbox = window['listbox']
    listbox.update(set_to_index=[i], scroll_to_index=i)
    # update window with new image
    image_elem.update(data=get_img_data(filename, first=True))
    compare_image_elem.update(data=get_img_data(compare_filename, first=True))
    # update window with filename
    filename_display_elem.update(filename)
    compare_filename_display_elem.update(compare_filename)
    # update page display
    file_num_display_elem.update('File {} of {}'.format(i+1, num_files))

window.close()
