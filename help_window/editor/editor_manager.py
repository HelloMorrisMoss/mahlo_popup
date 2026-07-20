import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

from .article_editor import ArticleEditor
from .file_manager import rename_resource, delete_resource, upload_media, move_resource


class EditorManager(tk.Toplevel):
    """
    Main entry point for help content editing.
    Allows browsing files and folders, renaming them, and launching the ArticleEditor.
    """

    def __init__(self, parent, content_manager, live_viewer=None):
        super().__init__(parent)
        self.title("Help Content Editor")
        self.geometry("400x600")

        self.parent = parent
        self.content_manager = content_manager
        self.live_viewer = live_viewer
        self.project_root = os.getcwd()

        self._setup_ui()
        self._refresh_tree()

    def _setup_ui(self):
        toolbar = ttk.Frame(self, padding=5)
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="New Article", command=self._new_article).pack(side="left", padx=2)
        ttk.Button(toolbar, text="New Folder", command=self._new_folder).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Import Media", command=self._import_media).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Refresh", command=self._refresh_tree).pack(side="left", padx=2)

        self.tree = ttk.Treeview(self)
        self.tree.pack(fill="both", expand=True)
        self.tree.heading("#0", text="Help Content", anchor="w")

        self.tree.bind("<Double-1>", self._on_double_click)

        # Context menu
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Edit", command=self._edit_selected)
        self.menu.add_command(label="Rename", command=self._rename_selected)
        self.menu.add_command(label="Move to Folder", command=self._move_selected)
        self.menu.add_separator()
        self.menu.add_command(label="Delete", command=self._delete_selected)

        self.tree.bind("<Button-3>", self._show_menu)

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        content_dir = self.content_manager.content_dir
        self._populate_tree("", content_dir)

    def _populate_tree(self, parent_node, path):
        for item in sorted(os.listdir(path)):
            abs_path = os.path.join(path, item)
            is_dir = os.path.isdir(abs_path)

            node = self.tree.insert(parent_node, "end", text=item,
                                    values=(abs_path,), open=False)

            if is_dir:
                self._populate_tree(node, abs_path)

    def _show_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)

    def _edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            return

        abs_path = self.tree.item(selected[0])["values"][0]
        if os.path.isfile(abs_path) and abs_path.endswith(".json"):
            self._open_editor(abs_path)
        else:
            messagebox.showinfo("Info", "Please select a JSON article to edit.")

    def _on_double_click(self, event):
        self._edit_selected()

    def _open_editor(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            title = "Untitled"
            for block in data:
                if block.get("type") == "header":
                    title = block.get("content", "Untitled")
                    break

            editor = ArticleEditor(self, data, title, file_path,
                                   on_save=self._on_article_saved,
                                   live_viewer=self.live_viewer)
            editor.grab_set()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open editor: {e}")

    def _on_article_saved(self, file_path, data):
        self._refresh_tree()
        if hasattr(self.parent, 'refresh_list'):
            self.parent.refresh_list()

    def _new_article(self):
        selected = self.tree.selection()
        if selected:
            base_path = self.tree.item(selected[0])["values"][0]
            if os.path.isfile(base_path):
                base_path = os.path.dirname(base_path)
        else:
            base_path = self.content_manager.content_dir

        name = simpledialog.askstring("New Article", "Enter article name (without .json):")
        if name:
            file_path = os.path.join(base_path, f"{name}.json")
            if os.path.exists(file_path):
                messagebox.showerror("Error", "File already exists.")
                return

            initial_data = [{"type": "header", "content": name}]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=4)

            self._refresh_tree()
            self._open_editor(file_path)

    def _new_folder(self):
        selected = self.tree.selection()
        if selected:
            base_path = self.tree.item(selected[0])["values"][0]
            if os.path.isfile(base_path):
                base_path = os.path.dirname(base_path)
        else:
            base_path = self.content_manager.content_dir

        name = simpledialog.askstring("New Folder", "Enter folder name:")
        if name:
            path = os.path.join(base_path, name)
            os.makedirs(path, exist_ok=True)
            self._refresh_tree()

    def _import_media(self):
        selected = self.tree.selection()
        if selected:
            dest_context = self.tree.item(selected[0])["values"][0]
        else:
            dest_context = self.content_manager.content_dir

        file_paths = filedialog.askopenfilenames(title="Select Media Files to Import")
        if file_paths:
            for fp in file_paths:
                try:
                    upload_media(self.project_root, dest_context, fp)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not import {os.path.basename(fp)}: {e}")
            self._refresh_tree()

    def _rename_selected(self):
        selected = self.tree.selection()
        if not selected:
            return

        abs_path = self.tree.item(selected[0])["values"][0]
        old_name = os.path.basename(abs_path)

        new_name = simpledialog.askstring("Rename", f"Enter new name for '{old_name}':", initialvalue=old_name)
        if new_name and new_name != old_name:
            try:
                rename_resource(self.project_root, abs_path, new_name)
                self._refresh_tree()
                if hasattr(self.parent, 'refresh_list'):
                    self.parent.refresh_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename: {e}")

    def _move_selected(self):
        selected = self.tree.selection()
        if not selected:
            return

        abs_path = self.tree.item(selected[0])["values"][0]
        content_dir = self.content_manager.content_dir

        # Get all folders in help_content
        folders = []
        for root, dirs, files in os.walk(content_dir):
            folders.append(root)

        if not folders:
            return

        # Create a simple selection dialog
        move_win = tk.Toplevel(self)
        move_win.title("Move to Folder")
        move_win.geometry("400x300")
        move_win.grab_set()

        ttk.Label(move_win, text=f"Select target folder for '{os.path.basename(abs_path)}':", padding=10).pack()

        lb = tk.Listbox(move_win)
        lb.pack(fill="both", expand=True, padx=10, pady=5)

        # Sort folders for better UX
        folders.sort()

        for f in folders:
            rel = os.path.relpath(f, content_dir)
            if rel == ".":
                rel = "(root)"
            lb.insert("end", rel)

        def do_move():
            idx = lb.curselection()
            if not idx:
                return

            target_folder = folders[idx[0]]
            if os.path.abspath(target_folder) == os.path.abspath(os.path.dirname(abs_path)):
                move_win.destroy()
                return

            try:
                move_resource(self.project_root, abs_path, target_folder)
                self._refresh_tree()
                if hasattr(self.parent, 'refresh_list'):
                    self.parent.refresh_list()
                move_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not move: {e}")

        ttk.Button(move_win, text="Move", command=do_move).pack(pady=10)

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return

        abs_path = self.tree.item(selected[0])["values"][0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{os.path.basename(abs_path)}'?"):
            try:
                delete_resource(self.project_root, abs_path)
                self._refresh_tree()
                if hasattr(self.parent, 'refresh_list'):
                    self.parent.refresh_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete: {e}")
