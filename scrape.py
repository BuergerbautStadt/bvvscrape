# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import re

from time import sleep

import sqlite3
import pickle

import sys

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
    },
    "umweltbeteiligung": {
      "library": "https://umwelt-beteiligung.de/berlin/bibliothek"
    }
}

def initdb():
    c = db.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS proceedings ( id integer primary key autoincrement, borough text not null, bvv_identifier text not null, first_found text not null );")
    c.execute("CREATE TABLE IF NOT EXISTS finds (id integer primary key autoincrement, proceeding_id integer not null, url text  not null, data text not null, fetched_date text not null );")
    c.execute("CREATE TABLE IF NOT EXISTS files (id integer primary key autoincrement, find_id integer not null, filename text not null, request text not null );")

    db.commit()

    c.close()  
        

def scrape():
    request_year = 2015
    if len(sys.argv) >= 2 and sys.argv[1].isdigit():
        request_year = int(sys.argv[1])

    bvv(request_year)
    agh()
    umweltbeteiligung()


def bvv(request_year):
    request_range = bvv_request_year(request_year)

    for borough in urls["bvv"]["boroughs"]:
        url = urls["bvv"]["pattern"].format(urls["bvv"]["boroughs"][borough])
        bvv_single(borough, url, request_range)

def bvv_request_year(numeric_year):
    return "{}-{}".format(numeric_year-1, numeric_year)

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
        match = re.search(r"(Bebauungsplan|B(\.)?-Plan) ([\w\d]+-[\w\d]+)", unicode(link.string), re.IGNORECASE)

        if match is not None:
            ident = unicode(match.group(2))
            print("  {}".format(ident))
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

        for ipt in document.select('input[type=hidden]'):
            if ipt['name'] == "DOLFDNR":
                params["DOLFDNR"] = ipt['value']

            if ipt['name'] == "VOLFDNR":
                params["VOLFDNR"] = ipt['value']

            if ipt['name'] == "options":
                params["options"] = ipt['value']

        # http://docs.python-requests.org/en/latest/user/advanced/#prepared-requests
        prep = requests.Request(
            'POST', 
            "https://www.berlin.de{}".format(document.get("action")), 
            params
        ).prepare()

        if "DOLFDNR" in params: 
            print("    - {}".format(params["DOLFDNR"]))
        else:
            print("    - {}".format(params["VOLFDNR"]))

        files.append({ "name": document.select('input[type=submit]')[0].get('value'), "request": pickle.dumps(prep) })

    return files

def agh():
    pass

def umweltbeteiligung():
    sleep(1)

    url = urls["umweltbeteiligung"]["library"]

def add_find(data):
    if data["date"] is None:
        data["date"] = 'now'

    # check if it is in the proceedings
    check_proceeding_sql = "SELECT id FROM proceedings WHERE bvv_identifier = ?;"

    c = db.cursor()
    c.execute(check_proceeding_sql, (data["bvv_identifier"],))
    proceedings = c.fetchall()

    proceeding_id = None
    if c.rowcount < 1:
        insert_proceeding_sql = "INSERT INTO proceedings VALUES(NULL, ?, ?, ?);"
        c.execute(insert_proceeding_sql, (data["borough"], data["bvv_identifier"], data["date"]))
        db.commit()

        proceeding_id = c.lastrowid
    else:
        proceeding_id = proceedings[0]["id"]
    
    check_find_sql = "SELECT * FROM finds WHERE url = ? AND fetched_date = ?;"
    c.execute(check_find_sql, (data["link"], data["date"]))
    finds = c.fetchall()

    current_find_id = None
    if c.rowcount < 1 and proceeding_id is not None:
        insert_find_sql = "INSERT INTO finds VALUES(NULL, ?, ?, ?, ?);"
        c.execute(insert_find_sql, (proceeding_id, data["link"], data["description"], data["date"]))
        db.commit()

        current_find_id = c.lastrowid

    check_file_sql = "SELECT * FROM files WHERE find_id = ?;"
    c.execute(check_file_sql, (current_find_id,))

    if c.rowcount < 1 and current_find_id is not None:
        for file_info in data["files"]:
            insert_file_sql = "INSERT INTO files VALUES(NULL, ?, ?, ?);"
            c.execute(insert_file_sql, (current_find_id, file_info["name"], file_info["request"]))
            db.commit()

################################################################################
db = sqlite3.connect('db.sqlite')

initdb()
scrape()

db.close()
################################################################################
