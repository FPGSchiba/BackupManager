import json
import threading

from flask import Flask, Response, request

from src.functions.scheduler.scheduler import Scheduler
from src.functions.ftp_server import main
from src.functions.utils.config import Config
from src.functions.utils.storage import get_all_configurations, config_exists, update_configuration, create_config, \
    delete_config

scheduler = Scheduler()
scheduler.start()

th = threading.Thread(target=main, daemon=True, name='FTP-Thread')
th.start()

CONF = Config()

app = Flask(__name__)


@app.route('/', methods=['GET'])
def version():
    """
    Gets the Version of the Intent-Detection Module (Test)
    :return: A Response with the current Version of the Intent-Detection API
    """
    return "<h1>BackupManager: V0.1</h1>"


@app.route('/backups/get/', methods=['GET'])
def get_all_backup_configs():
    """
    Gets all configurations saved and used by the system.
    :return: A Flask response with all Configurations
    """
    return Response(json.dumps(get_all_configurations()), status=200)


@app.route('/backups/update/<name>', methods=['POST'])
def update_named_job(name: str):
    """
    Updates a Configuration with the name in the url and with the contents given in the body
    :param name: the name of the configuration to update
    :return:  A Flask response with a success or error message depending on the execution
    """
    if config_exists(name):
        new_config = request.json
        if update_configuration(name, new_config):
            scheduler.reload()
            return Response(json.dumps({'message': f'Updated Config for {name}'}), status=200)
        else:
            return Response(json.dumps({'message': f'Could not update Config, please try again later.'}), status=500)
    return Response(json.dumps({'message': f'No such config: {name} exists.'}), status=404)


@app.route('/backups/create', methods=['POST'])
def create_new_config():
    """
    Creates a new Configuration for a Backup
    :return: A Flask response with a success or error message depending on the execution
    """
    config = request.json
    if create_config(config):
        scheduler.reload()
        return Response(json.dumps({'message': f'Created Config.'}), status=200)
    return Response(json.dumps({'message': f'Name for config already exists or problem creating config.'}), status=400)


@app.route('/backups/delete/<name>', methods=['GET'])
def delete_backup_config(name: str):
    """
    Deletes a Configuration
    :param name: the name of the configuration to delete
    :return: A Flask response with a success or error message depending on the execution
    """
    if delete_config(name):
        scheduler.reload()
        return Response(json.dumps({'message': f'Deleted Config.'}), status=200)
    return Response(json.dumps({'message': f'Could not find config: {name}.'}), status=404)


if __name__ == '__main__':
    app.run(host=CONF.api.host, port=CONF.api.port)
