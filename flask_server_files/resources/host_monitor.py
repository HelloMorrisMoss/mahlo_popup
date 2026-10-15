from flask_restful import Resource

from flask_server_files.monitors.host_monitor import find_recent_pdf


class HostMonitor(Resource):
    def get(self):
        found_path = find_recent_pdf()

        if found_path:
            # Use forward slashes in the response path as per specification example
            return {"new_report_found": True, "new_report_path": found_path.replace('\\', '/')}, 200
        else:
            return {"new_report_found": False, "new_report_path": None}, 200
