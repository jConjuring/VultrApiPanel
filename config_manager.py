import json
import os

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        """Load config file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                return {"api_key": ""}
        return {"api_key": ""}

    def save_config(self, api_key):
        """Save API key to config file."""
        self.config["api_key"] = api_key
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)

    def get_api_key(self):
        """Return stored API key."""
        return self.config.get("api_key", "")
