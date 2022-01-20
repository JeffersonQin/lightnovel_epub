import sys
import requests
import os
import unicodedata
import re
import click
import traceback

from utils import echo

def _download_file(url, dir, headers):
	echo.push_subroutine(sys._getframe().f_code.co_name)

	echo.clog(f'start downloading: {url} => {dir}')
	ret = 0
	try:
		# start and block request
		r = requests.get(url, stream=True, headers=headers, timeout=3000)
		# obtain content length
		length = int(r.headers['content-length'])
		echo.clog(f'file size: {size_description(length)}')
		if os.path.exists(dir) and os.path.getsize(dir) == length:
			echo.clog(f'file already exists {dir}')
		else:
			# start writing
			f = open(dir, 'wb+')
			# show in progressbar
			with click.progressbar(label="Downloading from remote: ", length=length) as bar:
				for chunk in r.iter_content(chunk_size = 512):
					if chunk:
						f.write(chunk)
						bar.update(len(chunk))
			echo.csuccess('Download Complete.')
			f.close()
	except Exception as err:
		echo.cerr(f'Error: {repr(err)}')
		traceback.print_exc()
		ret = 1
	finally:
		echo.pop_subroutine()
		return ret


def download_file(url, dir, headers, trial=5):
	fail_count = 0
	while True:
		ret = _download_file(url, dir, headers)
		if ret == 0:
			return
		if fail_count < trial:
			fail_count += 1
			echo.cerr(f'Download failed, Trial {fail_count}/{trial}')
		else:
			echo.cexit('Download failed. Exceeded trial limit.')


def _download_webpage(url, headers, encoding):
	'''
	Download webpage from url.
	:param url: url to download
	'''
	echo.push_subroutine(sys._getframe().f_code.co_name)

	echo.clog(f'start downloading: {url} => memory')
	# download
	try:
		return requests.get(url=url, headers=headers).content.decode(encoding)
	except Exception as e:
		echo.cerr(f'error: {repr(e)}')
		traceback.print_exc()
		return -1
	finally:
		echo.pop_subroutine()


def download_webpage(url, headers, encoding='utf-8', trial=5):
	'''
	Download webpage from url.
	:param url: url to download
	:param trial: number of trials
	'''
	fail_count = 0
	while True:
		ret = _download_webpage(url, headers, encoding)
		if ret != -1:
			return ret
		if fail_count < trial:
			fail_count += 1
			echo.cerr(f'Download failed, Trial {fail_count}/{trial}')
		else:
			echo.cexit('Download failed. Exceeded trial limit.')


def size_description(size):
	'''
	Taken and modified from https://blog.csdn.net/wskzgz/article/details/99293181
	'''
	def strofsize(integer, remainder, level):
		if integer >= 1024:
			remainder = integer % 1024
			integer //= 1024
			level += 1
			return strofsize(integer, remainder, level)
		else:
			return integer, remainder, level

	units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
	integer, remainder, level = strofsize(size, 0, 0)
	if level + 1 > len(units):
		level = -1
	return ( '{}.{:>03d} {}'.format(integer, remainder, units[level]) )
