import datetime
import json
import logging
import pickle
import threading

import rpyc
from rpyc.utils.server import ThreadedServer

from main import Popup

lg = logging.getLogger('mds_popup_window')
logging.basicConfig()
lg.setLevel(logging.DEBUG)


date_time = datetime.datetime.now()


class MonitorService(rpyc.Service):
    """Listens for 'Mahlo is stopped and there are new messages' signal to check the database, then displays a popup."""
    def __init__(self):
        super().__init__()
        self.pop_up_showing = False
        self.pop_up_thread = None

    def on_connect(self, connection):
        lg.debug('\nConnected on {}'.format(date_time))

    def on_disconnect(self, connection):
        lg.debug('Disconnected on {}\n'.format(date_time))

    def check_db_new_messages(self):
        from dev_common import get_dummy_dict

        msg_dict = get_dummy_dict(5.2)

        if not self.pop_up_thread:
            lg.debug('popup thread is %s', self.pop_up_thread)
            self.pop_up_thread = threading.Thread(target=Popup, args=(msg_dict,), kwargs={'monitor_service': self})
            self.pop_up_showing = True
            self.pop_up_thread.start()
            # Popup(json.loads(messages_json))
            lg.debug('after')
        return True

    # def exposed_simplest_popup(self):
    #     from main import dev_popup
    #
    #     dev_popup()
    #
    # def exposed_show_popup(self, messages_dict):
    #     rpyc.async_(lambda: Popup(messages_dict))
    #
    # def exposed_show_popup_json(self, messages_json):
    #     rpyc.async_(lambda: Popup(json.loads(messages_json)))
    #     Popup(json.loads(messages_json))
    #
    # def exposed_show_popup_pickle(self, messages_pickle):
    #     rpyc.async_(lambda: Popup(pickle.loads(messages_pickle)))
    #     Popup(json.loads(messages_pickle))
    #
    # def exposed_show_popup_json_sync(self, messages_json):
    #     # TO DO: try starting an async thread in a sync call, don't need rpyc's async, just some async;didn't work
    #     lg.debug('%s', messages_json)
    #     t1 = threading.Thread(target=Popup, args=(messages_json,))
    #     t1.start()
    #     # Popup(json.loads(messages_json))
    #     lg.debug('after')
    #     return

    def exposed_check_db_for_new_messages(self):
        """Start an asynchronous check for new messages in the database. If found, show popup message."""
        self.check_db_new_messages()


def start_server():
    # # port to use...
    # port_str = ''
    # for c in 'lam1':
    #     oc = ord(c)
    #     print(c, oc)
    #     port_str += str(oc)
    # print(port_str)
    port = 1089710949
    thread_0 = ThreadedServer(MonitorService, port=port)
    thread_0.start()


if __name__ == "__main__":
    start_server()
    # pass
