#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import acloud
import argparse

from pprint import pprint
from acloud import __version__
from acloud._colorized import *
from acloud._compat import pyver
from acloud._getpass import GetPass
from acloud._progress import ProgressBar
from acloud._colorized.banner import banner
getpass = GetPass()



class CloudGuru(ProgressBar):

	def __init__(self, cookies=''):
		self.cookies = cookies
		super(CloudGuru, self).__init__()

	def course_list_down(self):
		course = acloud.courses(cookies=self.cookies)
		course_id = course.id
		course_name = course.title
		chapters = course.get_chapters()
		total_lectures = course.lectures
		total_chapters = course.chapters
		sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Course " + fb + sb + "'%s'.\n" % (course_name))
		sys.stdout.write (fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Chapter(s) (%s).\n" % (total_chapters))
		sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) (%s).\n" % (total_lectures))
		for chapter in chapters:
			chapter_id = chapter.id
			chapter_index = chapter.index
			chapter_title = chapter.title
			lectures = chapter.get_lectures()
			lectures_count = chapter.lectures
			sys.stdout.write ('\n' + fc + sd + "[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%s)\n" % (chapter_title))
			sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) (%s).\n" % (lectures_count))
			for lecture in lectures:
				lecture_id = lecture.id
				lecture_index = lecture.index
				lecture_title = lecture.title
				lecture_best = lecture.getbest()
				lecture_streams = lecture.streams
				lecture_assets = lecture.assets
				if lecture_streams:
					sys.stdout.write(fc + sd + "     - " + fy + sb + "duration   : " + fm + sb + str(lecture.duration)+ fy + sb + ".\n")
					sys.stdout.write(fc + sd + "     - " + fy + sb + "Lecture id : " + fm + sb + str(lecture_id)+ fy + sb + ".\n")
					for stream in lecture_streams:
						content_length = stream.get_filesize()
						if content_length != 0:
							if content_length <= 1048576.00:
								size = round(float(content_length) / 1024.00, 2)
								sz = format(size if size < 1024.00 else size/1024.00, '.2f')
								in_MB = 'KB' if size < 1024.00 else 'MB'
							else:
								size = round(float(content_length) / 1048576, 2)
								sz = format(size if size < 1024.00 else size/1024.00, '.2f')
								in_MB = "MB " if size < 1024.00 else 'GB '
							if lecture_best.dimention[1] == stream.dimention[1]:
								in_MB = in_MB + fc + sb + "(Best)" + fg + sd
							sys.stdout.write('\t- ' + fg + sd + "{:<23} {:<8}{}{}{}{}\n".format(str(stream), str(stream.dimention[1]) + 'p', sz, in_MB, fy, sb))
							time.sleep(0.5)
				if lecture_assets:
					for asset in lecture_assets:
						if asset.mediatype != 'external_link':
							content_length = asset.get_filesize()
							if content_length != 0:
								if content_length <= 1048576.00:
									size = round(float(content_length) / 1024.00, 2)
									sz = format(size if size < 1024.00 else size/1024.00, '.2f')
									in_MB = 'KB' if size < 1024.00 else 'MB'
								else:
									size = round(float(content_length) / 1048576, 2)
									sz = format(size if size < 1024.00 else size/1024.00, '.2f')
									in_MB = "MB " if size < 1024.00 else 'GB '
								sys.stdout.write('\t- ' + fg + sd + "{:<23} {:<8}{}{}{}{}\n".format(str(asset), asset.extension, sz, in_MB, fy, sb))

	def download_assets(self, lecture_assets='', filepath=''):
		if lecture_assets:
			for assets in lecture_assets:
				title = assets.filename
				mediatype = assets.mediatype
				if mediatype == "external_link":
					assets.download(filepath=filepath, quiet=True, callback=self.show_progress)
				else:
					sys.stdout.write(fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading asset(s)\n")
					sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading (%s)\n" % (title))
					try:
						retval = assets.download(filepath=filepath, quiet=True, callback=self.show_progress)
					except KeyboardInterrupt:
						sys.stdout.write (fc + sd + "\n[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
						sys.exit(0)
					else:
						msg     = retval.get('msg')
						if msg == 'already downloaded':
							sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Asset : '%s' " % (title) + fy + sb + "(already downloaded).\n")
						elif msg == 'download':
							sys.stdout.write (fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Downloaded  (%s)\n" % (title))
						else:
							sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Asset : '%s' " % (title) + fc + sb + "(download skipped).\n")
							sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "{}\n".format(msg))

	def download_lectures(self, lecture_best='', lecture_title='', inner_index='', lectures_count='', filepath=''):
		if lecture_best:
			sys.stdout.write(fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) : ({index} of {total})\n".format(index=inner_index, total=lectures_count))
			sys.stdout.write(fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Downloading (%s)\n" % (lecture_title))
			try:
				retval = lecture_best.download(filepath=filepath, quiet=True, callback=self.show_progress)
			except KeyboardInterrupt:
				sys.stdout.write (fc + sd + "\n[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
				sys.exit(0)
			msg = retval.get('msg')
			if msg == 'already downloaded':
				sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture : '%s' " % (lecture_title) + fy + sb + "(already downloaded).\n")
			elif msg == 'download':
				sys.stdout.write (fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Downloaded  (%s)\n" % (lecture_title))
			else:
				sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture : '%s' " % (lecture_title) + fc + sb + "(download skipped).\n")
				sys.stdout.write (fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "{}\n".format(msg))

	def download_lectures_only(self, lecture_best='', lecture_title='', inner_index='', lectures_count='', lecture_assets='', filepath=''):
		if lecture_best:
			self.download_lectures(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=inner_index, lectures_count=lectures_count, filepath=filepath)
		if lecture_assets:
			self.download_assets(lecture_assets=lecture_assets, filepath=filepath)

	def course_download(self, path='', quality=''):
		course = acloud.courses(cookies=self.cookies)
		course_id = course.id
		course_name = course.title
		chapters = course.get_chapters()
		total_lectures = course.lectures
		total_chapters = course.chapters
		sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sb + "Course " + fb + sb + "'%s'.\n" % (course_name))
		sys.stdout.write (fc + sd + "[" + fm + sb + "+" + fc + sd + "] : " + fg + sd + "Chapter(s) (%s).\n" % (total_chapters))
		sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Lecture(s) (%s).\n" % (total_lectures))
		if path:
			if '~' in path:
				path = os.path.expanduser(path)
			course_path = "%s\\%s" % (path, course_name) if os.name == 'nt' else "%s/%s" % (path, course_name)
		else:
			path = os.getcwd()
			course_path = "%s\\%s" % (path, course_name) if os.name == 'nt' else "%s/%s" % (path, course_name)
		for chapter in chapters:
			chapter_id = chapter.id
			chapter_index = chapter.index
			chapter_title = chapter.title
			lectures = chapter.get_lectures()
			lectures_count = chapter.lectures
			filepath = "%s\\%s" % (course_path, chapter_title) if os.name == 'nt' else "%s/%s" % (course_path, chapter_title)
			status = course.create_chapter(filepath=filepath)
			sys.stdout.write (fc + sd + "\n[" + fm + sb + "*" + fc + sd + "] : " + fm + sb + "Downloading chapter : ({index} of {total})\n".format(index=chapter_index, total=total_chapters))
			sys.stdout.write (fc + sd + "[" + fw + sb + "+" + fc + sd + "] : " + fw + sd + "Chapter (%s)\n" % (chapter_title))
			sys.stdout.write (fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "Found (%s) lectures ...\n" % (lectures_count))
			for lecture in lectures:
				lecture_id = lecture.id
				lecture_index = lecture.index
				lecture_title = lecture.title
				lecture_best = lecture.getbest()
				lecture_streams = lecture.streams
				lecture_assets = lecture.assets
				lecture_best = lecture.get_quality(best_quality=lecture_best, streams=lecture_streams, requested=quality)
				self.download_lectures_only(lecture_best=lecture_best, lecture_title=lecture_title, inner_index=lecture_index, lectures_count=lectures_count, lecture_assets=lecture_assets, filepath=filepath)


def main():
	sys.stdout.write(banner())
	version     = "%(prog)s {version}".format(version=__version__)
	description = 'A cross-platform python based utility to download courses from acloud.guru for personal offline use.'
	parser = argparse.ArgumentParser(description=description, conflict_handler="resolve")
	general = parser.add_argument_group("General")
	general.add_argument(
		'-h', '--help',\
		action='help',\
		help="Shows the help.")
	general.add_argument(
		'-v', '--version',\
		action='version',\
		version=version,\
		help="Shows the version.")

	authentication = parser.add_argument_group("Authentication")
	authentication.add_argument(
		'-c', '--cookies',\
		dest='cookies',\
		type=str,\
		help="Cookies to authenticate with.",metavar='')
	advance = parser.add_argument_group("Advance")
	advance.add_argument(
		'-o', '--output',\
		dest='output',\
		type=str,\
		help="Download to specific directory.",metavar='')
	advance.add_argument(
		'-q', '--quality',\
		dest='quality',\
		type=int,\
		help="Download specific video quality.",metavar='')
	advance.add_argument(
		'-i', '--info',\
		dest='info',\
		action='store_true',\
		help="List all lectures with available resolution.")

	options = parser.parse_args()

	if not options.cookies:
		
		prompt = fc + sd + "[" + fm + sb + "*" + fc + sd + "] : " + fg + sd + "cookie filename : " + fg + sb
		filename = getpass._getuser(prompt=prompt)
		
		if os.path.isfile(filename):
			
			f_in = open(filename)
			cookies = '\n'.join([line for line in (l.strip() for l in f_in) if line])
			f_in.close()

			acloud = CloudGuru(cookies=cookies)

			if options.info:
				acloud.course_list_down()

			if not options.info:
				acloud.course_download(path=options.output, quality=options.quality)

		else:
			sys.stdout.write('\n' + fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "file containing request headers is required.\n")
			sys.exit(0)

	if options.cookies:
		if os.path.isfile(options.cookies):
			f_in = open(options.cookies)
			cookies = '\n'.join([line for line in (l.strip() for l in f_in) if line])
			f_in.close()

			acloud = CloudGuru(cookies=cookies)

			if options.info:
				acloud.course_list_down()

			if not options.info:
				acloud.course_download(path=options.output, quality=options.quality)
		else:
			sys.stdout.write('\n' + fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sb + "unable to find file '%s'.\n" % (options.cookies))
			sys.exit(0)

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		sys.stdout.write ('\n' + fc + sd + "[" + fr + sb + "-" + fc + sd + "] : " + fr + sd + "User Interrupted..\n")
		sys.exit(0)