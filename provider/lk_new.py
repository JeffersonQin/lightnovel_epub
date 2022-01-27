import time
import sys
import traceback
import os
import requests
import js2py
from bs4 import BeautifulSoup

from utils import downloader
from utils import echo


DUMP_PATH = './dump'
DOCUMENT_DOWNLOAD_HEADERS = {
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	'accept-encoding': 'gzip, deflate, br',
	'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
	'cache-control': 'no-cache',
	'pragma': 'no-cache',
	'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Microsoft Edge";v="92"',
	'sec-ch-ua-mobile': '?0',
	'sec-fetch-dest': 'document',
	'sec-fetch-mode': 'navigate',
	'sec-fetch-site': 'same-origin',
	'sec-fetch-user': '?1',
	'upgrade-insecure-requests': '1',
	'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.84'
}
IMAGE_DOWNLOAD_HEADERS = {
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


def process_series_page(url):
	'''
	Process the series page.
	:param url: url to process
	'''
	echo.push_subroutine(sys._getframe().f_code.co_name)

	res = downloader.download_webpage(url, DOCUMENT_DOWNLOAD_HEADERS)
	# parse
	try:
		soup = BeautifulSoup(res, 'lxml')
		scripts = soup.find_all('script')

		for script in scripts:
			if script.string is not None:
				if script.string.startswith('window.__NUXT__'):
					context = js2py.EvalJs()
					context.execute(script.string)
					
					data = context.window.__NUXT__.to_dict()
					return data['data'][0]['series']['articles']
	except Exception as e:
		echo.cerr(f'error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('PARSING FAILED')
	finally:
		echo.pop_subroutine()


def obtain_article_content(url):
	'''
	download web content
	:param url: url to download
	'''
	echo.push_subroutine(sys._getframe().f_code.co_name)

	res = downloader.download_webpage(url, DOCUMENT_DOWNLOAD_HEADERS)
	# parse
	try:
		soup = BeautifulSoup(res, 'lxml')
		article = soup.find('article', id='article-main-contents')
	except Exception as e:
		echo.cerr(f'error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('PARSING FAILED')

	echo.pop_subroutine()
	return str(article)


def download_images(content, dump_path):
	"""
	download images from content
	:param content: html content
	:param dump_path: path to dump updated html
	:return:
	"""
	echo.push_subroutine(sys._getframe().f_code.co_name)
	
	echo.clog(f'Start Parsing Images')

	# parse images
	try:
		soup = BeautifulSoup(content, 'lxml')
		images = soup.find_all('img')
	except Exception as e:
		echo.cerr(f'Error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('PARSING FAILED')
	# download images
	try:
		i = 0
		for tag in images:
			i += 1
			echo.clog(f'Processing images: ({i} / {len(images)})')
			# parse
			link = str(tag.attrs['src'])
			if link.startswith('http') or link.startswith('//'):
				file_name = link.split('?')[0].split('/')[-1]
				file_dir = os.path.join(DUMP_PATH, file_name)
				# download
				downloader.download_file(link, file_dir, IMAGE_DOWNLOAD_HEADERS)
				# replace src
				tag.attrs['src'] = os.path.abspath(file_dir)
				# update html
				with open(dump_path, 'w', encoding='utf-8') as f:
					f.write(str(soup))
		return str(soup)
	except Exception as e:
		echo.cerr(f'error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('DOWNLOAD FAILED')
	finally:
		echo.pop_subroutine()


def process_article_page(url, dump_path):
	'''
	Process the article page.
	:param url: url to process
	:param dump_path: path to dump html
	:return: string of html content
	'''
	echo.push_subroutine(sys._getframe().f_code.co_name)

	try:
		flag = True
		# obtain html
		if dump_path is not None:
			if os.path.exists(dump_path):
				with open(dump_path, 'r', encoding='utf-8') as f:
					content = f.read()
				flag = False
		if flag:
			content = obtain_article_content(url)
			if dump_path is None:
				dump_path = os.path.join(DUMP_PATH, f'./{time.time_ns()}.html')
			with open(dump_path, 'w', encoding='utf-8') as f:
				f.write(content)
			echo.clog(f'Dumped HTML to {dump_path}')
		# download images
		content = download_images(content, dump_path)

		return content
	except Exception as e:
		echo.cerr(f'error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('PROCESS PAGE FAILED')
	finally:
		echo.pop_subroutine()


def get_contents(url, dump_path, html_dump):
	'''
	Get contents from url.
	:param url: url to process
	:param dump_path: path to dump things
	:param html_dump: html dump path
	'''
	global DUMP_PATH
	DUMP_PATH = dump_path

	echo.push_subroutine(sys._getframe().f_code.co_name)
	try:
		if 'series' in url:
			contents = []
			# series
			articles = process_series_page(url)
			i = 0
			for article in articles:
				i += 1
				echo.clog(f'Processing article {i} / {len(articles)}')
				a_title = article["title"]
				aid = article["aid"]
				echo.clog(f'Title: {a_title}')
				echo.clog(f'Article ID: {aid}')
				a_url = f'https://www.lightnovel.us/cn/detail/{aid}/'
				a_dump_path = os.path.join(dump_path, f'{aid}.html')
				a_content = process_article_page(a_url, a_dump_path)
				contents.append({
					'title': a_title,
					'content': a_content
				})
		else:
			# article
			contents = process_article_page(url, html_dump)
		
		return contents
	except Exception as e:
		echo.cerr(f'error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('GET CONTENTS FAILED')
	finally:
		echo.pop_subroutine()


def get_cover(cover_link, dump_path):
	'''
	Get cover from link.
	:param cover_link: link to cover
	:param dump_path: path to dump cover
	'''
	echo.push_subroutine(sys._getframe().f_code.co_name)
	try:
		cover_name = self.cover_link.split('?')[0].split('/')[-1]
		cover_dir = os.path.join(dump_path, cover_name)
		downloader.download_file(self.cover_link, cover_dir, IMAGE_DOWNLOAD_HEADERS)
		return cover_dir
	except Exception as e:
		echo.cerr(f'error: {repr(e)}')
		traceback.print_exc()
		echo.cexit('GET COVER FAILED')
	finally:
		echo.pop_subroutine()
