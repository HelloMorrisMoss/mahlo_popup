from flask import Flask, jsonify

from untracked_config.configuration_data import help_api_port


def start_flask_server(app_instance):
    """Starts a minimal Flask server to handle cross-process signaling."""
    flask_app = Flask(__name__)

    @flask_app.route('/bring_to_front', methods=['GET'])
    def signal_bring_to_front():
        # Use after() to ensure thread-safe interaction with Tkinter
        app_instance.after(0, app_instance.bring_to_front)
        return jsonify({"status": "success", "message": "Help window signaled to bring to front."})

    # Run on a dedicated port for the help system
    flask_app.run(port=help_api_port, debug=False, use_reloader=False)
