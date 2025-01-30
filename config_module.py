import json
import logging

class Config:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.base_url = None
        self.token = None
        self._load_config()

    def _load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.base_url = config.get('base_url', '').rstrip('/')
                self.token = config.get('token', '')
            if not self.base_url or not self.token:
                raise ValueError("Configuration file is missing 'base_url' or 'token'.")

            logging.info(f"Config loaded: base_url={self.base_url}")
        except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
            logging.error(f"Error loading configuration: {e}")
            raise
