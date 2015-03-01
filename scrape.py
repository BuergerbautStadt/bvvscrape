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

    c.execute("CREATE TABLE IF NOT EXISTS proceedings ( id integer primary key autoincrement, borough text not null, bvv_identifier text not null, first_found text not null );")
    c.execute("CREATE TABLE IF NOT EXISTS finds (id integer primary key autoincrement, proceeding_id integer not null, url text  not null, data text not null, fetched_date text not null );")
    c.execute("CREATE TABLE IF NOT EXISTS files (id integer primary key autoincrement, find_id integer not null, url text not null );")

    db.commit()

    c.close()  
        

def scrape():
    bvv(urls["bvv"])

def bvv(bvvurls):
    for borough in bvvurls["boroughs"]:
        url = bvvurls["pattern"].format(bvvurls["boroughs"][borough])
        bvv_single(borough, url)

def bvv_single(borough, url, request_range = "2010-2011"):
    print(u"Scraping BVV {}".format(borough))
    sleep(1)

    payload = { 
        "VO040FIL4": request_range, 
        "filtdatum": "filter", 
        "x": "0", 
        "y": "0" 
    }

    r = requests.post(url, params=payload)

    soup = BeautifulSoup(r.text)

    for row in soup.select("#rismain_raw tbody tr"):
        elements = list(row.find_all('td'))
        if len(elements) < 6:
          continue

        placeholder1, link, placeholder2, fraction, date, paper_type = elements
        # filter link for Bebauungsplan, B.-Plan, etc.
        match = re.search(r"(Bebauungsplan|B\.-Plan) ([\w\d-]+)", unicode(link.string), re.IGNORECASE)

        if match is not None:
            ident = unicode(match.group(2))
            data  = { 
                "borough": borough, 
                "bvv_identifier": ident, 
                "description": link.string, 
                "link": "https://www.berlin.de{}".format(link.a.get('href')), 
                "date": date.string
            }

            data["files"] = bvv_get_files(data["link"])

            add_find(data)

    

def bvv_get_files(url):
    sleep(1)
    r = requests.get(url)

    soup = BeautifulSoup(r.text)

    files = list()

    for document in soup.select('#rismain_raw .tk1 .me1 td[align=center] form'):
        # create prepared requests for each document
        params = dict()

        for ipt in document.input:
            if ipt.get('name') == "DOLFDNR":
                params["DOLFDNR"] = ipt.get('value')

            if ipt.get('name') == "options":
                params["options"] = ipt.get('value')

        prep = requests.Request(
            'POST', 
            "https://www.berlin.de{}".format(document.get("action")), 
            params
        ).prepare()

        files.append({ "name": document.select('input[type=submit]')[0].get('value'), "request": prep })

    return files

def add_find(data):
    if data["date"] is not None:
        data["date"] = 'now'

    # check if it is in the proceedings
    check_proceeding_sql = "SELECT id FROM proceedings WHERE bvv_identifier = ?;"

    c = db.cursor()
    c.execute(check_proceeding_sql, (data["bvv_identifier"],))
    c.fetchall()

    insert_id = None
    if c.rowcount < 1:
        insert_proceeding_sql = "INSERT INTO proceedings VALUES(NULL, ?, ?, ?);"
        c.execute(insert_proceeding_sql, (data["borough"], data["bvv_identifier"], data["date"]))
        db.commit()

        insert_id = c.lastrowid
    
    check_find_sql = "SELECT FROM finds WHERE url = ? AND fetched_date = ?"
    c.execute(check_find_sql, (data["link"], data["date"]))
    c.fetchall()

    if c.rowcount < 1 and insert_id is not None:
        insert_find_sql = "INSERT INTO finds VALUES(NULL, ?, ?, ?, ?);"
        c.execute(insert_find_sql, (insert_id, data["link"], data["description"], data["date"]))
        db.commit()

    # TODO: store files


################################################################################
db = sqlite3.connect('db.sqlite')

initdb()
scrape()

db.close()
################################################################################
