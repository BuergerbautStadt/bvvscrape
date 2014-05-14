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

casper.waitFor(function () {
  return this.evaluate(function() {
    return $('#indicator').css('display') == 'none';
  });
});

casper.thenEvaluate(function() {
  sel = document.querySelector('#Beschreibung');
  sel.value = 'Bebauungsplan';

  // this website, it's crazy
  applyFilter();
});

casper.waitFor(function () {
  return this.evaluate(function() {
    return $('#indicator').css('display') == 'none';
  });
});

casper.then(function() {
  data = this.evaluate(function () {
    rows = document.querySelectorAll('#vorgaenge tbody tr');
    var result = new Array();

    for (i = 0; i < rows.length; i++)
    {
      var description = rows[i].querySelector('td > strong').innerText;

      var id = description.match(/Bebauungsplans? ([\w-]+)/i);

      var date  = rows[i].childNodes[4].textContent.match(/(e|ü):([0-9.]+) /i);
      
      var documents = new Array();

      var link = rows[i].childNodes[0].textContent;

      $('#vorgaenge tbody tr:nth-child('+i+') a').each(function() { documents.push(this.href) });

      if (id)
      {
        d = date[2].split('.');
        d = new Date(parseInt(d[2]), parseInt(d[1]), parseInt(d[0]));
        
        xdate = new XDate(d);

        result.push({
          "description": description,
          "documents": documents,
          "date": xdate.toISOString(),
          "id": id[1],
          "link": "http://www.parlament-berlin.de/de/Dokumente/Drucksachen?Vorgang="+link
        });
      }
    }

    return result;
  });
});

casper.run(function() {
  fs.write("data/json/parlament.json", JSON.stringify(data, null, '\t'), 'w');
  casper.exit();
});
