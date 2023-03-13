import os
import tempfile
import threading
import time
import unittest

from flask_server_files.helpers import single_instance


class TestSingleInstance(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.lock_file = os.path.join(self.tempdir.name, 'my_program.lock')

    def tearDown(self):
        self.tempdir.cleanup()

    def test_single_instance(self):
        # Create a new thread to acquire the lock file
        def acquire_lock():
            with single_instance(self.lock_file):
                time.sleep(5)

        t = threading.Thread(target=acquire_lock)
        t.start()

        # Wait for the thread to acquire the lock file
        time.sleep(0.1)

        # Try to acquire the lock file again
        with self.assertRaises(OSError):
            with single_instance(self.lock_file, timeout=1):
                pass

        # Wait for the thread to release the lock file
        t.join()

        # Try to acquire the lock file again
        with single_instance(self.lock_file, timeout=1):
            pass
