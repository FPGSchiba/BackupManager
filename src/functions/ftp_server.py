from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from src.functions.utils.config import Config

CONF = Config()

# The port the FTP server will listen on.
# This must be greater than 1023 unless you run this script as root.
FTP_PORT = CONF.ftp.port

# The name of the FTP user that can log in.
FTP_USER = CONF.ftp.user

# The FTP user's password.
FTP_PASSWORD = CONF.ftp.password

# The directory the FTP user will have full read/write access to.
FTP_DIRECTORY = CONF.ftp.directory


def main():
    authorizer = DummyAuthorizer()

    # Define a new user having full r/w permissions.
    authorizer.add_user(FTP_USER, FTP_PASSWORD, FTP_DIRECTORY, perm='elradfmw')

    handler = FTPHandler
    handler.authorizer = authorizer

    # Define a customized banner (string returned when client connects)
    handler.banner = "Backup Manager by FPG Schiba"

    # Optionally specify range of ports to use for passive connections.
    # handler.passive_ports = range(60000, 65535)

    address = (CONF.ftp.host, FTP_PORT)
    server = FTPServer(address, handler)

    server.max_cons = 256
    server.max_cons_per_ip = 5

    server.serve_forever()


if __name__ == '__main__':
    main()
