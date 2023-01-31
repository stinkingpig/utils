#!/usr/bin/env python3
import ipaddress
import argparse
import re
import requests
import json

# only supporting ipv4 addresses at this time
# always goes to the internet instead of caching and comparing versions

# set up some command line options
# get the address in dotted quad notation
parser = argparse.ArgumentParser(
    prog = 'ip_is_public',
    description = 'Checks if an IPv4 address is public or not',
    epilog = 'I have no idea what I\'m doing')
parser.add_argument('ip_input')
args = parser.parse_args()

# check that it's a dotted quad address
if not re.match("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", args.ip_input):
    print(args.ip_input,"is not an IP address")
    raise SystemExit()

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

# Azure [BROKEN]
# documentation https://learn.microsoft.com/en-us/python/api/azure-mgmt-network/azure.mgmt.network.v2020_03_01.operations.publicipaddressesoperations?view=azure-python
# https://www.microsoft.com/en-us/download/details.aspx?id=56519
# The above download url requires human clicking to produce the below confirmation url which is only good for a day. Probably need to use Microsoft's SDK for Python (https://learn.microsoft.com/en-us/azure/developer/python/)
# Azure FedRAMP https://www.microsoft.com/en-us/download/details.aspx?id=57063
# Azure China https://www.microsoft.com/en-us/download/details.aspx?id=42064
# Azure Germany https://www.microsoft.com/download/details.aspx?id=57064
# maybe something here? https://community.f5.com/t5/codeshare/dynamic-ip-update-of-azure-ip-ranges-and-store-them-in-data/ta-p/291396
# note that format changed from XML to JSON in 2021, older scripts are not valid
# this script is also out of date https://adamtheautomator.com/azure-ip-ranges/
# azure_ip_ranges = requests.get('https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519').json()['values']
# azure_ips = [item['addressPrefixes'] for item in azure_ip_ranges]

# in_net_test(azure_ips,"Azure")

# Oracle Cloud https://docs.oracle.com/en-us/iaas/Content/General/Concepts/addressranges.htm
# https://docs.oracle.com/iaas/tools/public_ip_ranges.json
oci_ips = []
oci_ip_ranges = requests.get('https://docs.oracle.com/iaas/tools/public_ip_ranges.json').json()['regions']
for oci_regions in oci_ip_ranges: 
    for oci_region in oci_regions["cidrs"]:
        oci_ips.append(oci_region["cidr"])
in_net_test(oci_ips,"OCI")
