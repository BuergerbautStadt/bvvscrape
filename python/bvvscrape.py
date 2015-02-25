# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests

urls = {
  "bvv": {
    "pattern": "https://www.berlin.de/{}vo040.asp?showall=true",
    "boroughs": 
    {
      u"Charlottenburg-Wilmersdorf": "ba-charlottenburg-wilmersdorf/politik/bezirksverordnetenversammlung/online/",
      u"Friedrichshain-Kreuzberg": "friedrichshain-kreuzberg/politik-und-verwaltung/bezirksverordnetenversammlung/online/ba-",
      u"Lichtenberg": "ba-lichtenberg/bvv-online/",
      u"Marzahn-Hellersdorf": "ba-marzahn-hellersdorf/bvv-online/",
      u"Mitte": "ba-mitte/politik-und-verwaltung/bezirksverordnetenversammlung/online/",
      u"Neukölln": "ba-neukoelln/bvv-online/",
      u"Pankow": "ba-pankow/politik-und-verwaltung/bezirksverordnetenversammlung/online/",
      u"Reinickendorf": "ba-reinickendorf/politik-und-verwaltung/bezirksverordnetenversammlung/online/",
      u"Spandau": "ba-spandau/bvv-online/",
      u"Steglitz-Zehlendorf": "ba-steglitz-zehlendorf/politik-und-verwaltung/bezirksverordnetenversammlung/online/",
      u"Tempelhof-Schöneberg": "ba-tempelhof-schoeneberg/bvv-online/",
      u"Treptow-Köpenick": "ba-treptow-koepenick/politik-und-verwaltung/bezirksverordnetenversammlung/online/"
    }
  }

}

def bvv_single(url):
  payload = { "VO040FIL4": "2010-2011", "filtdatum": "filter", "x": "0", "y": "0" }
  r = requests.post(url, params=payload)

  soup = BeautifulSoup(r.text)

  for row in soup.select("#rismain_raw tbody tr"):
    # find Bebauungsplan, B.-Plan, etc.

def bvv(bvvurls):
  for borough in bvvurls["boroughs"]:
    url = bvvurls["pattern"].format(bvvurls["boroughs"][borough])
    print(url)

def scrape():
  bvv(urls["bvv"])

scrape()
