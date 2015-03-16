# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2
from urlparse import urljoin, unquote
import json
from time import sleep


def fetch_links(url):

    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html)
    titles = soup.findAll("a", {"class" : "view-node"})

    result = []

    for title in titles:
        result.append(urljoin(url, unquote(title['href'].encode("utf-8"))))

    return result

def fetch_fields(url):
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html)
    result = {}

    result["title"] = soup.find("h2", {"class":"node-title"}).text.encode("utf-8").strip()
    
    fields = soup.findAll("div", {"class" : "field"})
    for field in fields:
        key = field.findNext("div", {"class": "field-label"})
        if key:
            key = key.text.encode("utf-8").strip()
            k = key.rfind(":")
            key = key[:k]
        else:
            key = "desc"    

        if key == "Ort auf Karte":
            continue
            
        value = field.findNext("div", {"class": "field-items"})
        if value:
            value = value.text.encode("utf-8")
        else:
            value = ""    

        result[key] = value

    return result
            
def geturls(url):
    urls = []
    page = 0
    while True:
        currentPage = fetch_links(url + "%&page=" + str(page))
        if len(currentPage) == 0:
            break
        urls.extend(currentPage)
        page = page + 1

    return urls

def scrape(url):
    urls = geturls(url)
    result = []

    for url in urls:
        result.append(fetch_fields(url))
        sleep(0.3)

    return result
    

# Bebauungsplan frühzeitig
# Bebauungs- und Vorhaben- und Erschließungspläne
url = "https://umwelt-beteiligung.de/berlin/bibliothek?field_verfahrensart_tid[]=138&field_verfahrensart_tid[]=131&field_geolocation_wkn_value=&keys="
result = scrape(url)

print json.dumps(result, ensure_ascii=False, indent=2)

