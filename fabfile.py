# we don't want fabric to be a dependency anymore, so this is here basically for legacy
import py.sync_db
import py.create_db
import py.execute
import py.upload_command_file
import py.export_db
import py.import_db
import py.backup_db
import py.test

def sync_db():
    py.sync_db.execute()

def create_db():
    py.create_db.execute()

def execute(command):
    py.execute.execute(command)

def upload_command_file():
    py.upload_command_file.execute()

def export_db(filename = None):
    py.export_db.execute(filename)

def import_db(filename):
    py.import_db.execute(filename)

def backup_db(filename = None):
    py.backup_db.execute(filename)

def test():
    py.test.execute()