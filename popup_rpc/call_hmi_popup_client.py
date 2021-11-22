import json
import logging
import rpyc
import pickle


# if __name__ == '__main__':
server_ip = '127.0.0.1'
server_port = 1089710949
rpc_con = rpyc.connect(server_ip, server_port, config={'allow_public_attrs': True, 'sync_request_timeout': 10})
# rpc_con.root.exposed_simplest_popup()


lg = logging.getLogger('mds_popup_window')
logging.basicConfig()
lg.setLevel(logging.DEBUG)


from main import get_dummy_dict

msg_dict = get_dummy_dict(5.2)
# # todo: getting an error about trying to send this dict, might just be much easier to send it as a json string and
# #  wrap it on the other end...
# rpc_con.root.exposed_show_popup_json(json.dumps(msg_dict))
# rpc_con.root.exposed_show_popup_json(rpyc.async_(json.dumps(msg_dict)))

# rpyc.core.netref.
# rpyc.core.netref.builtins.dict()
# nrd = rpyc.core.netref._normalized_builtin_types['builtins.dict']()
# nrd.update(msg_dict)
# rpc_con.root.exposed_show_popup(rpyc.async_(nrd))
# rpc_con.root.exposed_show_popup_pickle(pickle.dumps(msg_dict))
# rpc_con.root.exposed_show_popup_json_sync(msg_dict)
if rpc_con.root.exposed_check_db_for_new_messages():
    lg.debug('server successfully contacted.')
