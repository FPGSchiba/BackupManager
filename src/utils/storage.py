import os
import shutil
from datetime import datetime


def get_backup_name():
    timestamp = datetime.now().strftime("%d%m%y-%H")
    return f"{timestamp}.tar.gz"


def remove_old_folder(folder: str):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    os.rmdir(folder)


if __name__ == '__main__':
    print(get_backup_name())
