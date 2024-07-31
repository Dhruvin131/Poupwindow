import PySimpleGUI as sg
from pynput import keyboard, mouse
import threading
import win32gui
import win32con
import win32api
import queue

# Global flag to indicate the popup is active
popup_active = True
command_queue = queue.Queue()

def get_window_handle(window_title):
    return win32gui.FindWindow(None, window_title)

def move_window_to_position(window_handle, x, y):
    # Get screen dimensions
    screen_width = win32api.GetSystemMetrics(0)  # Screen width
    screen_height = win32api.GetSystemMetrics(1) # Screen height
    
    # Constrain the x and y coordinates
    x = max(0, min(x, screen_width - 1))  # Constrain x within the screen width
    y = max(0, min(y, screen_height - 1)) # Constrain y within the screen height
    
    try:
        win32gui.SetWindowPos(window_handle, win32con.HWND_TOPMOST, x, y, 0, 0,
                              win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)
    except Exception as e:
        print(f"Error moving window: {e}")

# Handle keyboard events
def on_press(key):
    if popup_active:
        print(f"Blocked key press: {key}")
        command_queue.put('block')  # Indicate a block command

# Handle mouse events
def on_click(x, y, button, pressed):
    if pressed and popup_active:
        window_handle = get_window_handle('Break Time')
        if window_handle:
            try:
                rect = win32gui.GetWindowRect(window_handle)
                win_left, win_top, win_right, win_bottom = rect

                if not (win_left <= x <= win_right and win_top <= y <= win_bottom):
                    print(f"Mouse click outside window at ({x}, {y}). Moving window.")
                    move_window_to_position(window_handle, x, y)
                    command_queue.put('move')  # Indicate a move command
            except Exception as e:
                print(f"Error handling mouse click: {e}")

def run_event_listeners():
    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener.start()
    mouse_listener.start()
    keyboard_listener.join()
    mouse_listener.join()

def run_popup(window):
    global popup_active
    while popup_active:
        # Read the event from the GUI
        event, values = window.read(timeout=100)  # Polling the GUI
        if event == sg.WIN_CLOSED or event == 'OK':
            popup_active = False

        # Process commands from the event listeners
        while not command_queue.empty():
            command = command_queue.get()
            if command == 'block':
                # Handle blocking key press
                pass
            elif command == 'move':
                # Handle moving the window
                pass

    window.close()
    print("Popup window closed.")

# Define the layout for the PySimpleGUI window
layout = [[sg.Text('Take a break!')],
          [sg.Button('OK')]]

# Create the window in the main thread
window = sg.Window('Break Time', layout, return_keyboard_events=True,
                   finalize=True, keep_on_top=True, modal=True)

# Start the GUI event loop in the main thread

# Start event listeners in a separate thread
event_thread = threading.Thread(target=run_event_listeners, daemon=True)
event_thread.start()

run_popup(window)
# Wait for threads to finish
event_thread.join()
