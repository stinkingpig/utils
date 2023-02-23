#!/usr/bin/env python3
import ipaddress
import argparse
import re
import requests
import requests_cache
requests_cache.install_cache(cache_name='iaas_cache', expire_after=86400)
from bs4 import BeautifulSoup

# set up some command line options
parser = argparse.ArgumentParser(
    prog = 'ip_is_iaas',
    description = 'Checks if an IP address belongs to an IaaS provider',
    epilog = 'I have no idea what I\'m doing')
parser.add_argument('ip_input', help='a single IPv4 or IPv6 address')
args = parser.parse_args()

def check_amazon(ip_version, aws_url,aws_name):
    if ip_version == 4:
        aws_ip_ranges = requests.get(aws_url).json()['prefixes']
        amazon_ips = [item['ip_prefix'] for item in aws_ip_ranges]
        in_net_test(amazon_ips,aws_name)
    else:
        aws_ip_ranges = requests.get(aws_url).json()['ipv6_prefixes']
        amazon_ips = [item['ipv6_prefix'] for item in aws_ip_ranges]
        in_net_test(amazon_ips,aws_name)

def check_google(ip_version, goog_url,goog_name):
    # Note that the Service and Customer files are identical at this time.
    # Only synctoken differs.
    goog_ip_ranges = requests.get(goog_url).json()['prefixes']
    if ip_version == 4:
        goog_ips = [item['ipv4Prefix'] for item in goog_ip_ranges if "ipv4Prefix" in item]
        in_net_test(goog_ips,goog_name)
    else:
        goog_ips = [item['ipv6Prefix'] for item in goog_ip_ranges if "ipv6Prefix" in item]
        in_net_test(goog_ips,goog_name)

def check_oracle(ip_version, oci_url,oci_name):
    # Note that Oracle supports BYO IPv6 but does not appear to advertise their own IPv6 ranges
    # at this time
    oci_ips = []
    oci_ip_ranges = requests.get(oci_url).json()['regions']
    for oci_regions in oci_ip_ranges: 
        for oci_region in oci_regions["cidrs"]:
            oci_ips.append(oci_region["cidr"])
    in_net_test(oci_ips,oci_name)

def check_azure(ip_version, azure_url,azure_region):
    # the download page needs to be parsed with BS to get the real url, which changes regularly
    azure_ips = []
    azure_page = requests.get(azure_url)
    # parse HTML to get the real link
    soup = BeautifulSoup(azure_page.content, "html.parser")
    azure_link = soup.find('a', {'data-bi-containername':'download retry'})['href']
    azure_values = requests.get(azure_link).json()['values']
    azure_properties = [item['properties'] for item in azure_values]
    azure_prefixes = [item['addressPrefixes'] for item in azure_properties]
    for azure_prefix in azure_prefixes:
        for azure_range in azure_prefix:
            if ip_version == 4:
                if re.match("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}", azure_range):
                    azure_ips.append(azure_range)
            else:
                if not re.match("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}", azure_range):
                    azure_ips.append(azure_range)
    in_net_test(azure_ips,azure_region)


# subroutine to validate the input
# check that it's a dotted quad address, a valid ipv4, or a valid ipv6.
# exit if it's not something we can use
def validate_input(ip_input):
    if re.match("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", ip_input):
        try:
            addr = ipaddress.IPv4Address(ip_input)
            return addr.version
        except ipaddress.AddressValueError:
            print(ip_input, 'is not a valid IPv4 address')
            exit()
        else:
            if addr.is_multicast:
                print(ip_input, 'is an IPv4 multicast address')
                exit()
            if addr.is_private:
                print(ip_input, 'is an IPv4 private address')
                exit()
            if addr.is_global:
                print(ip_input, 'is an IPv4 global address')
            if addr.is_link_local:
                print(ip_input, 'is an IPv4 link-local address')
                exit()
            if addr.is_unspecified:
                print(ip_input, 'is an IPv4 site-local address')
                exit()
            if addr.is_reserved:
                print(ip_input, 'is an IPv4 reserved address')
                exit()
            if addr.is_loopback:
                print(ip_input, 'is an IPv4 loopback address')
                exit()
    else:
        try:
            addr = ipaddress.IPv6Address(ip_input)
            return addr.version
        except ipaddress.AddressValueError:
            print(ip_input, 'is not a valid IPv4 or IPv6 address')
            exit()
        else:
            if addr.is_multicast:
                print(ip_input, 'is an IPv6 multicast address')
                exit()
            if addr.is_private:
                print(ip_input, 'is an IPv6 private address')
                exit()
            if addr.is_global:
                print(ip_input, 'is an IPv6 global address')
            if addr.is_link_local:
                print(ip_input, 'is an IPv6 link-local address')
                exit()
            if addr.is_site_local:
                print(ip_input, 'is an IPv6 site-local address')
                exit()
            if addr.is_reserved:
                print(ip_input, 'is an IPv6 reserved address')
                exit()
            if addr.is_loopback:
                print(ip_input, 'is an IPv6 loopback address')
                exit()
            if addr.ipv4_mapped:
                print(ip_input, 'is an IPv6 mapped IPv4 address.')
                exit()
            if addr.sixtofour:
                print(ip_input, 'is an IPv6 RFC 3056 address')
                exit()
            if addr.teredo:
                print(ip_input, 'is an IPv6 RFC 4380 address')
                exit()

# subroutine to compare an ip with a subnet range
def in_net_test(iprange,iaas):
    for ip in iprange:
        address=ipaddress.ip_network(args.ip_input)
        network=ipaddress.ip_network(ip)
        if address.subnet_of(network):
            print(args.ip_input,"is in",str(network),"which belongs to",iaas)
            exit()

def main():
    ip_version = validate_input(args.ip_input)
    check_amazon(ip_version, "https://ip-ranges.amazonaws.com/ip-ranges.json", "AWS")
    check_azure(ip_version, "https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519","Azure US")
    check_azure(ip_version, "https://www.microsoft.com/en-us/download/confirmation.aspx?id=57063","Azure FedRAMP")
    check_azure(ip_version, "https://www.microsoft.com/download/confirmation.aspx?id=57064","Azure Germany")
    # NOT SUPPORTED: Azure China https://www.microsoft.com/en-us/download/details.aspx?id=42064
    # This is still in the old XML format
    check_google(ip_version, "https://www.gstatic.com/ipranges/goog.json", "GCP Services")
    check_google(ip_version, "https://www.gstatic.com/ipranges/cloud.json", "GCP Customers")
    check_oracle(ip_version, "https://docs.oracle.com/iaas/tools/public_ip_ranges.json", "OCI")

if __name__ == "__main__":
    main()

