#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''

Author  : Nasir Khan (r0ot h3x49)
Github  : https://github.com/r0oth3x49
License : MIT


Copyright (c) 2018 Nasir Khan (r0ot h3x49)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the
Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR
ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH 
THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

import re
import os
import sys
import time
import json
import codecs
import requests
if sys.version_info[:2] >= (3, 0):

    import ssl
    import urllib.request as compat_urllib

    from urllib.error import HTTPError as compat_httperr
    from urllib.error import URLError as compat_urlerr
    from urllib.parse import urlparse as compat_urlparse
    from urllib.request import Request as compat_request
    from urllib.request import urlopen as compat_urlopen
    from urllib.request import build_opener as compat_opener
    from html.parser import HTMLParser as compat_HTMLParser
    from http.cookies import SimpleCookie as ParseCookie
    from requests.exceptions import ConnectionError as conn_error
    from requests.exceptions import HTTPError as http_error

    encoding, pyver = str, 3
    ssl._create_default_https_context = ssl._create_unverified_context
    
else:
    
    import urllib2 as compat_urllib

    from urllib2 import Request as compat_request
    from urllib2 import urlopen as compat_urlopen
    from urllib2 import URLError as compat_urlerr
    from urllib2 import HTTPError as compat_httperr
    from urllib2 import build_opener as compat_opener
    from urlparse import urlparse as compat_urlparse
    from Cookie import SimpleCookie as ParseCookie
    from HTMLParser import HTMLParser as compat_HTMLParser
    from requests.exceptions import ConnectionError as conn_error
    from requests.exceptions import HTTPError as http_error

    encoding, pyver = unicode, 2


NO_DEFAULT = object()

PUBLIC_GRAPHQL_URL = 'https://prod-api.acloud.guru/bff/graphql/public'
PROTECTED_GRAPHQL_URL = 'https://prod-api.acloud.guru/bff/graphql/protected'

# queries ..
GRAPH_QUERY_COURSES = '''{"query":"query getAccessibleCourses{getAccessibleCourses{...courseFields}}fragment courseFields on CondensedCourse{title,uniqueid}","variables":{}}'''
GRAPH_QUERY_COURSE_INFO = '''{"query":"query getCourses($courseIds: [String!]!){getCourses(courseIds: $courseIds){title,uniqueid,url,changelogs{date,description}metadata{createdDate,updatedDate,notifyUpdatedDate}sections{title,url,sequence,sectionIdentifier,components{title,url,sequence,componentIdentifier,enhancedSyllabus,description,content{type ... on VideoContent{duration,type,videosources{key,duration,type,bucket,filesize,description}}... on QuizContent{type,quizName}}notes: resources{title,url,bucket,key}}}}}","variables":{"courseIds":["%s"]}}'''
GRAPH_QUERY_DOWNLOAD_LINKS = '''{"query":"query getRestrictedFiles($files: [Files]!) { getRestrictedFiles(files: $files) { urls } }","variables":{"files":[%s]}}'''

HEADERS = {
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15',
            'Host' : 'prod-api.acloud.guru',
            }


__ALL__ = [
    're',
    'os',
    'sys',
    'time',
    'json',
    'pyver',
    "codecs",
    'encoding',
    'requests',
    'conn_error',
    'http_error',
    'compat_urlerr',
    'compat_opener',
    'compat_urllib',
    'compat_urlopen',
    'compat_request',
    'compat_httperr',
    'compat_urlparse',
    'compat_HTMLParser',
    'ParseCookie',
    'HEADERS',
    'NO_DEFAULT',
    'PUBLIC_GRAPHQL_URL',
    'PROTECTED_GRAPHQL_URL',
    'GRAPH_QUERY_COURSES',
    'GRAPH_QUERY_COURSE_INFO',
    'GRAPH_QUERY_DOWNLOAD_LINKS',
    ]
