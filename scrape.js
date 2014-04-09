/** 
 * this script requires casparjs >= 1.1 with phantomjs >= 1.8
 **/

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

var ba_list = [
  "ba-charlottenburg-wilmersdorf",
  "ba-friedrichshain-kreuzberg",
  "ba-lichtenberg",
  "ba-marzahn-hellersdorf",
  "ba-mitte",
  "ba-neukoelln",
  "ba-pankow",
  "ba-reinickendorf",
  "ba-spandau",
  "ba-steglitz-zehlendorf",
  "ba-tempelhof-schoeneberg",
  "ba-treptow-koepenick"
];

var current = 0;

function makeReadable(ba)
{
  return ba.slice(3).replace(/-/, ' ').split(' ').map(function(e) {
    return e.charAt(0).toUpperCase() + e.slice(1);
  }).join(' ');
}

function buildURL(ba)
{
  return "http://www.berlin.de/" + ba + "/bvv-online/vo040.asp";
}

function evaluateURL()
{
  var rows = document.querySelectorAll('#rismain_raw tbody tr');
  var result = new Array();

  for (i = 0; i < rows.length; i++)
  {
    var link     = rows[i].getElementsByTagName('a');
    var date_col = rows[i].getElementsByTagName('td');
    
    date = date_col[4];
    if (date) 
    {
      date = date.innerText;

      xdate = date.split('.');
      xdate = new XDate(Date.UTC(parseInt(xdate[2]), parseInt(xdate[1]), parseInt(xdate[0])));

      description = link[0].innerText;
      id = description.match(/Bebauungsplan ([\w-]+)/i);

      if (id && id.length == 2)
      {
        result.push({ 
          "id": id[1],
          "link": link[0].href, 
          "description": description, 
          "date": xdate.toISOString(),
        });
      }
    }
  }

  return result;
}

function get(url)
{
  var resolutions;

  casper.echo("Processing '" + makeReadable(ba_list[current]) + "'");

  casper.start().open(url, 
  {
    'method': 'post',
    'data': 
    {
      VO040FIL1: '',
      filtvoname: 'filter',
      VO040FIL2: 'Bebauungsplan',
      filtvobetr1: 'filter',
      x: 9,
      y: 12
    }
  });

  casper.thenBypassUnless(function() {
    return this.exists("#rismain_raw tbody td.text4 a");
  }, 2);

  casper.thenClick("#rismain_raw tbody td.text4 a")
  casper.wait(750);

  casper.then(function() 
  {
    resolutions = this.evaluate(evaluateURL);
  });

  casper.run(function() {
    var out = "";

    for (i = 0; i < resolutions.length; i++)
    {
      out += resolutions[i].date + ": " + resolutions[i].link + "\n\n" + resolutions[i].description + "\n\n---\n\n";
    }

    fs.write('data/text/' + ba_list[current - 1].slice(3) +".txt", out, 'w');
    fs.write('data/json/' + ba_list[current - 1].slice(3) +".json", JSON.stringify(resolutions), 'w');
  });
}

get(buildURL(ba_list[current]));
casper.on('run.complete', function () {
  if (++current < ba_list.length)
  {
    //get(buildURL(ba_list[current]));
  } else
  {
    casper.exit();
  }
});
