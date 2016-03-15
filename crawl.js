/* globals process, require */
//get crawler
var Crawler = require("simplecrawler");

//read url from commandline
var url = process.argv.slice(2)[0];

var crawler = Crawler.crawl(url);

var error404 = 0;

var broken_links_buffer = '';
var cookie_buffer = '';


crawler.on("fetchcomplete", function(queueItem) {
    var queueSize = crawler.queue.length;
    var number_of_cookies = 0;
    if(queueItem.stateData.headers['set-cookie'] !== 'undefined')
        for(var cookie in queueItem.stateData.headers['set-cookie'])
        {
            number_of_cookies++;
            cookie_buffer += queueItem.url + ' set ' + queueItem.stateData.headers['set-cookie'][cookie] + " - referred by: " + queueItem.referrer + "\n";
        }

    console.log("200 Ok (", queueItem.stateData.requestTime, "ms, " + number_of_cookies + " cookies ) " + (crawler.queue.oldestUnfetchedIndex + 1) + " of " + queueSize + " urls: ", queueItem.url);

    //console.log(crawler.queue);
});

crawler.on("fetch404", function(queueItem) {
    error404++;
    broken_links_buffer += queueItem.url + " not found, referrer: " + queueItem.referrer + "\n";
    console.log("404 Not Found: ", queueItem.url);
});

crawler.on("complete", function(){
    var fs = require('fs');
    fs.writeFileSync('output/cookies.txt', cookie_buffer);
    fs.writeFileSync('output/broken_links.txt', broken_links_buffer);
    console.log("The maximum request latency was %dms.", crawler.queue.max("requestLatency"));
    console.log("The minimum download time was %dms.", crawler.queue.min("downloadTime"));
    console.log("The average resource size received is %d bytes.", crawler.queue.avg("actualDataSize"));
    if(error404 > 0)
        console.log("There have been 404 errors.");
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

