[![GitHub release](https://img.shields.io/badge/release-v0.1-brightgreen.svg?style=flat-square)](https://github.com/r0oth3x49/acloud-dl/releases/tag/v0.1)
[![GitHub stars](https://img.shields.io/github/stars/r0oth3x49/acloud-dl.svg?style=flat-square)](https://github.com/r0oth3x49/acloud-dl/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/r0oth3x49/acloud-dl.svg?style=flat-square)](https://github.com/r0oth3x49/acloud-dl/network)
[![GitHub issues](https://img.shields.io/github/issues/r0oth3x49/acloud-dl.svg?style=flat-square)](https://github.com/r0oth3x49/acloud-dl/issues)
[![GitHub license](https://img.shields.io/github/license/r0oth3x49/acloud-dl.svg?style=flat-square)](https://github.com/r0oth3x49/acloud-dl/blob/master/LICENSE)

# acloud-dl
**A cross-platform python based utility to download courses from acloud.guru for personal offline use.**

[![Capture.png](https://s26.postimg.cc/h8nxkvydl/Capture.png)](https://postimg.cc/image/nz4eublj9/)

## ***Features***

- Resume capability for a course video.
- List down course contents and video resolution, suggest the best resolution (option: `-i / --info`).
- Download lecture(s) requested resolution (option: `-q / --quality`).
- Download course to user requested path (option: `-o / --output`).
- Authentication using cookies (option: `-c / --cookies`).

## ***Extracting Cookies***

 - Login to your acloud.guru account via browser.
 - Once you are logged in right click on page the search for option called **Inspect Element** and click on that.
 - Under that look for **Network Tab** and click on that. Under that **Network Tab** click on Requests type **XHR** .
 - Now click on **Browse Courses** in the acloud.guru navbar and refresh the page you will see some requests under **Network Tab**.
 - Right click on any of the Requests which links to **acloud.guru**. Simply copy **Request Headers** and save to text file.
 - Done run the acloud-dl against that text file it will start downloading the course.

## ***Requirements***

- Python (2 or 3)
- Python `pip`
- Python module `requests`
- Python module `colorama`
- Python module `unidecode`
- Python module `six`
- Python module `requests[security]` or `pyOpenSSL`

## ***Module Installation***

	pip install -r requirements.txt
	
## ***Tested on***

- Windows 7/8/8.1/10
- Kali linux (2017.2)
- Ubuntu-LTS (64-bit) (tested with super user)
- Mac OSX 10.9.5 (tested with super user)
 
## ***Download acloud-dl***

You can download the latest version of acloud-dl by cloning the GitHub repository.

	git clone https://github.com/r0oth3x49/acloud-dl.git


## ***Usage***

***Steps before running acloud-dl.py which will list down courses you started***
 - Login to your acloud.guru account via browser.
 - Click on **Browse Courses**.
 - Move mouse to the course you want to download.
 - On mouseover you will see a button "GET" click on that.
 - It Will redirect to the course there is another button "START THIS COURSE" click on that.
 - Done, Now you can use the below usage.


***Download a course***

    python acloud-dl.py -c file_containing_cookie.txt
  
***Download course with specific resolution***

    python acloud-dl.py -c file_containing_cookie.txt -q 720
  
***Download course to a specific location***

    python acloud-dl.py -c file_containing_cookie.txt -o "/path/to/directory/"
  
***Download course with specific resolution to a specific location***

    python acloud-dl.py -c file_containing_cookie.txt -q 720 -o "/path/to/directory/"

***List down course information***

    python acloud-dl.py -c file_containing_cookie.txt --info


## **Advanced Usage**

<pre><code>
Author: Nasir khan (<a href="http://r0oth3x49.herokuapp.com/">r0ot h3x49</a>)

usage: acloud-dl.py [-h] [-v] [-c] [-o] [-q] [-i]

A cross-platform python based utility to download courses from acloud.guru for
personal offline use.

General:
  -h, --help       Shows the help.
  -v, --version    Shows the version.

Authentication:
  -c , --cookies   Cookies to authenticate with.

Advance:
  -o , --output    Download to specific directory.
  -q , --quality   Download specific video quality.
  -i, --info       List all lectures with available resolution.

Example:
  python acloud-dl.py -c cookies.txt
</code></pre>
