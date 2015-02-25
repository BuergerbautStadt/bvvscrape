# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import re

from time import sleep

import sqlite3

urls = {
    "bvv": {
        "pattern": "https://www.berlin.de/{}vo040.asp?showall=true",
        "boroughs": 
        {
            u"Charlottenburg-Wilmersdorf": "ba-charlottenburg-wilmersdorf/politik/bezirksverordnetenversammlung/online/",
            u"Friedrichshain-Kreuzberg": "friedrichshain-kreuzberg/politik-und-verwaltung/bezirksverordnetenversammlung/online/",
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

def initdb():
    c = db.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type = 'table'")

    if c.rowcount <= 0:
      c.execute("CREATE TABLE proceedings ( id integer primary key autoincrement, bvv text not null, bvv_identifier text not null, first_found text not null );")
      c.execute("CREATE TABLE finds (id integer primary key autoincrement, proceeding_id integer not null, url text  not null, data text not null, fetched_date numeric not null );")

      db.commit()

    c.close()  
        

def scrape():
    bvv(urls["bvv"])

def bvv(bvvurls):
    for borough in bvvurls["boroughs"]:
        url = bvvurls["pattern"].format(bvvurls["boroughs"][borough])
        bvv_single(url)

def bvv_single(url):
    payload = { 
        "VO040FIL4": "2010-2011", 
        "filtdatum": "filter", 
        "x": "0", 
        "y": "0" 
    }

    r = requests.post(url, params=payload)

    soup = BeautifulSoup(r.text)

    c = db.cursor()

    for row in soup.select("#rismain_raw tbody tr"):
        elements = list(row.find_all('td'))
        if len(elements) < 6:
          continue

        placeholder1, link, placeholder2, fraction, date, paper_type = elements
        # filter link for Bebauungsplan, B.-Plan, etc.
        match = re.search(r"Bebauungsplan ([\w\d-]+)", unicode(link.string), re.IGNORECASE)
        if match is not None:
            ident = match.group(1)
            

    db.commit()
    c.close()
    sleep(3)


db = sqlite3.connect('data/db.sqlite')

initdb()
#scrape()

db.close()
