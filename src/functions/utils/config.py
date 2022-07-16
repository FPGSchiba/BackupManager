import yaml
import os


def get_data_dir():
    return os.path.join(f"{os.path.sep}".join(__file__.split(os.path.sep)[0:-4]), "data")


STR_DATA_DIR = "{data-dir}"
DATA_DIR = get_data_dir()
CONFIG_FILE = os.path.join(DATA_DIR, "config.yaml")


class Jobs:
    def __init__(self, data):
        self.directory = str(data['directory']).replace(STR_DATA_DIR, DATA_DIR)
        self.configs = str(data["configurations"]).replace(STR_DATA_DIR, DATA_DIR)


class FTP:
    def __init__(self, data):
        self.host = str(data["host"])
        self.port = int(data["port"])
        self.user = str(data["user"])
        self.password = str(data["password"])
        self.directory = str(data["directory"]).replace(STR_DATA_DIR, DATA_DIR)


class Config:
    def __init__(self):
        with open(CONFIG_FILE, "r+", encoding="UTF-8") as config_file:
            data = yaml.load(config_file, yaml.Loader)
        self.jobs = Jobs(data["jobs"])
        self.ftp = FTP(data["ftp"])
