from modules import engine
from modules import out
from modules import apache

@engine.prepare_and_clean
def execute(location = None):
    if location is None:
        location = 'local'
    if location != 'local' and location != 'remote':
        out.log(location + ' is not a valid host. Allowed hosts are local and remote.', 'command', out.LEVEL_ERROR)
        engine.quit()
    out.log('allowing read access for all files to all users on ' + location + ' host.')
    apache.allow_read(location)


def help():
    out.log("Allow read to all users on local or remote host. First parameter is the host, which can be local or remote and defaults to local.", 'help')