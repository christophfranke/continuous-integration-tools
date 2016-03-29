# we don't want fabric to be a dependency anymore, so this is here basically for legacy
import py.sync_db
import py.create_db
import py.execute
import py.upload_command_file
import py.export_db
import py.import_db
import py.backup_db
import py.test
import py.upload_db
import py.cleanup
import py.phpinfo
import py.compile
import py.deploy
import py.download_www

def sync_db():
    py.sync_db.execute()

def create_db():
    py.create_db.execute()

def execute(command):
    py.execute.execute(command)

def upload_command_file():
    py.upload_command_file.execute()

def export_db(compression = None):
    py.export_db.execute(compression)

def import_db(filename, compression = None):
    py.import_db.execute(filename)

def backup_db(filename = None):
    py.backup_db.execute(filename)

def test():
    py.test.execute()

def upload_db(filename = None):
    py.upload_db.execute(filename)

def cleanup():
    py.cleanup.execute()

def phpinfo():
    py.phpinfo.execute()

def compile(types = None):
    py.compile.execute(types)

def deploy():
    py.deploy.execute()

def download_www():
    py.download_www.execute()