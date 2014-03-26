// this script requires casparjs >= 1.1

ba_list = [
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

var beschluesse = new Array;
var current = 0;

function buildURL(ba)
{
  return "http://www.berlin.de/" + ba + "/bvv-online/vo040.asp";
}

function getDocs()
{
  var rows = document.querySelectorAll('#rismain_raw tbody tr');
  var ret = new Array;

  for (i = 0; i < rows.length; i++)
  {
    link = rows[i].getElementsByTagName('a');
    d    = rows[i].getElementsByTagName('td')[4];

    dcheck = d[0].innerText.split('.');
    dcheck = new Date(Date.UTC(parseInt(dcheck[2]), parseInt(dcheck[1]), parseInt(dcheck[0])));

    today = new Date();

    if (link 
    &&  link.length == 1 
    &&  !link[0].href.endsWith('?showall=true'))
    {
      ret.push({
        "description": link[0].innerText,
        "href": link[0].href,
        "date": d[0].innerText
      });
    }
  }

  return ret;
}

/*for (i = 0; i < ba_list.length; i++)
{
  
}*/

var casper = require('casper').create({
  pageSettings: 
  {
    loadImages: false,
    loadPlugins: false
  }
});

var fs = require('fs');

casper.start();

casper.open(buildURL(ba_list[current]), 
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

casper.then(function()
{
  beschluesse = beschluesse.concat(this.evaluate(getDocs));
  console.log(beschluesse.length);
})

casper.run(function() {
  // this.echo(JSON.stringify(beschluesse));
  var out = "";
  
  for (i = 0; i < beschluesse.length; i++)
  {
    out += "beschluesse[i].date" + ": " + beschluesse[i].href + "\n\n" + beschluesse[i].description + "\n\n---\n\n";
  }

  //fs.write("beschluesse.txt", out, 'w');
  this.echo(out);

  this.exit();
});
