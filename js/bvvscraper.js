var exports = module.exports = function() {}

exports.prototype.constructor = function() {}

exports.prototype.scrape = function(spooky, borough, url)
{
    spooky.thenOpen(url);

    spooky.thenEvaluate(function(borough) {
        this.capture(borough+'.png');
    }, borough);
}
