from modules import engine
from modules import out
from modules import transfer
from modules import mysql
from modules import run

@engine.prepare_and_clean
def execute():
    out.log("testing all modules...")
    transfer.test_module()
    run.test_module()
    mysql.test_module()


def help():
    out.log("This command runs a test on all modules with a test function. if this works, your setup should be fine. If you expierience problems anyway, it is probably a bug.", 'help')
