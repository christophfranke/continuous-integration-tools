# -*- coding: utf-8 -*-
from fabric.api import local, put, get, env, run, cd, lcd
from fabric.contrib.project import rsync_project
from config import *
from project_config import *


LOCAL_ROOT_FOLDER = os.path.dirname(os.path.realpath(__file__)) + '/' + LOCAL_WWW_FOLDER

LOCAL_MYSQL = 'mysql -u ' + LOCAL_DB_USER + ' --password=' + LOCAL_DB_PASSWORD + ' ' + LOCAL_DB_NAME + ' '
LOCAL_MYSQLDUMP = 'mysqldump -u ' + LOCAL_DB_USER + ' --password=' + LOCAL_DB_PASSWORD + ' ' + LOCAL_DB_NAME + ' '

REMOTE_MYSQL = 'mysql -u ' + REMOTE_DB_USER + ' --password=' + REMOTE_DB_PASSWORD + ' ' + REMOTE_DB_NAME + ' '
REMOTE_MYSQLDUMP = 'mysqldump -u ' + REMOTE_DB_USER + ' --password=' + REMOTE_DB_PASSWORD + ' ' + REMOTE_DB_NAME + ' '

FABRIC_TMP_DIR = 'fabric-tmp-dir'
TMP_SQL_FILE = 'fabric-tmp.sql'

try:
	GIT_CURRENT_BRANCH = GIT_BRANCH
except:
	GIT_CURRENT_BRANCH = '' #default to no specific branch

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
	run('rm ' + TMP_SQL_FILE)


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

def execute(command):
	with cd(REMOTE_ROOT_FOLDER):
		run(command)

def update_db():
	update_local_db()

def sync_media():
	rsync_project(remote_dir=REMOTE_ROOT_FOLDER + '/wp-content/uploads/*', local_dir=LOCAL_ROOT_FOLDER + '/wp-content/uploads/', delete=False, upload=False)

def setup_ssh_key():
	put('~/.ssh/id_rsa.pub', '~/tmp')
	run('cat ~/tmp >> ~/.ssh/authorized_keys')
	run('rm ~/tmp')

def print_server_key():
	run('cat ~/.ssh/id_rsa.pub')


def update_remote_files():
	with cd(REMOTE_ROOT_FOLDER):
		run('git checkout -f ' + GIT_CURRENT_BRANCH)
		run('git clean -f wp-content/uploads/*')
		run('git pull')
		run('git submodule init')
		run('git submodule sync')
		run('git submodule update')
		custom_after_deploy_script()

def export_local_db(filename):
	local(LOCAL_MYSQLDUMP + '>' + filename)

def import_local_db(filename):
	execute_mysql_local(TRUNCATE_LOCAL_DB_SQL)	
	execute_file_local(filename)

def backup_db(filename):
	run('mkdir -p ' + FABRIC_TMP_DIR)
	with cd(FABRIC_TMP_DIR):
		run(REMOTE_MYSQLDUMP + '>dump.sql')
	get(FABRIC_TMP_DIR + '/dump.sql', filename)
	run('rm- rf ' + FABRIC_TMP_DIR)


def sync():
	update_local_db()
	sync_media()

def deploy():
	sync_media()
	update_remote_files()






