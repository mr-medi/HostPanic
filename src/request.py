from urllib.parse import urlparse
import socket
import ssl
from src.utilities import *
from bs4 import BeautifulSoup
from src.style import *

#---------------------------------------------------------------------------------------------
# CUSTOM FUNCTION TO PERFORM RAW HTTP REQUEST WITH CUSTOM HEADERS USING SOCKETS
#
# @url str Domain where to create the socket
# @path str Path of the URL where to make the request (Ex: /admin)
# @port int Port where to create the Socket
# @verbose bool Boolean to print or not more information about the request
# @headers array Custom headers to send in the request
# @tags array
# @return None (For the moment this function doesn't return anything)
#---------------------------------------------------------------------------------------------
def get_request(url, path, port, verbose, headers=[], tags=[]):
    cookie = ""
    headers2 = ['Pragma: no-cache', 'Accept: */*', 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0', 'Connection: close', 'Host: '+url]
    DEF = []

    for h in headers2:
        foundHeader = False
        name = str(h).split(':')[0]
        val = str(h).split(':')[1]

        for userHeader in headers:
            if name in userHeader:
                foundHeader = True
                u_header = userHeader.split(':')

                if len(u_header) >= 3:
                    DEF.append(u_header[0] + ": " + u_header[1]+":"+u_header[2])
                else:
                    DEF.append(u_header[0] + ": " + u_header[1])

        # JUST A CHECK TO NOT REPEAT HTTP HEADERS
        if not foundHeader:
            DEF.append(h)

        for i in headers:
            foundHeader = True
            u_header = i.split(':')
            if u_header[0] == "Cookie":
                cookie = u_header[1]

     #----------------------------------------------------------------------
     # ------> Build the RAW HTTP REQUEST <---------------------------------
     #----------------------------------------------------------------------
    host = ""
    xHost = ""

    if not "http" in path and not "/" in path:
        path = urlparse(url).path + "?" + urlparse(url).query
    if path == "":
        path = "/"

    request = "GET " + path + " HTTP/1.1\r\n"

    for i in DEF:
        name = i.split(':')[0].strip()
        val = i.split(':')[1].strip()

        if len(i.split(':')) >= 3 :
            val += ":"+i.split(':')[2]

        lineHeader = name + ": " + val + "\r\n"
        request += lineHeader

        if name == "Host":
            host = val
        if name == "X-Forwarded-Host":
            xHost = val

    if "http" in url:
        url = urlparse(url).netloc
    request += 'Cookie: ' + cookie+"\r\n"
    request += "\r\n"
    print(request)

    # --> CREATE SOCKET TO THE TARGET <--
    try:
        #----------------------------------------------------------------------
        # ------> Declaration of variables <----------------------------------
        #----------------------------------------------------------------------
        html = ""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        soc = context.wrap_socket(s, server_hostname=url)
        soc.settimeout(10)
        soc.connect((url, port))
        soc.send(bytes(request, 'UTF-8'))
        result = soc.recv(2000)
        headersRes = []
        htmlRaw = ""
        rawHeadersResponse = str(result, "UTF-8")
        rawHeadersResponse = rawHeadersResponse.split("\r\n\r\n")[0]

        #----------------------------------------------------------------------
        # ------> GET ALL HOST HEADER INJECTION IN HTTP HEADERS <--------------
        #----------------------------------------------------------------------
        positions = list(findall(host, rawHeadersResponse))

        # Foreach Injection in HTTP Headers we print it
        for i in positions:
            hostHTML = rawHeadersResponse[i:][:len(host)]
            if hostHTML != url:
                print(style.MAGENTA + '[ + ]' + style.RESET + "Found host injection in HTTP HEADER for " + style.UNDERLINE + host+ style.RESET)
                left = rawHeadersResponse[i - 90:][:90]
                right = rawHeadersResponse[i + len(host):][:90]

        # WHILE THE SERVER IS SENDING US THE RAW HTML WE PROCESS IT
        while (len(result) > 0):
            result = soc.recv(200)
            soup = BeautifulSoup(result, 'html.parser',from_encoding="iso-8859-1")
            parse = soup.prettify()
            html = soup.prettify()
            htmlRaw += str(html)

            # --------------> GET ALL HOST HEADER INJECTION IN THE BODY OF THE HTTP RESPONSE <--------------------
            if host not in url:
                positions = list(findall(host, parse))

                for i in positions:
                    html = soup.prettify()                    
                    hostHTML = html[i:][:len(host)]
                    left = html[i - 20:][:20]
                    right = html[i + len(host):][:40]
                    
                    print(style.MAGENTA + '[ + ]' + style.RESET + "Found host injection for " + style.UNDERLINE + soup.prettify()[i:][:len(host)] + style.RESET)
                    print(left + style.GREEN + hostHTML + style.RESET + right + "\r\n")

            # --------------> GET ALL X-FORWARDED-HOST HEADER INJECTION IN THE BODY OF THE HTTP RESPONSE <--------------------
            if xHost:
                positions = list(findall(xHost, parse))

                for i in positions:
                    html = soup.prettify()
                    hostHTML = html[i:][:len(xHost)]
                    left = html[i - 20:][:20]
                    right = html[i + len(xHost):][:40]

                    print(style.MAGENTA + '[ + ]' + style.RESET + "Found host injection for " + style.UNDERLINE + soup.prettify()[i:][:len(xHost)] + style.RESET)
                    print(left + style.GREEN + hostHTML + style.RESET + right + "\r\n")
            
            # Finally close the Socket
            s.close()

        httpCode = 100
        # If Verbose Mode print HTTP Headers Response and the RAW HTML
        if verbose:
            headersRaw = str(rawHeadersResponse).split("\r\n")
            if len(str(rawHeadersResponse).split("\r\n")[0]) > 1:
                httpCode = str(rawHeadersResponse).split("\r\n")[0].split(" ")[1]
            print("HTTP Code: " + style.GREEN + str(httpCode) + style.RESET + "\r\n")
            print(htmlRaw)

            for header in headersRaw:
                name = ""
                val = ""

                if len(header.split(':')) > 1:
                    name = header.split(':')[0]
                    val = header.split(':')[1]
                    print(style.YELLOW + name +style.RESET + ": " + val )

        # Follow Redirects if User Want To
        if int(httpCode) >= 300 and int(httpCode) <= 399:
            for header in headersRaw:
                if len(header.split(':')) > 1:
                    if header.split(':')[0] == "Location":
                        location = (header.split(':')[1]).replace(" ", "")
                        valid_url = location[0] == "/"
                        wait = input("\r\nPress Enter to follow the request to " + location + " : \r\n")

                        if valid_url:
                            get_request(url.replace(" ", ""), location, 443, True, ['Host:' + host, 'Cookie:' + cookie])
                            wait = input("-------------> Press Enter to FINISH <-----------------------\r\n")
        print("\r\n\r\n")
        
    # Manage possible exceptions because of the socket
    except socket.error as socketerror:
        print(style.RED + "Error => " + style.RESET + str(socketerror))
    except Exception as e:
        print(str(e))
        
        
#----------------------------
def getDiffTime(url, port, host):

    HEADERS = (
    	"GET / HTTP/1.1\r\n"
        "Host: "+str(host)+"\r\n"
    	"Accept: *\r\n"
        "User-Agent: Pozilla 8.1(Windows 20 Ultra Version)\r\n"
    	"Connection: close\r\n"
    	"\r\n"
      )

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        soc = context.wrap_socket(s, server_hostname = url)
        soc.connect((url, port))
        soc.send(bytes(HEADERS,'UTF-8'))
        result = soc.recv(10000000)

        #HEADERS
        headers = result.splitlines(True)
        finish = False
        age = ''
        cacheControl = ''
        xCache = ''

        for header in headers:
            if header == bytes('\r\n', 'utf-8'):
                finish = True
            if not finish:
                val = ''
                name = str(header).split(':')[0]
                try:
                    val = str(header).split(':')[1]
                except Exception:
                    pass
                if 'Age' in name:
                    age = val.strip("\\r\\n").replace("\\r\\n", "").replace(" ","").replace("'","")
                if 'X-Cache' in name:
                    xCache = val.strip("\\r\\n").replace("\\r\\n", "").replace(" ","").replace("'","")
                if 'Cache-Control' in name:
                    cacheControl = val.split('=')[1].strip("\\r\\n").replace("\\r\\n", "").replace(" ","").replace("'","")
                #print(style.GREEN+name+": "+style.RESET+val)

        print(style.GREEN+"Age: "+style.RESET+age)
        print(style.GREEN+"x-cache: "+style.RESET+xCache)
        print(style.GREEN+"cache-control: "+style.RESET+cacheControl)
        difftime = int(cacheControl) - int(age)
        print('Quedan ' + str(difftime) + ' seg')
        return difftime
        #HEADERS

        while (len(result) > 0):
            result = soc.recv(10000)

            soup = BeautifulSoup(result, 'html.parser')
            parse = soup.prettify()
            positions = list(findall('evil.com', parse))

            for i in positions:
                html = soup.prettify()
                print(style.YELLOW + '[ + ]' + style.RESET + "Found host injection for " + style.UNDERLINE + soup.prettify()[i:][:len(host)] + style.RESET)
                hostHTML = html[i:][:len(host)]
                left = html[i - 40:][:20]
                right = html[i + len(host):][:40]
                print(left + style.GREEN + hostHTML + style.RESET + right + "\r\n")


        s.close()
    except socket.error as socketerror:
        print(style.RED + "Error"+style.RESET)


def get_form_details(form):
    """Returns the HTML details of a form,
    including action, method and list of form controls (inputs, etc)"""
    details = {}
    # get the form action (requested URL)
    action = form.attrs.get("action").lower()
    # get the form method (POST, GET, DELETE, etc)
    # if not specified, GET is the default in HTML
    method = form.attrs.get("method", "get").lower()
    # get all form inputs
    inputs = []
    for input_tag in form.find_all("input"):
        # get type of input form control
        input_type = input_tag.attrs.get("type", "text")
        # get name attribute
        input_name = input_tag.attrs.get("name")
        # get the default value of that input tag
        input_value =input_tag.attrs.get("value", "")
        # add everything to that list
        inputs.append({"type": input_type, "name": input_name, "value": input_value})
    # put everything to the resulting dictionary
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details
