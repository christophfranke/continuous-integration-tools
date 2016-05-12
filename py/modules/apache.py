import run
import out
import engine





@out.indent
def append_to_hosts():
    out.log('appending ' + engine.LOCAL_DOMAIN + ' to ' + engine.LOCAL_ETC_HOSTS, 'apache')
    run.local('echo "127.0.0.1  ' + engine.LOCAL_DOMAIN + ' # appended by fabric deploy script." >>' + engine.LOCAL_ETC_HOSTS, sudo=True)

#todo: needs a safeguard to not append twice
@out.indent
def append_to_server_config():
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