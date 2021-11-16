import datetime
import logging

import rpyc
from rpyc.utils.server import ThreadedServer


lg = logging.getLogger('mds_popup_window')
logging.basicConfig()
lg.setLevel(logging.DEBUG)


date_time = datetime.datetime.now()


class MonitorService(rpyc.Service):
    def on_connect(self, connection):
        print('\nConnected on {}'.format(date_time))

    def on_disconnect(self, connection):
        print('Disconnected on {}\n'.format(date_time))

    def exposed_simplest_popup(self):
        from main import dev_popup

        dev_popup()


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
