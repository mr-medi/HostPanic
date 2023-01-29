# HostPanic

Hacking tool to seek host header injections and escalate it with other kind of vulns like web cache poissoning.

Feel free to contact me ([@medi_0ne](https://twitter.com/medi_0ne) ) for any suggestion using this tool.

# Attack Example

In the next Youtube video you can check how to perform a Routing Based SSRF based on a Portswigger Lab using my Tool.
I will share more examples soon about how to approach it.

Click to see it:

[![Click to see how to use my Tool to perform Routing Based SSRF on a Portswigger lab](https://img.youtube.com/vi/XHI_Ka9CGP4/0.jpg)](https://www.youtube.com/watch?v=XHI_Ka9CGP4)


## Installation

```bash
# Clone the repo
git clone https://github.com/mr-medi/HostPanic.git
```

## Running the tests

``` bash
python3 main.py -u https://www.google.com/ -v
```

### Break down into end to end tests

The first thing is to enter a URL or domain, with this data the script will generate a serie of payloads to test for and if any of them find any host header injection in the HTTP headers or in the HTML returned by the server will print out in the terminal.

Let´s take an example:

I enter the url "https://www.google.com/" as seen in the previous example.

The script will do a GET request with different host headers, for example a Port Injection like the following HTTP Header 'Host: domain:22'.
If this domain generate any link to construct the absolute URL and uses that header without sanitizes it you, then you can try to poisson that request with the reflected input as the host header and perform a responsible DOS attack to let the users without access that link.

In the next image you can see the sucesful result of a port injection in the host header in Google:
![Index page](https://github.com/mr-medi/HostPanic/blob/master/assets/hostpanic-1.jpg?raw=true)

## USAGE:
```
[*] NORMAL MODE
python3 main.py -u <URL>

[*] NORMAL MODE + VERBOSE (Print HTTP headers of response)
python3 main.py -u <URL> -v

[*] NORMAL MODE + TEST LOCAL IP RANGE IN HOST HEADER (Following example will do 254 request from 192.168.0.1 to 192.168.0.255)
python3 main.py -u <URL> -r "192.168.0."

[*] NORMAL MODE + ADD COOKIES TO EACH REQUEST
python3 main.py -u <URL> -c "Mycookie1=1;MyEvilcookie2=2"
```

## Authors

* **Mr.Medi**

## Special Thanks

This work is inspired by the following excellent researches:

* **James Kettle**, Practical HTTP Host header attacks (https://www.skeletonscribe.net/2013/05/practical-http-host-header-attacks.html)

## TODO

* **Test for Web Cache Poissoning attacks and try to escalate all the host header injections found**
* **Create a client to test for DNS pingbacks**
* **Export results in a JSON file**
* **Let the users to use his own list of payloads in the host header**
* **Comment and refactor the code**

