import glob
import importlib.util
import json
import os
import time

import schedule
import threading

from src.utils.config import Config

CONF = Config()


def load_module(location: str, path: str):
    """
    Loads a Module
    :param location: The Location of the Module
    :param path: The Path where the file is
    :return: the loaded and executed module
    """
    spec = importlib.util.spec_from_file_location(location, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_all_configs():
    files = glob.glob(CONF.jobs.configs)
    configs = []
    for file in files:
        with open(file, "r+", encoding="UTF-8") as f:
            configs.append(json.load(f))
    return configs


def get_file_path(job_type: str):
    root_file = os.path.sep.join(__file__.split(os.path.sep)[0:-1])
    return os.path.join(root_file, "jobs", f"{job_type}.py")


class Scheduler(threading.Thread):
    def __init__(self):
        super(Scheduler, self).__init__()
        self.running = True
        self.configs = []
        self.get_all_schedules()

    def get_all_schedules(self):
        self.configs = get_all_configs()
        for config in self.configs:
            job_config = config['job-config']
            job_type = job_config["type"]
            file = get_file_path(job_type)
            module = load_module(f'.jobs.{job_type}', file)
            func = getattr(module, 'start_download')
            job_interval = str(config["schedule"]["interval"])
            job_every = int(config["schedule"]["every"])
            if job_interval == "second":
                schedule.every(job_every).seconds.do(func, job_config=job_config)
            elif job_interval == "minute":
                schedule.every(job_every).minutes.do(func, job_config=job_config)
            elif job_interval == "hour":
                schedule.every(job_every).hours.do(func, job_config=job_config)
            elif job_interval == "day":
                schedule.every(job_every).days.do(func, job_config=job_config)
            elif job_interval == "week":
                schedule.every(job_every).weeks.do(func, job_config=job_config)
            else:
                raise KeyError(f"Job config: {job_config['name']} schedule is not well defined.")

    def run(self):
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def stop(self):
        schedule.clear()
        self.running = False

    def reload(self):
        schedule.clear()
        self.get_all_schedules()


if __name__ == '__main__':
    sched = Scheduler()
    sched.start()
