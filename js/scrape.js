var fs     = require("fs");
var Spooky = require('spooky');

var BVVScraper = require("./bvvscraper.js");

var spooky = new Spooky({
    child: {
        transport: 'http'
    },
    casper: {
        pageSettings: 
        {
            loadImages: true,
            loadPlugins: false,
        },
        clientScripts: ['bower_components/xdate/src/xdate.js', 'bower_components/xdate/src/extras.js'],
        //verbose: true,
        viewportSize: // circumvent being accidentally redirected to mobile sites based on screen real estate
        {
            width: 1280,
            height: 960
        }
    }
}, ghostbusters);

spooky.on('error', function(err) { console.log(err); });

function ghostbusters(err) {
     if (err) {
        e = new Error('Failed to initialize SpookyJS');
        e.details = err;
        throw e;
    }

    var URLs = require('./urls.json');
    
    spooky.start("http://www.berlin.de");

    var scpr = new BVVScraper();
    for (var borough in URLs.BVVScraper)
    {
        var url = URLs.BVVScraper[borough];    
        scpr.scrape(spooky, borough, url);
    }

    spooky.run();
}
