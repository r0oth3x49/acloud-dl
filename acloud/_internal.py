#!/usr/bin/python
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

import sys
import time

from ._colorized import *
from ._extract import CloudGuru
from ._shared import (
        CloudGuruCourse, 
        CloudGuruChapters, 
        CloudGuruLectures, 
        CloudLectureSubtitles,
        CloudGuruLectureStreams,
        CloudGuruLectureLectureAssets
    )
from ._getpass import GetPass

class InternCloudGuruCourse(CloudGuruCourse, CloudGuru, GetPass):
    def __init__(self, *args, **kwargs):
        self._info    = ''
        super(InternCloudGuruCourse, self).__init__(*args, **kwargs)

    def _fetch_course(self):
        if self._have_basic:
            return
        if self._cookies:
            sys.stdout.write('\033[2K\033[1G\r\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading accessible courses information .. \r")
            auth = self._login(cookies=self._cookies)
        if auth.get('login') == 'successful':
            courses = self._extract_accessible_courses()
            sys.stdout.write('\033[2K\033[1G\r\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading accessible courses information .. (done)\r\n")
            counter = 1
            for entry in courses:
                title = entry.get('title')
                sys.stdout.write(fc + sd + "[" + fm + sb + "%s" % (counter) + fc + sd + "] : " + fg + sb + "%s\n" % (title))
                counter += 1
            question = fc + sd + "[" + fw + sb + "?" + fc + sd + "] : " + fy + sb + "select course number between (1/%s): " % (len(courses))+ fg + sb
            ask_user = int(self._getuser(prompt=question))
            if ask_user and ask_user > 0 and ask_user <= len(courses):
                course_id = courses[ask_user-1].get('uniqueid')
                sys.stdout.write('\033[2K\033[1G\r\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading course information .. \r")
                self._info              =       self._real_extract(course_id=course_id)
                sys.stdout.write('\033[2K\033[1G\r\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloaded course information .. (done)\r\n")
                self._id                =       self._info['course_id']
                self._url               =       self._info['course_url']
                self._title             =       self._info['course_title']
                self._chapters_count    =       self._info['total_chapters']
                self._total_lectures    =       self._info['total_lectures']
                self._chapters          =       [InternCloudGuruChapter(z) for z in self._info['chapters']]
                self._logout()
                self._have_basic = True
            else:
                sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "User input is required, No input specified ..\n")
                sys.exit(0)


class InternCloudGuruChapter(CloudGuruChapters):
    
    def __init__(self, chapter):
        super(InternCloudGuruChapter, self).__init__()

        self._chapter_id        = chapter['chapter_id']
        self._chapter_title     = chapter['chapter_title']
        self._chapter_index     = chapter['chapter_index']
        self._lectures_count    = chapter['lectures_count']
        self._lectures          = [InternCloudGuruLecture(z) for z in chapter['lectures']]


class InternCloudGuruLecture(CloudGuruLectures):

    def __init__(self, lectures):
        super(InternCloudGuruLecture, self).__init__()
        self._info              = lectures

        self._lecture_id        = self._info['lecture_id']
        self._lecture_title     = self._info['lecture_title']
        self._lecture_index     = self._info['lecture_index']
        self._sources_count     = self._info['sources_count']
        self._assets_count      = self._info['assets_count']
        
        self._extension         = self._info.get('extension') or None
        self._duration          = self._info.get('duration') or None
        if self._duration:
            duration = int(self._duration)
            (mins, secs) = divmod(duration, 60)
            (hours, mins) = divmod(mins, 60)
            if hours == 0:
                self._duration = "%02d:%02d" % (mins, secs)
            else:
                self._duration = "%02d:%02d:%02d" % (hours, mins, secs)

    def _process_streams(self):
        streams = [InternCloudGuruLectureStream(z, self) for z in self._info['sources']] if self._sources_count > 0 else []
        self._streams = streams

    def _process_assets(self):
        assets  =   [InternCloudGuruLectureAssets(z, self) for z in self._info['assets']] if self._assets_count > 0 else []
        self._assets = assets

    def _process_subtitles(self):
        subtitles = InternCloudLectureSubtitles(self._info['subtitle_url'], self) if self._info['subtitle_url'] else ""
        self._subtitle = subtitles


class InternCloudGuruLectureStream(CloudGuruLectureStreams):

    def __init__(self, sources, parent):
        super(InternCloudGuruLectureStream, self).__init__(parent)

        self._mediatype = sources.get('type')
        self._extension = sources.get('extension')
        height = sources.get('height') or 0
        width = sources.get('width') or 0
        self._resolution = '%sx%s' % (width, height)
        self._dimention = width, height
        self._quality = self._resolution
        self._url = sources.get('url')
        self._path = sources.get('path')
        self._fsize = sources.get('size')


class InternCloudGuruLectureAssets(CloudGuruLectureLectureAssets):

    def __init__(self, assets, parent):
        super(InternCloudGuruLectureAssets, self).__init__(parent)

        self._mediatype = assets.get('type')
        self._extension = assets.get('extension')
        self._title = '{0:03d} {1!s}'.format(parent._lecture_index, assets.get('filename'))
        self._url = assets.get('url')

class InternCloudLectureSubtitles(CloudLectureSubtitles):

    def __init__(self, subtitle_url, parent):
        super(InternCloudLectureSubtitles, self).__init__(parent)

        self._mediatype = "sub"
        self._extension = "vtt"
        self._language = "en"
        self._url = subtitle_url