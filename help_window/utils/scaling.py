from typing import Dict, Any, Tuple


def calculate_dimensions(viewer_width: int, orig_w: int, orig_h: int, metadata: Dict[str, Any]) -> Tuple[int, int]:
    """
    Calculates target dimensions based on metadata and viewer width.
    Shared logic for images and videos.
    """
    target_w = None
    target_h = None

    # 1. Check size presets
    size_presets = {
        "thumbnail": 0.25,
        "small": 0.50,
        "medium": 0.75,
        "large": 0.90,
        "fill": 1.0
    }

    size = metadata.get("size")
    if size in size_presets:
        target_w = viewer_width * size_presets[size]

    # 2. Check width_pct
    width_pct = metadata.get("width_pct")
    if width_pct is not None:
        try:
            target_w = viewer_width * (float(width_pct) / 100.0)
        except (ValueError, TypeError):
            pass

    # 3. Check static width/height
    # Supports "1024x768" format or separate width/height keys
    static_size = metadata.get("width")
    if isinstance(static_size, str) and "x" in static_size:
        try:
            w, h = map(int, static_size.split("x"))
            target_w = w
            target_h = h
        except (ValueError, TypeError):
            pass
    elif metadata.get("width") and metadata.get("height"):
        try:
            target_w = int(metadata.get("width"))
            target_h = int(metadata.get("height"))
        except (ValueError, TypeError):
            pass

    # Default: use original size but capped at viewer width
    if target_w is None:
        target_w = orig_w

    # HLP-015: Responsive Scaling - MUST fit within viewer width
    if target_w > viewer_width:
        target_w = viewer_width

    # Maintain aspect ratio if height not explicitly set
    if target_h is None:
        # Avoid division by zero
        if orig_w > 0:
            ratio = target_w / orig_w
            target_h = orig_h * ratio
        else:
            target_h = orig_h

    return int(target_w), int(target_h)
