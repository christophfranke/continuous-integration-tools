from modules import engine
from modules import out
from modules import transfer
from modules import mysql

@engine.prepare_and_clean
def execute():
    out.log("Synchronizing local db...")
    remote_dump = mysql.create_remote_dump()
    local_dump = transfer.get_compressed(remote_dump)
    mysql.import_local_db(local_dump)


def help():
    out.log("This command makes a db dump on the remote, downloads the sql file, clears the local database and imports the sql file. In Short: It mirrors the remote db to your local db.", 'help')