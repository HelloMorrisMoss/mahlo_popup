import threading
import time
from collections import deque

from fresk.flask_app import start_flask_app
from main_window import Popup

# allow communication
f2p_queue = deque()
p2f_queue = deque()

flask_thread = threading.Thread(target=start_flask_app, args=(p2f_queue, f2p_queue))
flask_thread.setDaemon(True)
flask_thread.start()

# wait until the flask app has been passed since we'll want to use it right away in the popup
while not f2p_queue:
    time.sleep(1)

Popup(inbound_queue=f2p_queue, outbound_queue=p2f_queue)
