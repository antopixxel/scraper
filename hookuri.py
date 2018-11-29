#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# HookURI - Information Gathering Tools
# by black4t

import re
import os
import sys
import time
import socket
import requests
from bs4 import BeautifulSoup

YLW   = "\033[93m"
GRN   = "\033[92m"
RED   = "\033[91m"
RST   = "\033[0m"

os.system('clear')

print("""
ooooo ooooo                       oooo       ooooo  oooo oooooooooo  ooooo 
 888   888   ooooooo     ooooooo   888  ooooo 888    88   888    888  888  
 888ooo888 888     888 888     888 888o888    888    88   888oooo88   888  
 888   888 888     888 888     888 8888 88o   888    88   888  88o    888  
o888o o888o  88ooo88     88ooo88  o888o o888o  888oo88   o888o  88o8 o888o 
                                                                            
----------------  URI Extractor for Information Gathering  ---------------
""")

try:
    domain = input("Enter domain : ")

    if re.match("(http|https)://", domain):
        uri = domain
        host = domain.replace("http://","")
        ipaddr = socket.gethostbyname(host)

    elif re.match("^[a-z0-9]([a-z0-9-]+\.){1,}[a-z0-9]+\Z", domain):
        r = requests.get('http://'+ domain)
        uri = r.domain
        ipaddr = socket.gethostbyname(uri)

    else:
        print("URI not valid!")

    print("Hostname     : "+ host)
    print("IP Address   : "+ ipaddr)

    output = input("\nOutput file  : ")
    result = open(output, 'a')
    readfile = open(output, 'r')

    print("\n%s[+] Scraping URL from the target...%s" % (GRN, RST))

#--------------------------------------------------------------
# Scraping url in website, then write into files 'main.txt'
#--------------------------------------------------------------

    store = []

    r  = requests.get(uri, verify=False)
    data = r.text
    soup = BeautifulSoup(data)

    links = [a.get('href') for a in soup.find_all('a', href=True)]
    for url in links:
        rgx = re.search("(http|https)://.*", url)
        if rgx: 
            store.append(rgx.group())
        else: 
            rgx

    output = open('%s_main.txt' % host, 'a')
    with output as file:
        for line in store:
            file.write(str(line)+'\n')

#--------------------------------------------------------------
# Find match pattern after scraping using regex
#--------------------------------------------------------------

    read = open('%s_main.txt' % host, 'r')
    out = open('%s_result.txt' % host, 'a')
    with read as file:
        for line in file:
            lines = line.strip()

            req  = requests.get(lines)
            data = req.text
            soup = BeautifulSoup(data)

            links = [a.get('href') for a in soup.find_all('a', href=True)]
            for url in links:
                rgx = re.search("(http|https)://.*", url)
                if rgx: 
                    out.write(rgx.group()+'\n')
                else: 
                    rgx
                
#--------------------------------------------------------------
# Delete duplicate lines after scraping
#--------------------------------------------------------------

    count = 0
    lines = set()

    outfile = open('%s_result.txt' % host , 'r')
    for line in outfile:
        if line not in lines:
            count += 1
            result.write(line)
            lines.add(line)    

    result.close()

    os.remove('%s_result.txt' % host)

#--------------------------------------------------------------
# Filtering subdomain from target using regex
#--------------------------------------------------------------

    rgx_domain = r"^https?://([\w\d]+\.)" + re.escape(host)

    writedomain = open('%s_domain.txt' % host, 'w')
    subdomain = open('%s_subdomain.txt' % host, 'w')
    

    print("%s[+] Scraping domain and subdomain...%s" % (GRN, RST))

    with readfile as file:
        for line in file:
            rgx = re.search(rgx_domain, line)
            if rgx:  
                writedomain.write(rgx.group()+'\n')
            else:
                rgx

    cnt = 0
    lines = set()

    readomain = open('%s_domain.txt' % host, 'r')
    for line in readomain:
        if line not in lines:
            cnt += 1
            subdomain.write(line)
            lines.add(line)    

    subdomain.close()

#--------------------------------------------------------------
# Get directory list using regex
#--------------------------------------------------------------

    print("%s[+] Scraping directory list...%s" % (GRN, RST))

    dr = 0
    dirllist = open('%s_dirlist.txt' % host, 'w')
    with readfile as file:
        for line in file:
            rgx = re.sub(rgx_domain, '', line)
            if rgx:
                dr += 1
                dirllist.write(rgx.group()+'\n')
            else:
                rgx

except KeyboardInterrupt:
    print("\nExiting")

except requests.exceptions.Timeout:
    print("Timeout")
    
except requests.exceptions.TooManyRedirects:
    print("Too Many Redirects")

except requests.exceptions.RequestException as e:
    print(e)
    sys.exit(1)

print("\n%sTotal URL found :%s " % (YLW, RST) + str(count))
print("%sFound Subdomain :%s " % (YLW, RST) + str(cnt))
print("%sFound Directory list :%s " % (YLW, RST) + str(dr))