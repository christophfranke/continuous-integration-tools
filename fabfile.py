# we don't want fabric to be a dependency anymore, so this is here basically for legacy
import py.sync_db

def sync_db():
    py.sync_db.execute()