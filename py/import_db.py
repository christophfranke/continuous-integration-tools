from modules import engine
from modules import run
from modules import out
from modules import mysql

@engine.prepare_and_clean
def execute(filename = None):
    if filename is None:
        filename = engine.get_latest_database_dump()
    out.log("import database from " + filename + "...")
    mysql.import_local_db(filename)


def help():
    out.log("Reads a Database Dump file and imports it to your local database. Compression is is handled depending on the file ending. If no file is specified, the latest dump from the database folder is taken.", 'help')