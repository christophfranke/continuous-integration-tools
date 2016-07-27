from modules import engine
from modules import out
from modules import transfer

@engine.prepare_and_clean
def execute(filename = None):
    if filename is None:
        out.log('no filename specified. Please specify a file to upload as argument.')
    out.log("uploading " + engine.LOCAL_WWW_DIR + '/' + filename + "...")
    transfer.put(engine.LOCAL_WWW_DIR + '/' + filename, filename)

def help():
    out.log("Uploads a single file. Expects a filename as argument relative to the www directory.", 'help')