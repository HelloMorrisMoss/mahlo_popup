import io
from traceback import format_exc
import logging

import waitress

from flask import Flask, render_template, send_file
from flask import Response
from flask import request
# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# from __init__ import lg
# from update_display import get_recent_graph_obj
from popup_rpc.call_hmi_popup_client import rpc_con

lg = logging.getLogger('mds_popup_window')
logging.basicConfig()
lg.setLevel(logging.DEBUG)

server = Flask(__name__)
server._shutdown_bool = False

# TODO: how to enable https?
#  Would that actually be useful for anything here?


# @server.route('/plot.png')
# def plot_png():
#     try:
#         plt, fig, fig_ax = get_recent_graph_obj()
#         output = io.BytesIO()
#         FigureCanvas(fig).print_png(output)
#         return Response(output.getvalue(), mimetype='image/png')
#     except ValueError:
#         lg.warning(f'Probably, no recent data. {format_exc()}')
#         return send_file('./static/images/NoRecentData.png', mimetype='image/png')


@server.route("/")
def compression_refreshing():
    return render_template('compression.html')


@server.route('/lam1_msg')
def tell_lam1_to_check_for_messages():
    # TODO: security on this?
    rpc_con.root.exposed_check_db_for_new_messages()

    return str('Checking for messages!')


def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@server.route('/shutdown', methods=['GET'])
def shutdown():
    lg.debug('Shutting down flask server.')
    server._shutdown_bool = True
    shutdown_server()
    return 'Server shutting down...'


@server.route('/restart', methods=['GET'])
def restart():
    lg.debug('Restarting flask server.')
    shutdown_server()
    return 'Server restarting, navigate to your desired page.'


if __name__ == "__main__":
    while not server._shutdown_bool:
        try:
            lg.debug('starting server')
            host = '0.0.0.0'
            port = 5000
            # server.run(host=host)
            waitress.serve(server, host=host, port=port, threads=1)
        except:
            lg.error(format_exc())
