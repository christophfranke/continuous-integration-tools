from modules import engine
from modules import out
from modules import transfer
from modules import sync

@engine.prepare_and_clean
def execute(mode = None):
    if mode is None:
        mode = 'sync'
    out.log("synchronizing local files (" + mode + " mode)...")

    if mode == 'mirror':
        sync.download(True, True)
    if mode == 'clean':
        sync.download(False, True)
    if mode == 'sync':
        sync.download(False, False)
    if mode == 'all':
        sync.download(True, False)



def help():
    out.log("This command downloads all files that are present on the remote. It has four modes:", 'help')
    out.log('sync: Downloads all outdated files, keeps any additional local files. This is default behaviour.', 'help')
    out.log('all: Downloads all files regardless, keeps any additional local files.', 'help')
    out.log('mirror: Downloads all files regardless, deletes all files not present on the remote.', 'help')
    out.log('clean: Downloads all outdated files, deletes all files not present on the remote.', 'help')
