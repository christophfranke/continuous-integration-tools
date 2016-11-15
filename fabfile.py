#importing all the modules
import py.sync_db
import py.create_db
import py.execute
import py.upload_command_file
import py.export_db
import py.import_db
import py.backup_db
import py.test
import py.upload_db
import py.cleanup
import py.phpinfo
import py.compile
import py.deploy
import py.sync_files
import py.search
import py.replace
import py.create_wp_files
import py.error_log
import py.mount_passwords
import py.crawl
import py.show_config
import py.setup_remote
import py.generate_password
import py.create_htaccess
import py.diff
import py.optimize_images
import py.setup_local_domain
import py.restart
import py.upload_file
import py.add_ssh_key
import py.allow_read
import py.allow_write

def get_command_list():
    #use function attribute to cache result
    try:
        if get_command_list.exposed_func_list is not None:
            return get_command_list.exposed_func_list
    except AttributeError:
        pass

    #get all omported modules in the py scope
    all_func_list = dir(globals()['py'])

    #some of those are exposed using the same name as function here
    get_command_list.exposed_func_list = []
    not_exposed_func_list = []

    #split the function list into exposed and non-exposed
    for func in all_func_list:
        if func in globals() and callable(globals()[func]):
            get_command_list.exposed_func_list.append(func)
        else:
            not_exposed_func_list.append(func)

    #return only the exposed ones, since these are garuanteed to work (at least better than the not exposed ones!)
    get_command_list.exposed_func_list.sort()
    return get_command_list.exposed_func_list

#assumes valid command. You h ave to check yourself before calling this function.
def display_help_text(command):
    module = getattr(globals()['py'], command)
    return module.help()


def help(command = None):
    import py.modules.out as out
    if command == 'sync':
        out.log('sync is not a command but a shurtcut which executes the commands sync_db and sync_files in that order.')
        out.log('It takes one argument and passes it to sync_files. Please refer to sync_db and sync_files for further details.')
        return
    if command is None or not command in get_command_list():
        if command is not None:
            out.log('Sorry, we Could not find the command ' + str(command))
        out.log('Welcome. You are using deploy tools. You can use this file in two possible ways:')
        out.log('As a fabric deploy script file, you can start all commands using the syntax')
        out.log('')
        out.log('fab <command>[:<argument1>][,<argument2>][,<argument3>] ...')
        out.log('')
        out.log('If you dont want to add fabric to your dependencies, you can also use the built in way of invoking commands:')
        out.log('')
        out.log('python fabfile.py <command> [<argument1>] [<argument2>] [<argument3>] ...')
        out.log('')
        out.log('A list of supported commands is:')

        for func in get_command_list():
            out.log(func)

        out.log('')
        out.log('For more specific help use the help command with the command as argument:')
        out.log('fab help:<command>')
        out.log('python fabfile.py help <command>')
    else:
        out.log('This is the help text for the command ' + command + ':')
        out.log('')
        display_help_text(command)


def sync_db():
    py.sync_db.execute()

def create_db():
    py.create_db.execute()

def execute(command):
    py.execute.execute(command)

def upload_command_file():
    py.upload_command_file.execute()

def export_db():
    py.export_db.execute()

def import_db(filename = None):
    py.import_db.execute(filename)

def backup_db(filename = None):
    py.backup_db.execute(filename)

def test():
    py.test.execute()

def upload_db(filename = None):
    py.upload_db.execute(filename)

def cleanup():
    py.cleanup.execute()

def phpinfo():
    py.phpinfo.execute()

def compile(types = None):
    py.compile.execute(types)

def deploy(mode = None):
    py.deploy.execute(mode)

def sync_files(mode = None):
    py.sync_files.execute(mode)

def sync(mode = None):
    py.sync_db.execute()
    py.sync_files.execute(mode)

def search(find):
    py.search.execute(find)

def replace(find, replace):
    py.replace.execute(find, replace)

def create_wp_files(overwrite = None):
    py.create_wp_files.execute(overwrite)

def error_log():
    py.error_log.execute()

def mount_passwords():
    py.mount_passwords.execute()

def crawl(domain = None):
    py.crawl.execute(domain)

def show_config(key = None):
    py.show_config.execute(key)

def setup_remote():
    py.setup_remote.execute()

def generate_password():
    py.generate_password.execute()

def create_htaccess(overwrite = None):
    py.create_htaccess.execute(overwrite)

def diff():
    py.diff.execute()

def optimize_images(quality = None):
    py.optimize_images.execute(quality)

def setup_local_domain():
    py.setup_local_domain.execute()

def restart():
    py.restart.execute()

def upload_file(filename = None):
    py.upload_file.execute(filename)

def add_ssh_key():
    py.add_ssh_key.execute()

def allow_read(location = None):
    py.allow_read.execute(location)

def allow_write(location = None):
    py.allow_write.execute(location)

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        help()
    else:
        func_name = sys.argv[1]
        arg_list = sys.argv[2:]
        if func_name in locals():
            locals()[func_name](*arg_list)
        else:
            print 'Could not find command ' + func_name
            help()
