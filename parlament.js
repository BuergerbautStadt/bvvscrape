var XDate = require('xdate');
var fs = require('fs');

var casper = require('casper').create({
  pageSettings: 
  {
    loadImages: false,
    loadPlugins: false,
  },
  clientScripts: ['xdate.js'],
  verbose: true,
  viewportSize: // circumvent being accidentally redirected to mobile sites based on screen real estate
  {
    width: 1024,
    height: 768
  }
});

var data;

casper.start("http://www.parlament-berlin.de/de/Dokumente/Drucksachen");

casper.wait(1000);

casper.thenEvaluate(function() {
  sel = document.querySelector('#Beschreibung');
  sel.value = 'Bebauungsplan';

  applyFilter();
});

casper.wait(3000);

casper.then(function() {
  data = this.evaluate(function () {
    rows = document.querySelectorAll('#vorgaenge tbody tr');
    var result = new Array();

    for (i = 0; i < rows.length; i++)
    {
      var description = rows[i].querySelector('td > strong').innerText;
      var date  = rows[i].childNodes[4].textContent.match(/(e|ü):([0-9.]+) /i);
      var links = rows[i].querySelectorAll('a');

      if (date)
      {
        result.push({
          "description": description,
          "links": new Array()
        })

        /*for (j = 0; j < links.length; j++)
        {
          result["links"].push({
            "href": links[j].href,
            "description": links[j].innerText
          });
        }*/
      }
    }

    return result;
  });
});

casper.run(function() {
  fs.write("data/json/parlament.json", JSON.stringify(data, null, '\t'), 'w');
  casper.exit();
});
