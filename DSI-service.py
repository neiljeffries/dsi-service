import json
import os
import sys
import socket
import threading
import pystray
import getpass
from PIL import Image, ImageDraw
import time
import tkinter as tk
from tkinter import messagebox
from flask import Flask
from flask_cors import CORS
import ctypes


# Check if running as a frozen executable (e.g., PyInstaller)
# This allows the script to find the config file in the correct location
def get_config_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'config.json')
    else:
        return 'config.json'

with open(get_config_path()) as config_file:
    config = json.load(config_file)

# Ensure the config file has the required keys
# required_keys = ["host", "port", "cors_origins", "machine_name_route"]
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": config["cors_origins"]}})

# Get the machine name and user ID
def get_machine_name():
    try:
        machine_name = socket.gethostname()
    except Exception:
        machine_name = "unknown"
    try:
        user_id = getpass.getuser()
    except Exception:
        user_id = "unknown"
    return {
        "machine_name": machine_name,
        "user_id": user_id
    }

# Define the Flask route to return machine name and user ID
@app.route(config["machine_name_route"])
def machine_name():
    return get_machine_name()

# Function to run the Flask server in a separate thread
def run_flask(started_event):
    try:
        started_event.set()
        app.run(host=config["host"], port=config["port"], debug=False)
    except Exception as e:
        started_event.clear()

# Function to show the info window with machine name and user ID
def show_info_window():
    info = get_machine_name()
    root = tk.Tk()
    root.title("DSI Service Info")
    root.geometry("300x120")
    root.resizable(False, False)
    root.eval('tk::PlaceWindow . center')
    label1 = tk.Label(root, text=f"Machine Name: {info['machine_name']}", font=("Arial", 12))
    label1.pack(pady=(20, 5))
    label2 = tk.Label(root, text=f"User ID: {info['user_id']}", font=("Arial", 12))
    label2.pack(pady=(0, 10))
    btn = tk.Button(root, text="Close", command=root.destroy)
    btn.pack()
    root.mainloop()

# Function to create the system tray icon
def create_icon(started_event):
    icon_size = (64, 64)
    image = Image.new("RGBA", icon_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    # Draw green "DSI" text centered
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arialbd.ttf", 40)
    except Exception:
        font = ImageFont.load_default()
    text = "DSI"
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        text_width, text_height = font.getsize(text)
    x = (icon_size[0] - text_width) // 2
    y = (icon_size[1] - text_height) // 2
    draw.text((x, y), text, font=font, fill=(0, 200, 0, 255))

    def on_quit(icon, item):
        icon.stop()
        exit(0)

    # Function to show the info window in a separate thread
    # to avoid blocking the main thread
    def on_show_info(icon, item):
        threading.Thread(target=show_info_window, daemon=True).start()

    # Create the system tray icon with a menu
    # and set the tooltip to indicate the service status
    menu = pystray.Menu(
        pystray.MenuItem("Show Info", on_show_info),
        pystray.MenuItem("Exit DSI Service", on_quit)
    )
    icon = pystray.Icon("server", image, "DSI Service", menu)

    # Function to update the tooltip after a delay
    # and show a message box indicating success or failure
    def update_tooltip():
        time.sleep(1)
        if started_event.is_set():
            icon.title = "DSI Service is running"
            try:
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("DSI Service", "DSI Service started successfully.")
                root.destroy()
            except Exception:
                pass
        else:
            icon.title = "DSI Service failed to start"
            try:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("DSI Service", "Failed to start the Flask server.")
                root.destroy()
            except Exception:
                pass

    threading.Thread(target=update_tooltip, daemon=True).start()
    icon.run_detached()

# Function to check if the service is already running using a Windows named mutex
def already_running_mutex():
    # Use a Windows named mutex to ensure single instance
    mutex_name = "DSI_SERVICE_SINGLETON_MUTEX"
    kernel32 = ctypes.windll.kernel32
    kernel32.CreateMutexW(None, ctypes.c_bool(False), mutex_name)
    last_error = kernel32.GetLastError()
    # ERROR_ALREADY_EXISTS == 183
    if last_error == 183:
        return True
    return False

# This function checks if the service is already running by trying to create a named mutex.
if __name__ == "__main__":
    if already_running_mutex():
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("DSI Service", "DSI Service is already running.")
        root.destroy()
        sys.exit(0)
    started_event = threading.Event()
    flask_thread = threading.Thread(target=run_flask, args=(started_event,), daemon=True)
    flask_thread.start()
    create_icon(started_event)