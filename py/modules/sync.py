import engine
import out
import os
import fnmatch
import run
import json
import hashlib

#upload local files using ftp
@out.indent
def upload():
    files_uploaded = load_md5_table()
    files_current = create_md5_table()

    files_scheduled = []

    for f in files_current:
        if not f in files_uploaded or not files_current[f] == files_uploaded[f]:
            files_scheduled.append(f)

    print files_scheduled


def md5sum(filename):
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()

def save_md5_table(md5_table):
    md5_table_file = open(engine.LOCAL_MD5_TABLE_FILE, 'w')
    json.dump(md5_table, md5_table_file)
    md5_table_file.close()

def load_md5_table():
    try:
        #load form file
        md5_table_file = open(engine.LOCAL_MD5_TABLE_FILE, 'r')
        md5_table = json.load(md5_table_file)
        md5_table_file.close()
    except:
        #if that fails: return empty table
        md5_table = {}

    #give back
    return md5_table

def create_md5_table():
    files = []
    md5_table = {}
    for root, dirnames, filenames in os.walk(engine.LOCAL_WWW_DIR):
        for filename in fnmatch.filter(filenames, '*'):
            files.append(os.path.join(root, filename))

    for f in files:
        try:
            md5_table[f] = md5sum(f)
        except IndexError:
            pass

    return md5_table
