import os

import yaml
from dotenv import load_dotenv

load_dotenv(override=True)

_config = None


class ConfigLoader:
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
        with open(config_path, "r") as f:
            self._config = yaml.safe_load(f)

        self._env_mapping = {
            "groq_api_key": "GROQ_API_KEY",
            "model_name": "MODEL_NAME",
            "model_provider": "MODEL_PROVIDER",
        }

    def get(self, key, default=None):
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value

    def get_env(self, key, default=None):
        env_key = self._env_mapping.get(key, key.upper())
        return os.getenv(env_key, default)


def get_config():
    global _config
    if _config is None:
        _config = ConfigLoader()
    return _config
