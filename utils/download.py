import sys
import requests
import unicodedata
import re
import click
import traceback

from utils import echo

def download_file(url, dir):
	echo.push_subroutine(sys._getframe().f_code.co_name)

	echo.clog(f'start downloading: {url} => {dir}')
	try:
		# define request headers
		headers = {
			'accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
			'accept-encoding': 'gzip, deflate, br',
			'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
			'cache-control': 'no-cache',
			'pragma': 'no-cache',
			'referer': 'https://www.lightnovel.us/',
			'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Microsoft Edge";v="92"',
			'sec-ch-ua-mobile': '?0',
			'sec-fetch-dest': 'image',
			'sec-fetch-mode': 'no-cors',
			'sec-fetch-site': 'same-site',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84',
		}
		# start and block request
		r = requests.get(url, stream=True, headers=headers)
		# obtain content length
		length = int(r.headers['content-length'])
		echo.clog(f'file size: {size_description(length)}')
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
		return 1
	except Exception as err:
		echo.cerr(f'Error: {repr(err)}')
		traceback.print_exc()
		return 0
	finally:
		echo.pop_subroutine()


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
