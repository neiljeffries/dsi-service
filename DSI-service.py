from flask import Flask
from flask_cors import CORS
import socket
import threading
import pystray
from PIL import Image, ImageDraw

app = Flask(__name__)
CORS(app)  # Enable CORS for Angular

def get_machine_name():
    return {"machine_name": socket.gethostname()}

@app.route("/machine-name")
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
    app.run(host="0.0.0.0", port=5000, debug=False)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()  # Run Flask in the background
    create_icon()  # Show system tray icon
