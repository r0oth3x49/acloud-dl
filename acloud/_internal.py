#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""

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

"""

import sys
import time

from ._colorized import *
from ._extract import CloudGuru
from ._shared import (
    CloudGuruCourses,
    CloudGuruCourseDownload,
    CloudGuruCourse,
    CloudGuruChapters,
    CloudGuruLectures,
    CloudGuruQuizzes,
    CloudLectureSubtitles,
    CloudGuruLectureStreams,
    CloudGuruLectureLectureAssets,
)
from ._getpass import GetPass


class InternCloudGuruCourses(CloudGuruCourses, CloudGuru, GetPass):
    def __init__(self, *args, **kwargs):
        self._info = ""
        super(InternCloudGuruCourses, self).__init__(*args, **kwargs)

    def _fetch_courses(self):
        if self._have_basic_courses:
            return
        if self._cookies:
            auth = self._login(cookies=self._cookies)
        if auth.get("login") == "successful":
            courses = self._extract_accessible_courses()
            self._courses = [InternCloudGuruCourseDownload(
                c, self) for c in courses]
            self._have_basic_courses = True


class InternCloudGuruCourseDownload(CloudGuruCourseDownload):
    def __init__(self, course, parent):
        self._info = course
        self._session = parent._session
        super(InternCloudGuruCourseDownload, self).__init__()
        self._id = self._info.get("uniqueid") or self._info.get("id")
        self._title = self._info.get("title")

    def _process_course(self, keep_alive, download_quizzes):
        self._course = InternCloudGuruCourse(
            self._info, self._session, keep_alive, download_quizzes)


class InternCloudGuruCourse(CloudGuruCourse, CloudGuru):
    def __init__(self, course, session, keep_alive, download_quizzes):
        self._info = ""
        self._course = course
        self._session = session
        self._keep_alive = keep_alive
        self._download_quizzes = download_quizzes
        super(InternCloudGuruCourse, self).__init__()

    def _fetch_course(self):
        if self._have_basic:
            return
        course_id = self._course.get("uniqueid") or self._course.get("id")
        self._info = self._real_extract(course_id=course_id)
        self._id = self._info["course_id"]
        self._url = self._info["course_url"]
        self._title = self._info["course_title"]
        self._chapters_count = self._info["total_chapters"]
        self._total_lectures = self._info["total_lectures"]
        self._chapters = [InternCloudGuruChapter(
            z, self._session, self._download_quizzes) for z in self._info["chapters"]]
        if not self._keep_alive:
            self._logout()
        self._have_basic = True


class InternCloudGuruChapter(CloudGuruChapters):
    def __init__(self, chapter, session, download_quizzes):
        super(InternCloudGuruChapter, self).__init__()
        self._session = session
        self._download_quizzes = download_quizzes
        self._chapter_id = chapter["chapter_id"]
        self._chapter_title = chapter["chapter_title"]
        self._chapter_index = chapter["chapter_index"]
        self._lectures_count = chapter["lectures_count"]
        self._quizzes_count = chapter["quizzes_count"]
        self._lectures = [InternCloudGuruLecture(
            z) for z in chapter["lectures"]]
        if self._download_quizzes:
            self._quizzes = [InternCloudGuruQuiz(
                z, self._session) for z in chapter["quizzes"]]


class InternCloudGuruLecture(CloudGuruLectures):
    def __init__(self, lectures):
        super(InternCloudGuruLecture, self).__init__()
        self._info = lectures

        self._lecture_id = self._info["lecture_id"]
        self._lecture_title = self._info["lecture_title"]
        self._lecture_index = self._info["lecture_index"]
        self._sources_count = self._info["sources_count"]
        self._assets_count = self._info["assets_count"]

        self._extension = self._info.get("extension") or None
        self._duration = self._info.get("duration") or None
        if self._duration:
            duration = int(self._duration)
            (mins, secs) = divmod(duration, 60)
            (hours, mins) = divmod(mins, 60)
            if hours == 0:
                self._duration = "%02d:%02d" % (mins, secs)
            else:
                self._duration = "%02d:%02d:%02d" % (hours, mins, secs)

    def _process_streams(self):
        streams = (
            [InternCloudGuruLectureStream(z, self)
             for z in self._info["sources"]]
            if self._sources_count > 0
            else []
        )
        self._streams = sorted(streams, key=lambda k: k.dimention[1])

    def _process_assets(self):
        assets = (
            [InternCloudGuruLectureAssets(z, self)
             for z in self._info["assets"]]
            if self._assets_count > 0
            else []
        )
        self._assets = assets

    def _process_subtitles(self):
        subtitles = (
            InternCloudLectureSubtitles(self._info["subtitle_url"], self)
            if self._info["subtitle_url"]
            else ""
        )
        self._subtitle = subtitles


class InternCloudGuruQuiz(CloudGuruQuizzes, CloudGuru):
    def __init__(self, quiz, session):
        super(InternCloudGuruQuiz, self).__init__()
        self._info = quiz
        self._session = session

        self._quiz_id = self._info.get("quiz_id")
        self._quiz_title = self._info.get("quiz_title")
        self._quiz_description = self._info.get("quiz_description")
        self._quiz_number_of_questions = self._info.get(
            "quiz_number_of_questions")
        self._quiz_skill_level = self._info.get("quiz_skill_level")
        self._quiz_duration = self._info.get("quiz_duration")

    def _fetch_quiz_content(self):
        self._quiz_content = self._extract_quiz_content(self._quiz_id)


class InternCloudGuruLectureStream(CloudGuruLectureStreams):
    def __init__(self, sources, parent):
        super(InternCloudGuruLectureStream, self).__init__(parent)

        self._mediatype = sources.get("type")
        self._extension = sources.get("extension")
        height = sources.get("height") or 0
        width = sources.get("width") or 0
        self._resolution = "%sx%s" % (width, height)
        self._dimention = width, height
        self._quality = self._resolution
        self._url = sources.get("url")
        self._path = sources.get("path")
        self._fsize = sources.get("size")


class InternCloudGuruLectureAssets(CloudGuruLectureLectureAssets):
    def __init__(self, assets, parent):
        super(InternCloudGuruLectureAssets, self).__init__(parent)

        self._mediatype = assets.get("type")
        self._extension = assets.get("extension")
        self._title = "{0:03d} ".format(
            parent._lecture_index) + assets.get("filename")
        self._url = assets.get("url")


class InternCloudLectureSubtitles(CloudLectureSubtitles):
    def __init__(self, subtitle_url, parent):
        super(InternCloudLectureSubtitles, self).__init__(parent)

        self._mediatype = "sub"
        self._extension = "vtt"
        self._language = "en"
        self._url = subtitle_url
