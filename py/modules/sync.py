import engine
import out
import os
import fnmatch
import run
import json
import hashlib
import transfer

#upload local files using ftp
@out.indent
def upload(force_upload = False):
    #remember the files we uploaded last time
    files_uploaded = load_md5_table()
    #recalculate all md5 hashes
    files_current = create_md5_table()

    #check which have changed
    files_scheduled = []
    for f in files_current:
        if force_upload or not f in files_uploaded or not files_current[f] == files_uploaded[f]:
            out.log('scheduled for upload: ' + f, 'sync', out.LEVEL_INFO)
            files_scheduled.append(f)

    #uplaod new or modified files
    if len(files_scheduled) > 0:
        out.log('uploading ' + str(len(files_scheduled)) + ' files.', 'sync')
        transfer.put_multiple(files_scheduled)
    else:
        out.log('nothing to do, all files up to date.', 'sync')

    #save current list to file
    save_md5_table(files_current)


def md5sum(filename):
    md5 = hashlib.md5()
    with open(os.path.join(engine.LOCAL_WWW_DIR, filename), 'rb') as f:
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
        #for filename in fnmatch.filter(filenames, '*'):
        for filename in filenames:
            abs_file = os.path.join(root, filename)
            rel_file = abs_file[len(engine.LOCAL_WWW_DIR)+1:]
            files.append(rel_file)

    for f in files:
        try:
            md5_table[f] = md5sum(f)
        except IndexError:
            pass

    return md5_table
