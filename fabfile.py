# we don't want fabric to be a dependency anymore, so this is here basically for legacy
import py.sync_db
import py.create_db
import py.execute

def sync_db():
    py.sync_db.execute()

def create_db():
    py.create_db.execute()

def execute(command):
    py.execute.execute(command)