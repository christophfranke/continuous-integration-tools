from modules import engine
from modules import out
from modules import run


@engine.prepare_and_clean
def execute(types = None):

    if not engine.ENABLE_BUILD_SYSTEM:
        out.log('The build system is not enabled. Make sure you have set the ENABLE_BUILD_SYSTEM set to True in your config. Also note, that you will have to specify a SRC_URL and a BUILD_URL in you project config.', 'command', out.LEVEL_ERROR)
        return

    #compile all by default
    if types is None:
        types = 'all'

    #compile less
    if types == 'all' or types == 'less':
        out.log('compiling less files...')
        run.local('cd ' + engine.SCRIPT_DIR + ' && make ' + engine.MAKEFILE_VARS + ' less')

    #compile js
    if types == 'all' or types == 'js':
        out.log('compiling js files')
        local('cd ' + SCRIPT_DIR + ' && make ' + MAKEFILE_VARS + ' js')

    #compile mo
    if types == 'all' or types == 'mo':
        out.log('compiling mo files')

        engine.compile_mo_files()


def help():
    out.log('Compiles less, js and mo files. Takes a parameter specifying what to compile, options are less, js, mo, all (default).', 'help')