import validators
from urllib.parse import urlparse
import socket
import ssl
from src.utilities import *
from bs4 import BeautifulSoup
from src.style import *

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

    # BUILD RAW HTTP REQUEST
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

    request += 'Cookie: ' + cookie+"\r\n"
    request += "\r\n"
    print(request)

    # SOCKET
    try:
        if "http" in url:
            url = urlparse(url).netloc

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        soc = context.wrap_socket(s, server_hostname=url)
        soc.settimeout(10)
        soc.connect((url, port))
        soc.send(bytes(request, 'UTF-8'))
        result = soc.recv(2000)
        headersRes = []
        html = ""
        rawHeadersResponse = str(result, "UTF-8")
        rawHeadersResponse = rawHeadersResponse.split("\r\n\r\n")[0]

        # GET ALL HOST HEADER INJECTION IN HTTP HEADERS
        positions = list(findall(host, rawHeadersResponse))

        for i in positions:
            print(style.MAGENTA + '[ + ]' + style.RESET + "Found host injection in HTTP HEADER for " + style.UNDERLINE + host+ style.RESET)
            hostHTML = rawHeadersResponse[i:][:len(host)]
            left = rawHeadersResponse[i - 90:][:90]
            right = rawHeadersResponse[i + len(host):][:90]

            print(left + style.GREEN + hostHTML + style.RESET + right + "\r\n")

        while (len(result) > 0):
            result = soc.recv(200)

            soup = BeautifulSoup(result, 'html.parser')
            parse = soup.prettify()
            html = soup.prettify()


            # GET ALL HOST HEADER INJECTION IN RESPONSE
            if host not in url:
                positions = list(findall(host, parse))

                for i in positions:
                    html = soup.prettify()
                    print(style.MAGENTA + '[ + ]' + style.RESET + "Found host injection for " + style.UNDERLINE + soup.prettify()[i:][:len(host)] + style.RESET)
                    hostHTML = html[i:][:len(host)]
                    left = html[i - 20:][:20]
                    right = html[i + len(host):][:40]

                    print(left + style.GREEN + hostHTML + style.RESET + right + "\r\n")

            # X-FORWARDED-HOST HEADER INJECTION
            if xHost:
                positions = list(findall(xHost, parse))

                for i in positions:
                    html = soup.prettify()
                    hostHTML = html[i:][:len(xHost)]
                    left = html[i - 20:][:20]
                    right = html[i + len(xHost):][:40]

                    print(style.MAGENTA + '[ + ]' + style.RESET + "Found host injection for " + style.UNDERLINE + soup.prettify()[i:][:len(xHost)] + style.RESET)
                    print(left + style.GREEN + hostHTML + style.RESET + right + "\r\n")


            s.close()

        httpCode = 100
        # If Verbose print HTTP Headers Response
        if verbose:
            headersRaw = str(rawHeadersResponse).split("\r\n")
            if len(str(rawHeadersResponse).split("\r\n")[0]) > 1:
                httpCode = str(rawHeadersResponse).split("\r\n")[0].split(" ")[1]
            print(style.GREEN + str(httpCode) +style.RESET)

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
                        wait = input("Press Enter to follow the request to "+location+":")
                        if valid_url:
                            get_request(url.replace(" ", ""), location, 443, verbose, ['Host:' + host])
                            wait = input("Press Enter to FINISH")
        print("\r\n\r\n")
    except socket.error as socketerror:
        print(style.RED + "Error => "+style.RESET+str(socketerror))
    except Exception as e:
        print(str(e))

# BUILD HTTP REQUEST
def doRequest(method, url, path, port, verbose, headers=[]):
    cookie = "_lab=46%7cMCwCFE3mW1jkDkrJIQLmC%2f2OS7KAsF15AhR8%2bJNqw7maeB2xgKpOpoEJeYwcfkHo%2bRo84lgszJhY7j5BH5Bo4eAUwarF4ihMo%2fUX0Y68OKiwESQnJB7rDOkK4Kp7OGMTFDJ269CVQDwwQ8gkIjnSdj0rtxKZAoGHMnuvqa8ylAXu9Nw%3d; session=wZ9kWvz7TjKbqhWf4kHxWgRp8tHM66B3"
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

    # BUILD RAW HTTP REQUEST
    host = ""
    xHost = ""

    if not "http" in path and not "/" in path:
        path = urlparse(url).path + "?" + urlparse(url).query
    if path == "":
        path = "/"

    request = method + " " + path + " HTTP/1.1\r\n"

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

    request += 'Cookie: ' + cookie+"\r\n"
    request += "\r\n"
    print(request)

    # SOCKET
    try:
        if "http" in url:
            url = urlparse(url).netloc

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        soc = context.wrap_socket(s, server_hostname=url)
        soc.settimeout(10)
        soc.connect((url, port))
        soc.send(bytes(request, 'UTF-8'))
        result = soc.recv(500)
        headersRes = []
        html = ""
        rawHeadersResponse = str(result, "UTF-8")

        while (len(result) > 0):
            result = soc.recv(200)

            soup = BeautifulSoup(result, 'html.parser')
            parse = soup.prettify()
            html = soup.prettify()

            if verbose:
                print(html)

            # GET ALL HOST HEADER INJECTION IN RESPONSE
            positions = list(findall(host, parse))

            for i in positions:
                html = soup.prettify()
                print(style.MAGENTA + '[ + ]' + style.RESET + "Found host injection for " + style.UNDERLINE + soup.prettify()[i:][:len(host)] + style.RESET)
                hostHTML = html[i:][:len(host)]
                left = html[i - 20:][:20]
                right = html[i + len(host):][:40]

                print(left + style.GREEN + hostHTML + style.RESET + right + "\r\n")

            # X-FORWARDED-HOST HEADER INJECTION
            if xHost:
                positions = list(findall(xHost, parse))

                for i in positions:
                    html = soup.prettify()
                    print(style.MAGENTA + '[ + ]' + style.RESET + "Found host injection for " + style.UNDERLINE + soup.prettify()[i:][:len(xHost)] + style.RESET)
                    hostHTML = html[i:][:len(xHost)]
                    left = html[i - 20:][:20]
                    right = html[i + len(xHost):][:40]

                    print(left + style.GREEN + hostHTML + style.RESET + right + "\r\n")


            s.close()

        # If Verbose print HTTP Headers Response
        if verbose:
            headersRaw = str(rawHeadersResponse).split("\r\n")
            httpCode = str(rawHeadersResponse).split("\r\n")[0].split(" ")[1]
            print(style.GREEN + httpCode +style.RESET)
            for header in headersRaw:
                name = ""
                val = ""

                if len(header.split(':')) > 1:
                    name = header.split(':')[0]
                    val = header.split(':')[1]
                    if not "<html>" in name:
                        print(style.YELLOW + name +style.RESET + ": " + val )

        # Follow Redirects if User Want To
        httpCode = str(rawHeadersResponse).split("\r\n")[0].split(" ")[1]
        if int(httpCode) >= 300 and int(httpCode) <= 399:
            for header in headersRaw:
                if len(header.split(':')) > 1:
                    if header.split(':')[0] == "Location":
                        location = (header.split(':')[1]).replace(" ", "")
                        wait = input("Press Enter to follow the request to "+location+":")
                        get_prueba(url.replace(" ", ""), location, 443, verbose, ['Host:' + host])
                        wait = input("Press Enter to FINISH")

    except socket.error as socketerror:
        print(style.RED + "Error => "+style.RESET+str(socketerror))
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
