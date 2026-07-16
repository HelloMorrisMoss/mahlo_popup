"""Functionality for monitoring the host machine, specifically the vendor's software and functionality.

The PrintSVR.exe program sometimes either crashes or an operator mistakenly closes it. If it is not running, then
it will not be able to print PDF reports. Similarly, sometimes it enters a hung state - remaining
open but does not create PDF reports. The PDF reports are production-critical, so monitoring that the PrintSVR.exe
is running and creating PDF reports is essential.
"""

import os
import subprocess
import time

import requests

from log_and_alert.log_setup import lg
from untracked_config.configuration_data import port, printsvr_path, pdf_root_directory, pdf_created_window_seconds


def watchdog_check_printsvr():
    """
    Checks if PrintSVR.exe is running, attempts to restart it if it is not
    running, and sends a notification if the restart attempt fails.

    :raises Exception: Raised during errors in subprocess communication, notifications, or process management.

    :return: None
    """
    def is_running():
        try:
            # Use tasklist to check for the process on Windows
            output = subprocess.check_output('tasklist /FI "IMAGENAME eq PrintSVR.exe"', shell=True).decode()
            return "PrintSVR.exe" in output
        except Exception as e:
            lg.error(f"Error checking PrintSVR.exe: {e}")
            return False

    def send_notification():
        lg.error("Failed to ensure PrintSVR.exe is running. Sending notification.")
        msg_dct = {
            'additional_message_text': 'The Mahlo PDF print server program is not running, please restart the HMI. '
                                       '[try pressing the "Restart Mahlo HMI" button below 3 times]',
            'additional_message_short_text': 'PDF Error!'}
        try:
            # Send notification to the popup via the button_msg endpoint
            requests.post(f'http://localhost:{port}/button_msg', json=msg_dct, timeout=5)
        except Exception as e:
            lg.error(f"Failed to send failure notification: {e}")

    if not is_running():
        lg.warning("PrintSVR.exe is not running. Attempting to restart at %s", printsvr_path)
        try:
            # Start as a detached process with the correct working directory
            # to ensure it persists after the popup closes.
            cwd = os.path.dirname(printsvr_path)
            subprocess.Popen(printsvr_path, cwd=cwd, creationflags=subprocess.DETACHED_PROCESS)
            time.sleep(5)  # Give it some time to start
            if not is_running():
                send_notification()
            else:
                lg.info("PrintSVR.exe successfully restarted.")
        except Exception as e:
            lg.error(f"Exception during PrintSVR.exe restart attempt: {e}")
            send_notification()


def find_recent_pdf():
    """
    Checks to ensure that a report PDF has been created recently and returns its path if it exists.

    Searches for a recently created PDF file within a specified directory and its two most recent
    subdirectories that match a date format. The file must have been created within a
    specified time window.

    :return: The path to the most recent PDF file that matches the criteria, or None if no
        file is found.
    :rtype: str or None
    """
    import re

    root_dir = pdf_root_directory
    window_seconds = pdf_created_window_seconds

    if not os.path.exists(root_dir):
        lg.warning(f"PDF root directory does not exist: {root_dir}")
        return None

    # Get subdirectories with YYYYMMDD format
    date_pattern = re.compile(r'^\d{8}$')
    try:
        subdirs = [d for d in os.listdir(root_dir) if
                   os.path.isdir(os.path.join(root_dir, d)) and date_pattern.match(d)]
    except Exception as e:
        lg.error(f"Error listing directory {root_dir}: {e}")
        return None

    subdirs.sort(reverse=True)
    recent_dirs = subdirs[:2]

    # Paths to check: root and the two most recent date folders
    dirs_to_check = [root_dir] + [os.path.join(root_dir, d) for d in recent_dirs]

    now = time.time()

    for d in dirs_to_check:
        if not os.path.exists(d):
            continue
        try:
            for f in os.listdir(d):
                if not f.lower().endswith('.pdf'):
                    continue

                file_path = os.path.join(d, f)
                try:
                    # Windows often uses mtime for creation-like semantics for files, 
                    # but ctime is "creation time" on Windows.
                    creation_time = os.path.getctime(file_path)

                    if (now - creation_time) <= window_seconds:
                        return file_path
                except Exception as e:
                    lg.debug(f"Error getting ctime for {file_path}: {e}")
                    continue
        except Exception as e:
            lg.error(f"Error listing directory {d}: {e}")
            continue

    return None
