"""Starts the flask server and then the popup interface."""

import threading
from collections import deque

from dev_common import exception_one_line
from flask_server_files.flask_app import start_flask_app
from log_setup import lg
from main_window import MainWindow
from untracked_config.development_node import ON_DEV_NODE
from untracked_config.lam_num import LAM_NUM
from untracked_config.testing_this import testing_this

# allow communication between flask and the popup
f2p_queue = deque()
p2f_queue = deque()

# default
run_server = True
run_popup = True

# testing pieces individually
if ON_DEV_NODE:
    if testing_this == '1':
        run_popup = False
    elif testing_this == '2':
        run_server = False

else:
    if not LAM_NUM:
        run_popup = False  # don't run the popup on the oee server
try:
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
except Exception as exc:
    from email_alert import get_email_cfg_dict, set_up_alert
    from traceback import format_exc as fexc

    exc_text = fexc().replace('\\n', '\n')
    lg.error(exception_one_line(exc))

    # if anything goes wrong at this level, the program is crashing, it needs to be known, send an e-mail
    subject = f'Mahlo Popup on lam{LAM_NUM} has had an unhandled exception and is shutting down'
    body = f'''Exception context:
    {LAM_NUM=}
    {run_popup=}
    {run_server=}
    stacktrace:
    ''' + exc_text

    cfg = get_email_cfg_dict(lam_num=LAM_NUM)
    set_up_alert(cfg, subject=subject,
                 body=body)
