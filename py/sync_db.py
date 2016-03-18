import engine
import transfer

@engine.prepare_and_clean
def execute():
    remote_dump = engine.create_remote_dump()
    local_dump = transfer.get(remote_dump)
    engine.truncate_local_db()
    engine.execute_local_mysql_file(local_dump)


def help():
    print "This command makes a db dump on the remote, downloads the sql file, clears the local database and imports the sql file. In Short: It mirrors the remote db to your local db."