import engine
import run
import transfer
import out


TAR_SQL_CONTENT_FILENAME = 'dump.sql'

@out.indent
def test_module():
    out.log("Testing local mysql access...", 'mysql')
    execute_local_statement('SHOW TABLES;')
    out.log("Testing remote mysql access...", 'mysql')
    execute_remote_statement('SHOW TABLES;')

def execute_remote_file(filename):
    run.remote(engine.REMOTE_MYSQL_CMD + ' <' + filename)

def execute_remote_statement(statement):
    filename = engine.write_remote_file(statement, '.sql')
    execute_remote_file(filename)

#executes a mysql file locally
def execute_local_file(filename):
    run.local(engine.LOCAL_MYSQL_CMD + '<' + filename)

#executes a mysql statement locally. This is done by writing a mysql file and then pass it to the mysql client via cli.
def execute_local_statement(statement):
    filename = engine.write_local_file(statement, 'sql')
    execute_local_file(filename)

#executes a mysql file locally without selecting a db first. Useful for creating a database, for example
def execute_local_file_nodb(filename):
    run.local(engine.LOCAL_MYSQL_NO_DB_CMD + '<' + filename)

#executes a statement without selecting a database. You can for example create databases, users, etc..
def execute_local_statement_nodb(statement):
    filename = engine.write_local_file(statement, 'sql')
    execute_local_file_nodb(filename)

def create_local_db():
    execute_local_statement_nodb('CREATE DATABASE `' + engine.LOCAL_DB_NAME + '`;')

def export_local_db():
    filename = engine.get_database_dump_file()
    run.local(engine.LOCAL_MYSQLDUMP_CMD + '>' + filename)

#writes a database dump to file and returns its name
def create_remote_dump(use_compression = None):
    #export db on remote
    sql_file = engine.get_new_remote_file('sql')
    run.remote(engine.REMOTE_MYSQLDUMP_CMD + ' >' + sql_file)

    #compress it?
    if use_compression is None:
        use_compression = engine.USE_TAR_COMPRESSION
    if use_compression:
        #get tar file
        tar_file = engine.get_new_remote_file('gz')

        #temporarily rename the sql file
        transfer.remote_move(sql_file, TAR_SQL_CONTENT_FILENAME)
        #create tar archive
        run.remote('tar -czf ' + tar_file + ' ' + TAR_SQL_CONTENT_FILENAME)
        #move back sql file
        transfer.remote_move(TAR_SQL_CONTENT_FILENAME, sql_file)

        #return tar file
        filename = tar_file
    else:
        #return sql file
        filename = sql_file

    #done
    return filename

#truncates the remote db by executing some sql (truncation leaves the db empty, but it still exists)
def truncate_local_db():
    execute_local_statement(engine.TRUNCATE_LOCAL_DB_SQL)

def import_local_db(filename, use_compression = None):
    #is our file compressed?
    if use_compression is None:
        use_compression = engine.USE_TAR_COMPRESSION
    if use_compression:
        #uncompress
        run.local('tar -xzf ' + filename)
        #move file to tmp folder
        filename = engine.get_new_local_file('sql')
        transfer.local_move(TAR_SQL_CONTENT_FILENAME, filename)
        #set sql_file accordingly
        sql_file = filename
    else:
        sql_file = filename

    #wipe old db
    truncate_local_db()

    #refill db
    execute_local_file(sql_file)
