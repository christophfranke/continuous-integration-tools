from modules import engine
from modules import run
from modules import out
from modules import mysql

@engine.prepare_and_clean
def execute():
    out.log("exporting database...")
    mysql.export_local_db()


def help():
    out.log("Exports the local database by creating a mysql dump file using mysqldump and then compressing it.", 'help')