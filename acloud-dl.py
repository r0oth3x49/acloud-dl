#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=E,C,W,R

import sys
import time
import acloud
import argparse

from acloud import __version__
from acloud._colorized import *
from acloud._getpass import GetPass
from acloud._vtt2srt import WebVtt2Srt
from acloud._progress import ProgressBar
from acloud._colorized.banner import banner

getpass = GetPass()


class CloudGuru(WebVtt2Srt, ProgressBar, GetPass):

    def __init__(self, cookies=''):
        self.cookies = cookies
        super(CloudGuru, self).__init__()

    @staticmethod
    def courses_not_downloaded(coursesList, path="", isFiltering=False):
        if not isFiltering or path == "":
            return coursesList

        res = list()
        downloaded_courses = os.listdir(path)
        for course in coursesList:
            cr_name = '{}'.format(course)
            if cr_name in downloaded_courses:
                continue
            res.append(course)
        return res

    def courses_downloaded(self, path='', download_all=False, download_only_new=False):
        sys.stdout.write('\033[2K\033[1G\r\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb +
                         "Downloading accessible courses information .. \r")
        courses = self.courses_not_downloaded(acloud.courses(cookies=self.cookies), path, download_only_new)

        if not download_all:
            sys.stdout.write('\033[2K\033[1G\r\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb +
                             "Downloading accessible courses information .. (done)\r\n")
            counter = 1
            for course in courses:
                title = course.title
                sys.stdout.write(fc + sd + "[" + fm + sb + "%s" % counter + fc + sd + "] : " + fg + sb + "%s\n" % title)
                counter += 1
            question = fc + sd + "[" + fw + sb + "?" + fc + sd + "] : " + fy + sb + "select course number or range (1/%s/range): " % (len(courses)) + fg + sb
            ask_user = self._getuser(prompt=question)
            # setting default to download all if no user input is provided
            if ask_user and ask_user[-1] == '+':
                course_number = int(ask_user.split('+')[0])
                if 0 < course_number <= len(courses):
                    course_number = course_number - 1
                    courses = courses[course_number:len(courses)]
            elif ask_user and ask_user[-1] != "+":
                course_number = int(ask_user)
                if 0 < course_number <= len(courses):
                    course_number = course_number - 1
                    courses = [courses[course_number]]
            else:
                download_all = True

        for course in courses:
            course_name = course.title
            sys.stdout.write(
                "\n" + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Course " + fb + sb + "'%s'.\n" % course_name)
            sys.stdout.write(
                '\033[2K\033[1G\r\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading course information .. \r")
            course = course.get_course(keep_alive=download_all)
            sys.stdout.write(
                '\033[2K\033[1G\r\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloaded course information .. (done)\r\n")
            chapters = course.get_chapters()
            total_lectures = course.lectures
            total_chapters = course.chapters
            sys.stdout.write(
                fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Chapter(s) (%s).\n" % total_chapters)
            sys.stdout.write(
                fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) (%s).\n" % total_lectures)
            for chapter in chapters:
                chapter_title = chapter.title
                lectures = chapter.get_lectures()
                lectures_count = chapter.lectures
                sys.stdout.write(
                    '\n' + fc + sd + "[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%s)\n" % chapter_title)
                sys.stdout.write(
                    fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) (%s).\n" % lectures_count)
                for lecture in lectures:
                    lecture_id = lecture.id
                    lecture_best = lecture.getbest()
                    lecture_streams = lecture.streams
                    lecture_assets = lecture.assets
                    if lecture_streams:
                        sys.stdout.write(fc + sd + "     - " + fy + sb + "duration   : " + fm + sb + str(
                            lecture.duration) + fy + sb + ".\n")
                        sys.stdout.write(fc + sd + "     - " + fy + sb + "Lecture id : " + fm + sb + str(
                            lecture_id) + fy + sb + ".\n")
                        for stream in lecture_streams:
                            content_length = stream.get_filesize()
                            if content_length != 0:
                                if content_length <= 1048576.00:
                                    size = round(float(content_length) / 1024.00, 2)
                                    sz = format(size if size < 1024.00 else size / 1024.00, '.2f')
                                    in_megabytes = 'KB' if size < 1024.00 else 'MB'
                                else:
                                    size = round(float(content_length) / 1048576, 2)
                                    sz = format(size if size < 1024.00 else size / 1024.00, '.2f')
                                    in_megabytes = "MB " if size < 1024.00 else 'GB '
                                if lecture_best.dimention[1] == stream.dimention[1]:
                                    in_megabytes = in_megabytes + fc + sb + "(Best)" + fg + sd
                                sys.stdout.write('\t- ' + fg + sd + "{:<23} {:<8}{}{}{}{}\n".format(str(stream), str(
                                    stream.dimention[1]) + 'p', sz, in_megabytes, fy, sb))
                                time.sleep(0.5)
                    if lecture_assets:
                        for asset in lecture_assets:
                            if asset.mediatype != 'external_link':
                                content_length = asset.get_filesize()
                                if content_length != 0:
                                    if content_length <= 1048576.00:
                                        size = round(float(content_length) / 1024.00, 2)
                                        sz = format(size if size < 1024.00 else size / 1024.00, '.2f')
                                        in_megabytes = 'KB' if size < 1024.00 else 'MB'
                                    else:
                                        size = round(float(content_length) / 1048576, 2)
                                        sz = format(size if size < 1024.00 else size / 1024.00, '.2f')
                                        in_megabytes = "MB " if size < 1024.00 else 'GB '
                                    sys.stdout.write(
                                        '\t- ' + fg + sd + "{:<23} {:<8}{}{}{}{}\n".format(str(asset), asset.extension,
                                                                                           sz, in_megabytes, fy, sb))

    def download_subtitles(self, subtitle='', filepath=''):
        if subtitle:
            filename = "%s\\%s" % (filepath, subtitle.filename) if os.name == 'nt' else "%s/%s" % (
                filepath, subtitle.filename)
            try:
                retval = subtitle.download(filepath=filepath, quiet=True)
            except KeyboardInterrupt:
                sys.stdout.write(fc + sd + "\n[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
                sys.exit(0)
            else:
                msg = retval.get('msg')
                if msg == "download":
                    self.convert(filename=filename)

    def download_assets(self, lecture_assets='', filepath=''):
        if lecture_assets:
            for assets in lecture_assets:
                title = assets.filename
                mediatype = assets.mediatype
                if mediatype == "external_link":
                    assets.download(filepath=filepath, quiet=True, callback=self.show_progress)
                else:
                    sys.stdout.write(
                        fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading asset(s)\n")
                    sys.stdout.write(
                        fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading (%s)\n" % title)
                    try:
                        retval = assets.download(filepath=filepath, quiet=True, callback=self.show_progress)
                    except KeyboardInterrupt:
                        sys.stdout.write(
                            fc + sd + "\n[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
                        sys.exit(0)
                    else:
                        msg = retval.get('msg')
                        if msg == 'already downloaded':
                            sys.stdout.write(
                                fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Asset : '%s' " % title + fy + sb + "(already downloaded).\n")
                        elif msg == 'download':
                            sys.stdout.write(
                                fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Downloaded  (%s)\n" % title)
                        else:
                            sys.stdout.write(
                                fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Asset : '%s' " % title + fc + sb + "(download skipped).\n")
                            sys.stdout.write(
                                fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "{}\n".format(msg))

    def download_lectures(self, lecture_best='', lecture_title='', inner_index='', lectures_count='', filepath='',
                          user_extension=''):
        if lecture_best:
            sys.stdout.write(
                fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) : ({index} of {total})\n".format(
                    index=inner_index, total=lectures_count))
            sys.stdout.write(
                fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading (%s)\n" % lecture_title)
            try:
                retval = lecture_best.download(filepath=filepath, quiet=True, user_extension=user_extension,
                                               callback=self.show_progress)
            except KeyboardInterrupt:
                sys.stdout.write(fc + sd + "\n[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
                sys.exit(0)
            msg = retval.get('msg')
            if msg == 'already downloaded':
                sys.stdout.write(
                    fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture : '%s' " % lecture_title + fy + sb + "(already downloaded).\n")
            elif msg == 'download':
                sys.stdout.write(
                    fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Downloaded  (%s)\n" % lecture_title)
            else:
                sys.stdout.write(
                    fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture : '%s' " % lecture_title + fc + sb + "(download skipped).\n")
                sys.stdout.write(fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "{}\n".format(msg))

    def download_lectures_only(self, lecture_best='', lecture_title='', inner_index='', lectures_count='',
                               lecture_assets='', lecture_subs='', filepath='', user_extension=''):
        if lecture_best:
            self.download_lectures(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=inner_index,
                                   lectures_count=lectures_count, filepath=filepath,
                                   user_extension=user_extension)
        if lecture_assets:
            self.download_assets(lecture_assets=lecture_assets, filepath=filepath)
        if lecture_subs:
            self.download_subtitles(subtitle=lecture_subs, filepath=filepath)

    def course_download(self, path='', quality='', user_extension='', download_all=False, download_only_new=False):
        sys.stdout.write(
            '\033[2K\033[1G\r\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading accessible courses information .. \r")
        courses = self.courses_not_downloaded(acloud.courses(cookies=self.cookies), path, download_only_new)

        if not download_all:
            sys.stdout.write(
                '\033[2K\033[1G\r\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading accessible courses information .. (done)\r\n")
            counter = 1
            for course in courses:
                title = course.title
                sys.stdout.write(fc + sd + "[" + fm + sb + "%s" % counter + fc + sd + "] : " + fg + sb + "%s\n" % title)
                counter += 1
            question = fc + sd + "[" + fw + sb + "?" + fc + sd + "] : " + fy + sb + "select course number or range (1/%s/range): " % (
                len(courses)) + fg + sb
            ask_user = self._getuser(prompt=question)
            # setting default to download all if no user input is provided
            if ask_user and ask_user[-1] == '+':
                course_number = int(ask_user.split('+')[0])
                if 0 < course_number <= len(courses):
                    course_number = course_number - 1
                    courses = courses[course_number:len(courses)]
            elif ask_user and ask_user[-1] != "+":
                course_number = int(ask_user)
                if 0 < course_number <= len(courses):
                    course_number = course_number - 1
                    courses = [courses[course_number]]
            else:
                download_all = True
        for course in courses:
            course_name = course.title
            sys.stdout.write(
                "\n" + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Course " + fb + sb + "'%s'.\n" % course_name)
            sys.stdout.write(
                '\033[2K\033[1G\r\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloading course information .. \r")
            course = course.get_course(keep_alive=download_all)
            sys.stdout.write(
                '\033[2K\033[1G\r\r' + fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Downloaded course information .. (done)\r\n")
            chapters = course.get_chapters()
            total_lectures = course.lectures
            total_chapters = course.chapters
            sys.stdout.write(
                fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Chapter(s) (%s).\n" % total_chapters)
            sys.stdout.write(
                fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) (%s).\n" % total_lectures)
            if path:
                if '~' in path:
                    path = os.path.expanduser(path)
                course_path = "%s\\%s" % (path, course_name) if os.name == 'nt' else "%s/%s" % (path, course_name)
            else:
                path = os.getcwd()
                course_path = "%s\\%s" % (path, course_name) if os.name == 'nt' else "%s/%s" % (path, course_name)
            for chapter in chapters:
                chapter_index = chapter.index
                chapter_title = chapter.title
                lectures = chapter.get_lectures()
                lectures_count = chapter.lectures
                filepath = "%s\\%s" % (course_path, chapter_title) if os.name == 'nt' else "%s/%s" % (
                    course_path, chapter_title)
                _ = course.create_chapter(filepath=filepath)
                sys.stdout.write(
                    fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fm + sb + "Downloading chapter : ({index} of {total})\n".format(
                        index=chapter_index, total=total_chapters))
                sys.stdout.write(
                    fc + sd + "[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%s)\n" % chapter_title)
                sys.stdout.write(
                    fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Found (%s) lectures ...\n" % lectures_count)
                for lecture in lectures:
                    lecture_index = lecture.index
                    lecture_title = lecture.title
                    lecture_best = lecture.getbest()
                    lecture_streams = lecture.streams
                    lecture_assets = lecture.assets
                    lecture_subs = lecture.subtitle
                    lecture_best = lecture.get_quality(best_quality=lecture_best, streams=lecture_streams,
                                                       requested=quality)
                    self.download_lectures_only(lecture_best=lecture_best, lecture_title=lecture_title,
                                                inner_index=lecture_index, lectures_count=lectures_count,
                                                lecture_assets=lecture_assets, lecture_subs=lecture_subs,
                                                filepath=filepath, user_extension=user_extension)


def main():
    sys.stdout.write(banner())
    version = "%(prog)s {version}".format(version=__version__)
    description = 'A cross-platform python based utility to download courses from acloud.guru for personal offline use.'
    parser = argparse.ArgumentParser(description=description, conflict_handler="resolve")
    general = parser.add_argument_group("General")
    general.add_argument(
        '-h', '--help',
        action='help',
        help="Shows the help.")
    general.add_argument(
        '-v', '--version',
        action='version',
        version=version,
        help="Shows the version.")

    authentication = parser.add_argument_group("Authentication")
    authentication.add_argument(
        '-c', '--cookies',
        dest='cookies',
        type=str,
        help="Cookies to authenticate with.", metavar='')
    advance = parser.add_argument_group("Advance")
    advance.add_argument(
        '-o', '--output',
        dest='output',
        type=str,
        help="Download to specific directory.", metavar='')
    advance.add_argument(
        '-q', '--quality',
        dest='quality',
        type=int,
        help="Download specific video quality.", metavar='')
    advance.add_argument(
        '-i', '--info',
        dest='info',
        action='store_true',
        help="List all lectures with available resolution.")
    advance.add_argument(
        '-a', '--all',
        dest='download_all',
        action='store_true',
        help="Download all courses without any prompt (default: false).")
    advance.add_argument(
        '-n', '--new',
        dest='download_only_new',
        action='store_true',
        help="Download only courses that have not already been downloaded (default: false).")
    advance.add_argument(
        '-e', '--extension',
        dest='extension',
        type=str,
        help="Rename course lecture video/audio files extension to defined by user.")

    options = parser.parse_args()

    if not options.cookies:

        prompt = fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "cookie filename : " + fg + sb
        filename = getpass._getuser(prompt=prompt)

        if os.path.isfile(filename):

            f_in = open(filename)
            cookies = '\n'.join([line for line in (lines.strip() for lines in f_in) if line])
            f_in.close()

            cloud_guru = CloudGuru(cookies=cookies)

            if options.info:
                cloud_guru.courses_downloaded(path=options.output, download_only_new=options.download_only_new)

            if not options.info:
                cloud_guru.course_download(path=options.output, quality=options.quality,
                                           user_extension=options.extension,
                                           download_all=options.download_all,
                                           download_only_new=options.download_only_new)

        else:
            sys.stdout.write(
                '\n' + fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "file containing request headers is required.\n")
            sys.exit(0)

    if options.cookies:
        if os.path.isfile(options.cookies):
            f_in = open(options.cookies)
            cookies = '\n'.join([line for line in (lines.strip() for lines in f_in) if line])
            f_in.close()

            cloud_guru = CloudGuru(cookies=cookies)

            if options.info:
                cloud_guru.courses_downloaded(path=options.output, download_only_new=options.download_only_new)

            if not options.info:
                cloud_guru.course_download(path=options.output, quality=options.quality,
                                           user_extension=options.extension,
                                           download_all=options.download_all,
                                           download_only_new=options.download_only_new)
        else:
            sys.stdout.write(
                '\n' + fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "unable to find file '%s'.\n" % options.cookies)
            sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.stdout.write('\n' + fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
        sys.exit(0)
