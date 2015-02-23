var exports = module.exports = BVVScraper;

var BVVScraper = function()
{

}

BVVScraper.prototype.constructor = function() {}

BVVScraper.prototype.scrape = function(spooky, borough, url)
{
    spooky.thenOpen(url);

    spooky.thenEvaluate(function(borough) {
        this.capture(borough+'.png');
    }, borough);
}
