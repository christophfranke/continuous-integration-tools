from modules import out
from modules import engine
from modules import run

@engine.prepare_and_clean
def execute(find, replace):
    out.log('Replacing all occurences of ' + find + ' with ' + replace + ' in local database')
    run.local('php php/search-and-replace-db.php ' + engine.LOCAL_DB_HOST + ' ' + engine.LOCAL_DB_USER + ' ' + engine.LOCAL_DB_PASSWORD + ' ' + engine.LOCAL_DB_NAME + ' "' + find + '" "' + replace + '"')

def help():
    out.log('Replaces all occurences in of a string with another. Respects php serialized keys and reserializes them accordingly. A mysql script that contains all write operations performed during the replace is written to output/replace.sql.', 'help')