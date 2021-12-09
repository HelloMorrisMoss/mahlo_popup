import threading
import time
import tkinter
# import queue
from collections import deque

from flask_app import start_flask_app
from main_window import dev_popup, dev_popup_empty

# allow communication
f2p_queue = deque()
p2f_queue = deque()

flask_thread = threading.Thread(target=start_flask_app, args=(p2f_queue, f2p_queue))
flask_thread.setDaemon(True)
flask_thread.start()

# wait until the flask app has been passed since we'll want to use it right away in the popup
while not f2p_queue:
    time.sleep(1)

dev_popup_empty(inbound_queue=f2p_queue, outbound_queue=p2f_queue)

# import subprocess
#
#
# proc = subprocess.Popen(
#     ['cat', '-'],
#     stdin=subprocess.PIPE,
#     stdout=subprocess.PIPE,
# )
# msg = 'through stdin to stdout'.encode('utf-8')
# stdout_value = proc.communicate(msg)[0].decode('utf-8')
