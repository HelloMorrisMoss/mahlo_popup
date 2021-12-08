import threading
import tkinter
# import queue
from collections import deque

from flask_app import start_flask_app
from main_window import dev_popup


# allow communication
f2p_queue = deque()
p2f_queue = deque()

flask_thread = threading.Thread(target=start_flask_app, args=(p2f_queue, f2p_queue))
flask_thread.setDaemon(True)
flask_thread.start()

import  datetime
import time

while True:
    time.sleep(20)
    p2f_queue.append(f'popup sent msg at {datetime.datetime.now()}')
    while f2p_queue:
        print(f'message back: {f2p_queue.pop()} at {datetime.datetime.now()}')


# root = tkinter.Tk()

# signal_queue = queue.Queue()
#
# def new_signal(root_win):
#     root_win.event_generate('<<MessageGenerated>>')
#
#
# def get_new_signal(root_win, sig_queue):
#
#
#
#
# root.bind('<<MessageGenerated>>', lambda e: process(message_queue, e))

dev_popup()

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
