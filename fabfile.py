# -*- coding: utf-8 -*-
from fabric.api import local, put, get, env, run, cd, lcd
from fabric.contrib.project import rsync_project
from config import *


LOCAL_MYSQL = 'mysql -u ' + LOCAL_DB_USER + ' --password=' + LOCAL_DB_PASSWORD
LOCAL_MYSQLDUMP = 'mysqldump -u ' + LOCAL_DB_USER + ' --password=' + LOCAL_DB_PASSWORD

REMOTE_MYSQL = 'mysql -u ' + REMOTE_DB_USER + ' --password=' + REMOTE_DB_PASSWORD
REMOTE_MYSQLDUMP = 'mysqldump -u ' + REMOTE_DB_USER + ' --password=' + REMOTE_DB_PASSWORD

TMP_SQL_FILE = 'tmp.sql'


def execute_mysql_local(statement):
	local('echo "' + statement + '">' + TMP_SQL_FILE)
	local(LOCAL_MYSQL + ' ' + LOCAL_DB_NAME + ' <' + TMP_SQL_FILE)
	local('rm ' + TMP_SQL_FILE)

def execute_mysql_remote(statement):
	run('echo "' + statement + '">' + TMP_SQL_FILE)
	run(REMOTE_MYSQL + ' ' + REMOTE_DB_NAME + ' <' + TMP_SQL_FILE)
	run('rm ' + TMP_SQL_FILE)

def execute_file_remote(filename):
	put(filename, 'fabric-tmp-dir/tmp.sql')
	run(REMOTE_MYSQL + ' ' + REMOTE_DB_NAME + ' <fabric-tmp-dir/tmp.sql')
	run('rm fabric-tmp-dir/tmp.sql')



def update_local_db():
	#create fabric tmp dir
	run('mkdir -p fabric-tmp-dir')
	with cd('fabric-tmp-dir'):
		#dump database before changing
		run('mysqldump -u ' + REMOTE_DB_USER + ' --password=' + REMOTE_DB_PASSWORD + ' ' + REMOTE_DB_NAME + ' >dump.sql')
		#compress before downloading
		run('tar -acf dump.tar.gz dump.sql')
	#create local tmp dir
	local('mkdir -p fabric-tmp-dir')
	#download db
	get('fabric-tmp-dir/dump.tar.gz', 'fabric-tmp-dir/dump.tar.gz')
	#cleanup remote
	run('rm -rf fabric-tmp-dir')

	#unpack db
	with lcd('fabric-tmp-dir'):
		#extract db dump
		local('tar xf dump.tar.gz')
		#drop local db and recreate it
		execute_mysql_local('DROP DATABASE \\`' + LOCAL_DB_NAME + '\\`;CREATE DATABASE \\`' + LOCAL_DB_NAME + '\\`;')
		local(LOCAL_MYSQL + ' ' + LOCAL_DB_NAME + ' < dump.sql')

	#cleanup local
	local('rm -rf fabric-tmp-dir')

def update_db():
	update_local_db()

def sync_media():
	rsync_project(remote_dir=REMOTE_ROOT_FOLDER + '/wp-content/uploads/*', local_dir=LOCAL_ROOT_FOLDER + '/wp-content/uploads/', delete=False, upload=False)

def setup_ssh_key():
	put('~/.ssh/id_rsa.pub', '~/tmp')
	run('cat ~/tmp >> ~/.ssh/authorized_keys')
	run('rm ~/tmp')

def create_symlink():
	local('ln -s .. ~/www/' + LOCAL_HTTP_NAME)


def update_remote_files():
	with cd(REMOTE_ROOT_FOLDER):
		run('git checkout -f')
		run('git clean -f wp-content/uploads/*')
		run('git pull')
		run('git submodule init')
		run('git submodule sync')
		run('git submodule update')
		custom_after_deploy_script()


def setup():
	setup_ssh_key()
	local('rm -rf ' + LOCAL_ROOT_FOLDER + '/wp-contents/uploads/')
	sync_media()
	local(LOCAL_MYSQL + ' -e "CREATE DATABASE \\`' + LOCAL_DB_NAME + '\\`;"')
	update_local_db()
	create_symlink()

def sync():
	update_local_db()
	sync_media()

def deploy():
	sync_media()
	update_remote_files()






