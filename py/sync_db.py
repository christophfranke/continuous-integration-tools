from modules import engine

@engine.prepare_and_clean
def execute():
    out.log("[command] Synchronizing local db...", out.LEVEL_INFO)
    remote_dump = engine.create_remote_dump()
    local_dump = transfer.get_verbose(remote_dump)
    engine.truncate_local_db()
    mysql.execute_local_file(local_dump)


def help():
    out.log("This command makes a db dump on the remote, downloads the sql file, clears the local database and imports the sql file. In Short: It mirrors the remote db to your local db.", out.LEVEL_INFO)