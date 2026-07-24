import json
import os

from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from help_window.editor.file_manager import upload_media, delete_resource, rename_resource, move_resource, \
    consolidate_article_media
from untracked_config.configuration_data import help_api_port


def start_flask_server(app_instance):
    """Starts a minimal Flask server to handle cross-process signaling and web editor."""
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    flask_app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    def to_abs(path):
        if not path:
            return path
        if os.path.isabs(path):
            return path
        return os.path.abspath(os.path.join(project_root, path))

    def to_rel(path):
        if not path:
            return path
        try:
            return os.path.relpath(path, project_root).replace("\\", "/")
        except ValueError:
            return path.replace("\\", "/")

    @flask_app.route('/bring_to_front', methods=['GET'])
    def signal_bring_to_front():
        # Use after() to ensure thread-safe interaction with Tkinter
        app_instance.after(0, app_instance.bring_to_front)
        return jsonify({"status": "success", "message": "Help window signaled to bring to front."})

    @flask_app.route('/editor')
    def web_editor():
        return render_template('web_editor.html')

    @flask_app.route('/api/articles')
    def get_articles():
        articles = app_instance.content_manager.scan_content(force=True)
        # Convert absolute paths to something relative or just names for the web
        web_articles = []
        for a in articles:
            web_articles.append({
                "title": a["title"],
                "section": a["section"],
                "file_path": to_rel(a["file_path"]),
                "is_broken": a["is_broken"]
            })
        return jsonify(web_articles)

    @flask_app.route('/api/structure')
    def get_structure():
        content_dir = app_instance.content_manager.content_dir

        def build_tree(current_dir):
            node = {
                "name": os.path.basename(current_dir) or "Root",
                "path": to_rel(current_dir),
                "type": "folder",
                "is_media": os.path.basename(current_dir) == "media",
                "children": []
            }

            if node["is_media"]:
                node["item_count"] = len(
                    [f for f in os.listdir(current_dir) if os.path.isfile(os.path.join(current_dir, f))])

            try:
                for entry in os.scandir(current_dir):
                    if entry.is_dir():
                        node["children"].append(build_tree(entry.path))
                    elif entry.is_file() and entry.name.endswith(".json"):
                        # Get title from ContentManager if possible
                        article = next(
                            (a for a in app_instance.content_manager.articles if a["file_path"] == entry.path), None)
                        title = article["title"] if article else entry.name
                        node["children"].append({
                            "name": title,
                            "path": entry.path,
                            "type": "article",
                            "is_broken": article["is_broken"] if article else False
                        })
            except Exception as e:
                print(f"Error building tree for {current_dir}: {e}")

            return node

        # Ensure scan_content is up to date
        app_instance.content_manager.scan_content(force=True)
        tree = build_tree(content_dir)
        return jsonify(tree)

    @flask_app.route('/api/create_folder', methods=['POST'])
    def create_folder():
        data = request.json
        parent_path = to_abs(data.get('parent_path'))
        name = data.get('name')
        if not parent_path or not name:
            return jsonify({"error": "Parent path and name required"}), 400

        new_dir = os.path.join(parent_path, name)
        try:
            os.makedirs(new_dir, exist_ok=True)
            return jsonify({"status": "success", "path": to_rel(new_dir)})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @flask_app.route('/api/move', methods=['POST'])
    def web_move_resource():
        data = request.json
        old_path = to_abs(data.get('old_path'))
        new_parent = to_abs(data.get('new_parent'))
        if not old_path or not new_parent:
            return jsonify({"error": "Old path and new parent required"}), 400

        try:
            new_path = move_resource(project_root, old_path, new_parent)
            return jsonify({"status": "success", "new_path": to_rel(new_path)})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @flask_app.route('/api/rename', methods=['POST'])
    def web_rename_resource():
        data = request.json
        path = to_abs(data.get('path'))
        new_name = data.get('new_name')
        if not path or not new_name:
            return jsonify({"error": "Path and new name required"}), 400

        try:
            new_path = rename_resource(project_root, path, new_name)
            return jsonify({"status": "success", "new_path": to_rel(new_path)})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @flask_app.route('/api/delete', methods=['POST'])
    def web_delete_resource():
        data = request.json
        path = to_abs(data.get('path'))
        if not path:
            return jsonify({"error": "Path required"}), 400

        try:
            delete_resource(project_root, path)
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @flask_app.route('/api/consolidate', methods=['POST'])
    def web_consolidate():
        data = request.json
        path = to_abs(data.get('path'))
        article_content = data.get('content')
        if not path or article_content is None:
            return jsonify({"error": "Path and content required"}), 400

        try:
            new_content, changed = consolidate_article_media(project_root, path, article_content)
            return jsonify({"status": "success", "content": new_content, "changed": changed})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @flask_app.route('/api/media_list')
    def get_media_list():
        path = to_abs(request.args.get('path'))
        if not path or not os.path.isdir(path):
            return jsonify({"error": "Valid directory path required"}), 400

        files = []
        for f in os.scandir(path):
            if f.is_file():
                # We need a relative path for the preview
                content_dir = app_instance.content_manager.content_dir
                rel_path = os.path.relpath(f.path, content_dir).replace("\\", "/")
                files.append({
                    "name": f.name,
                    "rel_path": rel_path,
                    "url": f"/media/{rel_path}"
                })
        return jsonify(files)

    @flask_app.route('/api/article', methods=['GET'])
    def get_article_content():
        file_path = to_abs(request.args.get('path'))
        if not file_path or not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
        content = app_instance.content_manager.load_article_content(file_path)
        return jsonify(content)

    @flask_app.route('/api/article', methods=['POST'])
    def save_article():
        data = request.json
        file_path = to_abs(data.get('path'))
        content = data.get('content')
        if not file_path or content is None:
            return jsonify({"error": "Invalid data"}), 400

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=4)
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @flask_app.route('/api/create_article', methods=['POST'])
    def create_article():
        data = request.json
        title = data.get('title')
        section = data.get('section', "")

        if not title:
            return jsonify({"error": "Title required"}), 400

        # Determine filename
        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')]).strip().replace(' ', '_')
        filename = f"{safe_title}.json"

        content_dir = app_instance.content_manager.content_dir
        section_dir = os.path.join(content_dir, section)
        os.makedirs(section_dir, exist_ok=True)

        file_path = os.path.join(section_dir, filename)
        if os.path.exists(file_path):
            return jsonify({"error": "Article already exists"}), 409

        initial_content = [
            {"type": "title", "content": title},
            {"type": "paragraph", "content": "Start writing your article here..."}
        ]

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(initial_content, f, indent=4)
            return jsonify({"status": "success", "file_path": to_rel(file_path)})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @flask_app.route('/api/upload_media', methods=['POST'])
    def web_upload_media():
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        article_path = to_abs(request.form.get('article_path'))
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file:
            filename = secure_filename(file.filename)
            # We need a temp location to save the uploaded file before moving it via file_manager
            temp_path = os.path.join(os.path.dirname(__file__), "static", filename)
            file.save(temp_path)

            rel_path = upload_media(project_root, article_path, temp_path)

            # Remove temp file
            os.remove(temp_path)

            return jsonify({"status": "success", "path": rel_path})

    # Serve media files
    @flask_app.route('/media/<path:filename>')
    def serve_media(filename):
        # Media can be in various places, but usually under help_content
        content_dir = app_instance.content_manager.content_dir
        return send_from_directory(content_dir, filename)

    # Run on a dedicated port for the help system
    flask_app.run(host='0.0.0.0', port=help_api_port, debug=False, use_reloader=False)
