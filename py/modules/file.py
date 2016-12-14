from codecs import open

import os

import out

def local_not_empty(filename):
    if not os.path.isfile(filename):
        return False
    return os.path.getsize(filename) > 0


def write_local(content, suffix = None, permissions = None, filename = None):
    import engine
    if permissions is not None:
        out.log('Error: Setting permissions in write_local_file is not implemented yet.', 'engine', out.LEVEL_ERROR)
    if filename is None:
        filename = engine.get_new_local_file(suffix)
    if isinstance(content, str):
        content = unicode(content, 'utf-8' )
    file = open(filename, 'w', encoding='utf-8')
    file.write(content)
    file.close()
    return filename

def write_remote(content, suffix = None, permissions = None, filename = None):
    import engine
    import transfer
    local_file = write_local(content, suffix)
    if filename is None:
        remote_file = engine.get_new_remote_file(suffix)
    else:
        remote_file = filename
    transfer.put(local_file, remote_file, permissions = permissions)
    return remote_file

def read_local(filename):
    file = open(filename, 'r', encoding='utf-8')
    data = file.read()
    file.close()
    return data

def read_remote(filename):
    import transfer
    local_file = transfer.get(filename)
    return read_local(local_file)

def md5sum(filename):
    import engine
    import hashlib
    md5 = hashlib.md5()
    with open(os.path.join(engine.LOCAL_WWW_DIR, filename), 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()

def save_md5_table(md5_table, md5_table_file):
    import engine
    import json
    md5_table_file = open(engine.LOCAL_MD5_TABLE_FILE, 'w', encoding='utf-8')
    json.dump(md5_table, md5_table_file)
    md5_table_file.close()


