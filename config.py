"""Persistent config storage for provider settings.

Saves/loads ProviderConfig as JSON to ~/.prode_config.json.
API keys are stored locally — never committed to git.
"""

import json
import logging
from pathlib import Path
from dataclasses import asdict

logger = logging.getLogger(__name__)

from researcher import ProviderConfig

CONFIG_PATH = Path.home() / ".prode_config.json"


def load_config() -> ProviderConfig | None:
    """Load saved provider config. Returns None if no config exists."""
    if not CONFIG_PATH.exists():
        return None
    try:
        data = json.loads(CONFIG_PATH.read_text())
        return ProviderConfig(
            provider=data["provider"],
            model=data.get("model", ""),
            api_key=data.get("api_key"),
            base_url=data.get("base_url"),
        )
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("Config file corrupted, resetting: %s", exc)
        return None


def save_config(config: ProviderConfig) -> None:
    """Persist provider config to disk."""
    if not isinstance(config, ProviderConfig):
        raise TypeError("config must be ProviderConfig")
    CONFIG_PATH.write_text(json.dumps(asdict(config), indent=2))


def delete_config() -> None:
    """Remove saved config."""
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()
