from modules import engine
from modules import out
from modules import transfer
from modules import mysql

@engine.prepare_and_clean
def execute(filename = None):
    out.log("[command] Creating a backup of the remote db...", out.LEVEL_INFO)
    if filename is None:
        filename = engine.get_database_dump_file()
    remote_dump = mysql.create_remote_dump()
    transfer.get_verbose(remote_dump, filename)


def help():
    out.log("Exports the remote database by creating a mysql dump file using mysqldump.", out.LEVEL_INFO)