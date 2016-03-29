from modules import engine
from modules import out
from modules import sync

@engine.prepare_and_clean
def execute(filename = None):
    out.log("uploading all files to www directory...")
    sync.upload(True)



def help():
    out.log("Uploading the complete www directory and copies it to your local www directory. Watch out, this command overwrites all files without asking.", 'help')