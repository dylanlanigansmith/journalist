import json
import os



class Config:
    def __init__(self, filename='config.json', autoload=True):
        self.filename = filename
        self.config = None
        if autoload:
            self.load()  

    def ok(self):
        return self.config is not None
    
    def create_default(self):
        default_config = {
            'openapi_key': 'your_default_openai_api_key_here',
            'test_url': '',
            'test_prompt' : ''
        }
        with open(self.filename, 'w') as config_file:
            json.dump(default_config, config_file, indent=4)
        print(f"{self.filename} created with default values.")

    def load(self):
        if not os.path.exists(self.filename):
            print(f"{self.filename} not found. Creating default configuration.")
            self.create_default()
        
        with open(self.filename, 'r') as config_file:
            self.config = json.load(config_file)

    def __getitem__(self, key):
        if self.config is None:
            raise ValueError("Configuration not loaded.")
        return self.config.get(key, None)

    def __setitem__(self, key, value):
        if self.config is None:
            raise ValueError("Configuration not loaded.")
        self.config[key] = value
        # Optionally, you might want to save the updated configuration to file
        self.save()

    def save(self):
        """Save the current configuration to the file."""
        with open(self.filename, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)
    def dump(self):
        print("dumping config... \n")
        print(self.config)
        print("\n end config dump")

config = None


if __name__ == "__main__":
    print("testing config")
    config = Config()
    print("Config Ok = ", config.ok())
    config.dump()
