from modules import engine
from modules import out
from modules import transfer
from modules import mysql

@engine.prepare_and_clean
def execute():
    if engine.LOCAL_DB_NAME is not None:
        out.log("Synchronizing local db...")
        mysql.export_local_db()
        remote_dump = mysql.create_remote_dump(compression = True)
        local_dump = transfer.get(remote_dump)
        mysql.import_local_db(local_dump)
    else:
        out.log('No local database named, nothing to do.')


def help():
    out.log("This command makes a db dump on the remote, downloads the sql file, clears the local database and imports the sql file. In Short: It mirrors the remote db to your local db.", 'help')