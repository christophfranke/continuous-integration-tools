# -*- coding: utf-8 -*-
from fabric.api import local, put, get, env, run, cd, lcd
from fabric.contrib.project import rsync_project
from datetime import datetime
import fnmatch, os, time

try:
	from project_config import *
except ImportError:
	print "No Project config found. Using example config instead."
	from project_config_example import *

try:
	from config import *
except ImportError:
	from config_example import *


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

try:
	RELATIVE_LOCAL_PROJECT_ROOT
except NameError:
	RELATIVE_LOCAL_PROJECT_ROOT = '..'

LOCAL_ROOT_FOLDER = SCRIPT_DIR + '/' + RELATIVE_LOCAL_PROJECT_ROOT
LOCAL_WWW_FOLDER = LOCAL_ROOT_FOLDER + '/' + WWW_FOLDER

try:
	DB_FOLDER
except NameError:
	DB_FOLDER = LOCAL_ROOT_FOLDER + '/Datenbank'

SQL_DUMP_FILE = DB_FOLDER + '/dump-' + str(datetime.now()).replace(' ', '-') + '.sql'
SQL_GZ_DUMP_FILE = SQL_DUMP_FILE + '.gz'


REMOTE_WWW_FOLDER = REMOTE_ROOT_FOLDER + '/' + WWW_FOLDER

LOCAL_MYSQL = 'mysql -u ' + LOCAL_DB_USER + ' --password=' + LOCAL_DB_PASSWORD + ' ' + LOCAL_DB_NAME + ' '
LOCAL_MYSQLDUMP = 'mysqldump -u ' + LOCAL_DB_USER + ' --password=' + LOCAL_DB_PASSWORD + ' ' + LOCAL_DB_NAME + ' '

#concatenate mysql command strings
REMOTE_MYSQL_PARAMS = ' -u ' + REMOTE_DB_USER + ' --password=' + REMOTE_DB_PASSWORD + ' '
try:
	REMOTE_DB_PORT
	REMOTE_MYSQL_PARAMS += '--port=' + REMOTE_DB_PORT + ' '
except NameError:
	pass
try:
	REMOTE_DB_SOCKET
	REMOTE_MYSQL_PARAMS += '--socket=' + REMOTE_DB_SOCKET + ' '
except NameError:
	pass
REMOTE_MYSQL_PARAMS += REMOTE_DB_NAME + ' '

REMOTE_MYSQL = 'mysql' + REMOTE_MYSQL_PARAMS
REMOTE_MYSQLDUMP = 'mysqldump' + REMOTE_MYSQL_PARAMS

FABRIC_TMP_DIR = 'fabric-tmp-dir'
TMP_SQL_FILE = 'fabric-tmp.sql'
SSH_TMP_FILE = FABRIC_TMP_DIR + '/ssh-key-tmp-file'

try:
	RELATIVE_SRC_DIR = WWW_FOLDER + '/' + SRC_URL
	RELATIVE_BUILD_DIR = WWW_FOLDER + '/' + BUILD_URL

	SRC_DIR = LOCAL_ROOT_FOLDER + '/' + RELATIVE_SRC_DIR
	BUILD_DIR = LOCAL_ROOT_FOLDER + '/' + RELATIVE_BUILD_DIR

	REMOTE_BUILD_DIR = REMOTE_ROOT_FOLDER + '/' + RELATIVE_BUILD_DIR

	MAKEFILE_VARS = 'SRC=' + SRC_DIR + ' BUILD=' + BUILD_DIR + ' SRC_URL=' + SRC_URL + ' BUILD_URL=' + BUILD_URL + ' WWW_FOLDER=' + LOCAL_WWW_FOLDER
except:
	pass

try:
	GIT_CURRENT_BRANCH = GIT_BRANCH
except:
	GIT_CURRENT_BRANCH = '' #default to no specific branch


try:
	LOCAL_WP_FOLDER = LOCAL_ROOT_FOLDER + '/' + WP_FOLDER
	REMOTE_WP_FOLDER = REMOTE_ROOT_FOLDER + '/' + WP_FOLDER
