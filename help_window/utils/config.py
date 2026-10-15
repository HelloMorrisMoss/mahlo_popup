from typing import Dict, Any

# Global override for role
_role_override = None


def set_role_override(role: str):
    """Sets a global override for the instance role."""
    global _role_override
    if role in ("server", "subscriber"):
        _role_override = role


def get_settings() -> Dict[str, Any]:
    """Loads settings from untracked_config/settings.json."""
    try:
        from untracked_config.configuration_data import help_server_settings
        settings = help_server_settings.copy()
        if _role_override:
            settings["role"] = _role_override
        return settings
    except Exception:
        return {"role": _role_override} if _role_override else {}


def get_role() -> str:
    """Returns the role of the current instance ('server' or 'subscriber')."""
    return get_settings().get("role", "subscriber")


def is_server() -> bool:
    """Returns True if the current instance is a server."""
    return get_role() == "server"
