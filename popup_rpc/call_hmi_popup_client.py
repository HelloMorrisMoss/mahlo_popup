import rpyc

if __name__ == '__main__':
    server_ip = '127.0.0.1'
    server_port = 1089710949
    rpc_con = rpyc.connect(server_ip, server_port)
    rpc_con.root.exposed_simplest_popup()