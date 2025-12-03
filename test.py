import FreeSimpleGUI as sg

def create_main_window():
    layout = [[sg.Text("Main Window")], [sg.Button("Open Second Window")]]
    return sg.Window("Main", layout)

def create_second_window():
    layout = [[sg.Text("Second Window")], [sg.Button("Close Second Window")]]
    return sg.Window("Secondary", layout)

def main():
    window1 = create_main_window()
    window2 = None

    while True:
        event, values = window1.read(timeout=100) # Add a timeout to allow for other window events
        if event == sg.WIN_CLOSED:
            break
        if event == "Open Second Window" and window2 is None:
            window2 = create_second_window()
            # Optionally, hide the main window if you want only one visible at a time
            # window1.hide() 

        if window2:
            event2, values2 = window2.read(timeout=100)
            if event2 == sg.WIN_CLOSED or event2 == "Close Second Window":
                window2.close()
                window2 = None
                # Optionally, unhide the main window
                # window1.un_hide()

    window1.close()

if __name__ == "__main__":
    main()