except:
	LOCAL_WP_FOLDER = LOCAL_WWW_FOLDER
	REMOTE_WP_FOLDER = REMOTE_WWW_FOLDER

try:
	WP_FOLDER
except:
	WP_FOLDER = WWW_FOLDER



TRUNCATE_LOCAL_DB_SQL = 'DROP DATABASE `' + LOCAL_DB_NAME + '`;CREATE DATABASE `' + LOCAL_DB_NAME + '`;'
TRUNCATE_REMOTE_DB_SQL = 'DROP DATABASE `' + REMOTE_DB_NAME + '`;CREATE DATABASE `' + REMOTE_DB_NAME + '`;'

def execute_file_remote(filename):
	put(filename, TMP_SQL_FILE)
	run(REMOTE_MYSQL + '<' + TMP_SQL_FILE)
	run('rm ' + TMP_SQL_FILE)

def execute_file_local(filename):
	local(LOCAL_MYSQL + '<' + filename)

def execute_mysql_local(statement):
	file = open(TMP_SQL_FILE, 'w')
	file.write(statement)
	file.close()
	execute_file_local(TMP_SQL_FILE)
	local('rm ' + TMP_SQL_FILE)

def execute_mysql_remote(statement):
	file = open(TMP_SQL_FILE, 'w')
	file.write(statement)
	file.close()
	execute_file_remote(TMP_SQL_FILE)
	local('rm ' + TMP_SQL_FILE)

def create_tmp_dirs():
	local('mkdir -p ' + FABRIC_TMP_DIR)
	run('mkdir -p ' + FABRIC_TMP_DIR)

def remove_tmp_dirs():
	local('rm -rf ' + FABRIC_TMP_DIR)
	run('rm -rf ' + FABRIC_TMP_DIR)


def update_local_db():
	#create fabric tmp dir
	run('mkdir -p ' + FABRIC_TMP_DIR)
	with cd(FABRIC_TMP_DIR):
		#dump database before changing
		run(REMOTE_MYSQLDUMP + ' >dump.sql')
		#compress before downloading
		run('tar -acf dump.tar.gz dump.sql')
	#create local tmp dir
	local('mkdir -p ' + FABRIC_TMP_DIR)
	#download db
	get(FABRIC_TMP_DIR + '/dump.tar.gz', FABRIC_TMP_DIR + '/dump.tar.gz')
	#cleanup remote
	run('rm -rf ' + FABRIC_TMP_DIR)

	#drop local db and recreate it
	execute_mysql_local(TRUNCATE_LOCAL_DB_SQL)

	#unpack db
	with lcd(FABRIC_TMP_DIR):
		#extract db dump
		local('tar xf dump.tar.gz')
		local(LOCAL_MYSQL + '<dump.sql')

	#cleanup local
	local('rm -rf ' + FABRIC_TMP_DIR)

def upload_file_to_remote_db(filename):
	backup_db()
	execute_mysql_remote(TRUNCATE_REMOTE_DB_SQL)
	execute_file_remote(filename)


def upload_to_remote_db(filename=None):
	#dump local db if needed
	if filename == None:
		create_tmp_dirs()
		export_local_db(FABRIC_TMP_DIR + '/dump.sql')
		filename = FABRIC_TMP_DIR + '/dump.sql'

	#deploy to server
	upload_file_to_remote_db(filename)

	#cleanup
	remove_tmp_dirs()


def execute(command):
	with cd(REMOTE_ROOT_FOLDER):
		run(command)

def update_db():
	update_local_db()

def sync_media():
	rsync_project(remote_dir=REMOTE_WP_FOLDER + '/wp-content/uploads/*', local_dir=LOCAL_WP_FOLDER + '/wp-content/uploads/', delete=False, upload=False)
	with lcd(LOCAL_WWW_FOLDER):
		try:
			custom_after_sync_script()
		except NameError:
			print "No custom sync script function"

def setup_ssh_key():
	create_tmp_dirs()
	put('~/.ssh/id_rsa.pub', SSH_TMP_FILE)
	run('mkdir -p ~/.ssh')
	run('cat ' + SSH_TMP_FILE + ' >> ~/.ssh/authorized_keys')
	run('rm ' + SSH_TMP_FILE)
	remove_tmp_dirs()

