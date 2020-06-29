#!/usr/bin/python3
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

import os
import re
import sys
import json

from pprint  import  pprint
from ._auth  import  CloudGuruAuth
from ._compat import (
            re,
            time,
            pyver,
            encoding,
            conn_error,
            PUBLIC_GRAPHQL_URL,
            PROTECTED_GRAPHQL_URL,
            GRAPH_QUERY_COURSES,
            GRAPH_QUERY_COURSE_INFO,
            GRAPH_QUERY_DOWNLOAD_LINKS,
            )
from ._sanitize import (
            slugify,
            sanitize,
            SLUG_OK
            )
from ._colorized import *
from ._progress import ProgressBar



class CloudGuru(ProgressBar):
    
    def __init__(self):
        self._session = ''
        self._cookies = ''
        super(CloudGuru, self).__init__()

    def _clean(self, text):
        ok = re.compile(r'[^\\/:*?"<>|]')
        text = "".join(x if ok.match(x) else "_" for x in text)
        text = (text.lstrip('0123456789.- ')).rstrip('. ')
        return text

    def _sanitize(self, unsafetext):
        text = slugify(unsafetext, lower=False, spaces=True, ok=SLUG_OK + '()._-')
        return self._clean(text)

    def _extract_cookie_string(self, raw_cookies):
        try:
            mobj = re.search(r'(?is)(Authorization:\s*Bearer\s*(?P<access_token>(.+?)))(\"\s|\s)', raw_cookies)
            if not mobj:
                mobj = re.search(r'(?i)(?:auth0_token=(?P<access_token>[a-zA-Z0-9_.-]+))', raw_cookies)
            access_token = mobj.group('access_token')
        except:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Cookies error, Request Headers is required.\n")
            sys.stdout.write(fc + sd + "[" + fm + sb + "i" + fc + sd + "] : " + fg + sb + "Copy Request Headers for single request to a file, while you are logged in.\n")
            sys.exit(0)
        return {'access_token' : access_token}

    def _login(self, cookies=''):
        if cookies:
            auth = CloudGuruAuth()
            self._cookies = self._extract_cookie_string(raw_cookies=cookies)
            access_token = self._cookies.get('access_token')
            time.sleep(3)
            self._session = auth.authenticate(access_token=access_token)
        if self._session is not None:
            return {'login' : 'successful'}
        else:
            return {'login' : 'failed'}

    def _logout(self):

        return self._session.terminate()

    def _extract_accessible_courses(self):
        try:
            response = self._session._post(PUBLIC_GRAPHQL_URL, GRAPH_QUERY_COURSES)
        except conn_error as e:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Connection error : make sure your internet connection is working.\n")
            time.sleep(0.8)
            sys.exit(0)
        else:
            courses = response.json().get('data')
            if courses:
                accessable_courses = courses.get('getAccessibleCourses')
                if not accessable_courses:
                    sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Zero accessable courses: no courses found in your accessable courses.\n")
                    sys.stdout.write(fc + sd + "[" + fm + sb + "i" + fc + sd + "] : " + fg + sb + "Click 'START THIS COURSE' button to be able to get listed for download..\n")
                    sys.stdout.write(fc + sd + "[" + fm + sb + "i" + fc + sd + "] : " + fg + sb + "OR follow --> (https://github.com/r0oth3x49/acloud-dl#usage) for proper help..\n")
                    sys.exit(0)
                courses = accessable_courses
                for course in courses:
                    title_clean = self._clean(course.get("title"))
                    if title_clean:
                        course.update({"title": title_clean})
                return courses
            if not courses:
                if response.headers.get('x-amzn-ErrorType'):
                    sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Authorization error : it seems your authorization token is expired.\n")
                    sys.stdout.write(fc + sd + "[" + fm + sb + "i" + fc + sd + "] : " + fg + sb + "Login again & copy Request headers for a single request to file..\n")
                    sys.exit(0)

    def _extract_assets(self, assets):
        _temp = []
        if assets and isinstance(assets, list):
            for entry in assets:
                filename = self._sanitize(entry.get('title'))
                url = entry.get('url')
                bucket = entry.get('bucket')
                key = entry.get('key')
                regex = r"(?i)(?:^.*\.(?P<extension>jpg|gif|doc|pdf|zip|docx|ppt|pptx|pptm|txt|py|c|json|md|html|htm|sh|batch|bat))$"
                if url:
                    match = re.match(regex, url)
                    if match:
                        extension = match.group('extension')
                        _temp.append({
                                'url' : url,
                                'type' : 'file' if 'github' not in url else 'external_link',
                                'filename' : filename.rsplit('.', 1)[0] if '.' in filename else filename,
                                'extension' : extension,
                            })
                    if not match:
                        _temp.append({
                                'url' : url,
                                'type' : 'external_link',
                                'filename' : filename.rsplit('.', 1)[0] if '.' in filename else filename,
                                'extension' : 'txt',
                            })
                if not url:
                    query = '''{"bucket": "%s","filePath": "%s"}''' % (bucket, key)
                    query = GRAPH_QUERY_DOWNLOAD_LINKS % (query)
                    try:
                        data = self._session._post(PROTECTED_GRAPHQL_URL, query)
                    except conn_error as e:
                        pass
                    else:
                        response = data.json().get('data')
                        if response:
                            url = response['getRestrictedFiles'].get('urls')[0]
                            match = re.match(regex, url)
                            if match:
                                extension = match.group('extension')
                            if not match:
                                extension = filename.rsplit('.', 1)[-1] if '.' in url else 'zip'
                            _temp.append({
                                    'url' : url,
                                    'type' : 'file',
                                    'filename' : filename.rsplit('.', 1)[0] if '.' in filename else filename,
                                    'extension' : extension,
                                })
                        if not response:
                            if data.headers.get('x-amzn-ErrorType'):
                                sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Authorization error : it seems your authorization token is expired.\n")
                                sys.stdout.write(fc + sd + "[" + fm + sb + "i" + fc + sd + "] : " + fg + sb + "Login again & copy Request headers for a single request to file..\n")
                                sys.exit(0)

        return _temp

    def _extract_sources(self, sources):
        _temp = []
        for entry in sources:
            resolution = entry.get('description')
            if resolution == 'hls' or resolution == 'webm-720p' or resolution == 'web-preset':
                continue
            if resolution:
                source_type = entry.get('type').replace('video/', '')
                url = entry.get('key')
                bucket = entry.get('bucket')
                filesize = entry.get('filesize') or 0
                query = '''{"bucket": "%s","filePath": "%s"}''' % (bucket, url)
                if resolution == "2160p":
                    height, width = 2160, 3840
                elif resolution == "1440p":
                    height, width = 1440, 2560
                elif resolution == "1080p":
                    height, width = 1080, 1920
                elif resolution == "720p":
                    height, width = 720, 1280
                elif resolution == "480p":
                    height, width = 480, 854
                _temp.append({
                        'quality' : resolution,
                        'type' : 'video',
                        'extension' : source_type,
                        'path' : url,
                        'url' : query,
                        'height' : height,
                        'width' : width,
                        'size' : filesize
                    })
            if not resolution:
                source_type = entry.get('type').replace('video/', '')
                url = entry.get('key')
                bucket = entry.get('bucket')
                filesize = entry.get('filesize') or 0
                query = '''{"bucket": "%s","filePath": "%s"}''' % (bucket, url)
                _temp.append({
                        'quality' : resolution,
                        'type' : 'video',
                        'extension' : source_type,
                        'path' : url,
                        'url' : query,
                        'height' : 720,
                        'width' : 1280,
                        'size' : filesize
                    })
        return _temp

    def _extract_course_information(self, course):
        _temp = []
        chapters = course.get('chapters')
        lectures = [l.get('lectures') for l in chapters]
        for lecture in lectures:
            sources = [s.get('sources') for s in lecture]
            for entry in sources:
                query = [e.get('url') for e in entry]
                for _str in query:
                    _temp.append(_str)
        files = ','.join(_temp)
        query = GRAPH_QUERY_DOWNLOAD_LINKS % (files)
        try:
            response = self._session._post(PROTECTED_GRAPHQL_URL, query)
        except conn_error as e:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Connection error : make sure your internet connection is working.\n")
            time.sleep(0.8)
            sys.exit(0)
        else:
            data = response.json().get('data')
            if data:
                data = data['getRestrictedFiles'].get('urls')
                chapters = course.get('chapters')
                for entry in chapters:
                    lectures = entry.get('lectures')
                    for entry in lectures:
                        text = '\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading course information .. "
                        self._spinner(text)
                        sources = entry.get('sources')
                        for entry in sources:
                            path = entry.get('path')
                            for url in data:
                                if path in url:
                                    entry.update({'url' : url})
            if not data:
                if response.headers.get('x-amzn-ErrorType'):
                    sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Authorization error : it seems your authorization token is expired.\n")
                    sys.stdout.write(fc + sd + "[" + fm + sb + "i" + fc + sd + "] : " + fg + sb + "Login again & copy Request headers for a single request to file..\n")
                    sys.exit(0)
        return course

    def _extract_lectures(self, lectures):
        _temp = []
        for entry in lectures:
            lecture_title = self._sanitize(entry.get('title'))
            lecture_index = int(entry.get('sequence')) + 1
            lecture_id = entry.get('componentIdentifier')
            content_type = entry['content'].get('type')
            lecture = "{0:03d} {1!s}".format(lecture_index, lecture_title)
            assets = entry.get('notes')
            assets = self._extract_assets(assets)
            if content_type == 'video':
                sources = entry['content'].get('videosources')
                if not sources:
                    continue
                duration = entry['content'].get('duration')
                extension = entry['content'].get('type')
                sources = self._extract_sources(sources)
                subtitle_url = None
                for  s in sources:
                    cid = s.get("url")
                    if cid:
                        cid = cid.rsplit("/", 1)[-1]
                        cid = re.search(r"[a-zA-Z0-9]{8}\-[a-zA-Z0-9]{4}\-[a-zA-Z0-9]{4}\-[a-zA-Z0-9]{4}\-[a-zA-Z0-9]{12}", cid)
                        if cid:
                            subtitle_url = f"https://acloudguru-subtitles-production.s3.amazonaws.com/{cid.group()}.vtt"
                            break
                if lecture not in _temp:
                    _temp.append({
                            'lecture_title' : lecture,
                            'lecture_id' : lecture_id,
                            'lecture_index' : lecture_index,
                            'subtitle_url': subtitle_url,
                            'duration' : duration,
                            'extension' : extension,
                            'sources' : sources,
                            'assets' : assets,
                            'sources_count' : len(sources),
                            'assets_count' : len(assets)
                        })
        return _temp

    def _real_extract(self, course_id):

        acloud = {}
        query = GRAPH_QUERY_COURSE_INFO % (course_id)

        try:
            response = self._session._post(PUBLIC_GRAPHQL_URL, query)
        except conn_error as e:
            sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Connection error : make sure your internet connection is working.\n")
            time.sleep(0.8)
            sys.exit(0)
        else:
            course = response.json().get('data')
            if course:
                course = course['getCourses'][0]
                course_url = course.get('url')
                course_title = self._sanitize(course.get('title'))
                course_id = course.get('uniqueid')
                chapters = course.get('sections')

                acloud['course_id'] = course_id
                acloud['course_url'] = course_url
                acloud['course_title'] = course_title
                acloud['total_chapters'] = len(chapters)
                acloud['total_lectures'] = sum([len(chapter.get('components', [])) for chapter in chapters])
                acloud['chapters'] = []


                for entry in chapters:
                    chapter_title = self._sanitize(entry.get('title'))
                    chapter_id = entry.get('sectionIdentifier')
                    chapter_url = entry.get('url')
                    chapter_index = int(entry.get('sequence')) + 1
                    lectures_count = len(entry.get('components'))
                    lectures = entry.get('components')
                    chapter = "{0:02d} {1!s}".format(chapter_index, chapter_title)
                    acloud['chapters'].append({
                        'chapter_title' : chapter,
                        'chapter_id' : chapter_id,
                        'chapter_index' : chapter_index,
                        'lectures_count' : lectures_count,
                        'chapter_url' : chapter_url,
                        'lectures' : self._extract_lectures(lectures)
                    })
                acloud = self._extract_course_information(acloud)
            if not course:
                if response.headers.get('x-amzn-ErrorType'):
                    sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Authorization error : it seems your authorization token is expired.\n")
                    sys.stdout.write(fc + sd + "[" + fm + sb + "i" + fc + sd + "] : " + fg + sb + "Login again & copy Request headers for a single request to file..\n")
                    sys.exit(0)

        # with open("course.json", "w") as f:
        #     json.dump(acloud, f, indent=4)
        # f.close()
        # exit(0)
        return acloud
