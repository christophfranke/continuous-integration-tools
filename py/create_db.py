from modules import engine
from modules import transfer
from modules import out
from modules import mysql

@engine.prepare_and_clean
def execute():
    out.log("creating local db...")
    mysql.create_local_db()


def help():
    out.log("This command creates an empty local databse with the name configured in project configs.", 'help')