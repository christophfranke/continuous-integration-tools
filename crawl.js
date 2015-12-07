
//get crawler
var Crawler = require("simplecrawler");

//read url from commandline
var url = process.argv.slice(2)[0];

var crawler = Crawler.crawl(url);

/*
crawler.on("fetchcomplete", function(queueItem) {
	console.log("200 Ok(", queueItem.stateData.requestTime, "ms ): ", queueItem.url);
});
*/

crawler.on("fetch404", function(queueItem) {
	console.log("404 Not Found: ", queueItem.url, " referrer: ", queueItem.referrer);
});

crawler.parseScriptTags = false;
crawler.parseHTMLComments = false;
