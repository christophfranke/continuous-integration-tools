from modules import engine
from modules import run
from modules import out
from modules import mysql

@engine.prepare_and_clean
def execute(argument = None):
    if argument == 'local' or argument == 'remote' or argument is None:
        if argument is not None:
            domaintext = ' matching domain ' + argument
        else:
            domaintext = ''
        out.log('find latest database export in ' + engine.LOCAL_DB_DIR + domaintext)
        filename = engine.get_latest_database_dump(argument)
    else:
        filename = argument
    out.log("import database from " + filename)
    mysql.import_local_db(filename)


def help():
    out.log("Reads a Database Dump file and imports it to your local database. Compression is is handled depending on the file ending.", 'help')
    out.log("The first parameter may be a filename of a .sql or .sql.gz file to import.", 'help')
    out.log("You can also specify a domain (local/remote) and it will pick the latest dump from that domain in the database directory.", 'help')
    out.log("If no filename and no domain is specified, the latest export will be taken from the database directory.", 'help')
