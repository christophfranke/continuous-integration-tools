from modules import out
from modules import engine
from modules import run

@engine.prepare_and_clean
def execute(find):
    out.log('Searching local database for ' + find)
    run.local('php php/search-and-replace-db.php ' + engine.LOCAL_DB_HOST + ' ' + engine.LOCAL_DB_USER + ' ' + engine.LOCAL_DB_PASSWORD + ' ' + engine.LOCAL_DB_NAME + ' "' + find + '"')

def help():
    out.log('Search the local database for a given string. Shows a summary at the end of the search. A detailed output is being written to output/search.log', 'help')