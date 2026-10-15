import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Dict, Any, Callable

from .file_manager import upload_media, consolidate_article_media


class ArticleEditor(tk.Toplevel):
    """
    A WYSIWYG-ish editor for help articles.
    Provides controls to add, remove, and reorder blocks.
    Updates a live viewer if provided.
    """

    def __init__(self, parent, initial_data: List[Dict[str, Any]], title: str,
                 file_path: str, on_save: Callable[[str, List[Dict[str, Any]]], None],
                 live_viewer=None):
        super().__init__(parent)
        self.title(f"Editing Article: {title}")
        self.geometry("600x800")

        self.initial_data = initial_data
        self.blocks = list(initial_data)
        self.article_title = title
        self.file_path = file_path

        # Ensure mandatory title block at the start
        self._ensure_title_block()

        self.on_save = on_save
        self.live_viewer = live_viewer

        self.selected_index = -1

        self._setup_ui()
        self._refresh_block_list()

    def _ensure_title_block(self):
        """Enforces that the first block is a title block."""
        if not self.blocks:
            self.blocks.append({"type": "title", "content": self.article_title})
            return

        # Check if first block is title
        if self.blocks[0].get("type") == "title":
            return

        # Check if title exists elsewhere and move it to front
        title_idx = -1
        for i, block in enumerate(self.blocks):
            if block.get("type") == "title":
                title_idx = i
                break

        if title_idx != -1:
            title_block = self.blocks.pop(title_idx)
            self.blocks.insert(0, title_block)
        else:
            # Try to convert first header to title
            header_idx = -1
            for i, block in enumerate(self.blocks):
                if block.get("type") == "header":
                    header_idx = i
                    break

            if header_idx != -1:
                header_block = self.blocks.pop(header_idx)
                header_block["type"] = "title"
                self.blocks.insert(0, header_block)
            else:
                # Add a title block at the start
                self.blocks.insert(0, {"type": "title", "content": self.article_title})

    def _setup_ui(self):
        # Top toolbar
        toolbar = ttk.Frame(self, padding=5)
        toolbar.pack(fill="x")

        ttk.Button(toolbar, text="Save", command=self._save).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Cancel", command=self.destroy).pack(side="left", padx=5)
        ttk.Button(toolbar, text="Consolidate Media", command=self._consolidate).pack(side="right", padx=5)

        # Main content area (split into list and properties)
        paned = ttk.PanedWindow(self, orient="vertical")
        paned.pack(fill="both", expand=True)

        # Block List Frame
        list_frame = ttk.LabelFrame(paned, text="Blocks", padding=5)
        paned.add(list_frame, weight=1)

        self.block_listbox = tk.Listbox(list_frame, exportselection=False)
        self.block_listbox.pack(side="left", fill="both", expand=True)
        self.block_listbox.bind("<<ListboxSelect>>", self._on_block_select)

        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.block_listbox.yview)
        scroll.pack(side="right", fill="y")
        self.block_listbox.config(yscrollcommand=scroll.set)

        # List Controls
        list_controls = ttk.Frame(list_frame)
        list_controls.pack(side="bottom", fill="x")

        ttk.Button(list_controls, text="Up", width=5, command=self._move_up).pack(side="left", padx=2)
        ttk.Button(list_controls, text="Down", width=5, command=self._move_down).pack(side="left", padx=2)
        ttk.Button(list_controls, text="Remove", width=8, command=self._remove_block).pack(side="right", padx=2)

        # Block Properties Frame
        self.prop_frame = ttk.LabelFrame(paned, text="Block Properties", padding=10)
        paned.add(self.prop_frame, weight=1)

        # Add Block Buttons
        add_frame = ttk.LabelFrame(self, text="Add Block", padding=5)
        add_frame.pack(fill="x")

        types = ["title", "header", "subheader", "paragraph", "image", "video", "link", "separator"]
        for t in types:
            btn = ttk.Button(add_frame, text=t.capitalize(), command=lambda bt=t: self._add_block(bt))
            btn.pack(side="left", padx=2)

    def _refresh_block_list(self):
        self.block_listbox.delete(0, tk.END)
        for i, block in enumerate(self.blocks):
            b_type = block.get("type", "unknown")
            content = block.get("content", "")
            # Truncate content for display
            display_text = f"{i + 1}: [{b_type}] {content[:50]}"
            self.block_listbox.insert(tk.END, display_text)

        if self.live_viewer:
            self.live_viewer.load_article(self.article_title, self.blocks)

    def _on_block_select(self, event):
        selection = self.block_listbox.curselection()
        if not selection:
            return

        self.selected_index = selection[0]
        self._show_properties(self.blocks[self.selected_index])

    def _show_properties(self, block):
        # Clear prop_frame
        for widget in self.prop_frame.winfo_children():
            widget.destroy()

        b_type = block.get("type")

        ttk.Label(self.prop_frame, text=f"Type: {b_type}").pack(anchor="w")

        if b_type in ["title", "header", "subheader", "paragraph", "image", "video", "link"]:
            ttk.Label(self.prop_frame, text="Content:").pack(anchor="w")

            if b_type == "paragraph":
                text_widget = tk.Text(self.prop_frame, height=5, width=40)
                text_widget.insert("1.0", block.get("content", ""))
                text_widget.pack(fill="x", pady=5)
                text_widget.bind("<KeyRelease>", lambda e: self._update_block_content(text_widget.get("1.0", "end-1c")))
            else:
                entry_var = tk.StringVar(value=block.get("content", ""))
                entry = ttk.Entry(self.prop_frame, textvariable=entry_var)
                entry.pack(fill="x", pady=5)
                entry_var.trace_add("write", lambda *args: self._update_block_content(entry_var.get()))

                if b_type in ["image", "video"]:
                    ttk.Button(self.prop_frame, text="Browse...",
                               command=lambda: self._browse_file(entry_var)).pack(anchor="e")

        if b_type == "link":
            ttk.Label(self.prop_frame, text="Target (Article path):").pack(anchor="w")
            target_var = tk.StringVar(value=block.get("target", ""))
            target_entry = ttk.Entry(self.prop_frame, textvariable=target_var)
            target_entry.pack(fill="x", pady=5)
            target_var.trace_add("write", lambda *args: self._update_block_target(target_var.get()))

            ttk.Button(self.prop_frame, text="Browse Articles...",
                       command=lambda: self._browse_article(target_var)).pack(anchor="e")

        if b_type in ["image", "video"]:
            ttk.Label(self.prop_frame, text="Metadata (Size, etc.):").pack(anchor="w")
            # For simplicity, let's just use a string for now or specific fields
            size_var = tk.StringVar(value=block.get("size", ""))
            size_combo = ttk.Combobox(self.prop_frame, textvariable=size_var,
                                      values=["thumbnail", "small", "medium", "large", "fill"])
            size_combo.pack(fill="x", pady=5)
            size_var.trace_add("write", lambda *args: self._update_block_meta("size", size_var.get()))

    def _update_block_content(self, new_content):
        if self.selected_index != -1:
            self.blocks[self.selected_index]["content"] = new_content
            # Update listbox text without full refresh if possible, or just refresh
            self._refresh_preview()

    def _update_block_target(self, new_target):
        if self.selected_index != -1:
            self.blocks[self.selected_index]["target"] = new_target
            self._refresh_preview()

    def _update_block_meta(self, key, value):
        if self.selected_index != -1:
            self.blocks[self.selected_index][key] = value
            self._refresh_preview()

    def _refresh_preview(self):
        # Update listbox item
        idx = self.selected_index
        b_type = self.blocks[idx].get("type", "unknown")
        content = self.blocks[idx].get("content", "")
        self.block_listbox.delete(idx)
        self.block_listbox.insert(idx, f"{idx + 1}: [{b_type}] {content[:50]}")
        self.block_listbox.selection_set(idx)

        if self.live_viewer:
            self.live_viewer.load_article(self.article_title, self.blocks)

    def _add_block(self, b_type):
        if b_type == "title":
            if any(b.get("type") == "title" for b in self.blocks):
                messagebox.showwarning("Warning", "Article already has a title block.")
                return
            new_block = {"type": "title", "content": "New Title"}
            self.blocks.insert(0, new_block)
            idx = 0
        else:
            new_block = {"type": b_type, "content": f"New {b_type}"}
            if b_type == "link":
                new_block["target"] = ""
            self.blocks.append(new_block)
            idx = len(self.blocks) - 1

        self._refresh_block_list()
        self.block_listbox.selection_clear(0, tk.END)
        self.block_listbox.selection_set(idx)
        self.block_listbox.see(idx)
        self._on_block_select(None)

    def _remove_block(self):
        if self.selected_index != -1:
            if self.blocks[self.selected_index].get("type") == "title":
                messagebox.showwarning("Warning", "The title block cannot be removed.")
                return
            del self.blocks[self.selected_index]
            self.selected_index = -1
            self._refresh_block_list()
            for widget in self.prop_frame.winfo_children():
                widget.destroy()

    def _move_up(self):
        idx = self.selected_index
        if idx > 0:
            # Prevent moving something above the title block, or moving title block down
            if idx == 1 and self.blocks[0].get("type") == "title":
                return
            
            self.blocks[idx], self.blocks[idx - 1] = self.blocks[idx - 1], self.blocks[idx]
            self._refresh_block_list()
            self.block_listbox.selection_set(idx - 1)
            self.selected_index = idx - 1

    def _move_down(self):
        idx = self.selected_index
        if idx != -1 and idx < len(self.blocks) - 1:
            # Prevent moving title block down
            if idx == 0 and self.blocks[0].get("type") == "title":
                return

            self.blocks[idx], self.blocks[idx + 1] = self.blocks[idx + 1], self.blocks[idx]
            self._refresh_block_list()
            self.block_listbox.selection_set(idx + 1)
            self.selected_index = idx + 1

    def _browse_file(self, var):
        file_path = filedialog.askopenfilename(initialdir=os.getcwd())
        if file_path:
            try:
                # Always upload media to ensure it's in the correct project structure
                project_root = os.getcwd()
                rel_path = upload_media(project_root, self.file_path, file_path)
                var.set(rel_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not upload media: {e}")
                # Fallback to just setting the path if upload fails
                try:
                    rel_path = os.path.relpath(file_path, os.getcwd()).replace("\\", "/")
                    var.set(rel_path)
                except:
                    var.set(file_path)

    def _browse_article(self, var):
        # Look in help_window/help_content
        initial_dir = os.path.join(os.getcwd(), "help_window", "help_content")
        file_path = filedialog.askopenfilename(initialdir=initial_dir, filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                rel_path = os.path.relpath(file_path, os.getcwd())
                rel_path = rel_path.replace("\\", "/")
                var.set(rel_path)
            except ValueError:
                var.set(file_path)

    def _save(self):
        if not self.file_path:
            # New file - ask for location
            initial_dir = os.path.join(os.getcwd(), "help_window", "help_content")
            self.file_path = filedialog.asksaveasfilename(initialdir=initial_dir,
                                                          defaultextension=".json",
                                                          filetypes=[("JSON files", "*.json")])
            if not self.file_path:
                return

        try:
            # Update title from the first title block or header block if it exists
            found_title = False
            for block in self.blocks:
                if block.get("type") == "title":
                    self.article_title = block.get("content", "Untitled")
                    found_title = True
                    break

            if not found_title:
                for block in self.blocks:
                    if block.get("type") == "header":
                        self.article_title = block.get("content", "Untitled")
                        break

            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.blocks, f, indent=4)

            if self.on_save:
                self.on_save(self.file_path, self.blocks)

            messagebox.showinfo("Success", "Article saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save article: {e}")

    def _consolidate(self):
        if not self.file_path:
            messagebox.showinfo("Info", "Please save the article first to establish its location.")
            return

        if messagebox.askyesno("Consolidate Media",
                               "This will copy all referenced media files into this article's local media folder. Continue?"):
            try:
                project_root = os.getcwd()
                new_data, changed = consolidate_article_media(project_root, self.file_path, self.blocks)
                if changed:
                    self.blocks = new_data
                    self._refresh_block_list()
                    if self.selected_index != -1:
                        self._show_properties(self.blocks[self.selected_index])
                    messagebox.showinfo("Success", "Media consolidated successfully.")
                else:
                    messagebox.showinfo("Info", "All media is already consolidated.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not consolidate media: {e}")
