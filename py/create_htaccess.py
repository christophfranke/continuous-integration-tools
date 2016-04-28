from modules import engine
from modules import out
from modules import htaccess

@engine.prepare_and_clean
def execute(overwrite = None):
    out.log("Creating .htaccess files for deployment and local development...")
    upload_htaccess = False
    if overwrite is None:
        overwrite = 'fail'
    if overwrite == 'upload':
        upload_htaccess = True
        overwrite = 'overwrite'


    #prepare, i.e. take care of the possibly existing .htaccess file
    htaccess.prepare(overwrite, upload_htaccess)
    #create .htaccess.local
    htaccess.create_local_file()
    #create .htaccess.live
    htaccess.create_live_file(upload_htaccess)
    #creates a symlink only on your local machine
    htaccess.create_local_symlink()
    #create a symlink only on the remote machine
    if upload_htaccess:
        htaccess.create_remote_symlink()

    #ok
    if not upload_htaccess:
        out.log('created files .htaccess.live and .htacces.local on local machine. symlinks to those files have been created locally. To upload the newly created .htaccess files, use the deploy command or specify the upload argument (fab create_htaccess:upload).')
    else:
        out.log('created files .htaccess.live and .htaccess.local on your local machine. symlinks to thos files have been created locally and on the remote server. .htaccess.live has been uploaded.')


def help():
    out.log("This command creates 2 files and two symbolic links for you:", 'help')
    out.log("It creates a .htaccess.local: This is your local .htaccess file, that will for example never contain a basic auth entry.")
    out.log("It creates a .htaccess.live: This is your live .htaccess file, which will for example contain a basic auth entry, depending on your configuration.")
    out.log("It creates a symbolic link on your local machine, that points to .htaccess.local.")
    out.log("It creates a symbolic link on the remote server, that points to .htacces.live.")
    out.log("Just make sure to ignore .htaccess in your repository, as this now is a link that is context dependend (i.e. has different values on local/remote server).")
    out.log("The first argument specifies the overwrite mode. Allowed arguments are: fail, overwrite, upload.")
    out.log("fail will simply fail, if there is a .htaccess file already. This is the default behaviour.")
    out.log("overwrite will overwrite any existing .htaccess file.")
    out.log("upload will overwrite any existing .htaccess file and directly upload the .htaccess.live file.")
