import yaml, os
import asyncio

class YamlFile:
    """ Singleton class to handle reading and writing YAML files. """
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(YamlFile, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.yaml_folder = "./yaml/"
        self._cached_data = {}
        self._last_modified_times = {}
        if not os.path.exists(self.yaml_folder):
            os.makedirs(self.yaml_folder)
        self._initialized = True

    async def get(self, file_name: str):
        """ Retrieve and cache the contents of a YAML file. """
        file_path = os.path.join(self.yaml_folder, f"{file_name}.yaml")
        if not os.path.exists(file_path):
            return None

        current_mod_time = os.path.getmtime(file_path)
        if (file_name not in self._cached_data or self._last_modified_times.get(file_name) != current_mod_time):
            with open(file_path, "r") as config_file:
                self._cached_data[file_name] = yaml.safe_load(config_file)
                self._last_modified_times[file_name] = current_mod_time
        return self._cached_data.get(file_name)

    async def dump(self, file_name: str, data: dict):
        """ Write data to a YAML file and update the cache. """
        file_path = os.path.join(self.yaml_folder, f"{file_name}.yaml")
        with open(file_path, "w") as config_file:
            yaml.dump(data, config_file)
        # Update cache and modification time after writing
        self._cached_data[file_name] = data
        self._last_modified_times[file_name] = os.path.getmtime(file_path)


# Global singleton instance
yaml_instance = YamlFile()
# Variables to store the server data
server_id = None
id_map = None

async def __load_server_ids():
    global server_id, id_map
    id_map = await yaml_instance.get("id_map")
    if id_map:
        server_id = id_map.get("server")
asyncio.run(__load_server_ids())
