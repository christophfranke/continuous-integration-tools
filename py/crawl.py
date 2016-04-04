from modules import engine
from modules import out
from modules import run

@engine.prepare_and_clean
def execute(domain=None):
    if domain is None:
        domain = engine.REMOTE_ROOT_URL
    if domain is None:
        out.log("REMOTE_HTTP_ROOT not set, cannot crawl online page. Crawling local page instead.", 'command', out.LEVEL_WARNING)
        domain = engine.LOCAL_ROOT_URL
    if domain is None:
        outt.log("Cannot find LOCAL_HTTP_ROOT. Please provide a domain to crawl as argument.", 'command', out.LEVEL_ERROR)
    else:
        run.local('node js/crawl.js ' + domain)

def help():
    out.log("Crawls the domain and all outgoing links. Beware of overuse, this takes a while and is quite a workload for a server.", 'help')