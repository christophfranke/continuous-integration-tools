from modules import engine
from modules import out
from modules import htaccess

@engine.prepare_and_clean
def execute(overwrite = None):
    out.log("Creating .htaccess files for deployment and local development...")
    if overwrite is None:
            overwrite = 'fail'

    #prepare, i.e. take care of the possibly existing .htaccess file
    htaccess.prepare(overwrite)
    #create .htaccess.local
    htaccess.create_local_file()
    #create .htaccess.live
    htaccess.create_live_file()
    #creates a symlink only on your local machine
    htaccess.create_local_symlink()
    #create a symlink only on the remote machine
    htaccess.create_remote_symlink()

    #ok
    out.log('created files .htaccess.live and .htacces.local on local machine. symlinks to those files have been created locally and on the remote server. To upload the newly created .htaccess files, use the deploy command.')


def help():
    out.log("This command creates 2 files and two symbolic links for you:", 'help')
    out.log("It creates a .htaccess.local: This is your local .htaccess file, that will for example never contain a basic auth entry.")
    out.log("It creates a .htaccess.live: This is your live .htaccess file, which will for example contain a basic auth entry, depending on your configuration.")
    out.log("It creates a symbolic link on your local machine, that points to .htaccess.local.")
    out.log("It creates a symbolic link on the remote server, that points to .htacces.live.")
    out.log("Just make sure to ignore .htaccess in your repository, as this now is a link that is context dependend (i.e. has different values on local/remote server).")
    out.log("The first argument specifies the overwrite mode. Allowed arguments are: backup, overwrite, fail.")
    #out.log("backup will make rename the existing .htaccess to .htaccess.<timestamp>.backup before writing the files. This is the default behaviour.")
    out.log("overwrite will overwrite any existing .htaccess file. This is default behaviour if the previous file has been written by deploy tools.")
    out.log("fail will simply fail, if there is a .htaccess file already. This is the default behaviour if there is no deploy tools signature.")
