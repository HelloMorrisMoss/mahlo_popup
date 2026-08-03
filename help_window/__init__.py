# import os
# os.environ['SUPPRESS_AUTO_LOG_SETUP'] = 'True'
# from log_and_alert.log_setup import setup_logger, suppress_dependency_log_spam
# lg = setup_logger(file_log_params={'filename': 'help_window.log', 'maxBytes': 10000000,})
# suppress_dependency_log_spam()

from log_and_alert.log_setup import lg

lg.info('Help Window Initialized.')
