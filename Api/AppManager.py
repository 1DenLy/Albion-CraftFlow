import os
import json


class AppManager:
    def __init__(self, app_name="MyApp"):
        self.app_name = app_name
        self.base_dir = os.path.expanduser(f"~/.{app_name}")
        self.config_file = os.path.join(self.base_dir, "config.json")
        self.user_data_dir = os.path.join(self.base_dir, "users")
        self._initialize_directories()
        
    def _initialize_directories(self):
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.user_data_dir, exist_ok=True)

    def load_config(self):
        """Loads the application configuration."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self, config):
        """Saves the application configuration with backup."""
        backup_file = self.config_file + ".bak"

        # Create a backup if the file exists
        if os.path.exists(self.config_file):
            os.rename(self.config_file, backup_file)

        try:
            # Attempt to save the new file
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            # Restore from backup if an error occurs
            if os.path.exists(backup_file):
                os.rename(backup_file, self.config_file)
            raise e
        else:
            # Remove the backup if successful
            if os.path.exists(backup_file):
                os.remove(backup_file)

    def reset_config(self, default_config):
        """Resets the configuration to default settings."""
        self.save_config(default_config)

    def list_users(self):
        """Lists all users based on their directories."""
        return [f for f in os.listdir(self.user_data_dir) if os.path.isdir(os.path.join(self.user_data_dir, f))]



