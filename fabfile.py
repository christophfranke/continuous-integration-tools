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
import py.download_all_files
import py.upload_all_files
import py.sync_files
import py.search
import py.replace
import py.create_wp_files
import py.error_log
import py.mount_passwords
import py.crawl

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

def download_all_files():
    py.download_all_files.execute()

def upload_all_files():
    py.upload_all_files.execute()

def sync_files():
    py.sync_files.execute()

def sync():
    py.sync_db.execute()
    py.sync_files.execute()

def search(find):
    py.search.execute(find)

def replace(find, replace):
    py.replace.execute(find, replace)

def create_wp_files():
    py.create_wp_files.execute()

def error_log():
    py.error_log.execute()

def mount_passwords():
    py.mount_passwords.execute()

def crawl(domain = None):
    py.crawl.execute(domain)