def print_server_key():
	run('cat ~/.ssh/id_rsa.pub')


def update_remote_files():
	with cd(REMOTE_ROOT_FOLDER):
		run('git checkout -f ' + GIT_CURRENT_BRANCH)
		run('git clean -df ' + WP_FOLDER + '/wp-content/uploads/*')
		run('git pull')
		run('git submodule init')
		run('git submodule sync')
		run('git submodule update')
	try:
		BUILD_DIR
		compile()
		run('mkdir -p ' + REMOTE_BUILD_DIR)
		put(BUILD_DIR + '/', REMOTE_BUILD_DIR + '/../')
	except NameError:
		pass
	with cd(REMOTE_WWW_FOLDER):
		custom_after_deploy_script()

def export_local_db(filename=SQL_DUMP_FILE):
	local(LOCAL_MYSQLDUMP + '>' + filename)

def import_local_db(filename):
	execute_mysql_local(TRUNCATE_LOCAL_DB_SQL)	
	execute_file_local(filename)

def backup_db(filename=SQL_GZ_DUMP_FILE):
	#create tmp dir
	run('mkdir -p ' + FABRIC_TMP_DIR)
	with cd(FABRIC_TMP_DIR):
		#export
		run(REMOTE_MYSQLDUMP + '>dump.sql')
		#compress before downloading
		run('tar -acf dump.tar.gz dump.sql')
	#download
	get(FABRIC_TMP_DIR + '/dump.tar.gz', filename)
	#cleanup
	run('rm -rf ' + FABRIC_TMP_DIR)

#alias for backup_db
def backup_remote_db(filename):
	backup_db(filename)


def sync():
	update_local_db()
	sync_media()

def deploy():
	sync_media()
	update_remote_files()


def update_mo():
	files = []
	for root, dirnames, filenames in os.walk(LOCAL_WWW_FOLDER):
	    for filename in fnmatch.filter(filenames, '*.po'):
	        files.append(os.path.join(root, filename))

	for po in files:
		mo = po[:-3] + '.mo'
		# needs to be refreshed
		if not os.path.isfile(mo) or os.path.getmtime(po) > os.path.getmtime(mo):
			local('msgfmt -o ' + mo + ' ' + po)


def update_less():
	local('cd ' + SCRIPT_DIR + ' && make ' + MAKEFILE_VARS + ' less')

def update_js():
	local('cd ' + SCRIPT_DIR + ' && make ' + MAKEFILE_VARS + ' js')

def update_all():
	local('cd ' + SCRIPT_DIR + ' && make ' + MAKEFILE_VARS + ' js less')

def compile():
	update_mo()
	update_all()

def crawl():
	local('node crawl.js ' + LOCAL_HTTP_ROOT + ' >' + LOCAL_ROOT_FOLDER + '/broken_links')

def error_log():
	local('tail /var/log/apache2/error_log')

def search_db(find):
	local('php search-and-replace-db.php ' + LOCAL_DB_HOST + ' ' + LOCAL_DB_USER + ' ' + LOCAL_DB_PASSWORD + ' ' + LOCAL_DB_NAME + ' "' + find + '"')

def replace_in_db(find, replace):
	local('php search-and-replace-db.php ' + LOCAL_DB_HOST + ' ' + LOCAL_DB_USER + ' ' + LOCAL_DB_PASSWORD + ' ' + LOCAL_DB_NAME + ' "' + find + '" "' + replace + '"')

def remove_hostname_from_db(hostname):
	replace_in_db('http://' + hostname + '/', '/')
	replace_in_db('http://www.' + hostname + '/', '/')

def mount_passwords(PASSWORD_DIRECTORY='~/Zugangsdaten'):
	local('mkdir -p ' + PASSWORD_DIRECTORY)
	local('chmod 700 ' + PASSWORD_DIRECTORY)
	local('sshfs macmini@Mac-minis-Mac-mini.local:Zugangsdaten ' + PASSWORD_DIRECTORY)



