from src.functions.scheduler.scheduler import Scheduler
from src.functions.ftp_server import main

scheduler = Scheduler()
scheduler.start()

main()
