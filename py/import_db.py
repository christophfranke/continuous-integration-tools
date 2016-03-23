from modules import engine
from modules import run
from modules import out
from modules import mysql

@engine.prepare_and_clean
def execute(filename, compression = None):
    out.log("import database from " + filename + "...")
    mysql.import_local_db(filename)


def help():
    out.log("Reads a Database Dump file and iports it to your local database. Compression is expected depending on your USE_TAR_COMPRESSION settings. Beware: This might change in future.", 'help')