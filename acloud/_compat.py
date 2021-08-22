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

import re
import os
import sys
import time
import json
import html
import codecs
import requests
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
NO_DEFAULT = object()

# 'https://prod-api.acloud.guru/bff/graphql/public'
PUBLIC_GRAPHQL_URL = "https://prod-api.acloud.guru/bff/graphql"
PROTECTED_GRAPHQL_URL = "https://prod-api.acloud.guru/bff/graphql/protected"

# queries ..
GRAPH_QUERY_COURSES = {
    "query": "query getAccessibleCourses{getAccessibleCourses{...courseFields}}fragment courseFields on CondensedCourse{title,uniqueid}",
    "variables": {},
}
GRAPH_QUERY_DOWNLOAD_LINKS = {
    "query": "query getRestrictedFiles($files: [Files]!) { getRestrictedFiles(files: $files) { urls } }",
    "variables": {"files": []},
}
GRAPH_QUERY_COURSE_INFO = {
    "query": 'query courseOverviews($courseIds: [String!]) {courseOverviews(courseIds: $courseIds) {purchaseProductId shortTitle title type id url lectureCount quizCount isPublic publishedDate decommissionedDate duration topics { name } vendors { name } includesPracticeExams includesQuizzes isVisible metadata { createdDate notifyUpdatedDate updatedDate } sections { id courseId description title sequence url components { id title description url sequence courseId sectionId enhancedSyllabus metadata { createdDate notifyUpdatedDate updatedDate }resources { title url key bucket }content { type ... on VideoCourseComponentContent { contentId duration videoposter videosources(filter: { videoType: "video/mp4" }) { quality duration bucket key filesize type signedUrl }}... on QuizCourseComponentContent { quizId name quizName quizType duration }... on LabCourseComponentContent { description quickLabsId labImage }... on HandsOnLabComponentContent { labId duration }... on WhitepaperCourseComponentContent { url }... on TextCourseComponentContent { textsources { key bucket }}}}}}}',
    "variables": {"courseIds": []},
}


GRAPH_QUERY_UNPROTECTED_DOWNLOAD_LINKS = {
    "query": "query getUnprotectedContents($contentIds: [String!]!) {getUnprotectedContents(contentIds: $contentIds) {contentId,createdDate,transcodeStatus,transcodeStatusMessage,finishedDate,duration,mediaType,thumbnailList {url}sources {...SourceFragment,}adaptiveStreams {playlistKey,ext,streamType,segmentDuration,signedUrl,sources {...SourceFragment,}}}}fragment SourceFragment on AudioVisualSource {sourceType,ext,key,presetId,fileSize,duration,audioBitRate,audioMaxBitRate,frameRate,height,maxHeight,width,maxWidth,videoBitRate,videoMaxBitRate,segmentDuration,signedUrl,}",
    "variables": {"contentIds": []},
}

GRAPH_QUERY_SUBTITLE_LINKS = {
    "query": "query subtitleTranscription($contentIds: [String!]) {subtitleTranscription(contentIds: $contentIds) {id status transcriptionType subtitleUrl lastUpdated visibility}}",
    "variables": {"contentIds": []},
}

GRAPH_QUERY_QUIZ_OVERVIEW = {
    "query": """
            query Assessments_assessment($id: String) {
                Assessments_assessment(id: $id) {
                    id
                    title
                    description
                    numberOfQuestions
                    skillLevel
                    __typename
                }
                Assessments_attemptHistory(id: $id) {
                    id
                    status
                    grade {
                        score
                        __typename
                    }
                    createdDate
                    __typename
                }
            }
    """,
    "variables": {"id": ""},
}

GRAPH_QUERY_QUIZ_CONTENT = {
    "query": """
            mutation Assessments_createAttempt($input: Assessments_CreateAttemptInput!) {
                Assessments_createAttempt(input: $input) {
                    ... on Assessments_Attempt {
                        id
                        title
                        description
                        numberOfQuestions
                        skillLevel
                        questions {
                            id
                            questionId
                            questionText
                            type
                            possibleCorrect
                            choices {
                                id
                                text
                                __typename
                            }
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
            }
    """,
    "variables": {"input": {"assessmentId": ""}},
}

GRAPH_QUERY_QUIZ_ANSWER = {
    "operationName": "Assessments_submitChoices",
    "query": """
            mutation Assessments_submitChoices($input: Assessments_SubmitChoicesInput!) {
                Assessments_submitChoices(input: $input) {
                    ... on Assessments_QuestionResults {
                        isCorrect
                        correctAnswers {
                            id
                            questionId
                            text
                            explanation
                            correctAnswer
                            __typename
                        }
                        incorrectSelectedAnswers {
                            id
                            questionId
                            text
                            explanation
                            correctAnswer
                            __typename
                        }
                        __typename
                    }
                    __typename
                }
            }
    """,
    "variables": {
        "input": {
            "attemptId": "",
            "questionId": "",
            "selectedChoiceIds": []
        }
    },
}

GRAPH_QUERY_UseHasCourseAccess = {
    "operationName": "UseHasCourseAccess",
    "variables": {},
    "query": "query UseHasCourseAccess {  userAccessibleCourses(courseIds: []) { id  title  __typename  }}",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15",
    "Host": "prod-api.acloud.guru",
}


__ALL__ = [
    "re",
    "os",
    "sys",
    "time",
    "json",
    "html",
    "pyver",
    "codecs",
    "encoding",
    "requests",
    "conn_error",
    "http_error",
    "compat_urlerr",
    "compat_opener",
    "compat_urllib",
    "compat_urlopen",
    "compat_request",
    "compat_httperr",
    "compat_urlparse",
    "compat_HTMLParser",
    "ParseCookie",
    "HEADERS",
    "NO_DEFAULT",
    "PUBLIC_GRAPHQL_URL",
    "PROTECTED_GRAPHQL_URL",
    "GRAPH_QUERY_COURSES",
    "GRAPH_QUERY_COURSE_INFO",
    "GRAPH_QUERY_QUIZ_CONTENT",
    "GRAPH_QUERY_QUIZ_ANSWER",
    "GRAPH_QUERY_QUIZ_OVERVIEW",
    "GRAPH_QUERY_DOWNLOAD_LINKS",
    "GRAPH_QUERY_SUBTITLE_LINKS",
    "GRAPH_QUERY_UseHasCourseAccess",
    "GRAPH_QUERY_UNPROTECTED_DOWNLOAD_LINKS",
]
