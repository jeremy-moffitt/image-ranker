import FreeSimpleGUI as sg

# 1. Your dictionary data
data_dict = {
    'Item A': [10, 20, 30],
    'Item B': [40, 50, 60],
    'Item C': [70, 80, 90],
    'Item D': [100, 110, 120]
}

# 2. Extract headings (keys) and transform values into a list of lists (rows)
headings = list(data_dict.keys())
# The values are already lists, but they are organized by column, not row.
# We use zip(*) to transpose the data into rows.
# If all value lists have the same length, this works perfectly.
values = list(zip(*data_dict.values()))

# Example of what `values` looks like:
# [
#   (10, 40, 70, 100),
#   (20, 50, 80, 110),
#   (30, 60, 90, 120)
# ]

# 3. Define the PySimpleGUI layout
layout = [
    [sg.Text("Dictionary Data in a 4-Column Table")],
    [sg.Table(
        values=values,
        headings=headings,
        auto_size_columns=True,
        display_row_numbers=False,
        justification='right',
        key='-TABLE-',
        row_height=25
    )],
    [sg.Button('Exit')]
]

# 4. Create and run the window
window = sg.Window("Dict to Table Example", layout, finalize=True)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

window.close()