#!/usr/bin/env python3
import argparse
import re
import requests
import requests_cache 
import logging
requests_cache.install_cache(cache_name='brompton_cache', expire_after=86400)
from bs4 import BeautifulSoup
import os

# Looking for a deal on a Brompton? This script will regularly check the renewed site

# set up some command line options
parser = argparse.ArgumentParser(
    prog = 'check_brompton_renewed',
    description = 'Checks if Brompton\'s renewed bike list has changed. Delete cache file to reset.',
    epilog = 'I have no idea what I\'m doing.')
parser.add_argument('--site', help='Brompton site, defaults to US', required=False, default="US")
args = parser.parse_args()

def validate_input():
    www_list = ("de", "gr", "jp", "ae")
    if (args.site in www_list):
        logging.info("changing site argument from " + args.site + " to www")
        args.site = "www"
    global_list = ("ad", "ar", "au", "at", "bh", "be", "br", "ca", "cl", "cn", "hk", "mo", "co", "hr", "cz", "dk", "ee", "fi", "fr", "de", "gr", "hu", "in", "id", "ie", "il", "it", "jp", "kw", "lv", "lt", "lu", "my", "mx", "nl", "nz", "no", "om", "pe", "ph", "pl", "pt", "qa", "kp", "ro", "ru", "sa", "sg", "sk", "si", "es", "se", "ch", "tw", "th", "tr", "ae", "us", "uy")
    if (args.site in global_list):
        logging.info("changing site argument from " + args.site + " to global")
        args.site = "global"

def check_site():
    url = "https://" + args.site + ".brompton.com/c/bikes/renewed"
    brompton_page = requests.get(url)
    returns = list()
    # parse HTML to get the links
    soup = BeautifulSoup(brompton_page.content, "html.parser")
    for link in soup.find_all('a'):
        if (re.match(r'\/p\/.*-renewed-.*', link.get('href'))):
            return_link = (link.get('href'))
            return_url = "https://" + args.site + ".brompton.com" + return_link
            returns.append(return_url)
    logging.info("Found ", len(returns), " bikes on the site")
    if len(returns) == 0:
        returns.append({"status":"No new bikes."})
    return(returns)

def main():
    logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S %z')
    logger = logging.getLogger(u"check_brompton_renewed")
    logger.setLevel(logging.INFO)
    cache_file = "renewed_brompton_cache.txt"
    validate_input()
    # get the latest from the site
    brompton_results = check_site()   
    if 'status' in brompton_results[0]:
        print(brompton_results[0])
        exit()
    # make sure there's a cache file
    if not os.path.exists(cache_file):
        open(cache_file, 'a').close()
    # read the old cache
    with open(cache_file, 'r') as cfiler:
        cached_list = [line.rstrip('\n') for line in cfiler]
    new_list = list()
    for link in brompton_results:
        logging.info("Bike found:", link)
        new_list.append(link)
    #write the new cache
    with open(cache_file, 'w') as cfilew:
        for bike in new_list:
            cfilew.write(bike + '\n')
    # compare results
    discovery = set(new_list) ^ set(cached_list)
    for discovered_bike in discovery:
        logging.info("New bike found:", discovered_bike)
        print("New bike found:", discovered_bike)

if __name__ == "__main__":
    main()

