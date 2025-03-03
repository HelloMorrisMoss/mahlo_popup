"""Starts the flask server and then the popup interface."""
import os
import threading
from collections import deque
from traceback import format_exc as fexc

from dev_common import exception_one_line, restart_program, get_email_body_context
from flask_server_files.flask_app import start_flask_app
from flask_server_files.helpers import single_instance
from log_and_alert.email_alert import get_email_cfg_dict, set_up_alert
from log_and_alert.log_setup import lg, program_unique_id
from log_and_alert.program_restart_records import record_restart
from main_window import MainWindow
from restart_error import RestartError
from untracked_config.configuration_data import ON_DEV_NODE, HOSTNAME
from untracked_config.lam_num import LAM_NUM
from untracked_config.testing_this import testing_this

try:
    # if there is already an instance running, stop now
    lock_file_path = './mahlo_popup.lock'
    try:
        os.remove(lock_file_path)
    except FileNotFoundError:
        pass  # good

    with single_instance(lock_file_path):
        # allow communication between flask and the popup
        f2p_queue = deque()
        p2f_queue = deque()
        termination_queue = deque()

        f2p_queue.append({'program_unique_id': program_unique_id})
        p2f_queue.append({'program_unique_id': program_unique_id})

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

            else:
                # probably running on a mahlo pc, make it known that it's starting up
                subject = f'Mahlo Popup on lam{LAM_NUM} is starting up since no other instance is running.'
                body = get_email_body_context(run_popup, run_server, ON_DEV_NODE, HOSTNAME)

                cfg = get_email_cfg_dict(lam_num=LAM_NUM)
                set_up_alert(cfg, subject=subject,
                             body=body)

        if run_server and run_popup:
            # start the flask app in its own thread
            flask_thread = threading.Thread(target=start_flask_app, args=(p2f_queue, f2p_queue))
            flask_thread.daemon = True
            flask_thread.start()

            # start the popup (tkinter requires the main thread)
            MainWindow(inbound_queue=f2p_queue, outbound_queue=p2f_queue, termination_dict=termination_queue)
        elif run_server:
            lg.info('Starting the flask webserver without a popup.')
            start_flask_app(p2f_queue, f2p_queue)
        elif run_popup:
            lg.info('Starting popup without a flask server.')
            MainWindow(inbound_queue=f2p_queue, outbound_queue=p2f_queue)

        if termination_queue:
            lg.info('termination source returned!')
            raise termination_queue.pop()

except RestartError as rse:
    lg.info('RestartError found.')
    try:
        # Record the restart event
        record_restart(rse)
    except Exception as recording_exception:
        lg.exception("An error occurred during the handling of another error", recording_exception)
    finally:
        restart_program(lg, rse)

except OSError as ose:
    if str(ose) in ('Another instance of the program is already running.',
                    "[WinError 32] The process cannot access the file because it is being used by another process: "
                    "'./malo_popup.lock'"):
        lg.debug(ose)  # normal
    else:
        lg.error(ose)

except Exception as exc:
    exc_text = fexc().replace('\\n', '\n')
    lg.error(exception_one_line(exc))
    if not ON_DEV_NODE:
        # if anything goes wrong at this level, the program is crashing, it needs to be known, send an e-mail
        subject = f'Mahlo Popup on lam{LAM_NUM} has had an unhandled exception and is shutting down'
        body = get_email_body_context(run_popup, run_server, ON_DEV_NODE, HOSTNAME) + '\nstacktrace:\n' + exc_text

        cfg = get_email_cfg_dict(lam_num=LAM_NUM)
        set_up_alert(cfg, subject=subject,
                     body=body)
