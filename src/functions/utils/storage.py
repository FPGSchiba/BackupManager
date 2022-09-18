import glob
import json
import os

from src.functions.utils.config import Config

CONF = Config()


def get_all_configurations():
    files = glob.glob(CONF.jobs.configs)
    configs = []
    for file in files:
        with open(file, "r+", encoding="UTF-8") as f:
            name = os.path.basename(file).replace('.json', '')
            content = json.load(f)
            config = {
                f"{name}": content
            }
            configs.append(config)
    return configs


def update_configuration(config: str, new_content: dict):
    file = CONF.jobs.configs.replace('*', config)
    if os.path.isfile(file):
        with open(file, "w+", encoding='UTF-8') as w_file:
            json.dump(new_content, w_file)
        return True
    else:
        return False


def create_config(config: dict):
    name = list(config.keys())[0]
    file = CONF.jobs.configs.replace('*', name)
    if os.path.isfile(file):
        return False
    with open(file, "w+", encoding='UTF-8') as w_file:
        json.dump(config[name], w_file)
    return True


def config_exists(config: str):
    files = glob.glob(CONF.jobs.configs)
    for file in files:
        name = os.path.basename(file).replace('.json', '')
        if name == config:
            return True
    return False


def delete_config(name: str):
    file = CONF.jobs.configs.replace('*', name)
    if not os.path.isfile(file):
        return False
    os.remove(file)
    return True


if __name__ == '__main__':
    delete_config("minas-tirith-2")
