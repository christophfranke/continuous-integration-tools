from modules import engine
from modules import out
from modules import compile
from modules import sync

@engine.prepare_and_clean
def execute(mode = None):
    if engine.ENABLE_BUILD_SYSTEM:
        out.log('compiling first...')
        compile.all()

    if mode is None:
        mode = 'sync'

    out.log("deploying to server (" + mode + " mode)...")

    if mode == 'mirror':
        sync.upload(True, True)
    if mode == 'clean':
        sync.upload(False, True)
    if mode == 'sync':
        sync.upload(False, False)
    if mode == 'all':
        sync.upload(True, False)



def help():
    out.log("This command will synchronize your current www-directory with the remote www directory.", 'help')
    out.log('sync: Uploads all outdated files, keeps any additional remote files. This is default behaviour.', 'help')
    out.log('all: Uploads all files regardless, keeps any additional remote files.', 'help')
    out.log('mirror: Uploads all files regardless, deletes all files not present on the local filesystem.', 'help')
    out.log('clean: Uploads all outdated files, deletes all files not present on the local filesystem.', 'help')
