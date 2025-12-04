
Image-ranker
============

Image-ranker is a local application that allows users to select a folder containing
images ('.png', '.jpg', 'jpeg', '.tiff', '.bmp') for comparison to allow for sorting
them by clicking one image or the other in a sequence of comparisons.  

On start-up, select the folder containing the desired images, then choose between
`Vote Mode` and `View Images`.  

In Vote Mode, two images are displayed, and clicking one will deem that image the
winner, awarding it a winning vote. Depending on whether the "keep winner" toggle
is set, one or both images will be cycled to random images in the set. The table
below the images will update as votes are cast.  

In View Images mode, use the file selector on the left side to view individual images.


Getting Started
===============

1. Ensure that the python version appropriate version of tkinter is installed.
   For Leap 16.0 this means python313-tk
2. It is recommended to create a virtual env, such as:
   `python3 -m venv imagenv` 
3. activate the virtual env
   `source imagenv/bin/activate`
4. Install the requirements
   `pip3 install -r requirements.txt`
5. Create the environment variable file and paste your Gemini API Key.
   This is only necessary is the key is not already available as an env variable.
   `cp .env.example .env`

Using gemini to evaluate photos
===============================

Gemini evaluation of individual photos requires a Gemini API key.
The Gemini API key can be obtained from ai.google.dev , see:
https://ai.google.dev/gemini-api/docs/api-key

The key should be set as an env variable, such as in your
.bashrc file, explicitly at the command line, or in a .env file
as suggested in the `Getting Started` instructions. 

```
https://ai.google.dev/gemini-api/docs/api-key
```

If this key is not set, Gemini functionality will not be available


Running the Application
=======================

`python3 main.py`


