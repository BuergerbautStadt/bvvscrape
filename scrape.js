// this script requires casparjs >= 1.1
var casper = require('casper').create({
  pageSettings: 
  {
    loadImages: false,
    loadPlugins: false
  }
});

var fs = require('fs');

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

function buildURL(ba)
{
  return "http://www.berlin.de/" + ba + "/bvv-online/vo040.asp"; //"http://www.berlin.de/" + ba + "/bvv-online/vo040.asp";
}

function getDocs()
{
  var rows = document.querySelectorAll('#rismain_raw tbody tr');
  var result = new Array;

  for (i = 0; i < rows.length; i++)
  {
    var link = rows[i].getElementsByTagName('a');
    var date_col = rows[i].getElementsByTagName('td');
    
    date = date_col[4];
    if (date) date = date.innerText;

    result.push({ "link": link[0].href, "description": link[0].innerText, "date": date });
  }

  return result;
}

function type(obj){
    return Object.prototype.toString.call(obj).slice(8, -1);
}

function get(url)
{
  var beschluesse = new Array;

  casper.echo(ba_list[current]);

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
  }).then(function()
  {
    beschluesse = this.evaluate(getDocs);
  }).run(function() {
    var out = "";

    for (i = 0; i < beschluesse.length; i++)
    {
      //dcheck = beschluesse[i].date.split('.');
      //dcheck = new Date(Date.UTC(parseInt(dcheck[2]), parseInt(dcheck[1]), parseInt(dcheck[0])));

      //console.log(dcheck);

      out += beschluesse[i].date + ": " + beschluesse[i].link + "\n\n" + beschluesse[i].description + "\n\n---\n\n";
    }

    fs.write("beschluesse_" + ba_list[current - 1] +".txt", out, 'w');
  });
}

get(buildURL(ba_list[current]));
casper.on('run.complete', function () {
  if (++current < ba_list.length)
  {
    get(buildURL(ba_list[current]));
  } else
  {
    casper.exit();
  }
});
