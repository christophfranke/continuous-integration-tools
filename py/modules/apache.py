import run
import out
import engine





@out.indent
def append_to_hosts():
    try:
        engine.LOCAL_DOMAIN
    except:
        out.log('Your LOCAL_DOMAIN variable has not been set. Please specify a valid hostname and try again.')
        return
    out.log('appending ' + engine.LOCAL_DOMAIN + ' to ' + engine.LOCAL_ETC_HOSTS, 'apache')
    run.local('echo "127.0.0.1  ' + engine.LOCAL_DOMAIN + ' # appended by fabric deploy script." >>' + engine.LOCAL_ETC_HOSTS, sudo=True)

#todo: needs a safeguard to not append twice
@out.indent
def append_to_server_config():
    try:
        engine.LOCAL_DOMAIN
    except:
        out.log('Your LOCAL_DOMAIN variable has not been set. Please specify a valid hostname and try again.')
        return
    out.log('appending virtual hosts and directory directive to ' + engine.LOCAL_HTTPD_CONF, 'apache')
    run.local('echo "# virtual host set up by fabric deploy script." >>' + engine.LOCAL_HTTPD_CONF, sudo=True)
    run.local('echo "<VirtualHost *:80>" >>' + engine.LOCAL_HTTPD_CONF, sudo=True)
    run.local('echo "    DocumentRoot ' + engine.LOCAL_WWW_DIR + '" >>' + engine.LOCAL_HTTPD_CONF, sudo=True)
    run.local('echo "    ServerName ' + engine.LOCAL_DOMAIN + '" >>' + engine.LOCAL_HTTPD_CONF, sudo=True)
    run.local('echo "</VirtualHost>" >>' + engine.LOCAL_HTTPD_CONF, sudo=True)
    run.local('echo "" >>' + engine.LOCAL_HTTPD_CONF, sudo=True)
    run.local('echo "<Directory ' + engine.LOCAL_WWW_DIR + '>" >>' + engine.LOCAL_HTTPD_CONF, sudo=True)
    run.local('echo "    Options FollowSymLinks Multiviews" >>' + engine.LOCAL_HTTPD_CONF, sudo=True)
    run.local('echo "    MultiviewsMatch Any" >>' + engine.LOCAL_HTTPD_CONF, sudo=True)
    run.local('echo "    AllowOverride All" >>' + engine.LOCAL_HTTPD_CONF, sudo=True)
    run.local('echo "    Require all granted" >>' + engine.LOCAL_HTTPD_CONF, sudo=True)
    run.local('echo "</Directory>" >>' + engine.LOCAL_HTTPD_CONF, sudo=True)
    run.local('echo "# virtual host setup end" >>' + engine.LOCAL_HTTPD_CONF, sudo=True)
    run.local('echo "" >>' + engine.LOCAL_HTTPD_CONF, sudo=True)

@out.indent
def restart():
    out.log('restarting server', 'apache')
    run.local('apachectl graceful', sudo=True)

@out.indent
def allow_read(location = 'local'):
    command = 'chmod -R a+r ./*'
    if location == 'local':
        command = 'cd ' + engine.LOCAL_WWW_DIR + ' && ' + command
    if location == 'local':
        run.local(command)
    if location == 'remote':
        run.remote(command)

@out.indent
def allow_write(location = 'local'):
    command = 'chmod -R a+w ./*'
    if location == 'local':
        command = 'cd ' + engine.LOCAL_WWW_DIR + ' && ' + command
    if location == 'local':
        run.local(command)
    if location == 'remote':
        run.remote(command)
