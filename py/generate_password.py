from modules import engine
from modules import out
from modules import run

@engine.prepare_and_clean
def execute():
    out.log("generating password...")
    run.local('openssl rand -base64 15')


def help():
    out.log("Creates a strong random 20 characters password.", 'help')