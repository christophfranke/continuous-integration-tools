from modules import engine
from modules import mysql
from modules import out

import backup_db

@engine.prepare_and_clean
def execute(filename = None):
    out.log("uploading database...")
    #make a backup first
    backup_db.execute()
    if filename is None:
        #export db, if no filelname is specified
        filename = mysql.export_local_db()
    #upload and import it
    mysql.upload_to_remote_db(filename)


def help():
    out.log("Uploads the database to the production server. Note that this is overwriting all files on the server.", 'help')