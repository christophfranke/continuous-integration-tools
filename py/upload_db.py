from modules import engine
from modules import mysql
from modules import out
from modules import transfer

@engine.prepare_and_clean
def execute(filename = None):

    out.log("making a backup first")
    #make a backup first
    backup_file = engine.get_database_dump_file(compression = True, domain='remote')
    remote_dump = mysql.create_remote_dump(compression = True)
    transfer.get(remote_dump, backup_file)

    out.log("uploading database...")
    if filename is None:
        #export db, if no filelname is specified
        filename = mysql.export_local_db()
    #upload and import it
    mysql.upload_to_remote_db(filename)


def help():
    out.log("Uploads the database to the production server. Makes a backup of the remote database before overwriting it.", 'help')
    out.log("Takes a filename as argument. If none given, uploads the local database.")