#!/usr/bin/env python3
import argparse
import re
import requests
import requests_cache 
requests_cache.install_cache(cache_name='iaas_cache', expire_after=86400)
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# You don't want to inadvertently break the law, so you want to know countries your systems touch
# All restrictions: https://www.ecfr.gov/current/title-15/subtitle-B/chapter-VII/subchapter-C
# Summary: https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information
# BIS has a country list, but it doesn't cover regions (such as occupied Ukraine): https://www.bis.doc.gov/index.php/policy-guidance/country-guidance/sanctioned-destinations
# "We're not going to give you a list of countries": https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/where-is-ofacs-country-list-what-countries-do-i-need-to-worry-about-in-terms-of-us-sanctions
# The most comprehensive list is here: https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information
# But it still requires interpretation. For instance the "Western Balkans" have sanctions, but are not defined here. Some sources refer to Albania, Croatia, North Macedonia, Montenegro, Bosnia and Herzegovina, Serbia, and Kosovo as the Western Balkans, while others list 7 or 11 or 3 countries depending on when the list was produced and by who.

# set up some command line options
# get the address in dotted quad notation
parser = argparse.ArgumentParser(
    prog = 'us_trade_block_list',
    description = 'Checks if OFAC sanctions have changed recently',
    epilog = 'I have no idea what I\'m doing. I am not a lawyer.')
parser.add_argument('days_back', help='how many days back should the script look for new entries')
args = parser.parse_args()

def check_ofac(date_threshold):
    treasury_url="https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information"
    ofac_page = requests.get(treasury_url)
    # parse HTML to get the real link
    soup = BeautifulSoup(ofac_page.content, "html.parser")
    ofac_string = re.compile("\/policy-issues\/financial-sanctions\/recent-actions/\d{8}")
    counter = 0
    returns = []
    for link in soup.find_all('a', href=ofac_string):
        pub_date_raw = re.search(r'\/(\d{8})', link['href'])
        date_format = "%Y%m%d"
        pub_date = datetime.strptime(pub_date_raw.group(1), date_format)
        if pub_date >= date_threshold:
            full_link = "https://home.treasury.gov" + link['href']
            returns.append(full_link)
            counter += 1
    if counter == 0:
        returns.append("No new sanctions.")
    return(returns)

def set_days_back():
    today = datetime.today()
    date_threshold = today - timedelta(days = int(args.days_back))
    return(date_threshold)

def parse_ofac(ofac_results):
    if ofac_results[0] == "No new sanctions.":
        print(ofac_results[0])
        exit()
    else:
       for link in ofac_results:
            print("You should review",link,"at your earliest convenience")

def main():
    date_threshold = set_days_back()
    ofac_results = check_ofac(date_threshold)
    parse_ofac(ofac_results)

if __name__ == "__main__":
    main()

