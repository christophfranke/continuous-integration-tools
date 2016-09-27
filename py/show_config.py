from modules import engine
from modules import out

@engine.prepare_and_clean
def execute(key = None):
    out.log('These are all configuration settings.')
    config_vars = engine.get_config(key)
    if key is None:
        for k in config_vars:
            out.log(k + ' = ' + str(config_vars[k]))
    else:
        out.log(key + ' = ' + config_vars)

def help():
    out.log("This command will print all the variables, that are set in the engines environment that look like config variables.", 'help')