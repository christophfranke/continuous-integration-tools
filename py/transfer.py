import engine



def get(remote_file, local_file=None):
    if local_file is None:
        local_file = engine.get_new_local_file()
    print "Not implemented yet: [Download] " + remote_file + " -> " + local_file
    return local_file

def put(local_file, remote_file=None):
    if remote_file is None:
        remote_file = engine.get_new_remote_file()
    print "Not implemented yet: [Upload] " + local_file + " -> " + remote_file
    return remote_file
