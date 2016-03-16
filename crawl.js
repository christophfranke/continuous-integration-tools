/* globals process, require */
//get crawler
var Crawler = require("simplecrawler");
var now = require("performance-now");

//read url from commandline
var url = process.argv.slice(2)[0];

var crawler = Crawler.crawl(url);

var error404 = 0;

var broken_links_buffer = '';
var cookie_buffer = '';

function max(a, b)
{
    return (a > b ? a:b);
}
function min(a, b)
{
    return (a < b ? a:b);    
}

crawler.on("fetchcomplete", function(queueItem) {
    var queueSize = crawler.queue.length;
    var number_of_cookies = 0;
    if(queueItem.stateData.headers['set-cookie'] !== 'undefined')
    {
        for(var cookie in queueItem.stateData.headers['set-cookie'])
        {
            number_of_cookies++;
            cookie_buffer += queueItem.url + ' set ' + queueItem.stateData.headers['set-cookie'][cookie] + " - referred by " + queueItem.referrer + "\n";
        }
    }

    var percentageDone = (crawler.queue.oldestUnfetchedIndex) / (queueSize);
    if(percentageDone === 0)
        percentageDone = 0.01;
    var estimationError = 1.0 - min(2.0*percentageDone, 1.0);
    var timeLeft = ((0.001 + 0.001*estimationError)*(now() - startTime)*(1.0 / (percentageDone) - 1.0)).toFixed(1);
    if (crawler.queue.oldestUnfetchedIndex < 5 || percentageDone < 0.1)
        timeLeft = '?';
    //var timeEstimated = 35 - 0.001*(now() - startTime);
    //console.log(timeEstimated + " vs " + timeLeft + " at " + 100*percentageDone + "%" + ", estimationErrorIntensity: " + estimationError);
    console.log("200 Ok (", queueItem.stateData.requestTime, "ms, " + number_of_cookies + " cookies ) " + (crawler.queue.oldestUnfetchedIndex + 1) + " of " + (queueSize + 1) + " urls (" + timeLeft + " sec left): ", queueItem.url);

    //console.log(crawler.queue);
});

crawler.on("fetch404", function(queueItem) {
    error404++;
    broken_links_buffer += queueItem.url + " not found, referrer: " + queueItem.referrer + "\n";
    console.log("404 Not Found: ", queueItem.url);
});

crawler.on("complete", function(){
    var crawlTime = (0.001*(now() - startTime)).toFixed(2);
    var relCrawlTime = ((now() - startTime) / crawler.queue.length).toFixed(0);
    var fs = require('fs');
    fs.writeFileSync('output/cookies.txt', cookie_buffer);
    fs.writeFileSync('output/broken_links.txt', broken_links_buffer);
    console.log("The maximum request latency was %dms.", crawler.queue.max("requestLatency"));
    console.log("The minimum download time was %dms.", crawler.queue.min("downloadTime"));
    console.log("The average resource size received is %d bytes.", crawler.queue.avg("actualDataSize"));
    console.log("Crawling " + crawler.queue.length + " pages took " + crawlTime + " seconds (" + relCrawlTime + "ms per item).");
    if(error404 > 0)
        console.log("There have been 404 errors (" + error404 + " total).");
    else
        console.log("There were no 404 errors.");
});

crawler.addFetchCondition( function(parsedURL, queueItem){
    if (queueItem.host != crawler.host)
    {
        //console.log("Skipped " + parsedURL.protocol + '://' + parsedURL.host + parsedURL.path);
        return false;
    }

    return true;
});


//configure the crawler
crawler.parseScriptTags = true;
crawler.parseHTMLComments = false;
crawler.filterByDomain = false;
crawler.acceptCookies = true;
crawler.downloadUnsupported = false;

console.log('Start crawling ' + url);
var startTime = now();

