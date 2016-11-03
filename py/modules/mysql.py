import engine
import run
import transfer
import gzip
import out


@out.indent
def test_module():
    if engine.LOCAL_DB_NAME is not None:
        out.log("Testing local mysql access...", 'mysql')
        execute_local_statement('SHOW TABLES;')
        out.log("Local mysql access successful", 'mysql')
    else:
        out.log("Skipping local mysql access, because LOCAL_DB_NAME is not set.", 'mysql')
    if engine.REMOTE_DB_NAME is not None:
        out.log("Testing remote mysql access...", 'mysql')
        execute_remote_statement('SHOW TABLES;')
        out.log("Remote mysql access successful", 'mysql')
    else:
        out.log('Skipping remote mysql access, because REMOTE_DB_NAME is not set.', 'mysql')

def execute_remote_file(filename):
    run.remote(engine.REMOTE_MYSQL_CMD + ' <' + filename)

@out.indent
def execute_remote_statement(statement):
    out.log('executing statement remotely: ' + statement, 'mysql', out.LEVEL_VERBOSE)
    filename = engine.write_remote_file(statement, 'sql')
    execute_remote_file(filename)

#executes a mysql file locally
def execute_local_file(filename):
    run.local(engine.LOCAL_MYSQL_CMD + '<' + filename, False)

#executes a mysql statement locally. This is done by writing a mysql file and then pass it to the mysql client via cli.
@out.indent
def execute_local_statement(statement):
    out.log('executing statement locally: ' + statement, 'mysql', out.LEVEL_VERBOSE)
    filename = engine.write_local_file(statement, 'sql')
    execute_local_file(filename)

#executes a mysql file locally without selecting a db first. Useful for creating a database, for example
def execute_local_file_nodb(filename):
    run.local(engine.LOCAL_MYSQL_NO_DB_CMD + '<' + filename, False)

#executes a statement without selecting a database. You can for example create databases, users, etc..
def execute_local_statement_nodb(statement):
    filename = engine.write_local_file(statement, 'sql')
    execute_local_file_nodb(filename)

@out.indent
def create_local_db():
    out.log('creating local db', 'mysql')
    execute_local_statement_nodb('CREATE DATABASE `' + engine.LOCAL_DB_NAME + '`;')

@out.indent
def export_local_db(compression = True):
    filename = engine.get_database_dump_file(domain='local')
    if compression:
        final_filename = gzip.compressed_filename(filename)
    else:
        final_filename = filename
    out.log('exporting local db to ' + final_filename, 'mysql')
    run.local(engine.LOCAL_MYSQLDUMP_CMD + '>' + filename, False)
    if compression:
        return gzip.compress_local(filename)
    else:
        return filename

#writes a database dump to file and returns its name
@out.indent
def create_remote_dump(compression = False):
    import php
    out.log('create remote database dump', 'mysql')

    if engine.COMMAND_SYSTEM == 'PHP' and compression:
        php.start_buffer();

    #export db on remote
    sql_file = engine.get_new_remote_file('sql')
    run.remote(engine.REMOTE_MYSQLDUMP_CMD + ' >' + sql_file)

    #compress it?
    if compression:
        #compress
        filename = gzip.compress_remote(sql_file, True)
    else:
        #return sql file
        filename = sql_file

    php.end_buffer()

    #done
    return filename

#truncates the remote db by executing some sql (truncation leaves the db empty, but it still exists)
@out.indent
def truncate_local_db():
    out.log('truncate local database', 'mysql')
    execute_local_statement(engine.TRUNCATE_LOCAL_DB_SQL)

@out.indent
def truncate_remote_db():
    out.log('truncate remote database', 'mysql')
    execute_remote_statement(engine.TRUNCATE_REMOTE_DB_SQL)

@out.indent
def import_local_db(filename, compression = None):
    import os

    #is our file compressed?
    if compression is None:
        compression = gzip.is_compressed(filename)
    if compression:
        #uncompress
        sql_file = gzip.uncompress_local(filename)
    else:
        sql_file = filename

    #wipe old db
    if os.path.isfile(sql_file):
        truncate_local_db()
    else:
        out.log('File not found: ' + filename, 'mysql', out.LEVEL_ERROR)
        quit()

    #refill db
    out.log('importing local database from file ' + sql_file, 'mysql')
    execute_local_file(sql_file)

    #compress again, although it would have been better to not touch the compressed file in the first place
    if compression:
        gzip.compress_local(sql_file)

@out.indent
def upload_to_remote_db(filename, compression = None):
    out.log('uploading file to remote database: ' + filename, 'mysql')
    if compression is None:
        compression = gzip.is_compressed(filename)
    if compression:
        #if our file is already compressed, we just upload it normally and compress it on the remote
        remote_compressed = transfer.put(filename)
        remote_uncompressed = gzip.uncompress_remote(remote_compressed, True)
    else:
        #otherwise, we just upload it compressed and have it uncompressed automatically
        remote_uncompressed = transfer.put_compressed(filename)

    #truncate remote db and fill it with the new stuff
    truncate_remote_db()
    out.log('import remote database', 'mysql')
    execute_remote_file(remote_uncompressed)