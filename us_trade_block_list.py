#!/usr/bin/env python3
import argparse
import re
import requests
import requests_cache 
import logging
requests_cache.install_cache(cache_name='iaas_cache', expire_after=86400)
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from observe_http_sender import ObserveHttpSender

# You don't want to inadvertently break the law, so you want to know countries your systems touch
# All restrictions: https://www.ecfr.gov/current/title-15/subtitle-B/chapter-VII/subchapter-C
# Summary: https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information
# BIS has a country list, but it doesn't cover regions (such as occupied Ukraine): https://www.bis.doc.gov/index.php/policy-guidance/country-guidance/sanctioned-destinations
# "We're not going to give you a list of countries": https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information/where-is-ofacs-country-list-what-countries-do-i-need-to-worry-about-in-terms-of-us-sanctions
# The most comprehensive list is here: https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information
# But it still requires interpretation. For instance the "Western Balkans" have sanctions, but are not defined here. Some sources refer to Albania, Croatia, North Macedonia, Montenegro, Bosnia and Herzegovina, Serbia, and Kosovo as the Western Balkans, while others list 7 or 11 or 3 countries depending on when the list was produced and by who.

# set up some command line options
parser = argparse.ArgumentParser(
    prog = 'us_trade_block_list',
    description = 'Checks if OFAC sanctions have changed recently',
    epilog = 'I have no idea what I\'m doing. I am not a lawyer.')
parser.add_argument('days_back', help='how many days back should the script look for new entries')
parser.add_argument('--obvs', action=argparse.BooleanOptionalAction, help='write output to an Observe instance', default=False)
parser.add_argument('--customer_id', help='Your Observe customer ID. Required if obvs is True', required=False)
parser.add_argument('--ingest_token', help='Your Observe data stream token. Required if obvs is True', required=False)
parser.add_argument('--observe_host_name', help='Defaults to observeinc', required=False, default="observeinc")
args = parser.parse_args()

def validate_input():
    #if obvs is true, we'll need the other arguments too
    if args.obvs:
        if args.customer_id is None:
            print("Sorry, need your Observe customer ID")
            exit()
        if args.ingest_token is None:
            print("Sorry, need your Observe ingest token")
            exit()
        if args.observe_host_name is None:
            print("Sorry, need your Observe host name")
            exit()

def set_days_back():
    today = datetime.today()
    date_threshold = today - timedelta(days = int(args.days_back))
    print("Looking for updates since",date_threshold)
    return(date_threshold)

def check_ofac(date_threshold):
    treasury_url = "https://home.treasury.gov/policy-issues/financial-sanctions/sanctions-programs-and-country-information"
    ofac_page = requests.get(treasury_url)
    # parse HTML to get the links
    soup = BeautifulSoup(ofac_page.content, "html.parser")
    ofac_string = re.compile("\/recent-actions/\d{8}")
    returns = list()
    for link in soup.find_all('a', href=ofac_string):
        pub_date_raw = re.search(r'\/(\d{8})', link.get('href'))
        date_format = "%Y%m%d"
        pub_date = datetime.strptime(pub_date_raw.group(1), date_format)
        if pub_date >= date_threshold:
            returns.append({"url":"https://ofac.treasury.gov{0}".format(link.get('href'))})
    if len(returns) == 0:
        returns.append({"status":"No new sanctions."})
    return(returns)

def main():
    logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S %z')
    logger = logging.getLogger(u"us_trade_block_list")
    logger.setLevel(logging.INFO)
    date_threshold = set_days_back()
    if args.obvs == True:
        observer = ObserveHttpSender(args.customer_id, args.ingest_token, args.observe_host_name)
        observer.log.setLevel(logging.DEBUG)
        if not observer.check_connectivity():
            print("Cannot reach " + args.observe_host_name)
            exit()
    ofac_results = check_ofac(date_threshold)
    if 'status' in ofac_results[0].keys():
        print(ofac_results[0])
        exit()
    if args.obvs:
        for result in ofac_results:
            observer.post_observation(result)
        print("Posted update to " + args.observe_host_name + ". You should review at your earliest convenience")
    else:
       for link in ofac_results:
            print("You should review",link.get('url'),"at your earliest convenience")
    if args.obvs:
        observer.flush()

if __name__ == "__main__":
    main()

