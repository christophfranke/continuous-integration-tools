import engine
import run

#executes a mysql file locally
def execute_local_file(filename):
    run.local(engine.LOCAL_MYSQL_CMD + '<' + filename)

#executes a mysql statement locally. This is done by writing a mysql file and then pass it to the mysql client via cli.
def execute_local_statement(statement):
    filename = engine.write_local_file(statement)
    execute_local_file(filename)

#executes a mysql file locally without selecting a db first. Useful for creating a database, for example
def execute_local_file_nodb(filename):
    run.local(engine.LOCAL_MYSQL_NO_DB_CMD + '<' + filename)

#executes a statement without selecting a database. You can for example create databases, users, etc..
def execute_local_statement_nodb(statement):
    filename = engine.write_local_file(statement)
    execute_local_file_nodb(filename)

def create_local_db():
    execute_local_statement_nodb('CREATE DATABASE `' + engine.LOCAL_DB_NAME + '`;')

def export_local_db():
    filename = engine.get_database_dump_file()
    run.local(engine.LOCAL_MYSQLDUMP_CMD + '>' + filename)