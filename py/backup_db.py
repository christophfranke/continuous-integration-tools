from modules import engine
from modules import out
from modules import transfer
from modules import mysql

@engine.prepare_and_clean
def execute(filename = None):
    out.log("Creating a backup of the remote db...")
    if filename is None:
        filename = engine.get_database_dump_file(compression = True, domain='remote')
    remote_dump = mysql.create_remote_dump(compression = True)
    transfer.get(remote_dump, filename)


def help():
    out.log("Exports the remote database by creating a mysql dump file using mysqldump.", 'help')