import engine
import out

#oh no! it's a dependency: pyftpsync is required...
from ftpsync.targets import FsTarget
from ftpsync.ftp_target import FtpTarget
from ftpsync.synchronizers import UploadSynchronizer

#upload local files using ftp
@out.indent
def upload():
    #local filesystem
    local = FsTarget(engine.LOCAL_WWW_DIR)
    #ftp target
    remote = FtpTarget('/' + engine.REMOTE_WWW_DIR, engine.FTP_HOST, username = engine.FTP_USER, password = engine.FTP_PASSWORD, tls=True)
    #options
    opts = {"force": False, "delete_unmatched": True, "verbose": engine.LOG_LEVEL, "dry_run" : False}

    #run
    s = UploadSynchronizer(local, remote, opts)
    s.run()
