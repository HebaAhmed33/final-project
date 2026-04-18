"""
Configuration Analysis Input Mapper.
Normalizes raw configuration data into a standard boolean dictionary.
"""

# Mapping from raw config keys to normalized output keys
_KEY_MAP = {
    "firewall_rules_defined": "firewall_rules_defined",
    "logging_enabled": "logging_enabled",
    "backup_configured": "backup_configured",
    "network_segmentation_enabled": "network_segmentation_enabled",
    "remote_access_restricted": "remote_access_restricted",
}

# All normalized keys with their defaults
_DEFAULTS = {key: False for key in _KEY_MAP.values()}


def map_config_input(raw_config_data: dict) -> dict:
    """
    Normalize raw configuration data into a standard boolean dictionary.

    Parameters
    ----------
    raw_config_data : dict
        Raw key-value pairs from a configuration source.

    Returns
    -------
    dict
        Normalized dictionary with all expected keys, defaulting to False
        for any missing entries.
    """
    result = dict(_DEFAULTS)
    for raw_key, normalized_key in _KEY_MAP.items():
        if raw_key in raw_config_data:
            result[normalized_key] = bool(raw_config_data[raw_key])
    return result


if __name__ == "__main__":
    import json

    sample = {
        "firewall_rules_defined": True,
        "logging_enabled": False,
        "backup_configured": True,
    }
    print(json.dumps(map_config_input(sample), indent=2))
