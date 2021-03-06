from modules import engine
from modules import out

@engine.prepare_and_clean
def execute():
    out.log("cleaning up the local tmp directory")
    engine.clean_local_tmp_dir()
    out.log("cleaning up the remote tmp directory")
    engine.clean_remote_tmp_dir()
    if engine.ENABLE_BUILD_SYSTEM:
        out.log("cleaning up local build directory")
        engine.clean_build_dir()


def help():
    out.log("deletes all files in the local and remote tmp directories.", 'help')