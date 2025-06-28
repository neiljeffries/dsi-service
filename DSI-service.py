import json
import os
import sys
from flask import Flask
from flask_cors import CORS
import socket
import threading
import pystray
import getpass
from PIL import Image, ImageDraw
import time
import tkinter as tk
from tkinter import messagebox

def get_config_path():
    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app
        # path into variable _MEIPASS'.
        return os.path.join(sys._MEIPASS, 'config.json')
    else:
        return 'config.json'

# Load configuration from external file
with open(get_config_path()) as config_file:
    config = json.load(config_file)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": config["cors_origins"]}})  # Enable CORS with config

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

@app.route(config["machine_name_route"])
def machine_name():
    return get_machine_name()

# Start Flask server in a separate thread and signal when started
def run_flask(started_event):
    try:
        started_event.set()  # Signal before starting the server
        app.run(host=config["host"], port=config["port"], debug=False)
    except Exception as e:
        started_event.clear()

# Function to create an icon and update tooltip based on server status
def create_icon(started_event):
    icon_size = (64, 64)
    image = Image.new("RGBA", icon_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((10, 10, 54, 54), fill=(0, 255, 0))  # Bright green dot

    def on_quit(icon, item):
        icon.stop()
        exit(0)

    menu = pystray.Menu(pystray.MenuItem("Exit DSI Service", on_quit))
    icon = pystray.Icon("server", image, "DSI Service", menu)

    def update_tooltip():
        # Wait a moment for the Flask thread to start
        time.sleep(1)
        if started_event.is_set():
            icon.title = "DSI Service is running"
            # Show a popup for successful start
            try:
                root = tk.Tk()
                root.withdraw()
                messagebox.showinfo("DSI Service", "DSI Service started successfully.")
                root.destroy()
            except Exception:
                pass
        else:
            icon.title = "DSI Service failed to start"
            # Optionally show a popup
            try:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("DSI Service", "Failed to start the Flask server.")
                root.destroy()
            except Exception:
                pass

    threading.Thread(target=update_tooltip, daemon=True).start()
    icon.run()

if __name__ == "__main__":
    started_event = threading.Event()
    flask_thread = threading.Thread(target=run_flask, args=(started_event,), daemon=True)
    flask_thread.start()
    create_icon(started_event)