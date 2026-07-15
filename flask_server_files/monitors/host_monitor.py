import os
import subprocess
import time

import requests

from log_and_alert.log_setup import lg
from untracked_config.configuration_data import port, printsvr_path


def watchdog_check_printsvr():
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
            'additional_message_text': 'The Mahlo PDF print server program is not running, please restart the HMI. [try pressing the "Restart Mahlo HMI" button below 3 times]',
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
