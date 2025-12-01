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

Using gemini to evaluate photos
===============================

Gemini evaluation of individual photos requires a Gemini API key.
The Gemini API key can be obtained from ai.google.dev , see:
https://ai.google.dev/gemini-api/docs/api-key

The key should be set as an env variable, such as in your
.bashrc file or explicitly at the command line:

```
https://ai.google.dev/gemini-api/docs/api-key
```

If this key is not set, Gemini functionality will not be available


Running the Application
=======================

`python3 main.py`


