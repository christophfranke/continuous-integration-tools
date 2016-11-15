from modules import engine
from modules import out
from modules import compile
from modules import sync

@engine.prepare_and_clean
def execute(mode = None, server_owned = None):
    if engine.ENABLE_BUILD_SYSTEM:
        out.log('compiling first...')
        compile.all()

    if mode is None:
        mode = 'sync'
    if mode == 'server-owned':
        if server_owned is None:
            mode = 'sync'
        else:
            mode = server_owned
        server_owned = 'server-owned'

    out.log("deploying to server (" + mode + " mode)...")
    if server_owned == 'server-owned':
        out.log("overwriting server owned files (server-owned mode).")

    if mode == 'mirror':
        sync.upload(True, True, server_owned)
    if mode == 'clean':
        sync.upload(False, True, server_owned)
    if mode == 'sync':
        sync.upload(False, False, server_owned)
    if mode == 'all':
        sync.upload(True, False, server_owned)

    out.log("invalid mode, did nothing.", 'command', out.LEVEL_ERROR)



def help():
    out.log("This command will synchronize your current www-directory with the remote www directory.", 'help')
    out.log('sync: Uploads all outdated files, keeps any additional remote files. This is default behaviour.', 'help')
    out.log('all: Uploads all files regardless, keeps any additional remote files.', 'help')
    out.log('mirror: Uploads all files regardless, deletes all files not present on the local filesystem.', 'help')
    out.log('clean: Uploads all outdated files, deletes all files not present on the local filesystem.', 'help')
    out.log('', 'help')
    out.log('Certain direcories are considered to be server owned. These are directories we expect to change on a live site by user or site owner.', 'help')
    out.log('Those directories will be skipped for uploading modified files. New files will still be uploaded, but overwriting a file is potentially destructive.', 'help');
    out.log('You can force uploading modified fiels to those directories by additionally specifying the argument "server-owned" (without quotation marks).', 'help')
    out.log('You can specify the server-owned argument alone (will default to sync mode) or with one of the other arguments. The order of arguments does not matter.', 'help');
