# -*- coding: utf-8 -*-
from fabric.api import local, put, get, env, run, cd, lcd
from fabric.contrib.project import rsync_project
import fnmatch, os, time

from constants import *
import helper

#downloads the remote db and installs it locally
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
	helper.execute_mysql_local(TRUNCATE_LOCAL_DB_SQL)

	#unpack db
	with lcd(FABRIC_TMP_DIR):
		#extract db dump
		local('tar xf dump.tar.gz')
		local(LOCAL_MYSQL + '<dump.sql')

	#cleanup local
	local('rm -rf ' + FABRIC_TMP_DIR)

#just an alias of update_local_db
def sync_db():
	update_local_db()

#another alias of update_local_db
def update_db():
	update_local_db()


#uploads the current db to the remote db. if a filename is given, this file will be treated as the db dump file that will be uploaded instead.
def upload_to_remote_db(filename=None):
	#dump local db if needed
	if filename == None:
		helper.create_tmp_dirs()
		export_local_db(FABRIC_TMP_DIR + '/dump.sql')
		filename = FABRIC_TMP_DIR + '/dump.sql'

	#deploy to server
	helper.upload_file_to_remote_db(filename)

	#cleanup
	helper.remove_tmp_dirs()

#runs a command on the server
def execute(command):
	with cd(REMOTE_ROOT_FOLDER):
		run(command)

#syncs the uploads folder using rsync
def sync_media():
	rsync_project(remote_dir=REMOTE_WP_FOLDER + '/wp-content/uploads/*', local_dir=LOCAL_WP_FOLDER + '/wp-content/uploads/', delete=False, upload=False)
	with lcd(LOCAL_WWW_FOLDER):
		try:
			custom_after_sync_script()
		except NameError:
			print "No custom sync script function"

#appends the local key to the authorized_keys file on the servers .ssh folder (no pasword needs to be typed when connected, useful for rsync)
def setup_ssh_key():
	helper.create_tmp_dirs()
	put('~/.ssh/id_rsa.pub', SSH_TMP_FILE)
	run('mkdir -p ~/.ssh')
	run('cat ' + SSH_TMP_FILE + ' >> ~/.ssh/authorized_keys')
	run('rm ' + SSH_TMP_FILE)
	helper.remove_tmp_dirs()

#copies the server key to the clipboard, so it can be put into the deployment keys configuration
def copy_server_key():
	run('cat ~/.ssh/id_rsa.pub | pbcopy')


#updates the files on the remote using git
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

#alias of update_remote_files
def deploy_files():
	update_remote_files()

#exports the local db
def export_local_db(filename=SQL_DUMP_FILE):
	local(LOCAL_MYSQLDUMP + '>' + filename)

#imports a db dump file to the local db
def import_local_db(filename):
	execute_mysql_local(TRUNCATE_LOCAL_DB_SQL)	
	helper.execute_file_local(filename)

#makes a backup of the remote db. A filename can be specified. The standard filename contains a timestamp
def backup_db(filename=SQL_GZ_DUMP_FILE):
	helper.backup_db(filename)

#alias for backup_db
def backup_remote_db(filename):
	backup_db(filename)

#syncs the db and the media files
def sync():
	sync_db()
	sync_media()

#sync media first, then deploy the files. sync media is done, because any uploaded by someone else will be overwritten. The sync ensures, that these files are available locally then.
def deploy():
	sync_media()
	deploy_files()


#compiles all .po files to .mo files
def compile_mo():
	files = []
	for root, dirnames, filenames in os.walk(LOCAL_WWW_FOLDER):
	    for filename in fnmatch.filter(filenames, '*.po'):
	        files.append(os.path.join(root, filename))

	for po in files:
		mo = po[:-3] + '.mo'
		# needs to be refreshed
		if not os.path.isfile(mo) or os.path.getmtime(po) > os.path.getmtime(mo):
			local('msgfmt -o ' + mo + ' ' + po)

#compiles the less files
def compile_less():
	local('cd ' + SCRIPT_DIR + ' && make ' + MAKEFILE_VARS + ' less')

#compiles the js files
def compile_js():
	local('cd ' + SCRIPT_DIR + ' && make ' + MAKEFILE_VARS + ' js')

#compiles the all target
def compile_target_all():
	local('cd ' + SCRIPT_DIR + ' && make ' + MAKEFILE_VARS + ' js less')

#runs a complete compile of everything that possibly needs to be comiled
def compile():
	compile_mo()
	compile_target_all()

#starts the crawler and puts the reulst into a file called broken_links. takes a long time and has no referrer url...
def crawl():
	local('node crawl.js ' + LOCAL_HTTP_ROOT + ' >' + LOCAL_ROOT_FOLDER + '/broken_links')

#prints the error log
def error_log():
	local('tail /var/log/apache2/error_log')

#search the db for a given string
def search_db(find):
	local('php search-and-replace-db.php ' + LOCAL_DB_HOST + ' ' + LOCAL_DB_USER + ' ' + LOCAL_DB_PASSWORD + ' ' + LOCAL_DB_NAME + ' "' + find + '"')

#search and replace in the db for a given string. takes care of php serialize/unserialize data
def replace_in_db(find, replace):
	local('php search-and-replace-db.php ' + LOCAL_DB_HOST + ' ' + LOCAL_DB_USER + ' ' + LOCAL_DB_PASSWORD + ' ' + LOCAL_DB_NAME + ' "' + find + '" "' + replace + '"')

#removes the hostname from the db
def remove_hostname_from_db(hostname):
	replace_in_db('http://' + hostname + '/', '/')
	replace_in_db('http://www.' + hostname + '/', '/')


#mounts the passwords. they are on the mac mini remote in a protected folder.
def mount_passwords(PASSWORD_DIRECTORY='~/Zugangsdaten'):
	local('mkdir -p ' + PASSWORD_DIRECTORY)
	local('chmod 700 ' + PASSWORD_DIRECTORY)
	local('sshfs macmini@Mac-minis-Mac-mini.local:Zugangsdaten ' + PASSWORD_DIRECTORY + ' -o volname=Zugangsdaten')


