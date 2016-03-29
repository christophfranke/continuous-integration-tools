from modules import engine
from modules import out
from modules import compile
from modules import sync

@engine.prepare_and_clean
def execute():
    if engine.ENABLE_BUILD_SYSTEM:
        out.log('compiling first...')
        compile.all()
    out.log("deploying to server...")    
    sync.upload()

def help():
    out.log("This command will synchronize your current www-directory with the remote www directory.", 'help')