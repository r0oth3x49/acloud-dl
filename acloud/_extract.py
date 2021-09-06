#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=E,C,W,R

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

import os
import re
import sys
import json

from pprint import pprint
from ._auth import CloudGuruAuth
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
    GRAPH_QUERY_SUBTITLE_LINKS,
    GRAPH_QUERY_UseHasCourseAccess,
    GRAPH_QUERY_UNPROTECTED_DOWNLOAD_LINKS,
)
from ._sanitize import slugify, sanitize, SLUG_OK
from ._colorized import *
from ._progress import ProgressBar


class CloudGuru(ProgressBar):
    def __init__(self):
        self._session = ""
        self._cookies = ""
        super(CloudGuru, self).__init__()

    def _clean(self, text):
        ok = re.compile(r'[^\\/:*?"<>|]')
        text = "".join(x if ok.match(x) else "_" for x in text)
        text = (text.lstrip("0123456789.- ")).rstrip(". ")
        return text

    def _sanitize(self, unsafetext):
        text = slugify(unsafetext, lower=False, spaces=True, ok=SLUG_OK + "()._-")
        return self._clean(text)

    def _extract_cookie_string(self, raw_cookies):
        try:
            mobj = re.search(
                r"(?is)(Authorization:\s*Bearer\s*(?P<access_token>(.+?)))($|\s|\"|\')",
                raw_cookies,
            )
            if not mobj:
                mobj = re.search(
                    r"(?i)(?:auth0_token=(?P<access_token>[a-zA-Z0-9_.-]+))",
                    raw_cookies,
                )
            access_token = mobj.group("access_token")
        except:
            sys.stdout.write(
                fc
                + sd
                + "["
                + fr
                + sb
                + "-"
                + fc
                + sd
                + "] : "
                + fr
                + sb
                + "Cookies error, Request Headers is required.\n"
            )
            sys.stdout.write(
                fc
                + sd
                + "["
                + fm
                + sb
                + "i"
                + fc
                + sd
                + "] : "
                + fg
                + sb
                + "Copy Request Headers for single request to a file, while you are logged in.\n"
            )
            sys.exit(0)
        return {"access_token": access_token}

    def _login(self, cookies=""):
        if cookies:
            auth = CloudGuruAuth()
            self._cookies = self._extract_cookie_string(raw_cookies=cookies)
            access_token = self._cookies.get("access_token")
            time.sleep(3)
            self._session = auth.authenticate(access_token=access_token)
        if self._session is not None:
            return {"login": "successful"}
        else:
            return {"login": "failed"}

    def _logout(self):

        return self._session.terminate()

    def _extract_accessible_courses(self):
        try:
            response = self._session._post(
                PUBLIC_GRAPHQL_URL, GRAPH_QUERY_UseHasCourseAccess
            )
        except conn_error as e:
            sys.stdout.write(
                fc
                + sd
                + "["
                + fr
                + sb
                + "-"
                + fc
                + sd
                + "] : "
                + fr
                + sb
                + "Connection error : make sure your internet connection is working.\n"
            )
            time.sleep(0.8)
            sys.exit(0)
        else:
            courses = response.json().get("data")
            if courses:
                accessable_courses = courses.get("getAccessibleCourses") or courses.get(
                    "userAccessibleCourses"
                )
                if not accessable_courses:
                    sys.stdout.write(
                        fc
                        + sd
                        + "["
                        + fr
                        + sb
                        + "-"
                        + fc
                        + sd
                        + "] : "
                        + fr
                        + sb
                        + "Zero accessable courses: no courses found in your accessable courses.\n"
                    )
                    sys.stdout.write(
                        fc
                        + sd
                        + "["
                        + fm
                        + sb
                        + "i"
                        + fc
                        + sd
                        + "] : "
                        + fg
                        + sb
                        + "Click 'START THIS COURSE' button to be able to get listed for download..\n"
                    )
                    sys.stdout.write(
                        fc
                        + sd
                        + "["
                        + fm
                        + sb
                        + "i"
                        + fc
                        + sd
                        + "] : "
                        + fg
                        + sb
                        + "OR follow --> (https://github.com/r0oth3x49/acloud-dl#usage) for proper help..\n"
                    )
                    sys.exit(0)
                courses = accessable_courses
                for course in courses:
                    title_clean = self._clean(course.get("title"))
                    if title_clean:
                        course.update({"title": title_clean})
                return courses
            if not courses:
                sys.stdout.write(
                    "\033[2K\033[1G\r\r"
                    + fc
                    + sd
                    + "["
                    + fm
                    + sb
                    + "*"
                    + fc
                    + sd
                    + "] : "
                    + fg
                    + sb
                    + "Downloading accessible courses information .. ("
                    + fr
                    + sb
                    + "failed"
                    + fg
                    + sb
                    + ")\r\n"
                )
                errors = response.json().get("errors")
                if response.headers.get("x-amzn-ErrorType"):
                    sys.stdout.write(
                        fc
                        + sd
                        + "["
                        + fr
                        + sb
                        + "-"
                        + fc
                        + sd
                        + "] : "
                        + fr
                        + sb
                        + "Authorization error : it seems your authorization token is expired.\n"
                    )
                    sys.stdout.write(
                        fc
                        + sd
                        + "["
                        + fm
                        + sb
                        + "i"
                        + fc
                        + sd
                        + "] : "
                        + fg
                        + sb
                        + "Login again & copy Request headers for a single request to file..\n"
                    )
                    sys.exit(0)
                if errors:
                    for error in errors:
                        msg = error.get("message")
                        sys.stdout.write(
                            fc
                            + sd
                            + "["
                            + fr
                            + sb
                            + "-"
                            + fc
                            + sd
                            + "] : "
                            + fr
                            + sb
                            + "acloud-guru Says : {}.\n".format(msg)
                        )
                    sys.stdout.write(
                        fc
                        + sd
                        + "["
                        + fm
                        + sb
                        + "i"
                        + fc
                        + sd
                        + "] : "
                        + fg
                        + sb
                        + "Report the issue to 'https://github.com/r0oth3x49/acloud-dl/issues'\n"
                    )
                    sys.exit(0)

    def _extract_assets(self, assets):
        _temp = []
        if assets and isinstance(assets, list):
            for entry in assets:
                filename = self._sanitize(entry.get("title"))
                url = entry.get("url")
                bucket = entry.get("bucket")
                key = entry.get("key")
                regex = r"(?i)(?:^.*\.(?P<extension>jpg|gif|doc|pdf|zip|docx|ppt|pptx|pptm|txt|py|c|json|md|html|htm|sh|batch|bat))$"
                if url:
                    match = re.match(regex, url)
                    if match:
                        extension = match.group("extension")
                        _temp.append(
                            {
                                "url": url,
                                "type": "file"
                                if "github" not in url
                                else "external_link",
                                "filename": filename.rsplit(".", 1)[0]
                                if "." in filename
                                else filename,
                                "extension": extension,
                            }
                        )
                    if not match:
                        _temp.append(
                            {
                                "url": url,
                                "type": "external_link",
                                "filename": filename.rsplit(".", 1)[0]
                                if "." in filename
                                else filename,
                                "extension": "txt",
                            }
                        )
                # if not url and bucket and key:
                #     query = {"bucket": bucket,"filePath": key}
                #     query = GRAPH_QUERY_DOWNLOAD_LINKS % (query)
                #     try:
                #         data = self._session._post(PROTECTED_GRAPHQL_URL, query)
                #     except conn_error:
                #         pass
                #     else:
                #         response = data.json().get('data')
                #         if response:
                #             url = response['getRestrictedFiles'].get('urls')[0]
                #             match = re.match(regex, url)
                #             if match:
                #                 extension = match.group('extension')
                #             if not match:
                #                 extension = filename.rsplit('.', 1)[-1] if '.' in url else 'zip'
                #             _temp.append({
                #                     'url' : url,
                #                     'type' : 'file',
                #                     'filename' : filename.rsplit('.', 1)[0] if '.' in filename else filename,
                #                     'extension' : extension,
                #                 })
                #         if not response:
                #             if data.headers.get('x-amzn-ErrorType'):
                #                 sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "Authorization error : it seems your authorization token is expired.\n")
                #                 sys.stdout.write(fc + sd + "[" + fm + sb + "i" + fc + sd + "] : " + fg + sb + "Login again & copy Request headers for a single request to file..\n")
                #                 sys.exit(0)
        return _temp

    def _extract_sources(self, sources):
        _temp = []

        def ret_hw(res):
            height, width = 0, 0
            if res == "2160p":
                height, width = 2160, 3840
            elif res == "1440p":
                height, width = 1440, 2560
            elif res == "1080p":
                height, width = 1080, 1920
            elif res == "720p":
                height, width = 720, 1280
            elif res == "480p":
                height, width = 480, 854
            return height, width

        for entry in sources:
            resolution = entry.get("quality")
            key = entry.get("key")
            if not resolution:
                mobj = re.search(
                    r"(?is)(?P<resolution>(?:2160|1440|1080|720|480|360)p)", key
                )
                if mobj:
                    resolution = mobj.group("resolution")
            if (
                resolution == "hls"
                or resolution == "webm-720p"
                or resolution == "web-preset"
            ):
                continue
            if resolution:
                source_type = entry.get("type").replace("video/", "")
                url = entry.get("key")
                bucket = entry.get("bucket")
                signed_url = entry.get("signedUrl")
                filesize = entry.get("filesize") or 0
                query = {"bucket": bucket, "filePath": url}
                height, width = ret_hw(resolution)
                _temp.append(
                    {
                        "quality": resolution,
                        "type": "video",
                        "extension": source_type,
                        "path": url,
                        "url": query if not signed_url else signed_url,
                        "height": height,
                        "width": width,
                        "size": filesize,
                        "signed_url": signed_url,
                    }
                )
            if not resolution:
                source_type = entry.get("type").replace("video/", "")
                url = entry.get("key")
                bucket = entry.get("bucket")
                signed_url = entry.get("signedUrl")
                filesize = entry.get("filesize") or 0
                query = {"bucket": bucket, "filePath": url}
                # if acloud does not return the quality/resoltion hard code the height and width
                # this hack will get all the sources without breaking any functionality.
                # example course "Docker for DevOps - From Development to Production"
                # 1st chapter's lectures don't have any resolution/quality.
                height, width = 720, 1280
                _temp.append(
                    {
                        "quality": resolution,
                        "type": "video",
                        "extension": source_type,
                        "path": url,
                        "url": query if not signed_url else signed_url,
                        "height": height,
                        "width": width,
                        "size": filesize,
                        "signed_url": signed_url,
                    }
                )
        return _temp

    def _fetch_queryable(self, course):
        _temp = []
        chapters = course.get("chapters")
        lectures = [l.get("lectures") for l in chapters]
        for lecture in lectures:
            sources = [s.get("sources") for s in lecture]
            for entry in sources:
                query = [
                    e.get("url")
                    for e in entry
                    if e.get("type") != "hls" and isinstance(e.get("url"), dict)
                ]
                for queryable in query:
                    _temp.append(queryable)
        if _temp:
            _temp = [
                dict(tupleized)
                for tupleized in set(tuple(item.items()) for item in _temp)
            ]
        files = {}
        if _temp:
            files = {"files": _temp}
        return files

    def _extract_course_information(self, course):
        files = self._fetch_queryable(course=course)
        if files:
            GRAPH_QUERY_DOWNLOAD_LINKS.update({"variables": files})
            query = GRAPH_QUERY_DOWNLOAD_LINKS
            try:
                response = self._session._post(PROTECTED_GRAPHQL_URL, query)
            except conn_error as e:
                sys.stdout.write(
                    fc
                    + sd
                    + "["
                    + fr
                    + sb
                    + "-"
                    + fc
                    + sd
                    + "] : "
                    + fr
                    + sb
                    + "Connection error : make sure your internet connection is working.\n"
                )
                time.sleep(0.8)
                sys.exit(0)
            else:
                data = response.json().get("data")
                if data:
                    data = data["getRestrictedFiles"].get("urls", [])
                    chapters = course.get("chapters")
                    for chap in chapters:
                        lectures = chap.get("lectures")
                        for lec in lectures:
                            text = (
                                "\r"
                                + fc
                                + sd
                                + "["
                                + fm
                                + sb
                                + "*"
                                + fc
                                + sd
                                + "] : "
                                + fg
                                + sb
                                + "Downloading course information .. "
                            )
                            self._spinner(text)
                            sources = lec.get("sources")
                            for entry in sources:
                                path = entry.get("path")
                                for url in data:
                                    if path in url:
                                        entry.update({"url": url})
                if not data:
                    if response.headers.get("x-amzn-ErrorType"):
                        sys.stdout.write(
                            fc
                            + sd
                            + "["
                            + fr
                            + sb
                            + "-"
                            + fc
                            + sd
                            + "] : "
                            + fr
                            + sb
                            + "Authorization error : it seems your authorization token is expired.\n"
                        )
                        sys.stdout.write(
                            fc
                            + sd
                            + "["
                            + fm
                            + sb
                            + "i"
                            + fc
                            + sd
                            + "] : "
                            + fg
                            + sb
                            + "Login again & copy Request headers for a single request to file..\n"
                        )
                        sys.exit(0)
        return course

    def _fetch_hls_streams_by_content_ids(self, content_ids):
        _temp = []
        GRAPH_QUERY_UNPROTECTED_DOWNLOAD_LINKS["variables"].update(
            {"contentIds": content_ids}
        )
        query = GRAPH_QUERY_UNPROTECTED_DOWNLOAD_LINKS
        try:
            response = self._session._post(PROTECTED_GRAPHQL_URL, query)
        except conn_error as e:
            sys.stdout.write(
                fc
                + sd
                + "["
                + fr
                + sb
                + "-"
                + fc
                + sd
                + "] : "
                + fr
                + sb
                + "Connection error : make sure your internet connection is working.\n"
            )
            time.sleep(0.8)
            sys.exit(0)
        else:
            data = response.json()
            unprotected_contents = data.get("data", {}).get(
                "getUnprotectedContents", []
            )
            if unprotected_contents:
                for entry in unprotected_contents:
                    _id = entry.get("contentId")
                    sources = entry.get("sources", [])
                    _sources = []
                    for s in sources:
                        source_type = s.get("sourceType")
                        extension = s.get("ext")
                        height = s.get("height")
                        width = s.get("width")
                        url = s.get("signedUrl")
                        filesize = int(s.get("fileSize", "0"))
                        path = s.get("key")
                        resolution = str(height)
                        if height and width and source_type == "VIDEO_AUDIO":
                            _sources.append(
                                {
                                    "quality": resolution,
                                    "type": "hls",
                                    "extension": extension,
                                    "path": path,
                                    "url": url,
                                    "height": height,
                                    "width": width,
                                    "size": filesize,
                                }
                            )
                    if _sources:
                        _temp.append(
                            {
                                "lecture_id": _id,
                                "sources": _sources,
                                "sources_count": len(_sources),
                            }
                        )
        return _temp

    def _extract_subtitle(self, sub_ids):
        _temp = []
        GRAPH_QUERY_SUBTITLE_LINKS["variables"].update({"contentIds": sub_ids})
        query = GRAPH_QUERY_SUBTITLE_LINKS
        try:
            response = self._session._post(PROTECTED_GRAPHQL_URL, query)
        except conn_error as e:
            sys.stdout.write(
                fc
                + sd
                + "["
                + fr
                + sb
                + "-"
                + fc
                + sd
                + "] : "
                + fr
                + sb
                + "Connection error : make sure your internet connection is working.\n"
            )
            time.sleep(0.8)
            sys.exit(0)
        else:
            data = response.json()
            subtitles = data.get("data", {}).get("subtitleTranscription", [])
            if subtitles:
                for entry in subtitles:
                    _id = entry.get("id")
                    url = entry.get("subtitleUrl")
                    _temp.append({"subtitle_id": _id, "url": url})
        return _temp

    def _extract_sub_id(self, videoposter):
        _id = ""
        if videoposter:
            videoposter = videoposter.rsplit("/", 1)[-1]
            mobj = re.search(
                r"[a-zA-Z0-9]{8}\-[a-zA-Z0-9]{4}\-[a-zA-Z0-9]{4}\-[a-zA-Z0-9]{4}\-[a-zA-Z0-9]{12}",
                videoposter,
            )
            if mobj:
                _id = mobj.group()
        return _id

    def _extract_lectures(self, lectures):
        _temp = []
        contentid_list = []
        sub_ids = []
        for entry in lectures:
            lecture_title = self._sanitize(entry.get("title"))
            lecture_index = int(entry.get("sequence")) + 1
            lecture_id = entry.get("id")
            content_type = entry["content"].get("type")
            lecture = "{0:03d} {1!s}".format(lecture_index, lecture_title)
            assets = entry.get("resources")
            assets = self._extract_assets(assets)
            duration = entry["content"].get("duration")
            extension = entry["content"].get("type")
            if content_type == "video":
                videoposter = entry["content"].get("videoposter", "")
                content_id = entry["content"].get("contentId")
                sub_id = self._extract_sub_id(videoposter)
                if sub_id and sub_id not in sub_ids:
                    sub_ids.append(sub_id)
                if not sub_id and content_id:
                    sub_ids.append(content_id)
                if content_id:
                    contentid_list.append(content_id)
                    _temp.append(
                        {
                            "lecture_title": lecture,
                            "lecture_id": content_id,
                            "lecture_index": lecture_index,
                            "subtitle_id": sub_id,
                            "subtitle_url": None,
                            "duration": duration,
                            "extension": extension,
                            "sources": [],
                            "assets": assets,
                            "sources_count": 0,
                            "assets_count": len(assets),
                        }
                    )
                    continue
                sources = entry["content"].get("videosources")
                if not sources:
                    continue
                sources = self._extract_sources(sources)
                if lecture not in _temp:
                    _temp.append(
                        {
                            "lecture_title": lecture,
                            "lecture_id": lecture_id,
                            "lecture_index": lecture_index,
                            "subtitle_id": sub_id,
                            "subtitle_url": None,
                            "duration": duration,
                            "extension": extension,
                            "sources": sources,
                            "assets": assets,
                            "sources_count": len(sources),
                            "assets_count": len(assets),
                        }
                    )
        if contentid_list:
            streams = self._fetch_hls_streams_by_content_ids(contentid_list)
            for i in _temp:
                _id = i.get("lecture_id")
                text = (
                    "\r"
                    + fc
                    + sd
                    + "["
                    + fm
                    + sb
                    + "*"
                    + fc
                    + sd
                    + "] : "
                    + fg
                    + sb
                    + "Downloading course information .. "
                )
                self._spinner(text)
                for s in streams:
                    sid = s.get("lecture_id")
                    ss = s.get("sources")
                    sc = s.get("sources_count")
                    if sid == _id:
                        i.update({"sources": ss, "sources_count": sc})
        if sub_ids:
            sub_ids = list(set(sub_ids))
            subtitles = self._extract_subtitle(sub_ids)
            for i in _temp:
                for s in subtitles:
                    if i.get("subtitle_id") == s.get("subtitle_id"):
                        i.update({"subtitle_url": s.get("url")})
        return _temp

    def _real_extract(self, course_id):

        acloud = {}
        courses_ids = {"courseIds": [course_id]}
        GRAPH_QUERY_COURSE_INFO.update({"variables": courses_ids})
        query = GRAPH_QUERY_COURSE_INFO

        try:
            response = self._session._post(PUBLIC_GRAPHQL_URL, query)
        except conn_error as e:
            sys.stdout.write(
                fc
                + sd
                + "["
                + fr
                + sb
                + "-"
                + fc
                + sd
                + "] : "
                + fr
                + sb
                + "Connection error : make sure your internet connection is working.\n"
            )
            time.sleep(0.8)
            sys.exit(0)
        else:
            course = response.json().get("data")
            # json.dump(course, open("course.json", "w"), indent=4)
            if course:
                course = course["courseOverviews"][0]
                course_url = course.get("url")
                course_title = self._sanitize(course.get("title"))
                course_id = course.get("uniqueid")
                chapters = course.get("sections")

                acloud["course_id"] = course_id
                acloud["course_url"] = course_url
                acloud["course_title"] = course_title
                acloud["total_chapters"] = len(chapters)
                acloud["total_lectures"] = sum(
                    [len(chapter.get("components", [])) for chapter in chapters]
                )
                acloud["chapters"] = []

                for entry in chapters:
                    chapter_title = self._sanitize(entry.get("title"))
                    chapter_id = entry.get("sectionIdentifier")
                    chapter_url = entry.get("url")
                    chapter_index = int(entry.get("sequence")) + 1
                    lectures_count = len(entry.get("components"))
                    lectures = entry.get("components")
                    chapter = "{0:02d} {1!s}".format(chapter_index, chapter_title)
                    acloud["chapters"].append(
                        {
                            "chapter_title": chapter,
                            "chapter_id": chapter_id,
                            "chapter_index": chapter_index,
                            "lectures_count": lectures_count,
                            "chapter_url": chapter_url,
                            "lectures": self._extract_lectures(lectures),
                        }
                    )
                acloud = self._extract_course_information(acloud)
            if not course:
                if response.headers.get("x-amzn-ErrorType"):
                    sys.stdout.write(
                        fc
                        + sd
                        + "["
                        + fr
                        + sb
                        + "-"
                        + fc
                        + sd
                        + "] : "
                        + fr
                        + sb
                        + "Authorization error : it seems your authorization token is expired.\n"
                    )
                    sys.stdout.write(
                        fc
                        + sd
                        + "["
                        + fm
                        + sb
                        + "i"
                        + fc
                        + sd
                        + "] : "
                        + fg
                        + sb
                        + "Login again & copy Request headers for a single request to file..\n"
                    )
                    sys.exit(0)

        # json.dump(acloud, open("course-test01.json", "w"), indent=4)
        # exit(0)
        return acloud
