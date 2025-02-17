import json
import os
import sys
from flask import Flask
from flask_cors import CORS
import socket
import threading
import pystray
from PIL import Image, ImageDraw

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
    return {"machine_name": socket.gethostname()}

@app.route(config["machine_name_route"])
def machine_name():
    return get_machine_name()

# Function to create an icon
def create_icon():
    icon_size = (64, 64)
    image = Image.new("RGBA", icon_size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.ellipse((10, 10, 54, 54), fill=(0, 255, 0))  # Bright green dot

    def on_quit(icon, item):
        icon.stop()
        exit(0)

    menu = pystray.Menu(pystray.MenuItem("Exit DSI Service", on_quit))
    icon = pystray.Icon("server", image, "DSI Service is running", menu)
    icon.run()

# Start Flask server in a separate thread
def run_flask():
    app.run(host=config["host"], port=config["port"], debug=False)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()  # Run Flask in the background
    create_icon()  # Show system tray icon