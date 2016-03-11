/* globals process, require */
//get crawler
var Crawler = require("simplecrawler");

//read url from commandline
var url = process.argv.slice(2)[0];

var crawler = Crawler.crawl(url);

var crawled = 0;
var error404 = 0;

crawler.on("fetchcomplete", function(queueItem) {
    var queueSize = crawler.queue.length;
    crawled++;
    console.log("200 Ok (", queueItem.stateData.requestTime, "ms ) " + crawled + " of " + queueSize + " urls left: ", queueItem.url);
});

crawler.on("fetch404", function(queueItem) {
    var queueSize = crawler.queue.length - crawled;
    crawled++;
    error404++;
    console.error("404 Not Found: ", queueItem.url, " referrer: ", queueItem.referrer);
    console.log("404 Not Found " + crawled + " of " + queueSize + " urls left: ", queueItem.url);
});

crawler.on("complete", function(){
    console.log("The maximum request latency was %dms.", crawler.queue.max("requestLatency"));
    console.log("The minimum download time was %dms.", crawler.queue.min("downloadTime"));
    console.log("The average resource size received is %d bytes.", crawler.queue.avg("actualDataSize"));
    if(error404 > 0)
        console.log("There have been 404 errors. You can find the 404 links and its first referrer in {PROJECT_ROOT}/broken_links.");
    else
        console.log("There were no internal 404 errors.");
});

crawler.parseScriptTags = false;
crawler.parseHTMLComments = false;

console.log('Start crawling ' + url);