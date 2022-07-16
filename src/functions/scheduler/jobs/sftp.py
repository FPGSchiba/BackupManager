import hashlib
import json
import os
import tarfile

import pysftp

from src.utils.config import Config
from src.utils.storage import get_backup_name, remove_old_folder

CONF = Config()


def compress_backup(folder: str, download_folder):
    compressed_file = os.path.join(folder, get_backup_name())
    with tarfile.open(compressed_file, "w:gz") as tar:
        tar.add(download_folder, arcname=os.path.basename(folder))
    remove_old_folder(download_folder)


def generate_checksums(local_paths: list, folder: str):
    checksum_file = os.path.join(folder, "checksums.json")
    data = {}
    for local_path in local_paths:
        checksum = hashlib.sha256(open(local_path, 'rb').read()).hexdigest()
        data[local_path] = checksum
    with open(checksum_file, "w+", encoding="UTF-8") as file:
        json.dump(data, file)


def get_local_path(file: str, folder: str) -> str:
    temps = file.split("/")
    file = file.split("/")[-1]
    temps = [temp for temp in temps if temp != '']
    if len(temps) == 1:
        return os.path.join(folder, file)
    else:
        folders = temps[0:-1]
        local_path = folder
        for local_folder in folders:
            local_path = os.path.join(local_path, local_folder)
            if not os.path.isdir(local_path):
                os.mkdir(local_path)
        return os.path.join(local_path, file)


def download_files(folder: str, files: list, connection: pysftp.Connection):
    if not os.path.isdir(folder):
        os.mkdir(folder)
    local_paths = []
    for file in files:
        remote_path = file
        local_path = get_local_path(file, folder)
        local_paths.append(local_path)
        connection.get(remote_path, local_path, preserve_mtime=True)
    generate_checksums(local_paths, folder)


def get_all_files(folder: str, connection: pysftp.Connection):
    connection.chdir(folder)
    remote_root = connection.getcwd()
    folder_found = False
    new_folders = []
    files = []
    for item in connection.listdir():
        if connection.isdir(item):
            new_folders.append(item)
            folder_found = True
        else:
            files.append(os.path.join(remote_root, item).replace("\\", "/"))
    if folder_found:
        for new_folder in new_folders:
            files += get_all_files(new_folder, connection)
            connection.chdir(remote_root)
    return files


def start_download(job_config: dict):
    if job_config['type'] != "sftp":
        return
    print(f'Running Backup Job: {job_config["name"]}')
    folder = CONF.jobs.directory.replace("{job-name}", job_config['name'])
    if not os.path.isdir(folder):
        os.mkdir(folder)
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    with pysftp.Connection(job_config['host'], username=job_config['username'], password=job_config['password'],
                           cnopts=cnopts, port=job_config['port']) as connection:
        remote_root = connection.getcwd()
        files = []
        folders = []
        for item in connection.listdir():
            if connection.isdir(item):
                folders.append(item)
            else:
                files.append(item)
        for remote_folder in folders:
            files += get_all_files(remote_folder, connection)
            connection.chdir(remote_root)
        download_folder = os.path.join(folder, "downloads")
        download_files(download_folder, files, connection)
        compress_backup(folder, download_folder)


if __name__ == '__main__':
    start_download({
        "type": "sftp",
        "name": "minas-tirith",
        "host": "192.168.1.40",
        "port": 5657,
        "username": "craftzockerlp@gmail.com|2c1ddcb3",
        "password": "Password1"
    })
