from typing import List, Dict, Any


def process_article_data(viewer, title: str, article_data: List[Dict[str, Any]]):
    """
    Processes article data and renders it in the provided viewer.
    Decouples parsing logic from the ArticleViewer UI class.
    """
    viewer.title_var.set(title)
    viewer.clear()
    viewer.text_area.configure(state="normal")

    for block in article_data:
        block_type = block.get("type")
        content = block.get("content", "")

        if block_type == "header":
            viewer.text_area.insert("end", content + "\n", "header")
        elif block_type == "subheader":
            viewer.text_area.insert("end", content + "\n", "subheader")
        elif block_type == "paragraph":
            viewer.text_area.insert("end", content + "\n", "paragraph")
        elif block_type == "image":
            viewer._add_image(content, block)
        elif block_type == "video":
            viewer._add_video(content, block)
        elif block_type == "link":
            target = block.get("target", "")
            viewer._add_link(content, target)
        elif block_type == "separator":
            viewer.text_area.insert("end", "\n" + "-" * 40 + "\n\n", "center")

    viewer.text_area.configure(state="disabled")
