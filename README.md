# dsi-service


If not installed, download and install Python from python.org.

python --version

pip install pyinstaller
pip install flask
pip install flask-cors
pip install pystray pillow

pyinstaller --onefile --noconsole DSI-service.py
-or-
pyinstaller --noconsole DSI-service.py

Endpoint: http://localhost:5000/machine-name