#!/usr/bin/env python3
import ipaddress
import argparse
import re
import json
import requests
import requests_cache
requests_cache.install_cache('iaas_cache')
from bs4 import BeautifulSoup

# only supporting ipv4 addresses at this time
# always goes to the internet instead of caching and comparing versions

# set up some command line options
# get the address in dotted quad notation
parser = argparse.ArgumentParser(
    prog = 'ip_is_iaas',
    description = 'Checks if an IPv4 address belongs to an IaaS provider',
    epilog = 'I have no idea what I\'m doing')
parser.add_argument('ip_input')
args = parser.parse_args()

# check that it's a dotted quad address
if re.match("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", args.ip_input):
    try:
        addr = ipaddress.IPv4Address(args.ip_input)
    except ipaddress.AddressValueError:
        print(args.ip_input, 'is not a valid IPv4 address')
        exit()
    else:
        if addr.is_multicast:
            print(args.ip_input, 'is an IPv4 multicast address')
            exit()
        if addr.is_private:
            print(args.ip_input, 'is an IPv4 private address')
            exit()
        if addr.is_global:
            print(args.ip_input, 'is an IPv4 global address')
        if addr.is_link_local:
            print(args.ip_input, 'is an IPv4 link-local address')
            exit()
        if addr.is_unspecified:
            print(args.ip_input, 'is an IPv4 site-local address')
            exit()
        if addr.is_reserved:
            print(args.ip_input, 'is an IPv4 reserved address')
            exit()
        if addr.is_loopback:
            print(args.ip_input, 'is an IPv4 loopback address')
            exit()
else:
    try:
        addr = ipaddress.IPv6Address(args.ip_input)
    except ipaddress.AddressValueError:
        print(args.ip_input, 'is not a valid IPv4 or IPv6 address')
        exit()
    else:
        if addr.is_multicast:
            print(args.ip_input, 'is an IPv6 multicast address')
            exit()
        if addr.is_private:
            print(args.ip_input, 'is an IPv6 private address')
            exit()
        if addr.is_global:
            print(args.ip_input, 'is an IPv6 global address, Unsupported.')
            exit()
        if addr.is_link_local:
            print(args.ip_input, 'is an IPv6 link-local address')
            exit()
        if addr.is_site_local:
            print(args.ip_input, 'is an IPv6 site-local address')
            exit()
        if addr.is_reserved:
            print(args.ip_input, 'is an IPv6 reserved address')
            exit()
        if addr.is_loopback:
            print(args.ip_input, 'is an IPv6 loopback address')
            exit()
        if addr.ipv4_mapped:
            print(args.ip_input, 'is an IPv6 mapped IPv4 address.')
            exit()
        if addr.sixtofour:
            print(args.ip_input, 'is an IPv6 RFC 3056 address')
            exit()
        if addr.teredo:
            print(args.ip_input, 'is an IPv6 RFC 4380 address')
            exit()

# subroutine to compare an ip with a subnet range
def in_net_test(iprange,iaas):
    for ip in iprange:
        address=ipaddress.ip_network(args.ip_input)
        network=ipaddress.ip_network(ip)
        if address.subnet_of(network):
            print(args.ip_input,"is in",str(network),"which belongs to",iaas)
            exit()

# AWS https://docs.aws.amazon.com/general/latest/gr/aws-ip-ranges.html
aws_ip_ranges = requests.get('https://ip-ranges.amazonaws.com/ip-ranges.json').json()['prefixes']
amazon_ips = [item['ip_prefix'] for item in aws_ip_ranges]
in_net_test(amazon_ips,"AWS")

# Google Cloud service ranges https://www.gstatic.com/ipranges/goog.json
goog_ip_ranges = requests.get('https://www.gstatic.com/ipranges/goog.json').json()['prefixes']
goog_ips = [item['ipv4Prefix'] for item in goog_ip_ranges if "ipv4Prefix" in item]
in_net_test(goog_ips,"GCP Services")

# Google Cloud customer ranges https://www.gstatic.com/ipranges/cloud.json
# Note that this file is identical to the goog.json file at this time.
# Only synctoken differs.
gcp_ip_ranges = requests.get('https://www.gstatic.com/ipranges/cloud.json').json()['prefixes']
gcp_ips = [item['ipv4Prefix'] for item in gcp_ip_ranges if "ipv4Prefix" in item]
in_net_test(gcp_ips,"GCP Customers")

# Oracle Cloud https://docs.oracle.com/en-us/iaas/Content/General/Concepts/addressranges.htm
# https://docs.oracle.com/iaas/tools/public_ip_ranges.json
oci_ips = []
oci_ip_ranges = requests.get('https://docs.oracle.com/iaas/tools/public_ip_ranges.json').json()['regions']
for oci_regions in oci_ip_ranges: 
    for oci_region in oci_regions["cidrs"]:
        oci_ips.append(oci_region["cidr"])
in_net_test(oci_ips,"OCI")

# Azure 
# https://www.microsoft.com/en-us/download/details.aspx?id=56519 needs to be parsed to get the real url
# subroutine to get Azure data
def azure_data_collection(azure_url,azure_region):
    azure_ips = []
    page = requests.get(azure_url)
    azure_page = requests.get(azure_url)
    # parse HTML to get the real link
    soup = BeautifulSoup(azure_page.content, "html.parser")
    azure_link = soup.find('a', {'data-bi-containername':'download retry'})['href']
    azure_values = requests.get(azure_link).json()['values']
    azure_properties = [item['properties'] for item in azure_values]
    azure_prefixes = [item['addressPrefixes'] for item in azure_properties]
    for azure_prefix in azure_prefixes:
        for azure_range in azure_prefix:
            if re.match("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}", azure_range):
                azure_ips.append(azure_range)
    in_net_test(azure_ips,azure_region)

# Azure US = "https://www.microsoft.com/en-us/download/details.aspx?id=56519"
azure_data_collection("https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519","Azure US")
# Azure FedRAMP https://www.microsoft.com/en-us/download/details.aspx?id=57063
azure_data_collection("https://www.microsoft.com/en-us/download/confirmation.aspx?id=57063","Azure FedRAMP")
# Azure Germany https://www.microsoft.com/download/details.aspx?id=57064
azure_data_collection("https://www.microsoft.com/download/confirmation.aspx?id=57064","Azure Germany")
# NOT SUPPORTED: Azure China https://www.microsoft.com/en-us/download/details.aspx?id=42064
# This is still in the old XML format
