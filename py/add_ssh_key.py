from modules import engine
from modules import out
from modules import ssh

@engine.prepare_and_clean
def execute():
    out.log("deploying ssh key to server authfile. After this, you do not need to type you password to login to the server.")
    ssh.add_key_to_server()


def help():
    out.log("This command appends your local keyfile from ~/.ssh/id_rsa.pub to the servers authfile ~/.ssh/authorized_keys. These values are hard coded, so if the server is not configured in a standard way, this command is not compatible.", 'help')
