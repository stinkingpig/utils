#!/usr/bin/env python3
import ipaddress
import array as arr
import argparse
import re

# Why am I doing it this crazy way instead of just calling ipaddress.is_private 
# and ipaddress.is_reserved? Because my goal is to test the behavior of
# Observe-on-Snowflake, where I need to do this task with nothing but math or 
# POSIX regular expressions.

# NON-PUBLIC IPv4 RANGES
# >= 0.0.0.0 and <= 0.255.255.255
# >= 10.0.0.0 and <= 10.255.255.255
# >= 100.64.0.0 and <= 100.127.255.255
# >= 127.0.0.0 and <= 127.255.255.255
# >= 169.254.0.0 and <= 169.254.255.255
# >= 172.16.0.0 and <= 172.31.255.255
# >= 192.0.0.0 and <= 192.0.0.255
# >= 192.0.2.0 and <= 192.0.2.255
# >= 192.88.99.0 and <= 192.88.99.255
# >= 192.168.0.0 and <= 192.168.255.255
# >= 198.18.0.0 and <= 198.19.255.255	
# >= 198.51.100.0 and <= 198.51.100.255
# >= 203.0.113.0 and <= 203.0.113.255
# >= 224.0.0.0 and <= 255.255.255.255

# PUBLIC IPv4 RANGES
# > 0.255.255.255 and < 10.0.0.0 
# > 10.255.255.255 and < 100.64.0.0
# > 100.64.255.255 and < 127.0.0.0 
# > 127.255.255.255 and < 169.254.0.0 
# > 169.254.255.255 and < 172.16.0.0
# > 172.31.255.255 and < 192.0.0.0
# > 192.0.0.255 and < 192.0.2.0
# > 192.0.2.255 and < 192.88.99.0
# > 192.88.99.255 and < 192.168.0.0
# > 192.168.255.255 and < 198.18.0.0
# > 198.19.255.255 and < 198.51.100.0
# > 198.51.100.255 and < 203.0.113.0
# > 203.0.113.255 and < 224.0.0.0

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

# set up the array of non-public address boundaries
ip_boundaries_np = arr.array('l', [0,16777215,167772160,184549375,1681915904,1686110207,2130706432,2147483647,2851995648,2852061183,2886729728,2887778303,3221225472,3221225727,3221225984,3221226239,3227017984,3227018239,3232235520,3232301055,3323068416,3323199487,3325256704,3325256959,3405803776,3405804031,3758096384,4294967295])

# set up the array of public address boundaries
ip_boundaries_p = arr.array('l', [16777215,167772160,184549375,1681915904,1686110207,2130706432,2147483647,2851995648,2852061183,2886729728,2887778303,3221225472,3221225727,3221225984,3221226239,3227017984,3227018239,3232235520,3232301055,3323068416,3323199487,3325256704,3325256959,3405803776,3405804031,3758096384])

# turn the input into a long integer
ip_int = int(ipaddress.ip_address(args.ip_input))

# if it's contained by non-public boundaries, it's non-public
for start, stop in zip(*[iter(ip_boundaries_np)]*2):
    if ip_int >= start and ip_int <= stop:
        ip_start = ipaddress.IPv4Address(start)
        ip_stop = ipaddress.IPv4Address(stop)
        print(args.ip_input,"is a non-public address, between",ip_start,"and",ip_stop)
 
# if it's contained by public boundaries, it's public
for start, stop in zip(*[iter(ip_boundaries_p)]*2):
    if ip_int > start and ip_int < stop:
        ip_start = ipaddress.IPv4Address(start)
        ip_stop = ipaddress.IPv4Address(stop)
        print(args.ip_input,"is a public address, between",ip_start,"and",ip_stop)
