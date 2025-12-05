""" Builds the locale files for the image_ranker
"""

import os
import subprocess

LOCALE_DIR = "locale"  # folder with the locale files
DOMAIN = "main"       # domain for the app, currently just "main"

# each locale is in a folder matching its locale_code
# such as "en" for English and "pt-BR" for Portuguese (Brazilian)
for locale_code in os.listdir(LOCALE_DIR):
    locale_path = os.path.join(LOCALE_DIR, locale_code)
    if os.path.isdir(locale_path):
        lc_messages_path = os.path.join(locale_path, "LC_MESSAGES")
        # po files have the msgid and msgstr entries
        # mo files are the machine readable version
        po_file = os.path.join(lc_messages_path, f"{DOMAIN}.po")
        mo_file = os.path.join(lc_messages_path, f"{DOMAIN}.mo")

        if os.path.exists(po_file):
            print(f"Processing {po_file} into {mo_file}")
            try:
                subprocess.run(["msgfmt", "-o", mo_file, po_file], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error processing {po_file}: {e}")
        else:
            print(f"Warning: {po_file} not found.")