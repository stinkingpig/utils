#!/usr/bin/env python3
import argparse
import requests
import requests_cache
requests_cache.install_cache(cache_name='azure_ip_list_cache', expire_after=600)
import urllib.request
from bs4 import BeautifulSoup
import boto3

# set up some command line options
parser = argparse.ArgumentParser(
    prog = 'azure_ip_list_fetcher',
    description = 'Downloads the lists of Microsoft Azure IP addresses',
    epilog = 'I have no idea what I\'m doing')
parser.add_argument('--local', action=argparse.BooleanOptionalAction, help='write output to local files', default=False)
parser.add_argument('--s3', action=argparse.BooleanOptionalAction, help='write output to an S3 bucket', default=False)
parser.add_argument('--customer_id', help='Your Observe customer ID. Required if local is False', required=False)
parser.add_argument('--ingest_token', help='Your Observe data stream token. Required if local is False', required=False)
parser.add_argument('--observe_host_name', help='Defaults to collect.observeinc.com', required=False)
parser.add_argument('--bucket_name', help='Your AWS S3 Bucket name. Required if s3 is True', required=False)
parser.add_argument('--aws_access_key', help='Your AWS Access Key ID. Required if s3 is True', required=False)
parser.add_argument('--aws_secret_key', help='Your AWS Secret Key. Required if s3 is True', required=False)
args = parser.parse_args()

def validate_input():
    # If not local and s3, we can ignore the observe variables
    if not args.local:
        if args.s3 == True:
            if args.bucket_name == None:
                print("Sorry, need your S3 Bucket Name")
                exit()
            if args.aws_access_key == None:
                print("Sorry, need your AWS Access Key ID")
                exit()
            if args.aws_secret_key == None:
                print("Sorry, need your AWS Secret Key")
                exit()
    # If local is on and s3 is on, bail out
    if args.local == True and args.s3 == True:
        print("Sorry, local and s3 options conflict.")
        exit()
    # looks like s3
    if args.s3 == True and args.bucket_name != None:
        return
    # looks like Observe posting, validate all the needed variables
    if not args.local:
        if args.customer_id == None or args.ingest_token == None:
            if args.ingest_token == None:
                print("Sorry, need your ingest token")
                exit()
            print("Sorry, need to know where to send this")
            exit()
        if not args.observe_host_name:
            args.observe_host_name = "https://" + args.customer_id + ".collect.observeinc.com"
        else:
            args.observe_host_name = "https://" + args.customer_id + "." + args.observe_host_name

def fetch_azure(azure_url,azure_region):
    # the download page needs to be parsed with BS to get the real url, which changes regularly
    azure_page = requests.get(azure_url)
    # parse HTML to get the real link
    soup = BeautifulSoup(azure_page.content, "html.parser")
    azure_link = soup.find('a', {'data-bi-containername':'download retry'})['href']
    azure_filename = azure_region.replace(" ", "_") + ".json"
    with urllib.request.urlopen(azure_link) as response:
        azure_data = response.read()
        if args.local:
            try:
                azure_file = open(azure_filename, 'wb')
            except IOError:
                print("cannot open",azure_filename,"for writing")
            azure_file.write(azure_data)
            azure_file.close
        elif args.s3:
            s3_session = boto3.Session(
                aws_access_key_id = args.aws_access_key,
                aws_secret_access_key = args.aws_secret_key
            )
            s3_connection = s3_session.resource('s3')
            s3_connection.meta.client.put_object(
                Body = azure_data,
                Bucket = args.bucket_name,
                Key = azure_filename
            )
        else:
            observe_url = args.observe_host_name + "/v1/http"
            observe_token_header = 'Bearer ' + args.ingest_token
            observe_headers = {'Authorization': observe_token_header, 'Content-type': 'application/json'}
            try:
                observe_post = requests.post(observe_url, headers=observe_headers, data=azure_data)
                observe_post.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)

def main():
    validate_input()
    fetch_azure("https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519","Azure US")
    fetch_azure("https://www.microsoft.com/en-us/download/confirmation.aspx?id=57063","Azure FedRAMP")
    fetch_azure("https://www.microsoft.com/download/confirmation.aspx?id=57064","Azure Germany")
    # NOT SUPPORTED: Azure China https://www.microsoft.com/en-us/download/details.aspx?id=42064
    # This is still in the old XML format

if __name__ == "__main__":
    main()

