import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict

from const import CONFIG_PATH

USER_CONFIG_FILE = Path(CONFIG_PATH + "/user_config.json")
USER_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class UserConfig:
    ai_enabled: bool
    reminder_time: Optional[str]

    @classmethod
    def from_dict(cls, data: dict) -> "UserConfig":
        return cls(**data)

    def to_dict(self) -> dict:
        return asdict(self)


def load_all_configs() -> dict[int, UserConfig]:
    if not USER_CONFIG_FILE.exists():
        return {}

    try:
        raw = json.loads(USER_CONFIG_FILE.read_text())
    except json.JSONDecodeError:
        return {}

    result = {}

    for user_id_str, data in raw.items():
        result[int(user_id_str)] = UserConfig.from_dict(data)

    return result


def load_user_config(user_id: int) -> UserConfig:
    cfg = load_all_configs()
    return cfg.get(user_id)


def save_all_configs(cfg: dict):
    USER_CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


def save_user_config(user_id: int, config: UserConfig):
    """
    Save a single user's config.

    load_all_configs() returns: dict[int, UserConfig]
    save_all_configs() expects: dict[str, dict]  (serialisable)
    """
    # Load the in-memory map of UserConfig objects
    all_cfgs: Dict[int, UserConfig] = load_all_configs()

    # Convert existing objects to serialisable dicts with string keys
    serialisable = {uid: cfg_obj.to_dict() for uid, cfg_obj in all_cfgs.items()}

    # Insert/update this user's config (use the provided config dataclass)
    serialisable[user_id] = config.to_dict()

    # Persist to disk
    save_all_configs(serialisable)
