"""Starts the flask server and then the popup interface."""

import threading
from collections import deque

from fresk.flask_app import start_flask_app
from main_window import MainWindow

# allow communication
f2p_queue = deque()
p2f_queue = deque()

# start the flask app in its own thread
flask_thread = threading.Thread(target=start_flask_app, args=(p2f_queue, f2p_queue))
flask_thread.setDaemon(True)
flask_thread.start()

# start the popup (tkinter requires the main thread)
MainWindow(inbound_queue=f2p_queue, outbound_queue=p2f_queue)
