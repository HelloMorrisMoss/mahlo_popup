"""Starts the flask server and then the popup interface."""

import threading
from collections import deque

from fresk.flask_app import start_flask_app
from log_setup import lg
from main_window import MainWindow
from untracked_config.development_node import dev_node

# allow communication between flask and the popup
f2p_queue = deque()
p2f_queue = deque()

run_server = True
run_popup = True
if dev_node:
    from untracked_config.testing_this import testing_this

    if testing_this:
        response = testing_this
    else:
        response = input('Run: server 1, popup 2, both return:')
    if response == '1':
        run_popup = False
    elif response == '2':
        run_server = False
if run_server and run_popup:
    # start the flask app in its own thread
    flask_thread = threading.Thread(target=start_flask_app, args=(p2f_queue, f2p_queue))
    flask_thread.setDaemon(True)
    flask_thread.start()

    # start the popup (tkinter requires the main thread)
    MainWindow(inbound_queue=f2p_queue, outbound_queue=p2f_queue)
elif run_server:
    lg.info('Starting the flask webserver without a popup.')
    start_flask_app(p2f_queue, f2p_queue)
elif run_popup:
    lg.info('Starting popup without a flask server.')
    MainWindow(inbound_queue=f2p_queue, outbound_queue=p2f_queue)
