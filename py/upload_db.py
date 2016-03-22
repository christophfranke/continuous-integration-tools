from modules import engine
from modules import run
from modules import out

@engine.prepare_and_clean
def execute():
    out.log("[command] uploading database...", out.LEVEL_INFO)
    out.log("[command] Error: Not yet implemented.", out.LEVEL_ERROR)


def help():
    out.log("Uploads the database to the production server. Note that this is overwriting all files on the server.", out.LEVEL_INFO)